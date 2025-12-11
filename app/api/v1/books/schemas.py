from pydantic import BaseModel
from typing import Optional

# Modelo completo para POST (campos esenciales requeridos)
class BookCreate(BaseModel):
    id_IBSN: str
    title: str
    author: str
    gender: str
    weight: float
    price: float  # Requerido - cada libro debe tener su precio
    is_borrowed: bool = False  # Requerido para loans, con valor por defecto
    description: Optional[str] = ""
    frond_page_url: Optional[str] = ""
    yearPublished: Optional[int] = None
    editorial: Optional[str] = None

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