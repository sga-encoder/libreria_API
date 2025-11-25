"""
Schemas de Pydantic para validación de datos.
"""

from .user import UserCreate, UserUpdate
from .book import BookCreate, BookUpdate
from .loan import LoanCreate, LoanUpdate
from .auth import AuthLogin

__all__ = [
    # User schemas
    'UserCreate',
    'UserUpdate',
    # Book schemas
    'BookCreate',
    'BookUpdate',
    # Loan schemas
    'LoanCreate',
    'LoanUpdate',
    # Auth schemas
    'AuthLogin',
]