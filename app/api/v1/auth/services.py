from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core import create_access_token
from app.domain.services import UserService
from app.domain.models import User
from app.domain.models.enums import PersonRole


class AuthAPIService:
    """Servicio que encapsula la lógica de autenticación usada por el router.

    Provee métodos para autenticar usuarios y construir la respuesta del token.
    """

    def __init__(self, user_service: UserService, admin_service: UserService, expire_minutes: int):
        # Servicios separados para usuarios y administradores
        self.user_service = user_service
        self.admin_service = admin_service
        self._expire_minutes = expire_minutes

    def __authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Buscar usuario/admin por email y verificar contraseña."""
        # primero admin
        admin = self.admin_service.get_by_email(email)
        if admin and admin.verify_password(password):
            return admin
        if admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="✗ Contraseña incorrecta")

        # luego usuario
        user = self.user_service.get_by_email(email)
        if user and user.verify_password(password):
            return user
        if user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="✗ Contraseña incorrecta")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="✗ Usuario no encontrado")
    
    def __create_token_response(self, user: User, type_token: str = 'bearer') -> dict:
        """Construye y devuelve el dict con `access_token` y `token_type` para un usuario dado."""
        email = user.get_email() 
        role = user.get_role().name
        access_token = create_access_token(data={"sub": email, "role": role}, expires_delta=timedelta(minutes=self._expire_minutes))
        return (access_token, type_token)
    
    def login(self, email: str, password: str) -> dict:
        """Autentica usuario/admin y devuelve token."""
        try:
            user = self.__authenticate_user(email, password)
            
            # ✅ Verificar que esté activo
            if hasattr(user, 'is_active') and not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario inactivo o eliminado"
                )
            
            token = create_access_token({
                "sub": user.get_email(),
                "role": user.get_role().name
            }, timedelta(minutes=self._expire_minutes))
            
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    def loginWithJson(self, json: BaseModel):
        data = json.model_dump()
        user = self.__authenticate_user(data.get("email"), data.get("password"))
        return self.__create_token_response(user)



