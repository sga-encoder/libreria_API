import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import settings, oauth2_scheme, decode_access_token
from app.core.database import get_db
from app.persistence.repositories import UsersRepositorySQL, AdminsRepositorySQL, BooksRepositorySQL
from app.domain.services import UserService, AdminService, BookService, InventoryService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ==================== REPOSITORIOS ====================
def get_users_repository(db: Session = Depends(get_db)) -> UsersRepositorySQL:
    return UsersRepositorySQL(db)

def get_admins_repository(db: Session = Depends(get_db)) -> AdminsRepositorySQL:
    return AdminsRepositorySQL(db)

def get_books_repository(db: Session = Depends(get_db)) -> BooksRepositorySQL:
    return BooksRepositorySQL(db)

# ==================== SERVICIOS DE DOMINIO ====================
def get_user_service(repo: UsersRepositorySQL = Depends(get_users_repository)) -> UserService:
    return UserService(repo=repo)

def get_admin_service(repo: AdminsRepositorySQL = Depends(get_admins_repository)) -> AdminService:
    return AdminService(repo=repo)

def get_book_service(repo: BooksRepositorySQL = Depends(get_books_repository)) -> BookService:
    return BookService(repo=repo)

def get_inventory_service() -> InventoryService:
    return InventoryService(settings.DATA_PATH_INVENTARY)

# ==================== AUTENTICACIÓN ====================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    """Obtiene el usuario actual desde el token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = user_service.get_by_email(email)
    if user is None:
        raise credentials_exception
    
    # ✅ Evitar AttributeError si el modelo de dominio no expone is_active
    is_active = getattr(user, "is_active", True)
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o eliminado"
        )
    
    return user

def get_current_admin(
    token: str = Depends(oauth2_scheme),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Obtiene el admin actual desde el token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado. Se requieren permisos de administrador.",
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    role: str = payload.get("role")
    
    if email is None or role != "ADMIN":
        raise credentials_exception
    
    admin = admin_service.get_by_email(email)
    if admin is None:
        raise credentials_exception
    
    return admin

def verify_user_ownership(current_user, requested_user_id: str):
    """Verifica que el usuario actual sea el propietario del recurso."""
    # ✅ Manejar tanto User objects como strings
    current_id = current_user.get_id() if hasattr(current_user, 'get_id') else str(current_user)
    
    if current_id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso"
        )