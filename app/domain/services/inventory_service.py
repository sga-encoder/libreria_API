"""
Módulo de servicios de inventario.

Proporciona la clase InventoryService que maneja la carga, lectura,
creación, actualización y eliminación de libros usando BooksRepository.
Mantiene tanto la estructura de pila (inventario) como una lista ordenada.
 """
from app.domain.repositories import BooksRepository
from app.domain.structures import Stack
from app.domain.models import Book
from app.domain.algorithms import insertion_sort

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


