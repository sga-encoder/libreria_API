from .book import Book
from .bookshelf import BookShelf
from .enums import TypeOrdering

class BookCase:
    _stands : BookShelf
    _TypeOrdering : TypeOrdering
    _weighCapacity : float
    _capacityStands : int
    _store : Book
    
    def __init__(self, stands : BookShelf, TypeOrdering : TypeOrdering, weighCapacity : float, capacityStands : int, store : Book):
        self.set_stands(stands)
        self.set_TypeOrdering(TypeOrdering)
        self.set_weighCapacity(weighCapacity)
        self.set_capacityStands(capacityStands)
        self.set_store(store)
        
    @classmethod
    def from_dict(cls, data : dict): 
        return cls(
            stands=BookShelf[data["stands"]],
            TypeOrdering=TypeOrdering[data["TypeOrdering"]],
            weighCapacity=[data["weighCapacity"]],
            capacityStands=[data["capacityStands"]],
            store=Book[data["store"]]
        )
    def get_stands(self):
        return self._stands
    def get_TypeOrdering(self):
        return self._TypeOrdering
    def get_weighOrdering(self):
        return self._weighCapacity
    def get_capacityStands(self):
        return self._capacityStands
    def get_store(self):
        return self._store
    
    def set_stands(self, stands : BookShelf):
        self._stands = stands
    def set_TypeOrdering(self, TypeOrdering : TypeOrdering):
        self._TypeOrdering = TypeOrdering
    def set_weighCapacity(self, weighCapacity : float):
        self._weighCapacity = weighCapacity
    def set_capacityStands(self, capacityStands : int):
        self._capacityStands = capacityStands
    def set_store(self, store : Book):
        self._store = store

    def to_dict(self):
        return {
            "stands": self._stands,
            "TypeOrdering": self._TypeOrdering,
            "weighCapacity": self._weighCapacity,
            "capacityStands": self._capacityStands,
            "store": self._stands
        }
    
    def __str__(self):
        return f"Bookcase: {self._stands}, (weighCapacity: {self._weighCapacity}), (capacityStands : {self._capacityStands}) - Bookshelf : {self._stands} - TypeOrdering : {self._TypeOrdering} - Books : {self._store}"
    def __repr__(self):
        return f"Bookcase(stands={self._stands}, TypeOrdering={self._TypeOrdering}, weighCapacity={self._weighCapacity}, capacityStands={self._capacityStands}, store={self._store})"