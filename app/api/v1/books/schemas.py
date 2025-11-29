from pydantic import BaseModel
from typing import Optional

# Modelo completo para POST (todos los campos requeridos)
class BookCreate(BaseModel):
    id_IBSN: str
    title: str
    author: str
    gender: str
    weight: float
    price: float
    description: str
    frond_page_url: str
    is_borrowed: bool

# Modelo para PATCH (solo id requerido, el resto opcional)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    price: Optional[float] = None
    description: Optional[str] = None
    frond_page_url: Optional[str] = None
    is_borrowed: Optional[bool] = None