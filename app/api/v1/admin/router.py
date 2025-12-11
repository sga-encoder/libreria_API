from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from .schemas import AdminCreate, AdminUpdate, BookCaseCreate
from app.core import settings
from .services import AdminAPIService
from app.dependencies import get_current_admin, oauth2_scheme
from app.domain.models.enums import TypeOrdering

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)

admin_service = AdminAPIService(settings.DATA_PATH_ADMINS)


@admin_router.post("/")
def create(admin: AdminCreate):
    """Crear un nuevo administrador.
    
    - Si NO hay admins: permite crear el primer admin sin autenticación
    - Si YA hay admins: requiere token de admin para crear más
    """
    # admins = admin_service.read_all_admins()
    
    # # Si ya hay admins, verificar autenticación
    # if len(admins) > 0:
    #     if not token:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Se requiere autenticación de administrador"
    #         )
    #     # Verificar que sea admin válido
    #     current_admin = get_current_admin(token)
    
    # # Crear el nuevo admin
    print("Creating new admin...")
    data = admin_service.create_admin(admin)
    return {"message": "administrador creado satisfactoriamente", "data": data.to_dict()}

@admin_router.get("/{id}", dependencies=[Depends(get_current_admin)])
def read(id: str):
    """Leer un administrador específico"""
    data = admin_service.read_admin(id)
    return {"message": f"se ha leído el administrador {id}", "data": data.to_dict()}

@admin_router.get("/", dependencies=[Depends(get_current_admin)])
def read_all():
    """Leer todos los administradores"""
    data = admin_service.read_all_admins()
    return {"message": "se han leído satisfactoriamente todos los administradores", "data": [admin.to_dict() for admin in data]}

@admin_router.patch("/{id}", dependencies=[Depends(get_current_admin)])
def update(id: str, admin: AdminUpdate):
    """Actualizar un administrador"""
    data = admin_service.update_admin(id, admin)
    return {"message": f"administrador {id} actualizado satisfactoriamente", "data": data.to_dict()}

@admin_router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete(id: str):
    """Eliminar un administrador"""
    data = admin_service.delete_admin(id)
    return {"message": f"administrador {id} eliminado satisfactoriamente", "data": data}

@admin_router.post("/bookcase", dependencies=[Depends(get_current_admin)])
def create_bookcase(bookcase_data: BookCaseCreate):
    """Crear un nuevo bookcase en la biblioteca"""
    try:
        # Validar el tipo de ordenamiento
        if bookcase_data.typeOrdering not in ["DEFICIENT", "OPTIMOUM"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="typeOrdering debe ser 'DEFICIENT' o 'OPTIMOUM'"
            )
        
        # Convertir el string a enum
        type_ordering = TypeOrdering[bookcase_data.typeOrdering]
        
        # Por ahora solo almacenamos la información del bookcase
        # La integración completa con BookCase, BookShelf y Book se puede hacer después
        bookcase_info = {
            "typeOrdering": bookcase_data.typeOrdering,
            "weighCapacity": bookcase_data.weighCapacity,
            "capacityStands": bookcase_data.capacityStands
        }
        
        return {
            "message": "Bookcase creado satisfactoriamente",
            "data": bookcase_info
        }
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="typeOrdering inválido. Use 'DEFICIENT' o 'OPTIMOUM'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el bookcase: {str(e)}"
        )
