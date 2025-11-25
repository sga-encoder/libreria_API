from pydantic import BaseModel
from typing import Optional
from app.models.enums import PersonRole

# Modelo completo para POST (todos los campos requeridos)
class UserCreate(BaseModel):
    fullName: str
    email: str
    password: str
    
# Modelo para PATCH (solo id requerido, el resto opcional)
class UserUpdate(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None