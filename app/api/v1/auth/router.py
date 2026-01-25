from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_user_service, get_admin_service
from app.domain.services import UserService
from app.core import  settings 
from .schemas import UserIn, LoginRequest
from app.dependencies import get_current_user
from .services import AuthAPIService

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    admin_service: UserService = Depends(get_admin_service)
) -> AuthAPIService:
    """Inyecta AuthAPIService con servicios de usuario y admin."""
    return AuthAPIService(
        user_service=user_service,
        admin_service=admin_service,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )



@auth_router.post("/login")
def login(credentials: LoginRequest, auth_service: AuthAPIService = Depends(get_auth_service)):
    """Autenticar usuario o admin."""
    return auth_service.login(credentials.email, credentials.password)


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