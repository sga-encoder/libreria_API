from fastapi import APIRouter, Depends, HTTPException, status
from . import LoanCreate, LoanUpdate
from app.dependencies import get_current_admin, get_loan_service
from app.domain.services import LoanService

loan_router = APIRouter(
    prefix="/api/v1/loan",
    tags=["loan"]
)

@loan_router.post("/", dependencies=[Depends(get_current_admin)], status_code=status.HTTP_201_CREATED)
def create(
    loan: LoanCreate, 
    loan_service: LoanService = Depends(get_loan_service)
    ):
    """Crear un nuevo préstamo (solo admin)."""
    try:
        data = loan_service.create(loan.model_dump())
        return {"message": "Préstamo creado satisfactoriamente", "data": data.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@loan_router.get("/{id}")
def read(id: str, loan_service: LoanService = Depends(get_loan_service)):
    """Obtener los detalles de un préstamo por su ID con relaciones cargadas."""
    try:
        data = loan_service.get_by_id_with_details(id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
        return {"message": f"Préstamo {id} encontrado", "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@loan_router.get("/")
def read_all(loan_service: LoanService = Depends(get_loan_service)):
    """Obtener todos los préstamos con usuario y libro."""
    try:
        data = loan_service.get_all_with_details()
        return {"message": f"Se encontraron {len(data)} préstamos", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@loan_router.patch("/{id}", dependencies=[Depends(get_current_admin)])
def update(id: str, loan: LoanUpdate, loan_service: LoanService = Depends(get_loan_service)):
    """Actualizar un préstamo (solo admin)."""
    try:
        payload = loan.model_dump(exclude_unset=True)
        data = loan_service.update(id, payload)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
        return {"message": f"Préstamo {id} actualizado", "data": data.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@loan_router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete(id: str, loan_service: LoanService = Depends(get_loan_service)):
    """Eliminar un préstamo (solo admin)."""
    try:
        result = loan_service.delete(id)
        return {"message": f"Préstamo {id} eliminado", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@loan_router.post("/{id}/return", dependencies=[Depends(get_current_admin)])
def return_loan(id: str, loan_service: LoanService = Depends(get_loan_service)):
    """Marcar préstamo como devuelto (devolución de libro)."""
    try:
        result = loan_service.deactivate(id)
        return {"message": f"Préstamo {id} marcado como devuelto", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@loan_router.get("/user/{id_user}")
def get_loans_by_user(id_user: str, loan_service: LoanService = Depends(get_loan_service)):
    """Obtener todos los préstamos de un usuario."""
    try:
        data = loan_service.get_by_user(id_user)
        return {"message": f"Se encontraron {len(data)} préstamos del usuario", "data": [l.to_dict() for l in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@loan_router.get("/book/{id_ISBN}")
def get_loans_by_book(id_ISBN: str, loan_service: LoanService = Depends(get_loan_service)):
    """Obtener todos los préstamos de un libro."""
    try:
        data = loan_service.get_by_book(id_ISBN)
        return {"message": f"Se encontraron {len(data)} préstamos del libro", "data": [l.to_dict() for l in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@loan_router.get("/active/list")
def get_active_loans(loan_service: LoanService = Depends(get_loan_service)):
    """Obtener todos los préstamos activos."""
    try:
        data = loan_service.get_active()
        return {"message": f"Se encontraron {len(data)} préstamos activos", "data": [l.to_dict() for l in data]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return {
            "message": f"Error al ejecutar organización: {str(e)}",
            "data": None
        }