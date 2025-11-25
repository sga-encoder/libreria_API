from .book import book_router
from .loan import loan_router
from .user import user_router
from .auth import auth_router

__all__ = ['book_router', 'loan_router', 'user_router', 'auth_router']