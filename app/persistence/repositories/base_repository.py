from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model
    
    def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def read(self, id: str) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def read_all(self) -> List[T]:
        return self.db.query(self.model).all()
    
    def update(self, id: str, **kwargs) -> Optional[T]:
        obj = self.read(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj
    
    def delete(self, id: str) -> bool:
        obj = self.read(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False