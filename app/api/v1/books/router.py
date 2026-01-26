"""
Módulo de rutas para la API de libros (v1).

Proporciona endpoints para crear, leer, actualizar y eliminar libros con BD SQL.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import BookCreate, BookUpdate
from app.dependencies import get_current_admin, get_book_service
from app.domain.services import BookService

book_router = APIRouter(
    prefix="/api/v1/book",
    tags=["book"]
)

@book_router.post("/", dependencies=[Depends(get_current_admin)], status_code=status.HTTP_201_CREATED)
def create(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    """Crear un nuevo libro (solo admin)."""
    try:
        data = book_service.add(book.model_dump())
        return {"message": "Libro creado satisfactoriamente", "data": data.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@book_router.get("/{id_IBSN}")
def read(id_IBSN: str, book_service: BookService = Depends(get_book_service)):
    """Obtener los detalles de un libro por su ISBN."""
    try:
        data = book_service.get_by_isbn(id_IBSN)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
        return {"message": f"Libro {id_IBSN} encontrado", "data": data.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.get("/")
def read_all(book_service: BookService = Depends(get_book_service)):
    """Obtener todos los libros."""
    try:
        data = book_service.get_all()
        return {"message": f"Se encontraron {len(data)} libros", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.patch("/{id_IBSN}", dependencies=[Depends(get_current_admin)])
def update(id_IBSN: str, book: BookUpdate, book_service: BookService = Depends(get_book_service)):
    """Actualizar un libro (solo admin)."""
    try:
        payload = book.model_dump(exclude_unset=True)
        data = book_service.update(id_IBSN, payload)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
        return {"message": f"Libro {id_IBSN} actualizado", "data": data.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.delete("/{id_IBSN}", dependencies=[Depends(get_current_admin)])
def delete(id_IBSN: str, book_service: BookService = Depends(get_book_service)):
    """Eliminar un libro (solo admin)."""
    try:
        result = book_service.delete(id_IBSN)
        return {"message": f"Libro {id_IBSN} eliminado", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@book_router.get("/search/author/{author}")
def search_by_author(author: str, book_service: BookService = Depends(get_book_service)):
    """Buscar libros por autor."""
    try:
        data = book_service.get_by_author(author)
        return {"message": f"Se encontraron {len(data)} libros del autor '{author}'", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.get("/search/title/{title}")
def search_by_title(title: str, book_service: BookService = Depends(get_book_service)):
    """Buscar libros por título."""
    try:
        data = book_service.get_by_title(title)
        return {"message": f"Se encontraron {len(data)} libros con el título '{title}'", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.get("/search/genre/{genre}")
def search_by_genre(genre: str, book_service: BookService = Depends(get_book_service)):
    """Buscar libros por género."""
    try:
        data = book_service.get_by_genre(genre)
        return {"message": f"Se encontraron {len(data)} libros del género '{genre}'", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.get("/available/list")
def get_available(book_service: BookService = Depends(get_book_service)):
    """Obtener libros disponibles (no prestados)."""
    try:
        data = book_service.get_available()
        return {"message": f"Se encontraron {len(data)} libros disponibles", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@book_router.get("/borrowed/list")
def get_borrowed(book_service: BookService = Depends(get_book_service)):
    """Obtener libros prestados."""
    try:
        data = book_service.get_borrowed()
        return {"message": f"Se encontraron {len(data)} libros prestados", "data": [b.to_dict() for b in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
