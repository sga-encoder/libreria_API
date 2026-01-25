from fastapi import APIRouter, Depends
from . import UserCreate, UserUpdate
from app.dependencies import get_current_user, verify_user_ownership, get_user_service
from app.domain.services import UserService

user_router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)

@user_router.post("/")
def create(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    payload = user.model_dump()
    data = user_service.add(payload)
    return {"message": "usuario creado satisfactoriamente", "data": data.to_dict()}

@user_router.get("/{id}", dependencies=[Depends(get_current_user)])
def read(id: str, user_service: UserService = Depends(get_user_service)):
    data = user_service.get_by_id(id)
    return {"message": f"se ha leído el usuario {id}", "data": data.to_dict()}

@user_router.get("/")
def read_all(user_service: UserService = Depends(get_user_service)):
    data = user_service.get_all()
    return {"message": "se han leído satisfactoriamente todos los usuarios", "data": [user.to_dict() for user in data]}

@user_router.patch("/{id}")
def update(id: str, user: UserUpdate, 
           current_user=Depends(get_current_user), 
           user_service: UserService = Depends(get_user_service)):
    # ✅ Extraer el ID del usuario actual
    verify_user_ownership(current_user.get_id(), id)
    payload = user.model_dump(exclude_unset=True)
    data = user_service.update(id, payload)
    return {"message": f"usuario {id} actualizado satisfactoriamente", "data": data.to_dict()}

@user_router.delete("/{id}")
def delete(id: str, current_user=Depends(get_current_user), user_service: UserService = Depends(get_user_service)):
    # ✅ Extraer el ID del usuario actual
    verify_user_ownership(current_user.get_id(), id)
    data = user_service.delete(id)
    return {"message": f"usuario {id} eliminado satisfactoriamente", "data": data}