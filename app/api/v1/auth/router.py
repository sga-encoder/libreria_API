from fastapi import APIRouter
from .schemas import AuthLogin

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.post("/login")
def login(auth: AuthLogin):
    return {"message": "implement login", "data": auth}

@auth_router.post("/logout")
def logout():
    return {"message": "implement logout"}