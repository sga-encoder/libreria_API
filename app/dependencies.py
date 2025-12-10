from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
import logging
from app.core import settings, oauth2_scheme
from app.domain.services import UserService
from app.domain.models.enums import  PersonRole
from app.domain.models import User

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


user_service = UserService(settings.DATA_PATH_USERS)
admin_service = UserService(settings.DATA_PATH_ADMINS, role=PersonRole.ADMIN)

oauth2_scheme = oauth2_scheme  # reexport si quiere

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    
    # Buscar en usuarios normales
    users = user_service.get_users_all()
    for u in users:
        if u.get_email() == username:
            return u
    
    # Buscar en admins si no lo encontró en usuarios
    admins = admin_service.get_users_all()
    for a in admins:
        if a.get_email() == username:
            return a
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    
    # Buscar SOLO en admins
    admins = admin_service.get_users_all()
    for admin in admins:
        if admin.get_email() == username:
            return admin
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: requiere permisos de administrador")

def verify_user_ownership(user_id: str, current_user: User):
    """Verifica que el usuario autenticado sea el propietario del recurso o sea admin."""
    # Obtener el rol del usuario
    user_role = current_user.get_role()
    user_id_actual = current_user.get_id()
    
    # Si es admin, permitir
    if user_role.name == "ADMIN":
        return current_user
    
    # Si es usuario normal, verificar que sea el propietario
    if user_id_actual != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este usuario"
        )
    
    return current_user