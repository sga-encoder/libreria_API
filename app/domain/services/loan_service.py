"""
Módulo de servicios de préstamos.

Proporciona la clase LoanService que maneja la lógica de negocio
de los préstamos: gestión de inventario, colas de reservas,
sincronización con usuarios y validaciones de negocio.
"""
from typing import Optional
from datetime import datetime
from app.domain.repositories import LoansRepository
from app.domain.structures import Queue
from app.domain.models import Loan, Book, User, BookCase
from app.domain.models.enums import TypeOrdering
from app.domain.algorithms import insertion_sort
from app.domain.algorithms.defientOrganicer import DeficientOrganizer
from app.domain.algorithms.organizer_optimum import estanteria_optima
from app.domain.services.inventory_service import InventoryService


class LoanService:
    """
    Servicio de préstamos de la biblioteca.

    Atributos:
        __loans_repository (LoansRepository): Repositorio para persistencia de préstamos.
        __loans_records (list[Loan]): Lista en memoria de préstamos activos.
        __reservations_queue (Queue): Cola de reservas para libros prestados.
        __users (list[User]): Lista de usuarios del sistema.
        __inventory_service (InventoryService): Servicio de inventario para gestionar libros.
        __bookcase (Optional[BookCase]): Estantería para organizar libros según algoritmo.
    """

    __loans_records: list[Loan]
    __reservations_queue: Queue[tuple[User, Book]]
    __users: list[User]
    __inventory_service: InventoryService
    __bookcase: Optional[BookCase]

    def __init__(self, url: str, reservations_queue: Queue[tuple[User, Book]], users: list[User], inventory_service: InventoryService, user_service, bookcase: Optional[BookCase] = None) -> None:
        """
        Inicializa el servicio y carga los préstamos desde el repositorio.

        Args:
            url (str): URL o ruta de conexión al repositorio de préstamos.
            reservations_queue (Queue): Cola de reservas compartida.
            users (list[User]): Lista de usuarios del sistema.
            inventory_service (InventoryService): Servicio de inventario para gestionar libros.
            user_service (UserService): Servicio de usuarios para actualizar préstamos.
            bookcase (Optional[BookCase]): Estantería para organizar libros según algoritmo de ordenamiento.

        No devuelve nada. En caso de error, inicializa estructura vacía.
        """
        self.__loans_repository = LoansRepository(url)
        self.__reservations_queue = reservations_queue
        self.__users = users
        self.__inventory_service = inventory_service
        self.__user_service = user_service
        self.__bookcase = bookcase
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
        - Stack de inventario completo (inventory_service.get_inventary) - SOLO marca el flag
        - La instancia del libro
        
        Args:
            book (Book): Libro a marcar como prestado.
        """
        try:
            # Marcar en el inventario Stack (inventario completo - TODOS los libros)
            for inv_book in self.__inventory_service.get_inventary():
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
            order_books = self.__inventory_service.get_order_inventary()
            updated_books = [b for b in order_books if b.get_id_IBSN() != book.get_id_IBSN()]
            # Reconstruir la lista ordenada sin el libro
            order_books.clear()
            order_books.extend(updated_books)
        except Exception as e:
            print(f"Error removing book from ordered inventory: {e}")

    def __add_book_back_to_inventory(self, book: Book) -> None:
        """Reinserta un libro al inventario de disponibles cuando finaliza su préstamo.
        
        IMPORTANTE:
        - NO añade al Stack de inventario (inventary) - el libro nunca se eliminó de ahí
        - SÍ añade a la lista ordenada (order_inventary) - lo reintegra a disponibles
        - Marca el libro como disponible en el Stack de inventario
        - Si existe bookcase: aplica algoritmo de ordenamiento
        
        Args:
            book (Book): Libro a reintegrar al inventario de disponibles.
        """
        try:
            # Marcar como disponible en el inventario Stack (TODOS los libros)
            for inv_book in self.__inventory_service.get_inventary():
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
            order_books = self.__inventory_service.get_order_inventary()
            if book not in order_books:
                order_books.append(book)
                order_books = insertion_sort(
                    order_books,
                    key=lambda b: b.get_id_IBSN()
                )
                # Limpiar y actualizar la lista
                order_books_ref = self.__inventory_service.get_order_inventary()
                order_books_ref.clear()
                order_books_ref.extend(order_books)
        except Exception as e:
            print(f"Error adding book back to ordered inventory: {e}")

    def __get_bookcase(self) -> Optional[BookCase]:
        """Obtiene el bookcase del servicio si existe.
        
        Returns:
            Optional[BookCase]: El bookcase disponible o None si no existe.
        """
        return self.__bookcase

    def set_bookcase(self, bookcase: Optional[BookCase]) -> None:
        """Establece el bookcase para el servicio.
        
        Args:
            bookcase (Optional[BookCase]): El bookcase a establecer.
        """
        self.__bookcase = bookcase

    def __apply_ordering_algorithm(self, bookcase: Optional[BookCase]) -> None:
        """Aplica el algoritmo de ordenamiento correspondiente al tipo de bookcase.
        
        Dependiendo del tipo de ordenamiento del bookcase:
        - DEFICIENT: Utiliza DeficientOrganizer
        - OPTIMOUM: Utiliza estanteria_optima
        
        Args:
            bookcase (Optional[BookCase]): El bookcase con la configuración de ordenamiento.
        """
        try:
            if bookcase is None:
                return
            
            # Obtener los libros del inventario ordenado
            books = self.__inventory_service.get_order_inventary()
            if not books:
                return
            
            ordering_type = bookcase.get_TypeOrdering()
            weight_capacity = bookcase.get_weighOrdering()
            
            if ordering_type == TypeOrdering.DEFICIENT:
                # Usar DeficientOrganizer
                organizer = DeficientOrganizer(weight_capacity)
                bookcase_result, dangerous_combinations = organizer.organize(books)
                
                if dangerous_combinations:
                    print(f"⚠️ Se encontraron {len(dangerous_combinations)} combinaciones peligrosas.")
                    organizer.print_dangerous_combinations()
                
                print(f"✓ Libros organizados usando algoritmo DEFICIENT.")
                
            elif ordering_type == TypeOrdering.OPTIMOUM:
                # Convertir libros a formato para estanteria_optima
                libros_dict = []
                for book in books:
                    libros_dict.append({
                        "peso": book.get_weight(),
                        "valor": 1  # Valor base por defecto
                    })
                
                mejor_valor, mejor_solucion = estanteria_optima(libros_dict, weight_capacity)
                print(f"Libros organizados usando algoritmo OPTIMOUM. Valor óptimo: {mejor_valor}")
                # mejor_solucion se guarda implícitamente en el algoritmo
                
        except Exception as e:
            print(f"Error aplicando algoritmo de ordenamiento: {e}")

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
                    print(f"📚 Procesando reserva: asignando libro '{book.get_title()}' a {reserved_user.get_email()}")
                    
                    # Eliminar la reserva de la cola PRIMERO
                    reservations.pop(idx)
                    
                    # Vaciar la cola actual (mantener la referencia)
                    while not self.__reservations_queue.is_empty():
                        self.__reservations_queue.pop()
                    
                    # Re-poblar con las reservas restantes
                    for item in reservations:
                        self.__reservations_queue.push(item)
                    
                    # Ahora crear el préstamo usando el libro recién liberado (no el de la cola)
                    # Marcar libro como prestado en todas las colecciones PRIMERO
                    self.__mark_book_as_borrowed(book)
                    
                    # Persistir el cambio en el libro
                    try:
                        self.__inventory_service.update_book(book.get_id_IBSN(), {"is_borrowed": True})
                    except Exception as e:
                        print(f"Error persistiendo estado de libro prestado: {e}")
                    
                    # Crear el préstamo con datetime actual
                    loan_data = {
                        "user": reserved_user.to_dict(),
                        "book": book.to_dict(),
                        "loanDate": datetime.now().isoformat()
                    }
                    
                    # Persistir en el repositorio
                    try:
                        loan = self.__loans_repository.create(loan_data)
                    except Exception as e:
                        print(f"❌ Error persistiendo préstamo desde reserva: {e}")
                        return False
                    
                    # Actualizar lista de préstamos del usuario (guardar solo el ID)
                    try:
                        reserved_user.add_loan(loan)  # Pasar objeto completo
                        # Persistir el cambio en el usuario (incluyendo loans e historial)
                        self.__user_service.update_user(reserved_user.get_id(), {
                            "loans": reserved_user.get_loans(),
                            "historial": reserved_user.get_historial()
                        })
                    except Exception as e:
                        print(f"Error añadiendo préstamo a usuario: {e}")
                    
                    # Extraer libro del inventario
                    self.__remove_book_from_inventory(book)
                    
                    # Aplicar algoritmo de ordenamiento si existe bookcase
                    bookcase = self.__get_bookcase()
                    if bookcase:
                        self.__apply_ordering_algorithm(bookcase)
                    
                    # Añadir a la lista local de préstamos
                    try:
                        self.__loans_records.append(loan)
                    except Exception as e:
                        print(f"Error añadiendo préstamo a registros: {e}")
                    
                    print(f"✅ Préstamo automático creado exitosamente desde reserva")
                    return True
        except Exception as e:
            print(f"❌ Error procesando cola de reservas: {e}")
        
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
            except Exception as e:
                print(f"Error añadiendo a cola de reservas: {e}")
            return None
        
        # Marcar libro como prestado en todas las colecciones PRIMERO
        self.__mark_book_as_borrowed(book)
        
        # Persistir el cambio en el libro
        try:
            self.__inventory_service.update_book(book.get_id_IBSN(), {"is_borrowed": True})
        except Exception as e:
            print(f"Error persistiendo estado de libro prestado: {e}")
        
        # Crear el préstamo con datetime actual (ahora el libro ya tiene is_borrowed: true)
        loan_data = {
            "user": user.to_dict(),
            "book": book.to_dict(),
            "loanDate": datetime.now().isoformat()
        }
        
        # Persistir en el repositorio
        try:
            loan = self.__loans_repository.create(loan_data)
        except Exception as e:
            print(f"Error persistiendo préstamo: {e}")
            return None
        
        # Actualizar lista de préstamos del usuario (pasar objeto completo para historial)
        try:
            user.add_loan(loan)  # Pasar el objeto completo para que se guarde en historial
            # Persistir el cambio en el usuario (incluyendo loans e historial)
            self.__user_service.update_user(user.get_id(), {
                "loans": user.get_loans(),
                "historial": user.get_historial()
            })
        except Exception as e:
            print(f"Error añadiendo préstamo a usuario: {e}")
        
        # Extraer libro del inventario
        self.__remove_book_from_inventory(book)
        
        # Aplicar algoritmo de ordenamiento si existe bookcase
        bookcase = self.__get_bookcase()
        if bookcase:
            self.__apply_ordering_algorithm(bookcase)
        
        # Añadir a la lista local de préstamos
        try:
            self.__loans_records.append(loan)
        except Exception as e:
            print(f"Error añadiendo préstamo a registros: {e}")
        
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
        2. Registra el préstamo antiguo en el historial del usuario.
        3. Libera el libro anterior (lo marca disponible y lo reinserta al inventario).
        4. Aplica algoritmo de ordenamiento al agregar el libro antiguo.
        5. Si el nuevo libro está disponible, crea un nuevo préstamo.
        6. Procesa la cola de reservas para el libro anterior.
        7. Aplica algoritmo de ordenamiento al remover el nuevo libro.
        8. Elimina el préstamo antiguo de los registros.
        9. El historial ahora contiene el préstamo antiguo Y el nuevo.
        
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
        
        # IMPORTANTE: Agregar el préstamo ANTIGUO COMPLETO al historial ANTES de hacer cualquier cambio
        # Esto preserva toda la información del préstamo que se va a reemplazar
        try:
            user.add_to_historial(loan_to_update)
        except Exception as e:
            print(f"Error añadiendo préstamo antiguo al historial: {e}")
        
        # Liberar el libro anterior
        self.__add_book_back_to_inventory(old_book)
        
        # Aplicar algoritmo de ordenamiento al agregar el libro antiguo
        bookcase = self.__get_bookcase()
        if bookcase:
            self.__apply_ordering_algorithm(bookcase)
        
        # Procesar reservas para el libro anterior
        self.__process_reservation_queue(old_book)
        
        # Validar que el nuevo libro no esté prestado
        if new_book.get_is_borrowed():
            print(f"Libro {new_book.get_id_IBSN()} ya está prestado. Añadiendo usuario a la cola de reservas.")
            try:
                self.__reservations_queue.push((user, new_book))
            except Exception as e:
                print(f"Error añadiendo a cola de reservas: {e}")
            return None
        
        # Marcar libro como prestado y extraer del inventario
        self.__mark_book_as_borrowed(new_book)
        self.__remove_book_from_inventory(new_book)
        
        # Aplicar algoritmo de ordenamiento al remover el nuevo libro
        if bookcase:
            self.__apply_ordering_algorithm(bookcase)
        
        # Crear el nuevo préstamo sin llamar a create_loan para evitar duplicar ordenamiento
        loan_data = {
            "user": user.to_dict(),
            "book": new_book.to_dict(),
            "loan_date": datetime.now().isoformat()
        }
        
        # Persistir en el repositorio
        try:
            new_loan = self.__loans_repository.create(loan_data)
        except Exception as e:
            print(f"Error persistiendo nuevo préstamo: {e}")
            return None
        
        # Actualizar lista de préstamos del usuario y agregar nuevo préstamo al historial
        try:
            user.add_loan(new_loan)  # Pasar objeto completo - Esto añade el nuevo préstamo a loans Y al historial
            # Persistir el cambio en el usuario (incluyendo loans e historial)
            # El historial ahora tiene: préstamo antiguo + préstamo nuevo
            self.__user_service.update_user(user.get_id(), {
                "loans": user.get_loans(),
                "historial": user.get_historial()
            })
        except Exception as e:
            print(f"Error añadiendo nuevo préstamo a usuario: {e}")
        
        # Añadir a la lista local de préstamos
        try:
            self.__loans_records.append(new_loan)
        except Exception as e:
            print(f"Error añadiendo nuevo préstamo a registros: {e}")
        
        # Eliminar el préstamo antiguo de los registros
        if new_loan is not None:
            try:
                self.__loans_repository.delete(id)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del repositorio: {e}")
            
            # Eliminar de la lista local
            try:
                if loan_to_update in self.__loans_records:
                    self.__loans_records.remove(loan_to_update)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo de la lista local: {e}")
            
            try:
                # Eliminar del usuario (solo de loans activos, NO del historial)
                user.remove_loan(loan_to_update)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del usuario: {e}")
        
        return new_loan
        # Eliminar el préstamo antiguo de los registros
        if new_loan is not None:
            try:
                self.__loans_repository.delete(id)
            except Exception as e:
                print(f"Error eliminando préstamo antiguo del repositorio: {e}")
            
            # Eliminar de la lista local
            try:
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
        2. Registra el préstamo en el historial del usuario antes de eliminarlo.
        3. Marca el libro como disponible.
        4. Reintegra el libro al inventario (stack y lista ordenada).
        5. Aplica algoritmo de ordenamiento al agregar el libro.
        6. Procesa la cola de reservas para ese libro.
        7. Elimina el préstamo de los registros globales y locales.
        8. Elimina el préstamo de la lista de préstamos activos del usuario.
        
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
        
        # IMPORTANTE: Agregar el préstamo COMPLETO al historial ANTES de eliminarlo
        # Esto preserva toda la información del préstamo (usuario, libro, fecha)
        try:
            user.add_to_historial(loan_to_delete)
        except Exception as e:
            print(f"Error añadiendo préstamo al historial: {e}")
        
        # Eliminar del repositorio primero
        try:
            result = self.__loans_repository.delete(id)
            if not result:
                return False
        except Exception as e:
            print(f"Error eliminando préstamo del repositorio: {e}")
            return False
        
        # Eliminar de la lista local del servicio
        try:
            if loan_to_delete in self.__loans_records:
                self.__loans_records.remove(loan_to_delete)
        except Exception as e:
            print(f"Error eliminando préstamo de la lista local: {e}")
        
        # Eliminar de la lista de préstamos activos del usuario (NO del historial)
        try:
            user.remove_loan(loan_to_delete)
        except Exception as e:
            print(f"Error eliminando préstamo del usuario: {e}")
        
        # Persistir cambios del usuario (lista de préstamos Y historial actualizado)
        self.__user_service.update_user(user.get_id(), {
            "loans": user.get_loans(),
            "historial": user.get_historial()
        })
        
        # Reintegrar el libro al inventario (marca is_borrowed = False)
        self.__add_book_back_to_inventory(book)
        
        # Persistir cambios del libro como disponible
        # IMPORTANTE: Hacerlo ANTES de procesar reservas
        self.__inventory_service.update_book(book.get_id_IBSN(), {"is_borrowed": False})
        
        # Aplicar algoritmo de ordenamiento al agregar el libro
        bookcase = self.__get_bookcase()
        if bookcase:
            self.__apply_ordering_algorithm(bookcase)
        
        # Procesar reservas para el libro liberado
        # Esto creará un nuevo préstamo si hay alguien esperando
        # y marcará el libro como prestado nuevamente
        self.__process_reservation_queue(book)
        
        return True