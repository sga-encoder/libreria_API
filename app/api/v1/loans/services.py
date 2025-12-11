from fastapi import HTTPException, status
from app.domain.services import LoanService, InventoryService, UserService
from app.domain.models import Loan, BookCase, BookShelf
from app.domain.models.enums import TypeOrdering
from app.domain.structures import Queue
from typing import Tuple, Optional

"""Módulo de servicios para la API de préstamos.

Provee una capa intermedia entre los endpoints de la API y la lógica de dominio
(LoanService). Contiene la clase LoanAPIService que orquesta operaciones
como crear, leer, actualizar y eliminar préstamos, además de gestionar
la cola de reservas y los estados del inventario.
"""

class LoanAPIService:
    """Servicio de API para operaciones sobre préstamos.

    Esta clase encapsula un LoanService y expone métodos que manejan la
    entrada/salida necesaria para los endpoints de la API (validación mínima,
    conversión de modelos y manejo de excepciones HTTP apropiadas).

    Atributos:
        __loan_service (LoanService): servicio de dominio para la gestión de préstamos.
        __inventory_service (InventoryService): servicio de dominio para gestionar inventario.
        __user_service (UserService): servicio de dominio para gestionar usuarios.
        __bookcase (Optional[BookCase]): estantería para organizar libros según algoritmo.
    """
    
    def __init__(self, loan_url: str, inventory_url: str, user_url: str, bookcase: Optional[BookCase] = None) -> None:
        """Inicializa el servicio con las URLs de los repositorios y bookcase opcional.

        Args:
            loan_url (str): URL o configuración para el repositorio de préstamos.
            inventory_url (str): URL o configuración para el repositorio de libros.
            user_url (str): URL o configuración para el repositorio de usuarios.
            bookcase (Optional[BookCase]): Estantería para organizar libros según algoritmo.
                Si no se proporciona, se puede establecer posteriormente con set_bookcase().
        """
        self.__inventory_service = InventoryService(inventory_url)
        self.__user_service = UserService(user_url)
        reservations_queue: Queue[Tuple] = Queue()
        users = self.__user_service.get_users_all() or []
        self.__bookcase = bookcase
        self.__loan_service = LoanService(loan_url, reservations_queue, users, self.__inventory_service, bookcase)
    
    def set_bookcase(self, bookcase: BookCase) -> None:
        """Establece o actualiza la estantería para aplicar algoritmos de ordenamiento.

        Args:
            bookcase (BookCase): Instancia de BookCase con algoritmo configurado.
        """
        self.__bookcase = bookcase
        self.__loan_service.set_bookcase(bookcase)
    
    def get_bookcase(self) -> Optional[BookCase]:
        """Obtiene la estantería actual si está configurada.

        Returns:
            Optional[BookCase]: Instancia de BookCase o None si no está configurada.
        """
        return self.__bookcase
    
    def create_bookcase_with_algorithm(self, algorithm_type: TypeOrdering, weight_capacity: float, 
                                      capacity_stands: int) -> BookCase:
        """Crea una nueva instancia de BookCase con el algoritmo especificado.

        Args:
            algorithm_type (TypeOrdering): Tipo de algoritmo (DEFICIENT o OPTIMOUM).
            weight_capacity (float): Capacidad de peso por estante.
            capacity_stands (int): Capacidad de estantes.

        Returns:
            BookCase: Nueva instancia de BookCase configurada.
        """
        bookshelf = BookShelf(books=[])
        bookcase = BookCase(
            stands=bookshelf,
            TypeOrdering=algorithm_type,
            weighCapacity=weight_capacity,
            capacityStands=capacity_stands,
            store=[]
        )
        self.set_bookcase(bookcase)
        return bookcase
    
    def execute_organization(self) -> dict:
        """Ejecuta manualmente el algoritmo de organización configurado en el BookCase.
        
        Solo puede ser llamado por administradores. Ejecuta el algoritmo de ordenamiento
        (DEFICIENT o OPTIMOUM) sobre todos los libros del inventario.
        
        Returns:
            dict: Resultado de la organización con detalles del algoritmo ejecutado.
            
        Raises:
            HTTPException: 400 si no hay BookCase configurado o no hay libros en inventario.
        """
        if self.__bookcase is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay BookCase configurado. Use POST /bookcase/configure primero."
            )
        
        # Obtener libros del inventario
        books = self.__inventory_service.get_order_inventary()
        if not books:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay libros en el inventario para organizar."
            )
        
        algorithm_type = self.__bookcase.get_TypeOrdering()
        weight_capacity = self.__bookcase.get_weighOrdering()
        
        result = {
            "algorithm_type": str(algorithm_type),
            "weight_capacity": weight_capacity,
            "books_processed": len(books),
            "execution_status": "success"
        }
        
        if algorithm_type == TypeOrdering.DEFICIENT:
            from app.domain.algorithms.defientOrganicer import DeficientOrganizer
            
            organizer = DeficientOrganizer(weight_capacity)
            bookcase_result, dangerous_combinations = organizer.organize(books)
            
            result["dangerous_combinations_found"] = len(dangerous_combinations)
            
            if dangerous_combinations:
                print(f"⚠️ Se encontraron {len(dangerous_combinations)} combinaciones peligrosas.")
                organizer.print_dangerous_combinations()
        
        elif algorithm_type == TypeOrdering.OPTIMOUM:
            from app.domain.algorithms.organizer_optimum import estanteria_optima
            
            libros_dict = [{"peso": book.get_weight(), "valor": 1} for book in books]
            mejor_valor, mejor_solucion = estanteria_optima(libros_dict, weight_capacity)
            result["optimal_value"] = mejor_valor
            print(f"✓ Libros organizados usando algoritmo OPTIMOUM. Valor óptimo: {mejor_valor}")
        
        return result
    
    def create_loan(self, user_email: str, book_id: str) -> Loan:
        """Crea un nuevo préstamo para un usuario y un libro.

        Busca el usuario por email, obtiene el libro del inventario y crea
        el préstamo a través del LoanService.

        Args:
            user_email (str): email del usuario que solicita el préstamo.
            book_id (str): ISBN del libro a prestar.

        Returns:
            Loan: préstamo creado.

        Raises:
            HTTPException: 404 si no encuentra usuario o libro, 400 si el libro está prestado,
                          500 si ocurre un error interno.
        """
        try:
            # Buscar el usuario
            user = None
            users = self.__user_service.get_users_all()
            for u in users:
                if u.get_email() == user_email:
                    user = u
                    break
            
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            
            # Obtener el libro del inventario
            book = self.__inventory_service.get_book_by_id(book_id)
            if book is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
            
            # Crear el préstamo
            loan = self.__loan_service.create_loan(user, book)
            if loan is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pudo crear el préstamo (libro prestado o error)"
                )
            
            return loan
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error creating loan: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creando préstamo")
    
    def read_loan(self, loan_id: str) -> Loan | None:
        """Obtiene un préstamo por su ID.

        Args:
            loan_id (str): ID del préstamo a leer.

        Returns:
            Loan | None: instancia Loan si se encuentra, None en caso contrario.

        Raises:
            HTTPException: 404 si no se encuentra, 500 en errores internos.
        """
        try:
            loan = self.__loan_service.get_loan_by_id(loan_id)
            if loan is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
            return loan
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error reading loan: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo préstamo")
    
    def read_all_loans(self) -> list[Loan]:
        """Devuelve la lista completa de préstamos registrados.

        Returns:
            list[Loan]: lista de préstamos.

        Raises:
            HTTPException: 404 si no hay préstamos, 500 en errores internos.
        """
        try:
            loans = self.__loan_service.read_all_loans()
            if loans is None or len(loans) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay préstamos registrados")
            return loans
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error reading all loans: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo préstamos")
    
    def update_loan(self, loan_id: str, new_book_id: str) -> Loan | None:
        """Actualiza un préstamo existente reemplazando el libro.

        Obtiene el nuevo libro del inventario y delega la actualización
        al LoanService, que maneja la liberación del libro anterior y
        el procesamiento de la cola de reservas.

        Args:
            loan_id (str): ID del préstamo a actualizar.
            new_book_id (str): ISBN del nuevo libro.

        Returns:
            Loan | None: nuevo préstamo creado o None si hay error.

        Raises:
            HTTPException: 404 si no encuentra el préstamo o libro, 500 en errores internos.
        """
        try:
            # Obtener el nuevo libro
            new_book = self.__inventory_service.get_book_by_id(new_book_id)
            if new_book is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nuevo libro no encontrado")
            
            # Actualizar el préstamo
            loan = self.__loan_service.update_loan(loan_id, new_book)
            if loan is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el préstamo")
            
            return loan
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating loan: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando préstamo")
    
    def delete_loan(self, loan_id: str) -> bool:
        """Elimina un préstamo y reintegra el libro al inventario.

        Delega la eliminación al LoanService, que se encarga de:
        - Marcar el libro como disponible
        - Reintegrarlo al inventario
        - Procesar la cola de reservas
        - Eliminar del registro de préstamos

        Args:
            loan_id (str): ID del préstamo a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            HTTPException: 404 si no se encuentra el préstamo, 500 en errores internos.
        """
        try:
            result = self.__loan_service.delete_loan(loan_id)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado para eliminar")
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error deleting loan: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error eliminando préstamo")