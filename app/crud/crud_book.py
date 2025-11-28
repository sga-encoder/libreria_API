from app.models import Book
from app.crud.interface import ICrud
from app.utils import Stack, FileManager, FileType
from app.services import Library



class CRUDBook(ICrud[Book]):
    __file : FileManager
    
    def __init__(self, url: str) -> None:
        self.__file = FileManager(url, FileType.JSON)
        self.load()
        
        
    def load(self):
        print("Cargando libros desde el archivo en CRUDBook")
        books_data = self.read_all()
        # Cargar los libros en el inventario de la biblioteca
        Library.set_inventary(books_data)
        print(Library.get_inventary())
        
        
    def create(self, json: dict) -> Book:
        print("implementando create en CRUDBook")
        # Aceptar tanto dicts como modelos Pydantic (BookCreate)
        # Preferir model_dump() (Pydantic v2), caer a dict() si no existe
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        else:
            data = json
            
        instance = Book.from_dict(data)
        
            
        self.__file.append(instance.to_dict())
        Library.push_inventary(instance)
        
            
        return instance
    
    def read(self, id):
        print("implementando read en CRUDBook")
        return id
    
    def read_all(self):
        books_data = self.__file.read()
        books = Stack[Book]()
        for data in books_data:
            book = Book.from_dict(data)
            books.push(book)
        return books
    
    def update(self, id: str, json: dict) -> Book:
        print("implementando update en CRUDBook")
        # Aceptar tanto dicts como modelos Pydantic (BookUpdate)
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        else:
            data = json
        # Ensure the id key matches the Book model expectation
        data["id_IBSN"] = id
        return Book.from_dict(data)
    
    def delete(self, id: str) -> bool:
        print("implementando delete en CRUDBook")
        return True
    