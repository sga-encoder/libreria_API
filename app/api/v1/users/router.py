from fastapi import APIRouter,  Depends
from . import UserCreate, UserUpdate
from app.core import settings
from .services import UserAPIService
from app.dependencies import get_current_user, verify_user_ownership

user_router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)


user_service = UserAPIService(settings.DATA_PATH_USERS)


@user_router.post("/")
def create(user: UserCreate):
    data = user_service.create_user(user)
    
    return {"message": "usuario creado satisfactoriamente",  "data": data.to_dict()}

@user_router.get("/{id}", dependencies=[Depends(get_current_user)])
def read(id: str):
    data = user_service.read_user(id)
    return {"message":  f"se ha leído el usuario {id}", "data": data.to_dict()}

@user_router.get("/")
def read_all():
    data = user_service.read_all_users()
    return {"message": "se han leído satisfactoriamente todos los usuarios", "data": [user.to_dict() for user in data]}

@user_router.patch("/{id}")
def update(id: str, user: UserUpdate, current_user = Depends(get_current_user)):
    verify_user_ownership(id, current_user)
    data = user_service.update_user(id, user)
    return {"message": f"usuario {id} actualizado satisfactoriamente", "data": data.to_dict()}


@user_router.delete("/{id}")
def delete(id: str, current_user = Depends(get_current_user)):
    verify_user_ownership(id, current_user)
    data = user_service.delete_user(id)
    return {"message": f"usuario {id} eliminado satisfactoriamente", "data": data}