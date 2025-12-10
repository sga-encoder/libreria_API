from app.domain.services import UserService
from pydantic import BaseModel
from app.domain.models import User
from app.domain.models.enums import PersonRole
from fastapi import HTTPException, status


class AdminAPIService:
    """Servicio de API para gestionar operaciones de administradores.
    
    Esta clase actúa como intermediario entre la API REST y el servicio de dominio,
    manejando las solicitudes HTTP y convirtiendo datos entre modelos Pydantic y de dominio.
    
    Attributes:
        __admin_service (UserService): Servicio de dominio para operaciones con administradores.
    """
    def __init__(self, url: str) -> None:
        """Inicializa el servicio de administradores.
        
        Args:
            url (str): Ruta o URL del archivo donde se almacenan los administradores.
        """
        self.__admin_service = UserService(url, role=PersonRole.ADMIN)
        
    def create_admin(self, json: BaseModel) -> User:
        """Crea un nuevo administrador a través de la API.
        
        Args:
            json (BaseModel): Modelo Pydantic con los datos del administrador.
            
        Returns:
            User: El administrador creado.
            
        Raises:
            HTTPException: Si ocurre un error durante la creación.
        """
        try:
            data = json.model_dump()
            result = self.__admin_service.add(data)
            return result
        except Exception as e:
            print(f"Error creating admin: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo crear el administrador")
        
    def read_admin(self, id: str) -> User | None:
        """Lee un administrador específico por ID a través de la API.
        
        Args:
            id (str): ID del administrador a leer.
            
        Returns:
            User | None: El administrador encontrado.
            
        Raises:
            HTTPException: Si el administrador no se encuentra o hay error.
        """
        try:
            result = self.__admin_service.get_user_by_id(id)
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado")
            return result
        except Exception as e:
            print(f"Error reading admin: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo el administrador")
        
    def read_all_admins(self) -> list[User]:
        """Lee todos los administradores a través de la API.
        
        Returns:
            list[User]: Lista de todos los administradores.
            
        Raises:
            HTTPException: Si no hay administradores o hay error.
        """
        try:
            result = self.__admin_service.get_users()
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay administradores disponibles")
            return result
        except Exception as e:
            print(f"Error reading all admins: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo todos los administradores")
        
    def update_admin(self, id: str, json: BaseModel) -> User | None:
        """Actualiza un administrador existente a través de la API.
        
        Args:
            id (str): ID del administrador a actualizar.
            json (BaseModel): Modelo Pydantic con los nuevos datos.
            
        Returns:
            User | None: El administrador actualizado.
            
        Raises:
            HTTPException: Si el administrador no se encuentra o hay error.
        """
        try:
            data = json.model_dump(exclude_unset=True)
            result = self.__admin_service.update_user(id, data)
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado para actualizar")
            return result
        except Exception as e:
            print(f"Error updating admin: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando el administrador")
        
    def delete_admin(self, id: str) -> bool:
        """Elimina un administrador por ID a través de la API.
        
        Args:
            id (str): ID del administrador a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa.
            
        Raises:
            HTTPException: Si el administrador no se encuentra o hay error.
        """
        try:
            result = self.__admin_service.delete_user(id)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado para eliminar")
            return result
        except Exception as e:
            print(f"Error deleting admin: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error eliminando el administrador")