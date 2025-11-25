from pydantic import BaseModel
from typing import Optional
from app.models.enums import BookGender

# Modelo completo para POST (todos los campos requeridos)
class BookCreate(BaseModel):
    id_IBSN: str
    title: str
    author: str
    gender: BookGender
    weight: float
    price: float
    is_borrowed: bool

# Modelo para PATCH (solo id requerido, el resto opcional)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    gender: Optional[BookGender] = None
    weight: Optional[float] = None
    price: Optional[float] = None
    is_borrowed: Optional[bool] = None