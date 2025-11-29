from fastapi import APIRouter
from app.schemas import LoanCreate, LoanUpdate
from app.crud import CRUDLoan
from app.services import Library

loan_router = APIRouter(
    prefix="/loan",
    tags=["loan"]
)
loan_crud = CRUDLoan(Library.get_loanRecords(), Library.get_reservationsQueue(), Library.get_user())
@loan_router.post("/")
def create(loan: LoanCreate):
    data = loan_crud.create(loan)
    return {
        "message": f'sea creado el Prestamo satisfactoriamente',
        "data": data
    }

@loan_router.get("/{id}")
def read(id: str):
    data = loan_crud.read(id)
    return {
        "message":  f"sea a leido el prestamo {id}",
        "data": data}

@loan_router.get("/")
def read_all():
    data = loan_crud.read_all()
    return {
        "message": f"se a leido satisfactoriamente todos los prestamo", 
        "data": data
    }

@loan_router.patch("/{id}")
def update(id:str, loan: LoanUpdate):
    data = loan_crud.update(id, loan)
    return {
        "message": f"sea actualizado el prestamo con el {id} satisfactoriamente", 
        "data": data
    }

@loan_router.delete("/{id}")
def delete(id: str):
    data = loan_crud.delete(id)
    return {"message": f"se elimino el prestamo con este {id} satisfactoriamente", "data": data}