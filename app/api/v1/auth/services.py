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

    def __init__(self, users_url: str, admins_url: str, expire_minutes: int):
        # Servicios separados para usuarios y administradores
        self.user_service = UserService(users_url)
        self.admin_service = UserService(admins_url)
        self._expire_minutes = expire_minutes

    def __authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Buscar usuario por email y verificar contraseña."""
        users = self.user_service.get_users_all() or []
        admins = self.admin_service.get_users_all() or []
        all_people = users + admins
        
        for user in all_people:
            if email == user.get_email():
                if user.verify_password(password):
                    return user
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="✗ Contraseña incorrecta")
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="✗ Usuario no encontrado")
    
    def __create_token_response(self, user: User, type_token: str = 'bearer') -> dict:
        """Construye y devuelve el dict con `access_token` y `token_type` para un usuario dado."""
        email = user.get_email() 
        role = user.get_role().name
        access_token = create_access_token(data={"sub": email, "role": role}, expires_delta=timedelta(minutes=self._expire_minutes))
        return (access_token, type_token)
    
    def loginWithJson(self, json: BaseModel):
        data = json.model_dump()
        user = self.__authenticate_user(data.get("email"), data.get("password"))
        return self.__create_token_response(user)
        
        

