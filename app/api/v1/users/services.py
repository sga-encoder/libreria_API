from app.domain.services import UserService
from pydantic import BaseModel
from app.domain.models import User
from  fastapi import HTTPException, status


class UserAPIService:
    """Servicio de API para gestionar operaciones de usuarios.
    
    Esta clase actúa como intermediario entre la API REST y el servicio de dominio,
    manejando las solicitudes HTTP y convirtiendo datos entre modelos Pydantic y de dominio.
    
    Attributes:
        __user_service (UserService): Servicio de dominio para operaciones con usuarios.
    """
    def __init__(self, url: str) -> None:
        """Inicializa el servicio de usuarios.
        
        Args:
            url (str): Ruta o URL del archivo donde se almacenan los usuarios.
        """
        self.__user_service = UserService(url)
        
    def create_user(self, json: BaseModel) -> User:
        """Crea un nuevo usuario a través de la API.
        
        Args:
            json (BaseModel): Modelo Pydantic con los datos del usuario.
            
        Returns:
            User: El usuario creado.
            
        Raises:
            HTTPException: Si ocurre un error durante la creación.
        """
        try:
            data = json.model_dump()
            result = self.__user_service.add(data)
            return result
        except Exception as e:
            print(f"Error creating user: {e}")
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo crear el usuario")
        
    def read_user(self, id: str) -> User | None:
        """Lee un usuario específico por ID a través de la API.
        
        Args:
            id (str): ID del usuario a leer.
            
        Returns:
            User | None: El usuario encontrado.
            
        Raises:
            HTTPException: Si el usuario no se encuentra o hay error.
        """
        try:
            result = self.__user_service.get_by_id(id)
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            return result
        except Exception as e:
            print(f"Error reading user: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo el usuario")
        
    def read_all_users(self) -> list[User]:
        """Lee todos los usuarios a través de la API.
        
        Returns:
            list[User]: Lista de todos los usuarios.
            
        Raises:
            HTTPException: Si no hay usuarios o hay error.
        """
        try:
            result = self.__user_service.get_all()
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay usuarios disponibles")
            return result
        except Exception as e:
            print(f"Error reading all users: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error leyendo todos los usuarios")
        
    def update_user(self, id: str, json: BaseModel) -> User | None:
        """Actualiza un usuario existente a través de la API.
        
        Args:
            id (str): ID del usuario a actualizar.
            json (BaseModel): Modelo Pydantic con los nuevos datos.
            
        Returns:
            User | None: El usuario actualizado.
            
        Raises:
            HTTPException: Si el usuario no se encuentra o hay error.
        """
        try:
            data = json.model_dump(exclude_unset=True)
            result = self.__user_service.update(id, data)
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado para actualizar")
            return result
        except Exception as e:
            print(f"Error updating user: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando el usuario")
        
    def delete_user(self, id: str) -> bool:
        """Elimina un usuario por ID a través de la API.
        
        Args:
            id (str): ID del usuario a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa.
            
        Raises:
            HTTPException: Si el usuario no se encuentra o hay error.
        """
        try:
            result = self.__user_service.delete(id)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado para eliminar")
            return result
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error eliminando el usuario")