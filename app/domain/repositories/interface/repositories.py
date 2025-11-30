from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class RepositoriesInterface(ABC, Generic[T]):
    """
    Interfaz genérica para operaciones CRUD.
    """
    
    @abstractmethod
    def create(self, json: dict) -> T:
        """Crea una nueva entidad"""
        pass
    
    @abstractmethod
    def read(self, id: str) -> Optional[T]:
        """Lee una entidad por ID"""
        pass
    
    @abstractmethod
    def read_all(self) -> List[T]:
        """Lee todas las entidades"""
        pass

    
    @abstractmethod
    def update(self, id: str, json: dict) -> Optional[T]:
        """Actualiza una entidad existente"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Elimina una entidad por ID"""
        pass