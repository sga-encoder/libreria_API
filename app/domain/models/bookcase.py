from .book import Book
from .bookshelf import BookShelf
from .enums import TypeOrdering
from typing import List

class  BookCase:
    _stands: List[BookShelf]  # Lista de estantes
    _TypeOrdering: TypeOrdering
    _weighCapacity: float
    _capacityStands: int
    _store: List[Book]  # Lista de libros almacenados
    
    def __init__(self, stands: List[BookShelf], TypeOrdering: TypeOrdering, weighCapacity: float, capacityStands: int, store: List[Book]):
        self.set_stands(stands if stands else [])
        self.set_TypeOrdering(TypeOrdering)
        self.set_weighCapacity(weighCapacity)
        self.set_capacityStands(capacityStands)
        self.set_store(store if store else [])
        
    @classmethod
    def from_dict(cls, data: dict): 
        stands = [BookShelf.from_dict(shelf_data) for shelf_data in data.get("stands", [])]
        store = [Book.from_dict(book_data) for book_data in data.get("store", [])]
        return cls(
            stands=stands,
            TypeOrdering=TypeOrdering[data["TypeOrdering"]],
            weighCapacity=data["weighCapacity"],
            capacityStands=data["capacityStands"],
            store=store
        )
    def get_stands(self) -> List[BookShelf]:
        return self._stands
    
    def get_TypeOrdering(self) -> TypeOrdering:
        return self._TypeOrdering
    
    def get_weighOrdering(self) -> float:
        return self._weighCapacity
    
    def get_capacityStands(self) -> int:
        return self._capacityStands
    
    def get_store(self) -> List[Book]:
        return self._store
    
    def set_stands(self, stands: List[BookShelf]):
        self._stands = stands
    
    def set_TypeOrdering(self, TypeOrdering: TypeOrdering):
        self._TypeOrdering = TypeOrdering
    
    def set_weighCapacity(self, weighCapacity: float):
        self._weighCapacity = weighCapacity
    
    def set_capacityStands(self, capacityStands: int):
        self._capacityStands = capacityStands
    
    def set_store(self, store: List[Book]):
        self._store = store
    
    def add_shelf(self, shelf: BookShelf):
        """Agrega un estante al bookcase."""
        self._stands.append(shelf)
        self._capacityStands = len(self._stands)

    def to_dict(self):
        return {
            "stands": [shelf.to_dict() for shelf in self._stands],
            "TypeOrdering": str(self._TypeOrdering),
            "weighCapacity": self._weighCapacity,
            "capacityStands": self._capacityStands,
            "store": [book.to_dict() for book in self._store]
        }
    
    def __str__(self):
        total_books = sum(len(shelf.get_books()) for shelf in self._stands)
        return f"BookCase: {len(self._stands)} shelves, {total_books} books, {self._TypeOrdering}, capacity: {self._weighCapacity}kg"
    
    def __repr__(self):
        return f"BookCase(stands={len(self._stands)}, TypeOrdering={self._TypeOrdering}, weighCapacity={self._weighCapacity}, capacityStands={self._capacityStands}, store={len(self._store)} books)"