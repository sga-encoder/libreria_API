from fastapi import APIRouter
from . import UserCreate, UserUpdate
from app.services import Library
from app.core import settings
from app.domain.models import User
from .services import UserAPIService

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


user_service = UserAPIService(settings.DATA_PATH_USERS)


@user_router.post("/")
def create(user: UserCreate):
    data = user_service.create_user(user)
    return {"message": "usuario creado satisfactoriamente",  "data": data.to_dict()}

@user_router.get("/{id}")
def read(id: str):
    data = user_service.read_user(id)
    return {"message":  f"se ha leído el usuario {id}", "data": data.to_dict()}

@user_router.get("/")
def read_all():
    data = user_service.read_all_users()
    return {"message": "se han leído satisfactoriamente todos los usuarios", "data": [user.to_dict() for user in data]}

@user_router.patch("/{id}")
def update(id: str, user: UserUpdate):
    data = user_service.update_user(id, user)
    return {"message": f"usuario {id} actualizado satisfactoriamente", "data": data.to_dict()}


@user_router.delete("/{id}")
def delete(id: str):
    data = user_service.delete_user(id)
    return {"message": f"usuario {id} eliminado satisfactoriamente", "data": data}