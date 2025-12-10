"""
Módulo de servicios de préstamos.

Proporciona la clase LoanService que maneja la lógica de negocio
de los préstamos: gestión de inventario, colas de reservas,
sincronización con usuarios y validaciones de negocio.
"""
from typing import Optional
from datetime import datetime
from app.domain.repositories import LoansRepository
from app.domain.structures import Queue, Stack
from app.domain.models import Loan, Book, User
from app.domain.algorithms import linear_search, insertion_sort
from app.domain.repositories.library import Library


class LoanService:
    """
    Servicio de préstamos de la biblioteca.

    Atributos:
        __loans_repository (LoansRepository): Repositorio para persistencia de préstamos.
        __loans_records (list[Loan]): Lista en memoria de préstamos activos.
        __reservations_queue (Queue): Cola de reservas para libros prestados.
        __users (list[User]): Lista de usuarios del sistema.
    """

    __loans_records: list[Loan]
    __reservations_queue: Queue[tuple[User, Book]]
    __users: list[User]

    def __init__(self, url: str, reservations_queue: Queue[tuple[User, Book]], users: list[User]) -> None:
        """
        Inicializa el servicio y carga los préstamos desde el repositorio.

        Args:
            url (str): URL o ruta de conexión al repositorio de préstamos.
            reservations_queue (Queue): Cola de reservas compartida.
            users (list[User]): Lista de usuarios del sistema.

        No devuelve nada. En caso de error, inicializa estructura vacía.
        """
        self.__loans_repository = LoansRepository(url)
        self.__reservations_queue = reservations_queue
        self.__users = users
        self.__load()

    def get_loans_records(self) -> list[Loan]:
        """
        Obtiene la lista de préstamos activos.

        Returns:
            list[Loan]: Lista de préstamos.
        """
        return self.__loans_records

    def get_reservations_queue(self) -> Queue[tuple[User, Book]]:
        """
        Obtiene la cola de reservas.

        Returns:
            Queue: Cola de reservas.
        """
        return self.__reservations_queue

    def __load(self):
        """
        Carga los préstamos desde el repositorio en las estructuras internas.

        Intenta leer todos los préstamos y actualizar estados de libros y usuarios.
        En caso de error inicializa estructuras vacías y registra el error por consola.
        """
        try:
            loans = self.__loans_repository.read_all()
            self.__loans_records = loans if loans else []
            
            # Actualizar estados de libros y usuarios
            for loan in self.__loans_records:
                try:
                    user = loan.get_user()
                    book = loan.get_book()
                    
                    # Actualizar usuario
                    if user:
                        user.add_loan(loan)
                    
                    # Actualizar libro
                    if book:
                        self.__mark_book_as_borrowed(book)
                        self.__remove_book_from_inventory(book)
                except Exception as e:
                    print(f"Error procesando préstamo durante carga: {e}")
                    
        except Exception as e:
            print(f"Error loading loans: {e}")
            self.__loans_records = []

    def __mark_book_as_borrowed(self, book: Book) -> None:
        """Marca un libro como prestado en el inventario global.
        
        Actualiza el estado en:
        - Stack de inventario completo (Library.get_inventary) - SOLO marca el flag
        - La instancia del libro
        
        Args:
            book (Book): Libro a marcar como prestado.
        """
        try:
            # Marcar en el inventario Stack (inventario completo - TODOS los libros)
            for inv_book in Library.get_inventary():
                if inv_book.get_id_IBSN() == book.get_id_IBSN():
                    inv_book.set_is_borrowed(True)
                    break
        except Exception as e:
            print(f"Error marking book as borrowed in inventory: {e}")
        
        try:
            # Marcar la instancia del libro
            book.set_is_borrowed(True)
        except Exception as e:
            print(f"Error marking book instance as borrowed: {e}")

    def __remove_book_from_inventory(self, book: Book) -> None:
        """Extrae un libro del inventario de disponibles al ser prestado.
        
        IMPORTANTE:
        - NO elimina del Stack de inventario (inventary) - ese contiene TODOS los libros
        - SÍ elimina de la lista ordenada (order_inventary) - esa solo contiene disponibles
        
        Args:
            book (Book): Libro a extraer del inventario de disponibles.
        """
        try:
            # Extraer SOLO de la lista ordenada (inventario de disponibles)
            order_books = Library.get_order_inventary()
            Library.set_order_inventary([b for b in order_books if b.get_id_IBSN() != book.get_id_IBSN()])
        except Exception as e:
            print(f"Error removing book from ordered inventory: {e}")
        
        # TODO: Implementar extracción desde bookcase/bookshelf cuando organizeroptimun esté disponible
        # self.__remove_from_bookcase(book)

    def __add_book_back_to_inventory(self, book: Book) -> None:
        """Reinserta un libro al inventario de disponibles cuando finaliza su préstamo.
        
        IMPORTANTE:
        - NO añade al Stack de inventario (inventary) - el libro nunca se eliminó de ahí
        - SÍ añade a la lista ordenada (order_inventary) - lo reintegra a disponibles
        - Marca el libro como disponible en el Stack de inventario
        - TODO: Reinsertar en Bookcase/Bookshelf cuando esté implementado
        
        Args:
            book (Book): Libro a reintegrar al inventario de disponibles.
        """
        try:
            # Marcar como disponible en el inventario Stack (TODOS los libros)
            for inv_book in Library.get_inventary():
                if inv_book.get_id_IBSN() == book.get_id_IBSN():
                    inv_book.set_is_borrowed(False)
                    break
        except Exception as e:
            print(f"Error unmarking book in inventory: {e}")
        
        try:
            # Marcar la instancia del libro como disponible
            book.set_is_borrowed(False)
        except Exception as e:
            print(f"Error unmarking book instance: {e}")
        
        try:
            # Reinsertar en la lista ordenada de disponibles manteniendo orden
            order_books = Library.get_order_inventary()
            order_books.append(book)
            order_books = insertion_sort(
                order_books,
                key=lambda b: b.get_id_IBSN()
            )
            Library.set_order_inventary(order_books)
        except Exception as e:
            print(f"Error adding book back to ordered inventory: {e}")
        
        # TODO: Implementar reinserción en bookcase/bookshelf cuando organizeroptimun esté disponible
        # self.__add_to_bookcase(book)

    def __process_reservation_queue(self, book: Book) -> bool:
        """Procesa la cola de reservas para un libro específico.
        
        Si hay reservas para el libro, crea automáticamente un nuevo préstamo
        para el usuario en la primera reserva y lo elimina de la cola.
        
        Args:
            book (Book): Libro cuyas reservas se van a procesar.
            
        Returns:
            bool: True si se procesó una reserva, False si no hay reservas.
        """
        try:
            reservations = self.__reservations_queue.to_list()
            for idx, (reserved_user, reserved_book) in enumerate(reservations):
                if reserved_book.get_id_IBSN() == book.get_id_IBSN():
                    print(f"Hay una reserva para este libro. Asignando al próximo usuario en la cola.")
                    # Crear el nuevo préstamo para el usuario en reserva
                    created = self.create_loan(reserved_user, reserved_book)
                    
                    if created is not None:
                        # Eliminar la reserva procesada y reconstruir la cola
                        reservations.pop(idx)
                        new_queue: Queue[tuple[User, Book]] = Queue()
                        for item in reservations:
                            new_queue.push(item)
                        self.__reservations_queue = new_queue
                        Library.set_reservationsQueue(new_queue)
                    return True
        except Exception as e:
            print(f"Error procesando cola de reservas: {e}")
        
        return False

    def create_loan(self, user: User, book: Book) -> Optional[Loan]:
        """Crea un nuevo préstamo y actualiza estados en inventario y usuario.
        
        Si el libro está prestado, lo añade a la cola de reservas.
        Si está disponible, crea el préstamo y actualiza:
        - Estado del libro (is_borrowed = True)
        - Inventario (extrae el libro)
        - Listas de préstamos del usuario
        - Registro global de préstamos
        
        Args:
            user (User): Usuario que solicita el préstamo.
            book (Book): Libro a prestar.
            
        Returns:
            Optional[Loan]: Préstamo creado, o None si está en reserva o hay error.
        """
        # Validar que se encontraron usuario y libro
        if user is None or book is None:
            print(f"Error: usuario o libro no encontrado. Usuario: {user}, Libro: {book}")
            return None
        
        # Si el libro ya está prestado, añadir a la cola de reservas
        if book.get_is_borrowed():
            print(f"Libro {book.get_id_IBSN()} ya está prestado. Añadiendo usuario a cola de reservas.")
            try:
                self.__reservations_queue.push((user, book))
                Library.set_reservationsQueue(self.__reservations_queue)
            except Exception as e:
                print(f"Error añadiendo a cola de reservas: {e}")
            return None
        
        # Crear el préstamo con datetime actual
        loan_data = {
            "user": user.to_dict(),
            "book": book.to_dict(),
            "loan_date": datetime.now().isoformat()
        }
        
        # Persistir en el repositorio
        try:
            loan = self.__loans_repository.create(loan_data)
        except Exception as e:
            print(f"Error persistiendo préstamo: {e}")
            return None
        
        # Actualizar lista de préstamos del usuario
        try:
            user.add_loan(loan)
        except Exception as e:
            print(f"Error añadiendo préstamo a usuario: {e}")
        
        # Marcar libro como prestado en todas las colecciones
        self.__mark_book_as_borrowed(book)
        
        # Extraer libro del inventario
        self.__remove_book_from_inventory(book)
        
        # Añadir a la lista local de préstamos
        try:
            self.__loans_records.append(loan)
        except Exception as e:
            print(f"Error añadiendo préstamo a registros: {e}")
        
        # Añadir al registro global de préstamos
        try:
            loan_records = Library.get_loanRecords()
            loan_records.append(loan)
            Library.set_loanRecords(loan_records)
        except Exception as e:
            print(f"Error actualizando registro global de préstamos: {e}")
        
        return loan

    def get_loan_by_id(self, id: str) -> Loan | None:
        """Lee un préstamo por su ID.

        Args:
            id (str): ID del préstamo.

        Returns:
            Loan | None: Préstamo encontrado, o None en caso de error.
        """
        try:
            loan = self.__loans_repository.read(id)
            return loan
        except Exception as e:
            print(f"Error reading loan: {e}")
            return None

    def read_all_loans(self) -> list[Loan] | None:
        """Recupera todos los préstamos del repositorio.

        Returns:
            list[Loan] | None: Lista de préstamos o None si no hay datos.
        """
        try:
            loans = self.__loans_repository.read_all()
            return loans
        except Exception as e:
            print(f"Error reading all loans: {e}")
            return None

    def update_loan(self, id: str, new_book: Book) -> Optional[Loan]:
        """Actualiza un préstamo existente reemplazando el libro.
        
        Proceso:
        1. Busca el préstamo por ID.
        2. Libera el libro anterior (lo marca disponible y lo reinserta al inventario).
        3. Si el nuevo libro está disponible, crea un nuevo préstamo.
        4. Procesa la cola de reservas para el libro anterior.
        5. Elimina el préstamo antiguo de los registros.
        
        Args:
            id (str): ID del préstamo a actualizar.
            new_book (Book): Nuevo libro para el préstamo.
            
        Returns:
            Optional[Loan]: Nuevo préstamo creado, o None si hay error.
        """
        # Buscar el préstamo a actualizar
        loan_to_update = self.__loans_repository.read(id)
        if loan_to_update is None:
            print(f"Préstamo {id} no encontrado para actualizar.")
            return None
        
        user = loan_to_update.get_user()
        old_book = loan_to_update.get_book()
        
        # Validar que se proporcionó un nuevo libro
        if new_book is None:
            print("No se proporcionó nuevo libro para la actualización. Operación abortada.")
            return None
        
        # Liberar el libro anterior
        self.__add_book_back_to_inventory(old_book)
        
        # Procesar reservas para el libro anterior
        self.__process_reservation_queue(old_book)
        
        # Validar que el nuevo libro no esté prestado
        if new_book.get_is_borrowed():
            print(f"Libro {new_book.get_id_IBSN()} ya está prestado. Añadiendo usuario a la cola de reservas.")
            try:
                self.__reservations_queue.push((user, new_book))
                Library.set_reservationsQueue(self.__reservations_queue)
            except Exception as e:
                print(f"Error añadiendo a cola de reservas: {e}")
            return None
        
        # Crear el nuevo préstamo
        new_loan = self.create_loan(user, new_book)
        
        # Eliminar el préstamo antiguo de los registros
        if new_loan is not None:
            try:
                self.__loans_repository.delete(id)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del repositorio: {e}")
            
            try:
                # Eliminar del registro global
                loan_records = Library.get_loanRecords()
                if loan_to_update in loan_records:
                    loan_records.remove(loan_to_update)
                    Library.set_loanRecords(loan_records)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del registro global: {e}")
            
            try:
                # Eliminar de la lista local
                if loan_to_update in self.__loans_records:
                    self.__loans_records.remove(loan_to_update)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo de la lista local: {e}")
            
            try:
                # Eliminar del usuario
                user.remove_loan(loan_to_update)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del usuario: {e}")
        
        return new_loan

    def delete_loan(self, id: str) -> bool:
        """Elimina un préstamo y reintegra el libro al inventario.
        
        Proceso:
        1. Busca el préstamo por ID.
        2. Marca el libro como disponible.
        3. Reintegra el libro al inventario (stack y lista ordenada).
        4. Procesa la cola de reservas para ese libro.
        5. Elimina el préstamo de los registros globales y locales.
        6. Elimina el préstamo de la lista de préstamos del usuario.
        
        Args:
            id (str): ID del préstamo a eliminar.
            
        Returns:
            bool: True si se eliminó exitosamente, False si no se encontró.
        """
        # Buscar el préstamo a eliminar
        loan_to_delete = self.__loans_repository.read(id)
        if loan_to_delete is None:
            print(f"Préstamo {id} no encontrado para eliminar.")
            return False
        
        book = loan_to_delete.get_book()
        user = loan_to_delete.get_user()
        
        # Reintegrar el libro al inventario
        self.__add_book_back_to_inventory(book)
        
        # Procesar reservas para el libro liberado
        self.__process_reservation_queue(book)
        
        # Eliminar del repositorio
        try:
            result = self.__loans_repository.delete(id)
            if not result:
                return False
        except Exception as e:
            print(f"Error eliminando préstamo del repositorio: {e}")
            return False
        
        # Eliminar del registro global de préstamos
        try:
            loan_records = Library.get_loanRecords()
            if loan_to_delete in loan_records:
                loan_records.remove(loan_to_delete)
                Library.set_loanRecords(loan_records)
        except Exception as e:
            print(f"Error eliminando préstamo del registro global: {e}")
        
        # Eliminar de la lista local del servicio
        try:
            if loan_to_delete in self.__loans_records:
                self.__loans_records.remove(loan_to_delete)
        except Exception as e:
            print(f"Error eliminando préstamo de la lista local: {e}")
        
        # Eliminar de la lista de préstamos del usuario
        try:
            user.remove_loan(loan_to_delete)
        except Exception as e:
            print(f"Error eliminando préstamo del usuario: {e}")
        
        return True
