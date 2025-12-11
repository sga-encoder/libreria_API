from app.domain.repositories import UsersRepository 
from app.domain.models import User
from app.domain.models.enums import PersonRole
from app.domain.algorithms import insertion_sort

class UserService:
    """Servicio para gestionar operaciones relacionadas con usuarios.
    
    Esta clase proporciona métodos para crear, leer, actualizar y eliminar usuarios,
    utilizando un repositorio para persistencia y manteniendo una caché interna ordenada.
    
    Attributes:
        __users (list[User]): Lista ordenada de usuarios en caché.
        user_repository (UsersRepository): Repositorio para operaciones de datos.
    """
    __users: list[User]
    
    def __init__(self, url: str, role: PersonRole = PersonRole.USER) -> None:
        """Inicializa el servicio de usuarios.
        
        Args:
            url (str): Ruta o URL del archivo donde se almacenan los usuarios.
        """
        self.__user_repository = UsersRepository(url, role=role)
        self.__load()
        
    def __load(self) -> None:
        """Carga y ordena los usuarios desde el repositorio.
        
        Lee todos los usuarios del repositorio, los ordena por ID y guarda la lista ordenada.
        En caso de error, inicializa la lista como vacía.
        """
        try:
            users = self.__user_repository.read_all()
            if users is None:
                self.__users = []
            else:
                self.__users = insertion_sort(
                    users,
                    key=lambda u: u.get_id()
                )
                self.__user_repository.save(self.__users)
        except Exception as e:
            print(f"Error loading users: {e}")
            self.__users = []



    def add(self, json):
        """Agrega un nuevo usuario al sistema.
        
        Crea el usuario en el repositorio, lo agrega a la caché y reordena la lista.
        
        Args:
            json: Datos del usuario en formato JSON o diccionario.
            
        Returns:
            User or None: El usuario creado si la operación fue exitosa, None en caso de error.
        """
        try:
            user = self.__user_repository.create(json)
            
            self.__users.append(user)
            self.__users = insertion_sort(
                self.__users,
                key=lambda u: u.get_id()
            )
            return user
        except Exception as e:
            print(f"Error adding user: {e}")
            import traceback
            traceback.print_exc()
            return None
            return None
        
    def get_user_by_id(self, user_id):
        """Obtiene un usuario específico por su ID.
        
        Args:
            user_id: ID del usuario a buscar.
            
        Returns:
            User or None: El usuario encontrado, o None si no existe o hay error.
        """
        try:
            user = self.__user_repository.read(user_id)
            return user
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        
    def get_users_all(self):
        """Obtiene todos los usuarios desde el repositorio.
        
        Returns:
            list[User] or None: Lista de todos los usuarios, o None en caso de error.
        """
        try:
            users = self.__user_repository.read_all()
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return None

    def update_user(self, user_id, user_data):
        """Actualiza los datos de un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar.
            user_data: Nuevos datos del usuario.
            
        Returns:
            User or None: El usuario actualizado, o None en caso de error.
        """
        try:
            book = self.__user_repository.update(user_id, user_data)
            self.__load()
            return book
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
        

    def delete_user(self, user_id):
        """Elimina un usuario del sistema.
        
        Args:
            user_id: ID del usuario a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        try:
            result = self.__user_repository.delete(user_id)
            if result:
                self.__load()
            return result
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False