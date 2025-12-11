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
    
    def get_total_value_by_author(self, author: str) -> dict:
        """Calcula el valor total de todos los libros de un autor específico.
        
        Utiliza el algoritmo TotalValue (recursivo con Stack) para procesar
        todos los libros del inventario y calcular el valor total de aquellos
        que pertenecen al autor especificado.
        
        Args:
            author (str): Nombre del autor cuyos libros se quieren valorar.
        
        Returns:
            dict: Diccionario con el autor, valor total y número de libros encontrados.
                  Formato: {
                      "author": str,
                      "total_value": float,
                      "books_count": int,
                      "books": list[dict]
                  }
        
        Raises:
            HTTPException: 500 en errores internos.
        """
        try:
            # Obtener el valor total usando el servicio de inventario
            total_value = self.__inventary_service.get_total_value_by_author(author)
            
            # Obtener los libros del autor para información adicional
            all_books = self.__inventary_service.get_inventary().to_list()
            author_books = [book for book in all_books if book.get_author() == author]
            
            return {
                "author": author,
                "total_value": round(total_value, 2),
                "books_count": len(author_books),
                "books": [
                    {
                        "title": book.get_title(),
                        "isbn": book.get_id_IBSN(),
                        "price": book.get_price()
                    }
                    for book in author_books
                ]
            }
        except Exception as e:
            print(f"Error calculating total value by author: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calculating total value for author: {author}"
            )
    
    def generate_global_report(
        self,
        file_path: str = None,
        format: str = "json",
        value_key: str = "price",
        descending: bool = True
    ) -> dict:
        """Genera un reporte global de todos los libros ordenados por valor.
        
        Obtiene todos los libros del inventario, los ordena por el campo de valor especificado,
        y opcionalmente guarda el reporte en formato CSV o JSON.
        
        Args:
            file_path: Ruta donde guardar el reporte (opcional). Si no se proporciona, solo retorna el reporte.
            format: Formato del archivo ('csv' o 'json'). Default: 'json'.
            value_key: Campo por el cual ordenar. Default: 'price'.
            descending: Si es True ordena de mayor a menor. Default: True.
        
        Returns:
            dict: Diccionario con:
                - books: lista de libros ordenados
                - total_books: cantidad total de libros
                - total_value: suma total de valores
                - file_saved: ruta del archivo guardado (si aplica)
                - format: formato utilizado
        
        Raises:
            HTTPException: 500 en errores internos.
        """
        try:
            # Generar el reporte usando el servicio de inventario
            report = self.__inventary_service.generate_global_report(
                file_path=file_path,
                format=format,
                value_key=value_key,
                descending=descending
            )
            
            # Calcular el total de valores
            total_value = sum(
                float(book.get(value_key, 0)) 
                for book in report
            )
            
            result = {
                "books": report,
                "total_books": len(report),
                "total_value": round(total_value, 2),
                "format": format
            }
            
            if file_path:
                result["file_saved"] = file_path
            
            return result
            
        except Exception as e:
            print(f"Error generating global report: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating global report: {str(e)}"
            )
    
    def get_average_weight_by_author(self, author: str) -> dict:
        """Calcula el peso promedio de los libros de un autor usando recursión de cola.
        
        Utiliza un algoritmo de tail recursion para procesar todos los libros y
        calcular el peso promedio de aquellos que pertenecen al autor especificado.
        El algoritmo muestra en consola cada paso de la recursión para demostrar
        el funcionamiento de la recursión de cola.
        
        Args:
            author: Nombre del autor cuyos libros se quieren analizar.
        
        Returns:
            dict: Diccionario con:
                - author: nombre del autor
                - average_weight: peso promedio en kg
                - total_books: cantidad de libros
                - books: lista de libros con detalles
        
        Raises:
            HTTPException: 500 en errores internos.
        """
        try:
            # Calcular usando el servicio de inventario
            result = self.__inventary_service.get_average_weight_by_author(author)
            
            return result
            
        except Exception as e:
            print(f"Error calculating average weight by author: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calculating average weight for author: {author}"
            )