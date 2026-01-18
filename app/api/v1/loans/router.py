from fastapi import APIRouter, Depends
from . import LoanCreate, LoanUpdate
from .schemas import BookCaseCreate, BookCaseInfo, TypeOrderingEnum
from .services import LoanAPIService
from app.core import settings
from app.dependencies import get_current_user, get_current_admin
from app.domain.models.enums import TypeOrdering

loan_router = APIRouter(
    prefix="/api/v1/loan",
    tags=["loan"]
)

# Inicializar servicio
loan_api_service = LoanAPIService(
    settings.DATA_PATH_LOANS_RECORDS, 
    settings.DATA_PATH_CURRENT_LOANS,
    settings.DATA_PATH_INVENTARY, 
    settings.DATA_PATH_USERS
)

# Crear BookCase con algoritmo DEFICIENT por defecto
try:
    loan_api_service.create_bookcase_with_algorithm(
        algorithm_type=TypeOrdering.DEFICIENT,
        weight_capacity=10.0,
        capacity_stands=5
    )
    print("[OK] BookCase inicializado con algoritmo DEFICIENT")
except Exception as e:
    print(f"[WARN] No se pudo inicializar BookCase: {e}")
    print("  Los prestamos funcionaran sin ordenamiento de estanterias")

@loan_router.post("/")
def create(loan: LoanCreate):
    """
    Crear un nuevo préstamo usando los datos proporcionados.

    Parámetros:
    - loan (LoanCreate): Objeto con email del usuario e ISBN del libro.

    Retorna:
    - dict: Mensaje de éxito y representación del préstamo creado.
    """
    data = loan_api_service.create(loan)
    return {
        "message": 'Préstamo creado satisfactoriamente',
        "data": data.to_dict() if hasattr(data, 'to_dict') else str(data)
    }

@loan_router.get("/{id}")
def read(id: str):
    """
    Obtener los detalles de un préstamo por su ID.

    Parámetros:
    - id (str): ID del préstamo a consultar.

    Retorna:
    - dict: Mensaje de éxito y representación del préstamo consultado.
    """
    data = loan_api_service.read_loan(id)
    return {
        "message": f"Préstamo {id} leído satisfactoriamente",
        "data": data.to_dict_with_objects() if hasattr(data, 'to_dict') else str(data)
    }

@loan_router.get("/")
def read_all():
    """
    Obtener la lista de todos los préstamos registrados.

    Retorna:
    - dict: Mensaje de éxito y lista de préstamos (cada uno como dict).
    """
    data = loan_api_service.read_all_loans()
    return {
        "message": "Se leyeron satisfactoriamente todos los préstamos", 
        "data": [loan.to_dict_with_objects() if hasattr(loan, 'to_dict') else str(loan) for loan in data]
    }

@loan_router.patch("/{id}")
def update(id: str, loan: LoanUpdate):
    """
    Actualizar un préstamo existente reemplazando el libro.

    Parámetros:
    - id (str): ID del préstamo a actualizar.
    - loan (LoanUpdate): Objeto con el nuevo ISBN del libro.

    Retorna:
    - dict: Mensaje de éxito y representación del nuevo préstamo.
    """
    data = loan_api_service.update(id, loan)
    return {
        "message": f"Préstamo {id} actualizado satisfactoriamente", 
        "data": data.to_dict_with_objects() if hasattr(data, 'to_dict') else str(data)
    }

@loan_router.delete("/{id}")
def delete(id: str):
    """
    Eliminar un préstamo identificado por su ID.

    Parámetros:
    - id (str): ID del préstamo a eliminar.

    Retorna:
    - dict: Mensaje de éxito y un booleano indicando la operación.
    """
    result = loan_api_service.delete(id)
    return {
        "message": f"Préstamo {id} eliminado satisfactoriamente",
        "data": result
    }


@loan_router.get("/reservations/queue")
def get_reservations_queue():
    """
    Obtener la lista de espera (reservation queue) de libros.
    
    Retorna la cola de reservas con todos los usuarios que están esperando
    por libros que actualmente están prestados.
    
    Retorna:
    - dict: Mensaje de éxito y lista de reservas con su posición.
    
    Ejemplo de respuesta:
    {
        "message": "Cola de reservas obtenida exitosamente",
        "data": [
            {
                "position": 1,
                "user_email": "juan.perez@test.com",
                "user_name": "Juan Pérez",
                "book_isbn": "9780156012195",
                "book_title": "El Principito"
            },
            ...
        ],
        "total_reservations": 4
    }
    """
    reservations = loan_api_service.get_reservations_queue()
    return {
        "message": "Cola de reservas obtenida exitosamente" if reservations else "No hay reservas en espera",
        "data": reservations,
        "total_reservations": len(reservations)
    }


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS DE BOOKCASE - Gestionar ordenamiento de libros
# ════════════════════════════════════════════════════════════════════════════

@loan_router.get("/bookcase/status")
def get_bookcase_status():
    """
    Obtener el estado actual del BookCase.
    
    Retorna:
    - dict: Información sobre si BookCase está configurado y sus parámetros.
    
    Ejemplo de respuesta:
    {
        "message": "Estado del BookCase",
        "data": {
            "is_configured": true,
            "algorithm_type": "DEFICIENT",
            "weight_capacity": 10.0,
            "capacity_stands": 5
        }
    }
    """
    bookcase = loan_api_service.get_bookcase()
    
    if bookcase is None:
        info = {
            "is_configured": False,
            "algorithm_type": None,
            "weight_capacity": None,
            "capacity_stands": None
        }
    else:
        info = {
            "is_configured": True,
            "algorithm_type": str(bookcase.get_TypeOrdering()),
            "weight_capacity": bookcase.get_weighOrdering(),
            "capacity_stands": bookcase.get_capacityStands()
        }
    
    return {
        "message": "Estado del BookCase",
        "data": info
    }


@loan_router.post("/bookcase/configure")
def configure_bookcase(config: BookCaseCreate):
    """
    Crear o actualizar la configuración del BookCase.
    
    Parámetros:
    - config (BookCaseCreate): Objeto con:
        - algorithm_type: "DEFICIENT" o "OPTIMOUM"
        - weight_capacity: Capacidad de peso en kg
        - capacity_stands: Cantidad de estantes
    
    Ejemplo de solicitud:
    {
        "algorithm_type": "DEFICIENT",
        "weight_capacity": 15.0,
        "capacity_stands": 8
    }
    
    Retorna:
    - dict: Mensaje de éxito y parámetros configurados.
    """
    try:
        # Convertir string a enum
        algorithm_enum = TypeOrdering[config.algorithm_type.value]
        
        # Crear BookCase con la configuración
        bookcase = loan_api_service.create_bookcase_with_algorithm(
            algorithm_type=algorithm_enum,
            weight_capacity=config.weight_capacity,
            capacity_stands=config.capacity_stands
        )
        
        return {
            "message": "BookCase configurado exitosamente",
            "data": {
                "algorithm_type": config.algorithm_type.value,
                "weight_capacity": config.weight_capacity,
                "capacity_stands": config.capacity_stands
            }
        }
    except Exception as e:
        return {
            "message": f"Error al configurar BookCase: {str(e)}",
            "data": None
        }


@loan_router.delete("/bookcase/disable")
def disable_bookcase():
    """
    Desactivar el BookCase (sin ordenamiento de estanterías).
    
    Los préstamos continuarán funcionando sin aplicar ordenamiento.
    
    Retorna:
    - dict: Mensaje de confirmación.
    """
    loan_api_service.set_bookcase(None)
    
    return {
        "message": "BookCase desactivado",
        "data": {
            "is_configured": False,
            "info": "Los préstamos funcionarán sin ordenamiento de estanterías"
        }
    }


@loan_router.post("/bookcase/organize", dependencies=[Depends(get_current_admin)])
def organize_bookcase():
    """
    Ejecutar manualmente el algoritmo de organización configurado.
    
    REQUIERE AUTENTICACIÓN DE ADMINISTRADOR
    
    Ejecuta el algoritmo de ordenamiento (DEFICIENT o OPTIMOUM) sobre todos
    los libros del inventario según la configuración actual del BookCase.
    
    Retorna:
    - dict: Resultado de la organización con detalles del algoritmo ejecutado.
    
    Ejemplo de respuesta:
    {
        "message": "Organización ejecutada exitosamente",
        "data": {
            "algorithm_type": "DEFICIENT",
            "weight_capacity": 10.0,
            "books_processed": 25,
            "dangerous_combinations_found": 3,
            "execution_status": "success"
        }
    }
    """
    try:
        result = loan_api_service.execute_organization()
        return {
            "message": "Organización ejecutada exitosamente",
            "data": result
        }
    except Exception as e:
        return {
            "message": f"Error al ejecutar organización: {str(e)}",
            "data": None
        }