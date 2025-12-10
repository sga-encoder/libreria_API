"""Repositorio de libros persistido en un archivo JSON.

Este módulo contiene la implementación de BooksRepository, una
implementación de RepositoriesInterface para objetos Book. Usa FileManager
para lectura/escritura de datos en formato JSON y mantiene una caché
local de los registros leídos.
"""
from app.domain.models import Book
from app.domain.structures import Stack
from app.utils import FileManager, FileType
from app.domain.algorithms import linear_search
from .interface import RepositoriesInterface

class BooksRepository(RepositoriesInterface[Book]):
    """Repositorio de Book respaldado por un archivo JSON.

    Aporta operaciones CRUD básicas sobre libros: create, read, read_all,
    update y delete. Mantiene una caché interna (_books_cache) que se
    sincroniza con el archivo mediante FileManager.
    """
    __file : FileManager
    __books: list[Book]
    
    def __init__(self, url: str) -> None:
        """Inicializa el repositorio.

        Args:
            url (str): Ruta o URL del archivo JSON donde se almacenan los libros.
        """
        self.__file = FileManager(url, FileType.JSON)
        self.__books = self.__file.read()

    def __refresh_books(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__books = self.__file.read()
        
    def __search_id(self, id: str) -> int:
        """Busca el índice de un libro por su id_IBSN.

        Args:
            id (str): Valor del id_IBSN a buscar.

        Returns:
            int: Índice del libro en la lista de datos, o -1 si no se encuentra.
        """
        self.__refresh_books()
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
        return self.__books[index]
    
    def create(self, json: dict) -> Book:
        """Crea un nuevo Book a partir de un dict y lo persiste.

        Args:
            json (dict): Datos del libro.

        Returns:
            Book: Instancia creada.
        """
        instance = Book.from_dict(json)
        self.__file.append(instance.to_dict())
        self.__refresh_books()
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
        self.__refresh_books()
        if not self.__books:
            print("No books found in the repository.")
            return None
        books = Stack[Book]()
        for data in self.__books:
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
        instance = Book.from_dict(self.__books[index])
        instance.update_from_dict(json)
        self.__books[index] = instance.to_dict()
        # print('update id_IBSN:', id, 'data:', json)
        
        self.__file.write(self.__books)
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
        self.__books.pop(index)
        self.__file.write(self.__books)
        return True
    
    def loan(self, id: str) -> bool:
        """Marca un libro como prestado (is_borrowed = True).
        
        Busca el libro por su id_IBSN, marca como prestado y persiste el cambio.
        
        Args:
            id (str): id_IBSN del libro a marcar como prestado.
            
        Returns:
            bool: True si se marcó como prestado exitosamente, False si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print(f"Book with id {id} not found for loan.")
            return False
        
        instance = Book.from_dict(self.__books[index])
        instance.set_is_borrowed(True)
        self.__books[index] = instance.to_dict()
        self.__file.write(self.__books)
        
        return True
    
    def return_loan(self, id: str) -> bool:
        """Marca un libro como disponible (is_borrowed = False).
        
        Busca el libro por su id_IBSN, marca como disponible y persiste el cambio.
        
        Args:
            id (str): id_IBSN del libro a marcar como disponible.
            
        Returns:
            bool: True si se marcó como disponible exitosamente, False si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print(f"Book with id {id} not found for return.")
            return False
        
        instance = Book.from_dict(self.__books[index])
        instance.set_is_borrowed(False)
        self.__books[index] = instance.to_dict()
        self.__file.write(self.__books)
        
        return True
    
    def __str__(self) -> str:
        """Representación legible del repositorio."""
        file_info = getattr(self.__file, "path", getattr(self.__file, "url", str(self.__file)))
        return f"BooksRepository(file={file_info!r}, cached_books={len(self.__books)})"

    def __repr__(self) -> str:
        """Representación no ambigua para debugging."""
        return f"BooksRepository(file={self.__file!r}, books_count={len(self.__books)})"
    
