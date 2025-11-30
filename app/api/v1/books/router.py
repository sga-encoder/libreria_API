"""
Módulo de rutas para la API de libros (v1).

Proporciona endpoints para crear, leer, actualizar y eliminar libros.
Cada función de ruta delega la lógica de negocio al BookAPIService y
devuelve una respuesta JSON con un mensaje y los datos correspondientes.
"""
from fastapi import APIRouter
from .services import BookAPIService
from .schemas import BookCreate, BookUpdate
from app.core import settings
from app.domain.models import Book

book_router = APIRouter(
    prefix="/book",
    tags=["book"]
)


book_service = BookAPIService(settings.DATA_PATH_INVENTARY)

@book_router.post("/")
def create(book: BookCreate):
    """
    Crear un nuevo libro usando los datos proporcionados.

    Parámetros:
    - book (BookCreate): Objeto con los datos necesarios para crear el libro.

    Retorna:
    - dict: Mensaje de éxito y representación del libro creado.
    """
    data:Book = book_service.create(book)
    return {"message": f'sea creado el libro satisfactoriamente',  "data": data.to_dict()}

@book_router.post("/ISBN/{id_IBSN}")
def create_by_ISBN(id_IBSN: str):
    """
    Crear un libro consultando información a partir del ISBN.

    Parámetros:
    - id_IBSN (str): Cadena que representa el ISBN del libro a crear.

    Retorna:
    - dict: Mensaje de éxito y representación del libro creado.
    """
    data:Book = book_service.create_by_ISBN(id_IBSN)
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
    data:Book = book_service.read(id_IBSN)
    return {"message":  f"sea a leido el libro {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.get("/")
def read_all():
    """
    Obtener la lista de todos los libros registrados.

    Retorna:
    - dict: Mensaje de éxito y lista de libros (cada uno como dict).
    """
    data:Book = book_service.read_all()
    return {"message": f"se a leido satisfactoriamente todos los libros", "data": [b.to_dict() for b in data]}

@book_router.patch("/{id_IBSN}")
def update(id_IBSN: str, book: BookUpdate):
    """
    Actualizar campos de un libro existente identificado por ISBN.

    Parámetros:
    - id_IBSN (str): ISBN del libro a actualizar.
    - book (BookUpdate): Objeto con los campos a actualizar.

    Retorna:
    - dict: Mensaje de éxito y representación del libro actualizado.
    """
    data:Book = book_service.update(id_IBSN, book)
    return {"message": f"sea actualizado el libro con el {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.delete("/{id_IBSN}")
def delete(id_IBSN:str):
    """
    Eliminar un libro identificado por su ISBN.

    Parámetros:
    - id_IBSN (str): ISBN del libro a eliminar.

    Retorna:
    - dict: Mensaje de éxito y un booleano indicando la operación.
    """
    data:Book = book_service.delete(id_IBSN)
    return {"message": f"se elimino el libro con este {id_IBSN} satisfactoriamente",   "data": True}

