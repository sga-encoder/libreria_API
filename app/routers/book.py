from fastapi import APIRouter, HTTPException, status
from app.schemas import BookCreate, BookUpdate
from app.crud import CRUDBook
from app.services import search_book_by_BookAPI

book_router = APIRouter(
    prefix="/book",
    tags=["book"]
)

book_crud = CRUDBook('data/json/books.json')

@book_router.post("/")
def create(book: BookCreate):
    data = book_crud.create(book)
    return {"message": f'sea creado el libro satisfactoriamente',  "data": data.to_dict()}

@book_router.post("/ISBN/{id_IBSN}")
def create_by_ISBN(id_IBSN: str):
    books = search_book_by_BookAPI(f'isbn:{id_IBSN}')
    # `search_book_by_BookAPI` devuelve una lista; tomar el primer resultado
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in external API")
    book_data = books[0]
    data = book_crud.create(book_data)
    return {"message": f'sea creado el libro satisfactoriamente',  "data": data.to_dict()}


@book_router.get("/{id_IBSN}")
def read(id_IBSN: str):
    data = book_crud.read(id_IBSN)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return {"message":  f"sea a leido el libro {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.get("/")
def read_all():
    data = book_crud.read_all()
    return {"message": f"se a leido satisfactoriamente todos los libros", "data": [b.to_dict() for b in data]}

@book_router.patch("/{id_IBSN}")
def update(id_IBSN: str, book: BookUpdate):
    data = book_crud.update(id_IBSN, book)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return {"message": f"sea actualizado el libro con el {id_IBSN} satisfactoriamente", "data": data.to_dict()}

@book_router.delete("/{id_IBSN}")
def delete(id_IBSN:str):
    data = book_crud.delete(id_IBSN)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return {"message": f"se elimino el libro con este {id_IBSN} satisfactoriamente",   "data": True}

