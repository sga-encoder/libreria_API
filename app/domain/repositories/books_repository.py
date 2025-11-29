"""Repositorio de libros persistido en un archivo JSON.

Este módulo contiene la implementación de BooksRepository, una
implementación de RepositoriesInterface para objetos Book. Usa FileManager
para lectura/escritura de datos en formato JSON y mantiene una caché
local de los registros leídos.
"""
from app.domain.models import Book
from app.domain.repositories import RepositoriesInterface
from app.domain.structures import Stack
from app.utils import FileManager, FileType
from app.domain.algorithms import linear_search

class BooksRepository(RepositoriesInterface[Book]):
    """Repositorio de Book respaldado por un archivo JSON.

    Aporta operaciones CRUD básicas sobre libros: create, read, read_all,
    update y delete. Mantiene una caché interna (_books_cache) que se
    sincroniza con el archivo mediante FileManager.
    """
    __file : FileManager
    _books_cache: list[Book]
    
    def __init__(self, url: str) -> None:
        """Inicializa el repositorio.

        Args:
            url (str): Ruta o URL del archivo JSON donde se almacenan los libros.
        """
        self.__file = FileManager(url, FileType.JSON)
        self._books_cache = self.__file.read()

    def _refresh_cache(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self._books_cache = self.__file.read()
        
    def __search_id(self, id: str) -> int:
        """Busca el índice de un libro por su id_IBSN.

        Args:
            id (str): Valor del id_IBSN a buscar.

        Returns:
            int: Índice del libro en la lista de datos, o -1 si no se encuentra.
        """
        self._refresh_cache()
        index = linear_search(
            self.read_all().to_list(),
            key=lambda book:book.get_id_IBSN(),
            item=Book.from_search_api(id=id)
        )
        return len(self.read_all().to_list()) - index -1
    
    def __search_book(self, id: str) -> dict | int:
        """Obtiene el diccionario del libro correspondiente al id dado.

        Args:
            id (str): id_IBSN del libro.

        Returns:
            dict | int: Diccionario con los datos del libro si se encuentra,
            o -1 si no existe.
        """
        index = self.__search_id(id)
        # return self._books_cache[index] if index != -1 else -1
        return self._books_cache[index]
    
    def create(self, json: dict) -> Book:
        """Crea un nuevo Book a partir de un dict y lo persiste.

        Args:
            json (dict): Datos del libro.

        Returns:
            Book: Instancia creada.
        """
        instance = Book.from_dict(json)
        self.__file.append(instance.to_dict())
        self._refresh_cache()
        return instance
    
    def read(self, id:str) -> Book | None:
        """Lee un libro por su id.

        Args:
            id: id_IBSN del libro.

        Returns:
            Book | None: Instancia Book si se encuentra, None en caso contrario.
        """
        book = self.__search_book(id)
        if book == -1:
            print(f"Book with id {id} not found.")
            return None
        instance = Book.from_dict(book)
        return instance
        
    def read_all(self) -> Stack[Book] | None:
        """Lee todos los libros y los devuelve en una pila (Stack).

        Returns:
            Stack[Book] | None: Pila con todas las instancias Book o None si la
            colección está vacía.
        """
        self._refresh_cache()
        if not self._books_cache:
            print("No books found in the repository.")
            return None
        books = Stack[Book]()
        for data in self._books_cache:
            book = Book.from_dict(data)
            books.push(book)
        return books
    
    def update(self, id: str, json: dict) -> Book | None:
        """Actualiza un libro existente con datos proporcionados.
        Args:
            id (str): id_IBSN del libro a actualizar.
            json (dict): Campos a actualizar.

        Returns:
            Book | None: Instancia actualizada o None si no se encontró.
        """
        
        index = self.__search_id(id)
        if index == -1:
            print(f"Book with id {id} not found for update.")
            return None
        instance = Book.from_dict(self._books_cache[index])
        instance.update_from_dict(json)
        self._books_cache[index] = instance.to_dict()
        print('update id_IBSN:', id, 'data:', json)
        
        self.__file.write(self._books_cache)
        return instance
        
    def delete(self, id: str) -> bool:
        """Elimina un libro por su id y persiste el cambio en el archivo.

        Args:
            id (str): id_IBSN del libro a eliminar.

        Returns:
            bool: True si se eliminó con éxito, False si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print(f"Book with id {id} not found for deletion.")
            return False
        self._books_cache.pop(index)
        self.__file.write(self._books_cache)
        return True
    
    def __str__(self) -> str:
        """Representación legible del repositorio."""
        file_info = getattr(self.__file, "path", getattr(self.__file, "url", str(self.__file)))
        return f"BooksRepository(file={file_info!r}, cached_books={len(self._books_cache)})"

    def __repr__(self) -> str:
        """Representación no ambigua para debugging."""
        return f"BooksRepository(file={self.__file!r}, books_count={len(self._books_cache)})"