from fastapi import APIRouter, Depends, HTTPException, status

from app.core import  settings 
from .schemas import UserIn
from app.dependencies import get_current_user
from .services import AuthAPIService

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Ejemplo: usuario ficticio. En producción usar repositorio/BD.
# Servicio de autenticación
auth_service = AuthAPIService(
    settings.DATA_PATH_USERS,
    settings.DATA_PATH_ADMINS,
    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)

@auth_router.post("/login")
async def login_json(payload: UserIn):
    access_token, type_token  = auth_service.loginWithJson(payload)
    return {"message": 'inicio de sesion  exitoso por Json',"access_token": access_token, "token_type": type_token}


@auth_router.post("/logout")
def logout():
    """Logout demo (no hay invalidación de tokens en este ejemplo)."""
    return {"message": "logged out"}


@auth_router.get("/me")
def read_me(current_user = Depends(get_current_user)):
    """Devuelve el usuario actual (usa `get_current_user`)."""
    try:
        return {"data": current_user.to_dict()}
    except Exception:
        return {"data": current_user}