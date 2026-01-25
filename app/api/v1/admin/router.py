from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import AdminCreate, AdminUpdate, BookCaseCreate
from app.dependencies import get_admin_service, get_current_admin, get_user_service
from app.core.security import oauth2_scheme
from app.domain.models.enums import TypeOrdering
from app.domain.services import UserService

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)


@admin_router.post("/")
def create(admin: AdminCreate, admin_service: UserService = Depends(get_admin_service)):
    """Crear un nuevo administrador.
    
    - Si NO hay admins: permite crear el primer admin sin autenticación
    - Si YA hay admins: requiere token de admin para crear más
    """
    try:
        print(f"Creating new admin with data: {admin}")
        data = admin_service.add(admin.model_dump())
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear administrador: el servicio devolvió None"
            )
        print(f"Admin created successfully: {data.get_id()}")
        return {"message": "administrador creado satisfactoriamente", "data": data.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear administrador: {str(e)}"
        )

@admin_router.get("/{id}", dependencies=[Depends(get_current_admin)])
def read(id: str, admin_service: UserService = Depends(get_admin_service)):
    """Leer un administrador específico"""
    data = admin_service.get_by_id(id)
    return {"message": f"se ha leído el administrador {id}", "data": data.to_dict()}

@admin_router.get("/", dependencies=[Depends(get_current_admin)])
def read_all(admin_service: UserService = Depends(get_admin_service)):
    """Leer todos los administradores"""
    data = admin_service.get_all()
    return {"message": "se han leído satisfactoriamente todos los administradores", "data": [admin.to_dict() for admin in data]}

@admin_router.patch("/{id}", dependencies=[Depends(get_current_admin)])
def update(id: str, admin: AdminUpdate, admin_service: UserService = Depends(get_admin_service)):
    """Actualizar un administrador"""
    data = admin_service.update(id, admin.model_dump(exclude_unset=True))
    return {"message": f"administrador {id} actualizado satisfactoriamente", "data": data.to_dict()}

@admin_router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete(id: str, admin_service: UserService = Depends(get_admin_service)):
    """Eliminar un administrador"""
    data = admin_service.delete(id)
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
        
@admin_router.get("/pila/{author}", dependencies=[Depends(get_current_admin)])
def read_by_author(author: str, token: str = Depends(oauth2_scheme), admin_service: UserService = Depends(get_admin_service)):
    """Leer administradores por autor"""
    # Nota: Este método no existe en UserService, puede necesitar implementación
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Método no implementado en UserService"
    )

@admin_router.get("/pila/{prices}", dependencies=[Depends(get_current_admin)])
def read_by_price_range(prices: str, token: str = Depends(oauth2_scheme), admin_service: UserService = Depends(get_admin_service)):
    """Leer administradores por rango de precios"""
    try:
        min_price_str, max_price_str = prices.split(",")
        min_price = float(min_price_str)
        max_price = float(max_price_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato de 'prices' debe ser 'min,max' con valores numéricos"
        )
    
    # Nota: Este método no existe en UserService, puede necesitar implementación
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Método no implementado en UserService"
    )


@admin_router.post("/bootstrap", status_code=status.HTTP_201_CREATED)
def bootstrap_admin(
    admin: AdminCreate,
    admin_service: UserService = Depends(get_admin_service)
):
    """Crear el primer administrador (solo si no hay admins).
    
    Este endpoint NO requiere autenticación y solo funciona una sola vez.
    """
    existing_admins = admin_service.get_all()
    
    if existing_admins and len(existing_admins) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ya existen administradores. No se puede crear otro sin autenticación."
        )
    
    try:
        data = admin_service.add(admin.model_dump())
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear administrador"
            )
        
        return {
            "message": "Administrador bootstrap creado satisfactoriamente",
            "data": data.to_dict(),
            "info": "Este es el primer admin. Guarda estas credenciales en un lugar seguro."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear administrador: {str(e)}"
        )

@admin_router.patch("/user/activate/{email}" , dependencies=[Depends(get_current_admin)])
def activate_user(email: str, _: str = Depends(get_current_admin), user_service: UserService = Depends(get_user_service)):
    """Activa un usuario por ID (solo admin)."""
    try:
        result = user_service.activate(email)
        return {"message": f"Usuario {email} activado", "data": result}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
