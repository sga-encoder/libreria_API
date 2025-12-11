"""
Módulo de servicios de inventario.

Proporciona la clase InventoryService que maneja la carga, lectura,
creación, actualización y eliminación de libros usando BooksRepository.
Mantiene tanto la estructura de pila (inventario) como una lista ordenada.
 """
from typing import List, Dict, Any, Optional
from app.domain.repositories import BooksRepository
from app.domain.structures import Stack
from app.domain.models import Book
from app.domain.algorithms import insertion_sort, TotalValue, generate_global_report, generate_and_save, get_average_weight_by_author

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

        No devuelve nada. En caso de error, inicializa inventario vacío.
        """
        self.__books_repository = BooksRepository(url)
        self.__load()
        
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

        Intenta leer todos los libros, crear la pila de inventario y la lista ordenada.
        En caso de error inicializa estructuras vacías y registra el error por consola.
        """
        try:
            inventary = self.__books_repository.read_all()
            if inventary is None:
                self.__inventary = Stack[Book]()
                self.__order_inventary = []
            else:
                self.__inventary = inventary
                # Cargar los libros en el inventario de la biblioteca
                self.__order_inventary = insertion_sort(
                    self.__inventary.to_list(),
                    key=lambda book: book.get_id_IBSN()
                )
        except Exception as e:
            print(f"Error loading inventory: {e}")
            self.__inventary = Stack[Book]()
            self.__order_inventary = []
        
    def add_book(self, json: dict) -> Book:
        """
        Crea y añade un libro al inventario.

        Args:
            json (dict): Datos del libro a crear.

        Returns:
            Book: Instancia del libro creada.

        Lanza la excepción original si falla la creación en el repositorio.
        """
        try:
            book = self.__books_repository.create(json)
            self.__inventary.push(book)
            self.__order_inventary = insertion_sort(
                self.__inventary.to_list(),
                key=lambda b: b.get_id_IBSN()
            )
            #falta poner la logica de bookCase
            return book
        except Exception as e:
            print(f"Error adding book: {e}")
            raise e
    
    def get_book_by_id(self, id_IBSN: str) -> Book:
        """
        Lee un libro por su ISBN.

        Args:
            id_IBSN (str): Identificador ISBN del libro.

        Returns:
            Book: Libro encontrado, o None en caso de error.
        """
        try:
            book = self.__books_repository.read(id_IBSN)
            return book
        except Exception as e:
            print(f"Error reading book: {e}")
            return None
    
    def read_all_books(self) -> list[Book] :
        """
        Recupera todos los libros del repositorio.

        Returns:
            list[Book] | None: Lista de libros (a partir de la pila) o None si no hay datos.
            En caso de error devuelve la excepción.
        """
        try:
            books = self.__books_repository.read_all()
            return books.to_list() if books else None
        except Exception as e:
            print(f"Error reading all books: {e}")
            return None
    
    def update_book(self, id_IBSN: str, json: dict) -> Book :
        """
        Actualiza los datos de un libro y recarga el inventario si la operación fue exitosa.

        Args:
            id_IBSN (str): ISBN del libro a actualizar.
            json (dict): Campos a actualizar.

        Returns:
            Book: Libro actualizado, o la excepción en caso de error.
        """
        try:    
            book = self.__books_repository.update(id_IBSN, json)
            self.__load()
                
            #falta poner la logica de bookCase
            # falta implementar la actualizcion de libros en loans
            return book
        except Exception as e:
            print(f"Error updating book: {e}")
            return None
    
    def delete_book(self, id_IBSN: str) -> bool:
        """
        Elimina un libro por su ISBN y recarga el inventario si la eliminación fue exitosa.

        Args:
            id_IBSN (str): ISBN del libro a eliminar.

        Returns:
            bool: True si se eliminó, False en caso contrario, o la excepción en caso de error.
        """
        try:
            #fata no eliminar libros si aun estan prestados
            result = self.__books_repository.delete(id_IBSN)
            if result:
                self.__load()
            return result
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False
    
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
            # Obtener todos los libros del inventario como lista
            books = self.__inventary.to_list()
            
            if not books:
                return 0.0
            
            # Usar el algoritmo TotalValue para calcular el valor total
            total_value = TotalValue(books, author)
            
            return total_value
        except Exception as e:
            print(f"Error calculating total value by author: {e}")
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
            # Obtener todos los libros del inventario
            books = self.__inventary.to_list()
            
            # Convertir libros a diccionarios
            books_dicts = [book.to_dict() for book in books]
            
            # Generar el reporte usando la función de algoritmos
            report = generate_and_save(
                books=books_dicts,
                file_path=file_path,
                format=format,
                value_key=value_key,
                descending=descending
            )
            
            return report
        except Exception as e:
            print(f"Error generating global report: {e}")
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
            # Obtener todos los libros del inventario
            books = self.__inventary.to_list()
            
            if not books:
                return {
                    "author": author,
                    "average_weight": 0.0,
                    "total_books": 0,
                    "books": []
                }
            
            # Usar el algoritmo de recursión de cola
            result = get_average_weight_by_author(books, author)
            
            return result
        except Exception as e:
            print(f"Error calculating average weight by author: {e}")
            return {
                "author": author,
                "average_weight": 0.0,
                "total_books": 0,
                "books": []
            }


