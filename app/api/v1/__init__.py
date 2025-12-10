from .auth import auth_router
from .books import book_router
from .loans import loan_router
from .users import user_router
from .admin.router import admin_router
__all__ = ["auth_router", "book_router", "loan_router", "user_router"]