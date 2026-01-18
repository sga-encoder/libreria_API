from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# Usar IDs en los schemas evita que Pydantic intente generar esquemas
# para clases arbitrarias (por ejemplo, modelos de dominio / ORM).

class TypeOrderingEnum(str, Enum):
    """Enumeración de algoritmos de ordenamiento disponibles"""
    DEFICIENT = "DEFICIENT"
    OPTIMOUM = "OPTIMOUM"


class LoanCreate(BaseModel):
    id_user: str
    id_ISBN_book: str


class LoanUpdate(BaseModel):
    id_ISBN_book: str


class BookCaseCreate(BaseModel):
    """Schema para crear/configurar un BookCase"""
    algorithm_type: TypeOrderingEnum = TypeOrderingEnum.DEFICIENT
    weight_capacity: float = 10.0
    capacity_stands: int = 5
    
    class Config:
        description = "Configuración del BookCase para ordenamiento de libros"


class BookCaseInfo(BaseModel):
    """Schema para información del BookCase actual"""
    algorithm_type: Optional[str] = None
    weight_capacity: Optional[float] = None
    capacity_stands: Optional[int] = None
    is_configured: bool = False
    
    class Config:
        description = "Información del BookCase configurado"