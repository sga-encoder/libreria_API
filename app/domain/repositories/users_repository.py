from app.utils import FileManager, FileType
from app.domain.models import User, Person
from app.domain.models.enums import PersonRole
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
    
    def __init__(self, url: str, role: PersonRole = PersonRole.USER ) -> None:
        """Inicializa el repositorio.

        Args:
            url (str): Ruta o URL del archivo donde se almacenan los usuarios.
        """
        self.__file = FileManager(url, FileType.JSON)
        self.__users = self.__file.read()
        self.__role = role
        
    def __refresh_users(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__users = self.__file.read()
        
    def __search_id(self, id: str) -> int:
        """Busca el índice de un usuario por su ID utilizando búsqueda binaria optimizada.
        
        Args:
            id (str): ID del usuario a buscar.
            
        Returns:
            int: Índice del usuario en la lista original, o -1 si no se encuentra.
        """
        self.__refresh_users()
        
        # Crear diccionario para mapeo rápido: id -> índice en self.__users
        id_to_index = {}
        for i, user_dict in enumerate(self.__users):
            user_id = user_dict.get('id')
            if user_id:
                id_to_index[user_id] = i
        
        # Búsqueda O(1) en diccionario
        if id in id_to_index:
            return id_to_index[id]
        
        return -1

    def create(self, json: dict):
        """Crea un nuevo usuario y lo agrega al repositorio.
        
        Args:
            json (dict): Datos del usuario en formato diccionario.
            
        Returns:
            User: Instancia del usuario creado.
        """
        instance = None
        
        if self.__role == PersonRole.ADMIN:
            instance = Person.from_dict(json, PersonRole.ADMIN, password_is_hashed=False)
        elif self.__role == PersonRole.USER:
            instance = User.from_dict(json, password_is_hashed=False)
            
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
            print("Usuario no encontrado. 1")
            return None
        instance = None
        if self.__role == PersonRole.ADMIN:
            instance = Person.from_dict(self.__users[user], role=PersonRole.ADMIN)
        elif self.__role == PersonRole.USER:
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
            user = None
            if self.__role == PersonRole.ADMIN:
                user = Person.from_dict(data, role=PersonRole.ADMIN)
            elif self.__role == PersonRole.USER:
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
            print("Usuario no encontrado. 2")
            return None
        
        instance = None
        if self.__role == PersonRole.ADMIN:
            instance = Person.from_dict(self.__users[index], role=PersonRole.ADMIN)
        elif self.__role == PersonRole.USER:
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
            print("Usuario no encontrado. 3")
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

    def add_loan(self, id_user: str, loan) -> bool:
        """Agrega un préstamo a un usuario.
        
        Actualiza tanto la instancia del usuario como el archivo.
        
        Args:
            id_user (str): ID del usuario al que se le agregará el préstamo.
            loan: Objeto del préstamo a agregar.
            
        Returns:
            bool: True si el préstamo fue agregado exitosamente, False en caso contrario.
        """
        index = self.__search_id(id_user)
        if index == -1:
            print("Usuario no encontrado. 4")
            return False
        
        # Obtener la instancia del usuario
        user = self.read(id_user)
        if user is None:
            return False
        
        # Agregar el préstamo a la instancia
        user.add_loan(loan)
        
        # Actualizar en la caché interna
        self.__users[index] = user.to_dict()
        
        # Guardar en el archivo
        self.__file.write(self.__users)
        
        return True

    def delete_loan(self, id_user: str, id_loan: str) -> bool:
        """Elimina un préstamo de un usuario.
        
        Actualiza tanto la instancia del usuario como el archivo.
        
        Args:
            id_user (str): ID del usuario del cual se eliminará el préstamo.
            id_loan (str): ID del préstamo a eliminar.
            
        Returns:
            bool: True si el préstamo fue eliminado exitosamente, False en caso contrario.
        """
        index = self.__search_id(id_user)
        if index == -1:
            print("Usuario no encontrado. 5")
            return False
        
        # Obtener la instancia del usuario
        user = self.read(id_user)
        if user is None:
            return False
        
        # Obtener los préstamos del usuario
        loans = user.get_loans()
        
        # Buscar y eliminar el préstamo por su ID
        loan_to_remove = None
        for loan in loans:
            if hasattr(loan, 'get_id') and loan.get_id() == id_loan:
                loan_to_remove = loan
                break
            elif isinstance(loan, dict) and loan.get('id') == id_loan:
                loan_to_remove = loan
                break
        
        if loan_to_remove is None:
            print(f"Préstamo con ID {id_loan} no encontrado para el usuario.")
            return False
        
        # Eliminar el préstamo de la instancia
        user.delete_loan(loan_to_remove)
        
        # Actualizar en la caché interna
        self.__users[index] = user.to_dict()
        
        # Guardar en el archivo
        self.__file.write(self.__users)
        
        return True