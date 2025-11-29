from fastapi import APIRouter
from . import UserCreate, UserUpdate
from app.domain.repositories import UsersRepository
from app.services import Library


user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


user_crud = UsersRepository(Library.get_user())


@user_router.get("/")
def read_all():
    data = user_crud.read_all()
    return {"message": "se han leído satisfactoriamente todos los usuarios", "data": data}


@user_router.get("/{id}")
def read(id: str):
    data = user_crud.read(id)
    return {"message":  f"se ha leído el usuario {id}", "data": data}


@user_router.post("/")
def create(user: UserCreate):
    data = user_crud.create(user)
    return {"message": "usuario creado satisfactoriamente",  "data": data}


@user_router.patch("/{id}")
def update(id: str, user: UserUpdate):
    data = user_crud.update(id, user)
    return {"message": f"usuario {id} actualizado satisfactoriamente", "data": data}


@user_router.delete("/{id}")
def delete(id: str):
    data = user_crud.delete(id)
    return {"message": f"usuario {id} eliminado satisfactoriamente", "data": data}