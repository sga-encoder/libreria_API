from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Usar IDs en los schemas evita que Pydantic intente generar esquemas
# para clases arbitrarias (por ejemplo, modelos de dominio / ORM).
class LoanCreate(BaseModel):
    user: str
    book: str
    loanDate: datetime


class LoanUpdate(BaseModel):
    user: Optional[str] = None
    book: Optional[str] = None
    loanDate: Optional[datetime] = None