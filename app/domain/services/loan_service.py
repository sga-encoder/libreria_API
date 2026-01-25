"""Servicio de gestión de préstamos de libros.

Este módulo proporciona la lógica de negocio para la gestión completa de préstamos
de libros en la biblioteca, incluyendo el manejo de reservas, cola de espera,
y la integración con el sistema de inventario y estanterías.
"""
from app.core.logging_config import get_logger
from typing import Optional
from app.domain.repositories import LoansRepository
from app.domain.models import Loan, Book, BookCase
from .inventory_service import InventoryService
from .person.user_service import UserService
from .book_case_services import BookCaseService
from .reservation_service import ReservationQueueService
from app.domain.exceptions import BookAlreadyBorrowedException
from app.domain.exceptions import ValidationException, RepositoryException, ResourceNotFoundException



class LoanService:
    """Servicio para la gestión de préstamos de libros.
    
    Esta clase gestiona todo el ciclo de vida de los préstamos de libros,
    incluyendo la creación, actualización, devolución, y el manejo de
    reservas cuando los libros no están disponibles.
    
    Attributes:
        __loans_records: Lista de todos los préstamos históricos.
        __loans_records_repository: Repositorio para persistir préstamos.
        __current_loans: Lista de préstamos activos actualmente.
        __current_loans_fileManager: Gestor de archivos para préstamos actuales.
        __reservations_queue: Cola de reservas de usuarios esperando libros.
        __inventory_service: Servicio de gestión de inventario.
        __user_service: Servicio de gestión de usuarios.
        __bookcase_service: Servicio de gestión de estanterías y ordenamiento.
    """

    __loans: list[Loan]
    __loans_repository: LoansRepository
    __active_loans: list[Loan]
    __reservation_queue_service: ReservationQueueService
    __inventory_service: InventoryService
    __user_service: UserService
    __bookcase_service: BookCaseService

    def __init__(self, url_history_loans: str, url_active_loans: str, inventory_service: InventoryService, user_service: UserService, bookcase: Optional[BookCase] = None) -> None:
        """Inicializa el servicio de préstamos.
        
        Args:
            url_loans_records: Ruta al archivo de registros de préstamos.
            url_current_loans: Ruta al archivo de préstamos actuales.
            inventory_service: Servicio de inventario de libros.
            user_service: Servicio de gestión de usuarios.
            bookcase: Estantería opcional para ordenamiento (por defecto None).
        """
        self.logger = get_logger(__name__)
        
        self.__loans_repository = LoansRepository(url_history_loans, url_active_loans)
        self.__reservation_queue_service = ReservationQueueService()
        self.__inventory_service = inventory_service
        self.__user_service = user_service
        self.__bookcase_service = BookCaseService(bookcase)
        self.__load()
        
        self.logger.info(f"LoanService inicializado correctamente")

    def __load(self):
        """Carga los datos de préstamos desde el almacenamiento persistente.
        
        Lee tanto los registros históricos como los préstamos actuales,
        y actualiza el estado de los libros en el inventario.
        """
        try:
            self.logger.debug("Iniciando carga de préstamos...")
            
            self.__loans = self.__loans_repository.read_all_history_loans()
            self.__active_loans = self.__loans_repository.read_all()
            
            self.logger.info(
                f"Préstamos cargados: {len(self.__loans)} históricos, "
                f"{len(self.__active_loans)} activos"
            )
            
            # Inicializar como lista vacía si es None
            if self.__loans is None:
                self.logger.warning("No hay historial de préstamos, inicializando vacío")
                self.__loans = []
            if self.__active_loans is None:
                self.logger.warning("No hay préstamos activos, inicializando vacío")
                self.__active_loans = []
            
            # Actualizar estados de libros y usuarios
            try:
                self.__inventory_service.delete_books_from_ordered_list(self.__active_loans)
                
            except Exception as e:
                    self.logger.warning(f"Error procesando préstamo durante carga: {e}")
        except Exception as e:
            self.logger.error(f"Error cargando préstamos: {e}", exc_info=True)
            self.__loans = []
            self.__active_loans = []

    def get_loans_records(self) -> list[Loan]:
        """Obtiene todos los registros históricos de préstamos.
        
        Returns:
            Lista con todos los préstamos registrados en el sistema.
        """
        return self.__loans

    def get_reservation_queue_service(self) -> ReservationQueueService:
        """Obtiene el servicio de cola de reservas.
        
        Returns:
            Servicio de gestión de reservas.
        """
        return self.__reservation_queue_service

    def set_bookcase(self, bookcase: Optional[BookCase]) -> None:
        """Configura la estantería para aplicar algoritmos de ordenamiento.
        
        Args:
            bookcase: Estantería a configurar o None para desactivar.
        """
        self.__bookcase_service.set_bookcase(bookcase)

    def __apply_ordering_algorithm(self) -> None:
        """Aplica el algoritmo de ordenamiento de libros si hay una estantería configurada.
        
        Note:
            Delega la lógica al BookCaseService.
        """
        if self.__bookcase_service.has_bookcase_configured():
            books = self.__inventory_service.get_order_inventary()
            self.__bookcase_service.apply_ordering_algorithm(books)

    def __process_reservation_queue(self, book: Book) -> bool:
        """Procesa la cola de reservas cuando un libro se devuelve.
        
        Args:
            book: Libro devuelto para procesar reservas
            
        Returns:
            True si se procesó una reserva exitosamente, False si no había reservas
            
        Raises:
            ValidationException: Si el libro es inválido
            RepositoryException: Si falla la creación del préstamo automático
            
        Note:
            Si falla al crear el préstamo, re-encola al usuario automáticamente.
        """
        try:
            # Validar entrada
            if not book or not isinstance(book, Book):
                self.logger.error(f"Libro inválido para procesar reservas: {book}")
                raise ValidationException(f"Libro inválido para procesar reservas")
            
            if not self.__reservation_queue_service.has_reservations_for_book(book):
                self.logger.debug(f"No hay reservas para '{book.get_title()}'")
                return False
            
            reserved_user = self.__reservation_queue_service.pop_reservation(book)
            
            if reserved_user is None:
                self.logger.warning(f"Cola retornó None para '{book.get_title()}'")
                return False
            
            self.logger.info(
                f"Procesando reserva: asignando '{book.get_title()}' a "
                f"{reserved_user.get_fullName()} ({reserved_user.get_email()})"
            )
            
            # Crear préstamo automático con estructura correcta
            loan_data = {
                "id_user": reserved_user.get_id(),
                "id_ISBN_book": book.get_id_IBSN()
            }
            
            # Intentar crear préstamo automático
            try:
                loan = self.create(loan_data)
                self.logger.info(
                    f"Préstamo automático {loan.get_id()} creado exitosamente desde reserva"
                )
                return True
            
            except BookAlreadyBorrowedException as e:
                # Caso extraño: el libro debería estar disponible
                self.logger.error(
                    f"Libro '{book.get_title()}' marcado como prestado al procesar reserva: {e}"
                )
                # Re-encolar usuario
                self.__reservation_queue_service.add_reservation(book, reserved_user)
                return False
            
            except ValidationException as e:
                # Error de datos: no re-encolar
                self.logger.error(f"Error de validación procesando reserva: {e}")
                return False
            
            except RepositoryException as e:
                # Error de persistencia: re-encolar usuario
                self.logger.error(f"Error de repositorio procesando reserva: {e}")
                self.__reservation_queue_service.add_reservation(book, reserved_user)
                return False
            
        except ValidationException:
            raise
        
        except Exception as e:
            # Error inesperado: NO re-encolar (puede causar loop infinito)
            self.logger.critical(
                f"Error inesperado procesando cola de reservas: {e}",
                exc_info=True
            )
            return False        

    def create(self, json: dict) -> Loan:
        """Crea un nuevo préstamo de libro.
        
        Args:
            json: Diccionario con 'id_user' e 'id_ISBN_book'.
            
        Returns:
            El préstamo creado exitosamente.
            
        Raises:
            ValidationException: Si faltan datos obligatorios o son inválidos
            ResourceNotFoundException: Si el libro no existe
            BookAlreadyBorrowedException: Si el libro ya está prestado (usuario se agrega a cola)
            RepositoryException: Si hay error de persistencia
                                         
        Note:
            Si el libro ya está prestado, el usuario se agrega automáticamente
            a la cola de reservas antes de lanzar BookAlreadyBorrowedException.
        """
        
        
        try:
            if not json or not isinstance(json, dict):
                raise ValidationException("los datos del prestamo debe ser un diccionario valido")
            
            id_book, id_user = json.get("id_ISBN_book"), json.get("id_user")
            
            if not id_book or not id_user:
                raise ValidationException(f"Faltan datos obligatorios: 'id_ISBN_book' y 'id_user'\n Valores recibidos: {json}")
            
            book = self.__inventory_service.get_by_id(id_book)
            
            if book is None:
                raise ValidationException(f"Libro con ISBN {id_book} no encontrado en el sistema.")
            if book.get_is_borrowed():
                raise BookAlreadyBorrowedException(f"El libro {id_book} ya está prestado.")
            
            try:
                loan = self.__loans_repository.create(json)
            except Exception as e:
                raise RepositoryException(f"Error creando préstamo en el repositorio: {e}")
            
            # Asegurar que __loans es una lista válida
            if self.__loans is None:
                self.__loans = []
            
            self.__loans.append(loan)
            self.__inventory_service.loan_book(loan.get_book().get_id_IBSN())
            self.__inventory_service.delete_books_from_ordered_list([loan])
            self.__user_service.add_loan(loan.get_user().get_id(), loan)
            
            #-------pendiente de revisar-------#
            # Aplicar algoritmo de ordenamiento si existe bookcase
            self.__apply_ordering_algorithm()
            self.logger.info(f"Préstamo {loan.get_id()} creado para usuario {id_user} y libro {id_book}")
            return loan

        except BookAlreadyBorrowedException as e:
            self.logger.warning(f"Libro ya prestado, agregando a cola: {e}")
            # Obtener el usuario y el libro para agregar a la cola
            try:
                user = self.__user_service.get_by_id(json.get("id_user"))
                book = self.__inventory_service.get_by_id( json.get("id_ISBN_book"))
                
                if user and book:
                    self.__reservation_queue_service.add_reservation(book, user)
                    self.logger.info(f"Usuario {user.get_email()} añadido a cola para '{book.get_title()}'")
                else:
                    self.logger.error("Usuario o libro no encontrado para agregar a reserva")
            except Exception as inner_e:
                self.logger.error(f"Error agregando a cola de reservas: {inner_e}", exc_info=True)
            raise
                
        except (ValidationException, ResourceNotFoundException, RepositoryException) as e:
            self.logger.error(f"Error creando préstamo: {e}")
            raise
        except Exception as e:
            self.logger.critical(f"Error persistiendo préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")

    def get_by_id(self, id: str) -> Loan:
        """Obtiene un préstamo por su identificador.
        
        Args:
            id: Identificador único del préstamo.
            
        Returns:
            El préstamo encontrado.
            
        Raises:
            ValidationException: Si el ID es inválido
            ResourceNotFoundException: Si el préstamo no existe
            RepositoryException: Si hay error de repositorio
        """
        try:
            if not id or not isinstance(id, str):
                self.logger.error(f"ID de préstamo inválido: {id}")
                raise ValidationException(f"ID de préstamo inválido: {id}")
            
            self.logger.debug(f"Buscando préstamo {id}")
            loan = self.__loans_repository.read(id)
            
            if loan is None:
                self.logger.warning(f"Préstamo {id} no encontrado")
                raise ResourceNotFoundException(f"Préstamo con ID '{id}' no encontrado")
            
            self.logger.debug(f"Préstamo {id} encontrado exitosamente")
            return loan
            
        except (ValidationException, ResourceNotFoundException):
            raise
        
        except Exception as e:
            self.logger.error(f"Error buscando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error buscando préstamo: {e}")

    def get_all(self) -> list[Loan]:
        """Obtiene todos los préstamos activos del sistema.
        
        Returns:
            Lista con todos los préstamos activos.
            
        Raises:
            RepositoryException: Si hay error al leer préstamos
        """
        try:
            self.logger.debug("Obteniendo todos los préstamos activos")
            self.__active_loans = self.__loans_repository.read_all()
            
            if self.__active_loans is None:
                self.logger.warning("No hay préstamos activos, retornando lista vacía")
                self.__active_loans = []
            
            self.logger.info(f"Obtenidos {len(self.__active_loans)} préstamos activos")
            return self.__active_loans
            
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos activos: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo préstamos: {e}")

    def update(self, id: str, json: dict) -> Loan:
        """Actualiza un préstamo existente, gestionando cambio de libro.
        
        Args:
            id: Identificador del préstamo a actualizar.
            json: Diccionario con los nuevos datos (puede incluir 'id_ISBN_book').
            
        Returns:
            El préstamo actualizado.
            
        Raises:
            ValidationException: Si los datos son inválidos o el libro es igual al actual
            ResourceNotFoundException: Si el préstamo o el nuevo libro no existen
            BookAlreadyBorrowedException: Si el nuevo libro ya está prestado
            RepositoryException: Si hay error de persistencia
            
        Note:
            Si se cambia el libro prestado:
            1. Se libera el libro anterior al inventario
            2. Se procesa la cola de reservas del libro anterior
            3. Se actualiza el préstamo en base de datos
            4. Se marca el nuevo libro como prestado
        """
        try:
            if not id or not isinstance(id, str):
                self.logger.error(f"ID de préstamo inválido: {id}")
                raise ValidationException(f"ID de préstamo inválido: {id}")
            
            if not json or not isinstance(json, dict):
                self.logger.error("Datos de actualización inválidos")
                raise ValidationException("Los datos de actualización deben ser un diccionario")
            
            self.logger.debug(f"Actualizando préstamo {id} con datos: {json}")
            
            loan_to_update = self.__loans_repository.read(id)
        
            if loan_to_update is None:
                self.logger.warning(f"Préstamo {id} no encontrado para actualizar")
                raise ResourceNotFoundException(f"Préstamo con ID '{id}' no encontrado")
            
            old_book = loan_to_update.get_book()
            id_new_book = json.get("id_ISBN_book")
            
            self.logger.debug(
                f"Préstamo actual: Usuario {loan_to_update.get_user().get_id()} "
                f"con Libro {old_book.get_id_IBSN()}"
            )
            
            if id_new_book:
                if id_new_book == old_book.get_id_IBSN():
                    self.logger.warning(f"Intento de actualizar con el mismo libro: {id_new_book}")
                    raise ValidationException(
                        f"El nuevo libro debe ser diferente al actual ({old_book.get_title()})"
                    )
                
                new_book = self.__inventory_service.get_by_id(id_new_book)
            
                if new_book is None:
                    self.logger.error(f"Nuevo libro {id_new_book} no encontrado")
                    raise ResourceNotFoundException(
                        f"Libro con ISBN '{id_new_book}' no encontrado en el inventario"
                    )
                
                if new_book.get_is_borrowed():
                    self.logger.warning(
                        f"Nuevo libro {id_new_book} ya está prestado. "
                        f"No se puede asignar al préstamo {id}"
                    )
                    raise BookAlreadyBorrowedException(
                        f"El libro '{new_book.get_title()}' ya está prestado. "
                        f"No se puede reasignar al préstamo."
                    )
                     
                try:
                    self.logger.info(
                        f"Devolviendo libro anterior '{old_book.get_title()}' al inventario"
                    )
                    self.__inventory_service.return_loan_book(old_book.get_id_IBSN())
                    self.__inventory_service.add_book_to_ordered_list(old_book)
                    
                    self.logger.debug(f"Procesando cola de reservas para '{old_book.get_title()}'")
                    self.__process_reservation_queue(old_book)
                    
                except Exception as e:
                    self.logger.error(
                        f"Error al devolver el libro anterior '{old_book.get_title()}': {e}",
                        exc_info=True
                    )
                    raise RepositoryException(f"Error al devolver el libro anterior: {e}")
                    
                self.__apply_ordering_algorithm()
            
        
            self.logger.info(f"Persistiendo actualización del préstamo {id}")
            try:
                new_loan = self.__loans_repository.update(id, json)
            except Exception as e:
                self.logger.error(f"Error al persistir actualización: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando préstamo en repositorio: {e}")
        
            if new_loan is None:
                self.logger.critical(f"Repositorio retornó None al actualizar préstamo {id}")
                raise RepositoryException(
                    "El préstamo no pudo ser actualizado (repositorio retornó None)"
                )
        

            if id_new_book:
                try:
                    self.logger.info(f"Marcando nuevo libro '{new_book.get_title()}' como prestado")
                    self.__inventory_service.loan_book(new_book.get_id_IBSN())
                    self.__inventory_service.delete_books_from_ordered_list([new_loan])
                    self.logger.debug(f"Nuevo libro {new_book.get_id_IBSN()} actualizado en inventario")
                except Exception as e:
                    self.logger.error(f"Error actualizando inventario con nuevo libro: {e}", exc_info=True)
                    raise RepositoryException(f"Error actualizando inventario: {e}")
            
            self.logger.info(
                f"Préstamo {id} actualizado exitosamente. "
                f"Nuevo libro: {new_book.get_title() if id_new_book else 'sin cambios'}"
            )
            return new_loan
        except (ValidationException, ResourceNotFoundException, BookAlreadyBorrowedException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")

    def delete(self, id: str) -> bool:
        """Elimina (finaliza) un préstamo y devuelve el libro.
        
        Args:
            id: Identificador del préstamo a eliminar.
            
        Returns:
            True si el préstamo se eliminó exitosamente.
            
        Raises:
            ValidationException: Si el ID es inválido
            ResourceNotFoundException: Si el préstamo no existe
            RepositoryException: Si hay error de persistencia
            
        Note:
            Al eliminar un préstamo:
            1. Se elimina del repositorio
            2. Se elimina del usuario
            3. Se procesa automáticamente la cola de reservas
            4. Se aplica algoritmo de ordenamiento
        """    
        try:
            if not id or not isinstance(id, str):
                self.logger.error(f"ID de préstamo inválido: {id}")
                raise ValidationException(f"ID de préstamo inválido: {id}")
            
            self.logger.debug(f"Eliminando préstamo {id}")
            
            loan = self.__loans_repository.read_in_history_loan(id)
            if loan is None:
                self.logger.warning(f"Préstamo {id} no encontrado para eliminar")
                raise ResourceNotFoundException(
                    f"Préstamo con ID '{id}' no encontrado en el sistema"
                )
            
            book = loan.get_book()
            user = loan.get_user()
            
            self.logger.info(
                f"Eliminando préstamo {id}: Usuario {user.get_fullName()}, "
                f"Libro '{book.get_title()}'"
            )
            
            # Eliminar del repositorio
            try:
                self.__loans_repository.delete(id)
                self.logger.debug(f"Préstamo {id} eliminado del repositorio")
            except Exception as e:
                self.logger.error(
                    f"Error eliminando préstamo del repositorio: {e}",
                    exc_info=True
                )
                raise RepositoryException(f"Error eliminando préstamo del repositorio: {e}")
            
            # Eliminar del usuario
            try:
                if not self.__user_service.delete_loan(user.get_id(), loan):
                    self.logger.error(f"Fallo al eliminar préstamo del usuario {user.get_id()}")
                    raise RepositoryException(
                        f"No se pudo eliminar el préstamo del usuario {user.get_fullName()}"
                    )
                self.logger.debug(f"Préstamo eliminado del usuario {user.get_id()}")
            except RepositoryException:
                raise
            except Exception as e:
                self.logger.error(
                    f"Error eliminando préstamo del usuario: {e}",
                    exc_info=True
                )
                raise RepositoryException(f"Error eliminando préstamo del usuario: {e}")
            
            # Procesar cola de reservas
            try:
                self.logger.debug(f"Procesando cola de reservas para '{book.get_title()}'")
                reservation_processed = self.__process_reservation_queue(book)
                
                if reservation_processed:
                    self.logger.info(
                        f"Reserva procesada automáticamente para '{book.get_title()}'"
                    )
                else:
                    self.logger.debug(f"No hay reservas pendientes para '{book.get_title()}'")
                    
            except Exception as e:
                # No crítico: el préstamo ya fue eliminado
                self.logger.warning(f"Error procesando cola de reservas: {e}")
            
            # Aplicar algoritmo de ordenamiento
            try:
                self.__apply_ordering_algorithm()
                self.logger.debug("Algoritmo de ordenamiento aplicado")
            except Exception as e:
                # No crítico
                self.logger.warning(f"Error aplicando ordenamiento: {e}")
            
            self.logger.info(f"Préstamo {id} eliminado exitosamente")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        
        except Exception as e:
            self.logger.critical(f"Error inesperado eliminando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado eliminando préstamo: {e}")

    def process_pending_reservations(self, book_id: str) -> bool:
        """Procesa manualmente las reservas pendientes de un libro.
        
        Args:
            book_id: ISBN del libro para procesar reservas.
            
        Returns:
            True si se procesó alguna reserva, False si no había o libro prestado.
            
        Raises:
            ValidationException: Si el ISBN es inválido
            ResourceNotFoundException: Si el libro no existe
            RepositoryException: Si hay error de persistencia
            
        Note:
            Útil para procesamiento manual o corrección de estados.
            Solo procesa si el libro está disponible.
        """
        try:
            if not book_id or not isinstance(book_id, str):
                self.logger.error(f"ISBN inválido: {book_id}")
                raise ValidationException(f"ISBN inválido: {book_id}")
            
            self.logger.debug(f"Procesando reservas manualmente para libro {book_id}")
            
            book = self.__inventory_service.get_by_id(book_id)
            
            if book is None:
                self.logger.warning(f"Libro {book_id} no encontrado")
                raise ResourceNotFoundException(
                    f"Libro con ISBN '{book_id}' no encontrado en el inventario"
                )
            
            if book.get_is_borrowed():
                self.logger.info(
                    f"Libro '{book.get_title()}' aún está prestado, no procesando reservas"
                )
                return False
            
            return self.__process_reservation_queue(book)
            
        except (ValidationException, ResourceNotFoundException):
            raise
        
        except Exception as e:
            self.logger.error(
                f"Error procesando reservas manualmente: {e}",
                exc_info=True
            )
            raise RepositoryException(f"Error procesando reservas: {e}")