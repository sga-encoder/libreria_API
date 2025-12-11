from  fastapi import HTTPException, status
from app.domain.services import InventoryService
from app.domain.models import Book
from pydantic import BaseModel
from app.integrations import search_book

"""Módulo de servicios para la API de libros.

Provee una capa intermedia entre los endpoints de la API y la lógica de dominio
(InventoryService). Contiene la clase BookAPIService que orquesta operaciones
como crear, leer, actualizar y eliminar libros, además de buscar libros
externamente por ISBN.
"""

class BookAPIService:
    """Servicio de API para operaciones sobre libros.

    Esta clase encapsula un InventoryService y expone métodos que manejan la
    entrada/salida necesaria para los endpoints de la API (validación mínima,
    conversión de modelos y manejo de excepciones HTTP apropiadas).

    Atributos:
        __inventary_service (InventoryService): servicio de dominio para la gestión de inventario.
    """
    def __init__(self, url: str) -> None:
        """Inicializa el servicio con la URL del inventario.

        Args:
            url (str): URL o configuración necesaria para instanciar InventoryService.
        """
        self.__inventary_service = InventoryService(url)
        
    def create_book(self, json: BaseModel) -> Book:
        """Crea un libro a partir de un modelo Pydantic.

        Convierte el BaseModel recibido a dict, delega la creación en el
        InventoryService y devuelve el Book creado.

        Args:
            json (BaseModel): modelo de entrada con los datos del libro.

        Returns:
            Book: libro creado.

        Raises:
            HTTPException: 500 si ocurre un error interno.
        """
        try:
            data = json.model_dump()
            result = self.__inventary_service.add_book(data)
            return result
        except Exception as e:
            print(f"Error creating book: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo crear el libro")
        
    def create_book_by_ISBN(self, id_IBSN: str) -> Book:
        """Crea un libro buscando los datos por ISBN en una API externa.

        Realiza la búsqueda externa usando search_book, toma el primer resultado
        y lo agrega al inventario.

        Args:
            id_IBSN (str): ISBN del libro a buscar.

        Returns:
            Book: libro creado a partir de los datos externos.

        Raises:
            HTTPException: 404 si no se encuentra el libro en la API externa.
        """
        try:
            books = search_book(f'isbn:{id_IBSN}')
            book_data = books[0]
            result = self.__inventary_service.add_book(book_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in external API")

    def read_book(self, id_IBSN: str) -> Book | None:
        """Obtiene un libro del inventario por su ISBN.

        Args:
            id_IBSN (str): ISBN del libro a leer.

        Returns:
            Book | None: instancia Book si se encuentra, None en caso contrario.

        Raises:
            HTTPException: 404 si no se encuentra, 500 en errores internos.
        """
        try:
            result = self.__inventary_service.get_book_by_id(id_IBSN)
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error reading book")
        
    def read_all_books(self) -> list[Book]:
        """Devuelve la lista completa de libros del inventario.

        Returns:
            list[Book]: lista de libros.

        Raises:
            HTTPException: 404 si no hay libros, 500 en errores internos.
        """
        try:
            books_stack = self.__inventary_service.get_inventary()
            if books_stack is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
            return books_stack.to_list()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error reading all books")
        
    def update_book(self, id_IBSN: str, json: BaseModel) -> Book | None:
        """Actualiza los campos de un libro existente.

        Realiza un model_dump excluyendo campos no seteados y delega la actualización
        al repositorio de libros.

        Args:
            id_IBSN (str): ISBN del libro a actualizar.
            json (BaseModel): modelo Pydantic con los campos a actualizar.

        Returns:
            Book | None: libro actualizado o None si no existe.

        Raises:
            HTTPException: 404 si no se encuentra el libro, 500 en errores internos.
        """
        try:
            data = json.model_dump(exclude_unset=True)
            book = self.__inventary_service.update_book(id_IBSN, data)
            if book is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found for update")
            return book
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating book")
    
    def delete_book(self, id_IBSN: str) -> bool:
        """Elimina un libro del inventario por su ISBN.

        Args:
            id_IBSN (str): ISBN del libro a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            HTTPException: 404 si no se encuentra el libro, 500 en errores internos.
        """
        try:
            result = self.__inventary_service.delete_book(id_IBSN)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found for deletion")
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error deleting book: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting book")