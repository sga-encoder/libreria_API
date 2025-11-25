from app.models import Book
from app.crud.interface import ICrud


class CRUDBook(ICrud[Book]):
    def __init__(self, books: list[Book], orderBooks: list[Book]) -> None:
        self.__books = books
        self.__orderBooks = orderBooks
        
    def create(self, json: dict) -> Book:
        print("implementando create en CRUDBook")
        # Aceptar tanto dicts como modelos Pydantic (BookCreate)
        # Preferir model_dump() (Pydantic v2), caer a dict() si no existe
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        return Book.from_dict(data)
    
    def read(self, id):
        print("implementando read en CRUDBook")
        return id
    
    def read_all(self):
        print("implementando read_all en CRUDBook")
        return self.__books
    
    def update(self, id: str, json: dict) -> Book:
        print("implementando update en CRUDBook")
        # Aceptar tanto dicts como modelos Pydantic (BookUpdate)
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        # Ensure the id key matches the Book model expectation
        data["id_IBSN"] = id
        return Book.from_dict(data)
    
    def delete(self, id: str) -> bool:
        print("implementando delete en CRUDBook")
        return True
    