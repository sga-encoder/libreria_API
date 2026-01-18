"""
Módulo de servicios de inventario.

Proporciona la clase InventoryService que maneja la carga, lectura,
creación, actualización y eliminación de libros usando BooksRepository.
Mantiene tanto la estructura de pila (inventario) como una lista ordenada.
 """
import logging
from typing import List, Dict, Any, Optional
from app.domain.repositories import BooksRepository
from app.domain.structures import Stack
from app.domain.models import Book, Loan
from app.domain.algorithms import insertion_sort, TotalValue, generate_global_report, generate_and_save, get_average_weight_by_author, binary_search
from app.domain.exceptions import ValidationException, ResourceNotFoundException, RepositoryException

class InventoryService:
    """
    Servicio de inventario de la biblioteca.

    Atributos:
        books_repository (BooksRepository): Repositorio para persistencia de libros.
        __inventary (Stack[Book]): Pila con los libros actuales en inventario.
        __order_inventary (list[Book]): Lista con los libros ordenados por ISBN.
    """

    __inventary: Stack[Book]
    __order_inventary: list[Book]
    
    def __init__(self, url: str) -> None:
        """
        Inicializa el servicio y carga el inventario desde el repositorio.

        Args:
            url (str): URL o ruta de conexión al repositorio de libros.
            
        Raises:
            ValidationException: Si url no es válido.
            RepositoryException: Si hay error al cargar el inventario.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if not url or not isinstance(url, str):
            self.logger.error(f"URL inválida: {url}")
            raise ValidationException(f"La URL debe ser una cadena no vacía, recibido: {type(url).__name__}")
        
        self.__books_repository = BooksRepository(url)
        self.__load()
        
        self.logger.info("InventoryService inicializado correctamente")
        
    def get_inventary(self) -> Stack[Book]:
        """
        Obtiene la pila de inventario.

        Returns:
            Stack[Book]: Pila con los libros almacenados.
        """
        return self.__inventary
    
    def get_order_inventary(self) -> list[Book]:
        """
        Obtiene la lista de inventario ordenada.

        Returns:
            list[Book]: Lista de libros ordenada por ISBN.
        """
        return self.__order_inventary
        
    def __load(self):
        """
        Carga los libros desde el repositorio en las estructuras internas.

        Lee todos los libros, crea la pila de inventario y la lista ordenada de libros disponibles.
        
        Raises:
            RepositoryException: Si hay error crítico al cargar el inventario.
        """
        try:
            self.logger.debug("Iniciando carga de inventario...")
            inventary = self.__books_repository.read_all()
            
            if inventary is None:
                self.logger.warning("No hay libros en el repositorio, inicializando inventario vacío")
                self.__inventary = Stack[Book]()
                self.__order_inventary = []
            else:
                self.__inventary = inventary
                order_inventary = []
                
                for book in self.__inventary.to_list():
                    if not book.get_is_borrowed():
                        order_inventary.append(book)
                
                self.logger.debug(f"Ordenando {len(order_inventary)} libros disponibles...")
                self.__order_inventary = insertion_sort(
                    order_inventary,
                    key=lambda book: book.get_id_IBSN()
                )
                
                total_books = len(self.__inventary.to_list())
                available_books = len(self.__order_inventary)
                self.logger.info(
                    f"Inventario cargado: {total_books} libros totales, "
                    f"{available_books} disponibles"
                )
                
        except RepositoryException:
            raise
        except Exception as e:
            self.logger.error(f"Error crítico cargando inventario: {e}", exc_info=True)
            raise RepositoryException(f"Error crítico al cargar inventario: {e}")
        
    def add(self, json: dict) -> Book:
        """
        Crea y añade un libro al inventario.

        Args:
            json (dict): Datos del libro a crear.

        Returns:
            Book: Instancia del libro creada.
            
        Raises:
            ValidationException: Si json no es válido o faltan campos obligatorios.
            RepositoryException: Si hay error al crear o guardar el libro.
        """
        try:
            if not json or not isinstance(json, dict):
                self.logger.error(f"Datos de libro inválidos: {type(json).__name__}")
                raise ValidationException("Los datos del libro deben ser un diccionario válido")
            
            # Validar campos obligatorios
            required_fields = ["id_IBSN", "title", "author"]
            missing_fields = [field for field in required_fields if not json.get(field)]
            
            if missing_fields:
                self.logger.error(f"Faltan campos obligatorios: {missing_fields}")
                raise ValidationException(
                    f"Faltan campos obligatorios: {', '.join(missing_fields)}"
                )
            
            self.logger.debug(f"Creando libro con ISBN: {json.get('id_IBSN')}")
            
            try:
                book = self.__books_repository.create(json)
            except Exception as e:
                self.logger.error(f"Error al crear libro en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error creando libro en repositorio: {e}")
            
            self.__inventary.push(book)
            self.__order_inventary = insertion_sort(
                self.__inventary.to_list(),
                key=lambda b: b.get_id_IBSN()
            )
            
            self.logger.info(f"Libro '{book.get_title()}' agregado exitosamente (ISBN: {book.get_id_IBSN()})")
            return book
            
        except (ValidationException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado agregando libro: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
    
    def get_by_id(self, id_IBSN: str) -> Book:
        """
        Lee un libro por su ISBN.

        Args:
            id_IBSN (str): Identificador ISBN del libro.

        Returns:
            Book: Libro encontrado.
            
        Raises:
            ValidationException: Si id_IBSN es inválido.
            ResourceNotFoundException: Si el libro no existe.
            RepositoryException: Si hay error de repositorio.
        """
        try:
            if not id_IBSN or not isinstance(id_IBSN, str):
                self.logger.error(f"ISBN inválido: {id_IBSN}")
                raise ValidationException(f"ISBN inválido: {id_IBSN}")
            
            self.logger.debug(f"Buscando libro con ISBN {id_IBSN}")
            
            book = self.__books_repository.read(id_IBSN)
            
            if book is None:
                self.logger.warning(f"Libro con ISBN {id_IBSN} no encontrado")
                raise ResourceNotFoundException(f"Libro con ISBN '{id_IBSN}' no encontrado")
            
            self.logger.debug(f"Libro encontrado: {book.get_title()}")
            return book
            
        except (ValidationException, ResourceNotFoundException):
            raise
        except Exception as e:
            self.logger.error(f"Error obteniendo libro: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo libro: {e}")
    
    def read_all(self) -> list[Book]:
        """
        Recupera todos los libros del repositorio.

        Returns:
            list[Book]: Lista de todos los libros.
            
        Raises:
            RepositoryException: Si hay error al obtener libros.
        """
        try:
            self.logger.debug("Obteniendo todos los libros del inventario")
            books = self.__books_repository.read_all()
            
            if books is None:
                self.logger.warning("No hay libros en el repositorio, retornando lista vacía")
                return []
            
            book_list = books.to_list()
            self.logger.info(f"Obtenidos {len(book_list)} libros del inventario")
            return book_list
            
        except Exception as e:
            self.logger.error(f"Error obteniendo todos los libros: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo libros: {e}")
        
    def get_all_not_borrowed(self) -> list[Book]:
        """
        Recupera todos los libros disponibles (no prestados) ordenados por ISBN.

        Returns:
            list[Book]: Lista de libros disponibles ordenados.
            
        Raises:
            RepositoryException: Si hay error al obtener libros.
        """
        try:
            self.logger.debug("Obteniendo libros disponibles (no prestados)")
            self.__inventary = self.__books_repository.read_all()
            
            if self.__inventary is None:
                self.logger.warning("No hay libros en el repositorio")
                self.__order_inventary = []
                return []
            
            order_inventary = []
            for book in self.__inventary.to_list():
                if not book.get_is_borrowed():
                    order_inventary.append(book)
            
            self.logger.debug(f"Ordenando {len(order_inventary)} libros disponibles")
            self.__order_inventary = insertion_sort(
                order_inventary,
                key=lambda book: book.get_id_IBSN()
            )
            
            self.logger.info(f"{len(self.__order_inventary)} libros disponibles obtenidos")
            return self.__order_inventary
            
        except Exception as e:
            self.logger.error(f"Error obteniendo libros disponibles: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo libros disponibles: {e}")
    
    def update(self, id_IBSN: str, json: dict) -> Book:
        """
        Actualiza los datos de un libro y recarga el inventario.

        Args:
            id_IBSN (str): ISBN del libro a actualizar.
            json (dict): Campos a actualizar.

        Returns:
            Book: Libro actualizado.
            
        Raises:
            ValidationException: Si id_IBSN o json son inválidos.
            ResourceNotFoundException: Si el libro no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not id_IBSN or not isinstance(id_IBSN, str):
                self.logger.error(f"ISBN inválido: {id_IBSN}")
                raise ValidationException(f"ISBN inválido: {id_IBSN}")
            
            if not json or not isinstance(json, dict):
                self.logger.error(f"Datos de actualización inválidos: {type(json).__name__}")
                raise ValidationException("Los datos de actualización deben ser un diccionario válido")
            
            self.logger.debug(f"Actualizando libro {id_IBSN} con datos: {json.keys()}")
            
            # Verificar que el libro existe
            existing_book = self.__books_repository.read(id_IBSN)
            if existing_book is None:
                self.logger.warning(f"Libro {id_IBSN} no encontrado para actualizar")
                raise ResourceNotFoundException(f"Libro con ISBN '{id_IBSN}' no encontrado")
            
            try:
                book = self.__books_repository.update(id_IBSN, json)
            except Exception as e:
                self.logger.error(f"Error actualizando libro en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando libro: {e}")
            
            if book is None:
                self.logger.critical(f"Repositorio retornó None al actualizar libro {id_IBSN}")
                raise RepositoryException("El libro no pudo ser actualizado")
            
            self.__load()
            self.logger.info(f"Libro '{book.get_title()}' actualizado exitosamente")
            return book
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado actualizando libro: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
    
    def delete(self, id_IBSN: str) -> bool:
        """
        Elimina un libro por su ISBN y recarga el inventario.

        Args:
            id_IBSN (str): ISBN del libro a eliminar.

        Returns:
            bool: True si se eliminó exitosamente.
            
        Raises:
            ValidationException: Si id_IBSN es inválido o el libro está prestado.
            ResourceNotFoundException: Si el libro no existe.
            RepositoryException: Si hay error al eliminar.
        """
        try:
            if not id_IBSN or not isinstance(id_IBSN, str):
                self.logger.error(f"ISBN inválido: {id_IBSN}")
                raise ValidationException(f"ISBN inválido: {id_IBSN}")
            
            self.logger.debug(f"Eliminando libro {id_IBSN}")
            
            # Verificar que el libro existe
            existing_book = self.__books_repository.read(id_IBSN)
            if existing_book is None:
                self.logger.warning(f"Libro {id_IBSN} no encontrado para eliminar")
                raise ResourceNotFoundException(f"Libro con ISBN '{id_IBSN}' no encontrado")
            
            # Validar que el libro no esté prestado
            if existing_book.get_is_borrowed():
                self.logger.warning(
                    f"No se puede eliminar el libro '{existing_book.get_title()}' porque está prestado"
                )
                raise ValidationException(
                    f"No se puede eliminar el libro '{existing_book.get_title()}' porque está prestado"
                )
            
            try:
                result = self.__books_repository.delete(id_IBSN)
            except Exception as e:
                self.logger.error(f"Error eliminando libro del repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error eliminando libro: {e}")
            
            if result:
                self.__load()
                self.logger.info(f"Libro con ISBN {id_IBSN} eliminado exitosamente")
            else:
                self.logger.error(f"No se pudo eliminar el libro {id_IBSN}")
                raise RepositoryException(f"No se pudo eliminar el libro {id_IBSN}")
            
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado eliminando libro: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")

    def loan_book(self, id_IBSN: str) -> bool:
        """
        Marca un libro como prestado.
        
        Args:
            id_IBSN: ISBN del libro a marcar como prestado.
            
        Returns:
            bool: True si se marcó exitosamente.
            
        Raises:
            ValidationException: Si id_IBSN es inválido.
            ResourceNotFoundException: Si el libro no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not id_IBSN or not isinstance(id_IBSN, str):
                self.logger.error(f"ISBN inválido: {id_IBSN}")
                raise ValidationException(f"ISBN inválido: {id_IBSN}")
            
            self.logger.debug(f"Marcando libro {id_IBSN} como prestado")
            
            try:
                self.__books_repository.loan(id_IBSN)
            except Exception as e:
                self.logger.error(f"Error al marcar libro como prestado: {e}", exc_info=True)
                raise RepositoryException(f"Error al marcar libro como prestado: {e}")
            
            self.logger.info(f"Libro {id_IBSN} marcado como prestado exitosamente")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado marcando libro como prestado: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
        
    def return_loan_book(self, id_IBSN: str) -> bool:
        """
        Marca un libro como devuelto (disponible).
        
        Args:
            id_IBSN: ISBN del libro a marcar como disponible.
            
        Returns:
            bool: True si se marcó exitosamente.
            
        Raises:
            ValidationException: Si id_IBSN es inválido.
            ResourceNotFoundException: Si el libro no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not id_IBSN or not isinstance(id_IBSN, str):
                self.logger.error(f"ISBN inválido: {id_IBSN}")
                raise ValidationException(f"ISBN inválido: {id_IBSN}")
            
            self.logger.debug(f"Marcando libro {id_IBSN} como disponible")
            
            try:
                self.__books_repository.return_loan(id_IBSN)
            except Exception as e:
                self.logger.error(f"Error al marcar libro como disponible: {e}", exc_info=True)
                raise RepositoryException(f"Error al marcar libro como disponible: {e}")
            
            self.logger.info(f"Libro {id_IBSN} marcado como disponible exitosamente")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado marcando libro como disponible: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")

    def add_book_to_ordered_list(self, book: Book) -> bool:
        """Añade un libro a la lista ordenada de inventario.

        Inserta el libro en la posición correcta para mantener el orden
        lexicográfico por ISBN. Solo afecta la lista ordenada; no modifica
        la pila de inventario ni el repositorio.

        Args:
            book (Book): Instancia del libro a añadir.

        Returns:
            bool: True si se añadió correctamente.
            
        Raises:
            ValidationException: Si book es None o inválido.
        """
        try:
            if book is None:
                self.logger.error("No se puede agregar un libro None a la lista ordenada")
                raise ValidationException("El libro no puede ser None")
            
            if not isinstance(book, Book):
                self.logger.error(f"Objeto inválido: {type(book).__name__}")
                raise ValidationException(f"Se esperaba Book, recibido: {type(book).__name__}")
            
            self.logger.debug(f"Agregando libro '{book.get_title()}' a lista ordenada")
            
            self.__order_inventary.append(book)
            self.__order_inventary = insertion_sort(
                self.__order_inventary,
                key=lambda b: b.get_id_IBSN()
            )
            
            self.logger.info(f"Libro '{book.get_title()}' agregado a lista ordenada")
            return True
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error agregando libro a lista ordenada: {e}", exc_info=True)
            raise RepositoryException(f"Error agregando libro a lista ordenada: {e}") 

    def delete_books_from_ordered_list(self, loans: List[Loan]) -> bool:
        """Elimina de la lista ordenada los libros asociados a los préstamos dados.

        Busca cada ISBN de los préstamos con `binary_search` sobre `__order_inventary`
        (lista ya ordenada lexicográficamente por ISBN). Solo afecta la lista ordenada;
        no modifica la pila de inventario ni el repositorio.

        Args:
            loans (List[Loan]): Préstamos cuyas referencias de libro se desean eliminar.

        Returns:
            bool: True si se eliminó al menos un libro.
            
        Raises:
            ValidationException: Si loans no es una lista válida.
        """
        try:
            if not isinstance(loans, list):
                self.logger.error(f"Loans debe ser una lista, recibido: {type(loans).__name__}")
                raise ValidationException(f"Loans debe ser una lista, recibido: {type(loans).__name__}")
            
            if not loans:
                self.logger.debug("Lista de préstamos vacía, no hay libros que eliminar")
                return False
            
            self.logger.debug(f"Eliminando {len(loans)} libros de la lista ordenada")
            
            indices_to_delete = []
            
            for loan in loans:
                try:
                    index = binary_search(
                        self.__order_inventary,
                        key=lambda book: book.get_id_IBSN(),
                        item=loan.get_book()
                    )
                    
                    if index >= 0:
                        indices_to_delete.append(index)
                        self.logger.debug(f"Libro '{loan.get_book().get_title()}' encontrado en índice {index}")
                        
                except (IndexError, Exception) as e:
                    self.logger.warning(f"Error buscando libro en lista ordenada: {e}")
                    continue
            
            if not indices_to_delete:
                self.logger.info("No se encontraron libros para eliminar de la lista ordenada")
                return False
            
            indices_to_delete.sort(reverse=True)
            
            for index in indices_to_delete:
                del self.__order_inventary[index]
            
            self.logger.info(f"{len(indices_to_delete)} libros eliminados de la lista ordenada")
            return True
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error eliminando libros de lista ordenada: {e}", exc_info=True)
            raise RepositoryException(f"Error eliminando libros de lista ordenada: {e}")
    
    def get_total_value_by_author(self, author: str) -> float:
        """
        Calcula el valor total de todos los libros de un autor específico.
        
        Utiliza el algoritmo TotalValue (recursivo con Stack) para procesar
        todos los libros del inventario y sumar el precio de aquellos que
        pertenecen al autor especificado.
        
        Args:
            author (str): Nombre del autor cuyos libros se quieren valorar.
        
        Returns:
            float: Valor total de todos los libros del autor.
                   Retorna 0.0 si no hay libros del autor o si el inventario está vacío.
        
        Ejemplos:
            >>> total = service.get_total_value_by_author("Gabriel García Márquez")
            >>> print(f"Valor total: ${total:.2f}")
        """
        try:
            if not author or not isinstance(author, str):
                self.logger.error(f"Autor inválido: {author}")
                raise ValidationException(f"El autor debe ser una cadena no vacía, recibido: {type(author).__name__}")
            
            self.logger.debug(f"Calculando valor total de libros del autor: {author}")
            
            books = self.__inventary.to_list()
            
            if not books:
                self.logger.info(f"No hay libros en inventario para calcular valor del autor {author}")
                return 0.0
            
            total_value = TotalValue(books, author)
            
            self.logger.info(f"Valor total de libros de '{author}': ${total_value:.2f}")
            return total_value
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error calculando valor total por autor: {e}", exc_info=True)
            return 0.0
    
    def generate_global_report(
        self,
        file_path: Optional[str] = None,
        format: str = "json",
        value_key: str = "price",
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """Genera un reporte global de todos los libros ordenados por valor.
        
        Obtiene todos los libros del inventario, los convierte a diccionarios,
        y genera un reporte ordenado por el campo de valor especificado.
        Opcionalmente guarda el reporte en formato CSV o JSON.
        
        Args:
            file_path: Ruta donde guardar el reporte (opcional). Si es None, solo retorna el reporte.
            format: Formato del archivo ('csv' o 'json'). Default: 'json'.
            value_key: Campo por el cual ordenar (debe existir en los diccionarios de libros). Default: 'price'.
            descending: Si es True ordena de mayor a menor, si es False de menor a mayor. Default: True.
        
        Returns:
            Lista de diccionarios con los libros ordenados por valor.
            Cada diccionario contiene todos los campos del libro.
        
        Ejemplos:
            >>> # Solo obtener el reporte ordenado
            >>> report = service.generate_global_report()
            >>> 
            >>> # Guardar en JSON
            >>> report = service.generate_global_report(file_path="./reports/inventory.json", format="json")
            >>> 
            >>> # Guardar en CSV con total
            >>> report = service.generate_global_report(file_path="./reports/inventory.csv", format="csv")
        """
        try:
            self.logger.debug(f"Generando reporte global de inventario (format={format}, value_key={value_key})")
            
            books = self.__inventary.to_list()
            
            if not books:
                self.logger.warning("No hay libros en inventario para generar reporte")
                return []
            
            books_dicts = [book.to_dict() for book in books]
            
            report = generate_and_save(
                books=books_dicts,
                file_path=file_path,
                format=format,
                value_key=value_key,
                descending=descending
            )
            
            if file_path:
                self.logger.info(f"Reporte global generado y guardado en: {file_path}")
            else:
                self.logger.info(f"Reporte global generado con {len(report)} libros")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte global: {e}", exc_info=True)
            return []
    
    def get_average_weight_by_author(self, author: str) -> Dict[str, Any]:
        """Calcula el peso promedio de los libros de un autor usando recursión de cola.
        
        Utiliza un algoritmo de tail recursion para procesar todos los libros del
        inventario y calcular el peso promedio de aquellos que pertenecen al autor
        especificado. La función muestra en consola cada paso de la recursión para
        fines educativos.
        
        Args:
            author: Nombre del autor cuyos libros se quieren analizar.
        
        Returns:
            Diccionario con:
            - author: nombre del autor
            - average_weight: peso promedio de sus libros en kg
            - total_books: cantidad de libros del autor
            - books: lista de libros con título, ISBN y peso
        
        Ejemplos:
            >>> result = service.get_average_weight_by_author("Gabriel García Márquez")
            >>> print(f"Peso promedio: {result['average_weight']} kg")
        """
        try:
            if not author or not isinstance(author, str):
                self.logger.error(f"Autor inválido: {author}")
                raise ValidationException(f"El autor debe ser una cadena no vacía, recibido: {type(author).__name__}")
            
            self.logger.debug(f"Calculando peso promedio de libros del autor: {author}")
            
            books = self.__inventary.to_list()
            
            if not books:
                self.logger.info(f"No hay libros en inventario para calcular peso promedio del autor {author}")
                return {
                    "author": author,
                    "average_weight": 0.0,
                    "total_books": 0,
                    "books": []
                }
            
            result = get_average_weight_by_author(books, author)
            
            self.logger.info(
                f"Peso promedio de libros de '{author}': {result['average_weight']:.2f} kg "
                f"({result['total_books']} libros)"
            )
            
            return result
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error calculando peso promedio por autor: {e}", exc_info=True)
            return {
                "author": author,
                "average_weight": 0.0,
                "total_books": 0,
                "books": []
            }