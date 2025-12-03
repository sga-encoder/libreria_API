from app.utils import FileManager, FileType
from app.domain.models import User
from .interface import RepositoriesInterface
from app.domain.algorithms import binary_search


class UsersRepository(RepositoriesInterface[User]):
    """Repositorio para gestionar usuarios en el sistema de biblioteca.
    
    Esta clase maneja las operaciones CRUD para usuarios, utilizando un archivo
    para persistencia de datos. Implementa la interfaz RepositoriesInterface.
    
    Attributes:
        __file (FileManager): Gestor de archivos para operaciones de I/O.
        __users (list[User]): Caché interna de usuarios cargados.
    """
    
    def __init__(self, url: str) -> None:
        """Inicializa el repositorio.

        Args:
            url (str): Ruta o URL del archivo donde se almacenan los usuarios.
        """
        self.__file = FileManager(url, FileType.JSON)
        self.__users = self.__file.read()
        
    def __refresh_users(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__users = self.__file.read()
        
    def __search_id(self, id: str) -> int:
        """Busca el índice de un usuario por su ID utilizando búsqueda binaria.
        
        Args:
            id (str): ID del usuario a buscar.
            
        Returns:
            int: Índice del usuario en la lista, o -1 si no se encuentra.
        """
        
        self.__refresh_users()
        index = binary_search(
            self.read_all(),
            key=lambda user:user.get_id(),
            item=User.from_search_api(id=id)
        )
        return  index

    def create(self, json: dict):
        """Crea un nuevo usuario y lo agrega al repositorio.
        
        Args:
            json (dict): Datos del usuario en formato diccionario.
            
        Returns:
            User: Instancia del usuario creado.
        """
        instance = User.from_dict(json)
        self.__file.append(instance.to_dict())
        self.__refresh_users()
        return instance
    

    def read(self, id: str):
        """Lee un usuario por su ID.
        
        Args:
            id (str): ID del usuario a leer.
            
        Returns:
            User or None: Instancia del usuario si se encuentra, None en caso contrario.
        """

        user = self.__search_id(id)
        if user == -1:
            print("Usuario no encontrado.")
            return None
        instance = User.from_dict(self.__users[user])
        return instance

    def read_all(self) -> list[User] | None:
        """Lee todos los usuarios del repositorio.
        
        Returns:
            list[User] or None: Lista de usuarios si existen, None si no hay usuarios.
        """
        self.__refresh_users()
        if not self.__users:
            print("No hay usuarios registrados.")
            return None
        users = []
        for data in self.__users:
            user = User.from_dict(data)
            users.append(user)
            
        return users

    def update(self, id: str, json: dict):
        """Actualiza un usuario existente por su ID.
        
        Args:
            id (str): ID del usuario a actualizar.
            json (dict): Nuevos datos del usuario en formato diccionario.
            
        Returns:
            User or None: Instancia del usuario actualizado si se encuentra, None en caso contrario.
        """
        index = self.__search_id(id)
        if index == -1:
            print("Usuario no encontrado.")
            return None
        instance = User.from_dict(self.__users[index])
        instance.update_from_dict(json)
        self.__users[index] = instance.to_dict()
        
        self.__file.write(self.__users)
        return instance

    def delete(self, id: str) -> bool:
        """Elimina un usuario por su ID.
        
        Args:
            id (str): ID del usuario a eliminar.
            
        Returns:
            bool: True si el usuario fue eliminado, False si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print("Usuario no encontrado.")
            return False
        self.__users.pop(index)
        self.__file.write(self.__users)
        return True
    
    def save(self, arr: list[User]) -> None:
        """Guarda una lista de usuarios en el archivo.
        
        Args:
            arr (list[User]): Lista de usuarios a guardar.
        """
        # Aceptar tanto lista de `User` como lista de `dict` (serializados).
        if arr is None:
            self.__file.write([])
            return

        # Si los elementos tienen `to_dict`, convertirlos.
        if all(hasattr(item, "to_dict") for item in arr):
            serial = [item.to_dict() for item in arr]
        elif all(isinstance(item, dict) for item in arr):
            serial = arr
        else:
            # Intentar convertir elemento a elemento, o fallar con mensaje claro.
            serial = []
            for item in arr:
                if hasattr(item, "to_dict"):
                    serial.append(item.to_dict())
                elif isinstance(item, dict):
                    serial.append(item)
                else:
                    raise ValueError("UsersRepository.save expects a list of User or a list of dicts")

        self.__file.write(serial)