"""
Módulo de rutas para la API de libros (v1).

Proporciona endpoints para crear, leer, actualizar y eliminar libros.
Cada función de ruta delega la lógica de negocio al BookAPIService y
devuelve una respuesta JSON con un mensaje y los datos correspondientes.
"""
from fastapi import APIRouter, Depends
from .services import BookAPIService
from .schemas import BookCreate, BookUpdate
from app.core import settings
from app.dependencies import get_current_user, get_current_admin

book_router = APIRouter(
    prefix="/api/v1/book",
    tags=["book"]
)


book_service = BookAPIService(settings.DATA_PATH_INVENTARY)

@book_router.post("/", dependencies=[Depends(get_current_admin)])
def create(book: BookCreate):
    """
    Crear un nuevo libro usando los datos proporcionados.

    Parámetros:
    - book (BookCreate): Objeto con los datos necesarios para crear el libro.

    Retorna:
    - dict: Mensaje de éxito y representación del libro creado.
    """
    data = book_service.create_book(book)
    return {"message": f'sea creado el libro satisfactoriamente',  "data": data.to_dict()}

@book_router.post("/ISBN/{id_IBSN}", dependencies=[Depends(get_current_admin)])
def create_by_ISBN(id_IBSN: str):
    """
    Crear un libro consultando información a partir del ISBN.

    Parámetros:
    - id_IBSN (str): Cadena que representa el ISBN del libro a crear.

    Retorna:
    - dict: Mensaje de éxito y representación del libro creado.
    """
    data = book_service.create_book_by_ISBN(id_IBSN)
    return {"message": f'sea creado el libro satisfactoriamente',  "data": data.to_dict()}

@book_router.get("/{id_IBSN}")
def read(id_IBSN: str):
    """
    Obtener los detalles de un libro por su ISBN.

    Parámetros:
    - id_IBSN (str): ISBN del libro a consultar.

    Retorna:
    - dict: Mensaje de éxito y representación del libro consultado.
    """
    data = book_service.read_book(id_IBSN)
    return {"message":  f"sea a leido el libro {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.get("/")
def read_all():
    """
    Obtener la lista de todos los libros registrados.

    Retorna:
    - dict: Mensaje de éxito y lista de libros (cada uno como dict).
    """
    data = book_service.read_all_books()
    return {"message": f"se a leido satisfactoriamente todos los libros", "data": [book.to_dict() for book in data]}

@book_router.patch("/{id_IBSN}", dependencies=[Depends(get_current_admin)])
def update(id_IBSN: str, book: BookUpdate):
    """
    Actualizar campos de un libro existente identificado por ISBN.

    Parámetros:
    - id_IBSN (str): ISBN del libro a actualizar.
    - book (BookUpdate): Objeto con los campos a actualizar.

    Retorna:
    - dict: Mensaje de éxito y representación del libro actualizado.
    """
    data  = book_service.update_book(id_IBSN, book)
    return {"message": f"sea actualizado el libro con el {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.delete("/{id_IBSN}",  dependencies=[Depends(get_current_admin)])
def delete(id_IBSN:str):
    """
    Eliminar un libro identificado por su ISBN.

    Parámetros:
    - id_IBSN (str): ISBN del libro a eliminar.

    Retorna:
    - dict: Mensaje de éxito y un booleano indicando la operación.
    """
    data  = book_service.delete_book(id_IBSN)
    return {"message": f"se elimino el libro con este {id_IBSN} satisfactoriamente",   "data": data}

@book_router.get("/author/{author}/total-value")
def get_total_value_by_author(author: str):
    """
    Calcular el valor total de todos los libros de un autor específico.
    
    Utiliza un algoritmo recursivo con pila (Stack) para procesar todos los libros
    del inventario y calcular el valor total de aquellos que pertenecen al autor.
    
    Parámetros:
    - author (str): Nombre del autor cuyos libros se quieren valorar.
    
    Retorna:
    - dict: Mensaje de éxito y datos con:
        - author: nombre del autor
        - total_value: valor total de sus libros
        - books_count: cantidad de libros encontrados
        - books: lista de libros con título, ISBN y precio
    
    Ejemplos:
    - GET /api/v1/book/author/George Orwell/total-value
    - GET /api/v1/book/author/Gabriel García Márquez/total-value
    """
    data = book_service.get_total_value_by_author(author)
    return {
        "message": f"Valor total calculado para el autor '{author}'",
        "data": data
    }

@book_router.get("/report/global")
def get_global_report(
    format: str = "json",
    value_key: str = "price",
    descending: bool = True,
    save_file: bool = False
):
    """
    Generar un reporte global de todos los libros ordenados por valor.
    
    Este endpoint obtiene todos los libros del inventario y los ordena por el campo
    de valor especificado (por defecto 'price'). Opcionalmente puede guardar
    el reporte en un archivo CSV o JSON.
    
    Parámetros de consulta:
    - format (str): Formato de salida ('csv' o 'json'). Default: 'json'.
    - value_key (str): Campo por el cual ordenar. Default: 'price'.
    - descending (bool): Si es True ordena de mayor a menor, False de menor a mayor. Default: True.
    - save_file (bool): Si es True guarda el reporte en un archivo. Default: False.
    
    Retorna:
    - dict: Mensaje de éxito y datos con:
        - books: lista de libros ordenados por valor
        - total_books: cantidad total de libros
        - total_value: suma total de valores
        - file_saved: ruta del archivo guardado (si save_file=True)
        - format: formato utilizado
    
    Ejemplos:
    - GET /api/v1/book/report/global
      Retorna el reporte en JSON sin guardar archivo
    
    - GET /api/v1/book/report/global?format=csv&save_file=true
      Retorna el reporte y lo guarda en CSV con fila de total
    
    - GET /api/v1/book/report/global?descending=false
      Retorna los libros ordenados de menor a mayor valor
    """
    # Definir ruta del archivo si se solicita guardar
    file_path = None
    if save_file:
        import os
        from datetime import datetime
        # Crear directorio de reportes si no existe
        reports_dir = "docs/demo/result_demos"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "csv" if format.lower() == "csv" else "json"
        file_path = f"{reports_dir}/global_report_{timestamp}.{extension}"
    
    data = book_service.generate_global_report(
        file_path=file_path,
        format=format,
        value_key=value_key,
        descending=descending
    )
    
    return {
        "message": "Reporte global generado exitosamente",
        "data": data
    }

@book_router.get("/author/{author}/average-weight")
def get_average_weight_by_author(author: str):
    """
    Calcular el peso promedio de todos los libros de un autor específico.
    
    Este endpoint utiliza un algoritmo de recursión de cola (tail recursion) para
    procesar todos los libros del inventario y calcular el peso promedio de aquellos
    que pertenecen al autor especificado.
    
    CARACTERÍSTICA EDUCATIVA:
    El algoritmo muestra en la consola del servidor cada paso de la recursión,
    demostrando cómo funciona la recursión de cola con acumuladores.
    
    Parámetros:
    - author (str): Nombre del autor cuyos libros se quieren analizar.
    
    Retorna:
    - dict: Mensaje de éxito y datos con:
        - author: nombre del autor
        - average_weight: peso promedio de sus libros en kg
        - total_books: cantidad de libros encontrados
        - books: lista de libros con título, ISBN y peso
    
    Ejemplos:
    - GET /api/v1/book/author/J.R.R. Tolkien/average-weight
      Calcula el peso promedio de todos los libros de Tolkien
    
    - GET /api/v1/book/author/Gabriel García Márquez/average-weight
      Calcula el peso promedio de todos los libros de García Márquez
    
    Nota:
    Revisar la consola del servidor para ver el proceso de recursión de cola
    paso a paso, incluyendo el estado de los acumuladores en cada llamada.
    """
    data = book_service.get_average_weight_by_author(author)
    return {
        "message": f"Peso promedio calculado para el autor '{author}' usando recursión de cola",
        "data": data
    }

