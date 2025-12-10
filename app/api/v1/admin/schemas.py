from pydantic import BaseModel
from typing import Optional

# Modelo completo para POST (todos los campos requeridos)
class AdminCreate(BaseModel):
    fullName: str
    email: str
    password: str
    
# Modelo para PATCH (solo id requerido, el resto opcional)
class AdminUpdate(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
