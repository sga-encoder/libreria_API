import logging
from app.domain.repositories import UsersRepository 
from app.domain.models import User, Loan
from app.domain.models.enums import PersonRole
from app.domain.algorithms import insertion_sort
from app.domain.exceptions import ValidationException, ResourceNotFoundException, RepositoryException

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
            role (PersonRole): Rol de los usuarios a gestionar (por defecto USER).
            
        Raises:
            ValidationException: Si url no es válido.
            RepositoryException: Si hay error al cargar usuarios.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if not url or not isinstance(url, str):
            self.logger.error(f"URL inválida: {url}")
            raise ValidationException(f"La URL debe ser una cadena no vacía, recibido: {type(url).__name__}")
        
        self.__user_repository = UsersRepository(url, role=role)
        self.__load()
        
        self.logger.info(f"UserService inicializado correctamente con rol {role.name}")
        
    def __load(self) -> None:
        """Carga y ordena los usuarios desde el repositorio.
        
        Lee todos los usuarios del repositorio, los ordena por ID y guarda la lista ordenada.
        
        Raises:
            RepositoryException: Si hay error crítico al cargar usuarios.
        """
        try:
            self.logger.debug("Iniciando carga de usuarios...")
            users = self.__user_repository.read_all()
            
            if users is None:
                self.logger.warning("No hay usuarios en el repositorio, inicializando lista vacía")
                self.__users = []
            else:
                self.logger.debug(f"Ordenando {len(users)} usuarios...")
                self.__users = insertion_sort(
                    users,
                    key=lambda u: u.get_id()
                )
                self.__user_repository.save(self.__users)
                self.logger.info(f"{len(self.__users)} usuarios cargados y ordenados exitosamente")
                
        except RepositoryException:
            raise
        except Exception as e:
            self.logger.error(f"Error crítico cargando usuarios: {e}", exc_info=True)
            raise RepositoryException(f"Error crítico al cargar usuarios: {e}")

    def add(self, json: dict) -> User:
        """Agrega un nuevo usuario al sistema.
        
        Crea el usuario en el repositorio, lo agrega a la caché y reordena la lista.
        
        Args:
            json: Datos del usuario en formato JSON o diccionario.
            
        Returns:
            User: El usuario creado exitosamente.
            
        Raises:
            ValidationException: Si json no es válido o faltan campos obligatorios.
            RepositoryException: Si hay error al crear o guardar el usuario.
        """
        try:
            if not json or not isinstance(json, dict):
                self.logger.error(f"Datos de usuario inválidos: {type(json).__name__}")
                raise ValidationException("Los datos del usuario deben ser un diccionario válido")
            
            # Validar campos obligatorios
            required_fields = ["fullName", "email", "password"]
            missing_fields = [field for field in required_fields if not json.get(field)]
            
            if missing_fields:
                self.logger.error(f"Faltan campos obligatorios: {missing_fields}")
                raise ValidationException(
                    f"Faltan campos obligatorios: {', '.join(missing_fields)}"
                )
            
            self.logger.debug(f"Creando usuario con email: {json.get('email')}")
            
            try:
                user = self.__user_repository.create(json)
            except Exception as e:
                self.logger.error(f"Error al crear usuario en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error creando usuario en repositorio: {e}")
            
            self.__users.append(user)
            self.__users = insertion_sort(
                self.__users,
                key=lambda u: u.get_id()
            )
            
            self.logger.info(f"Usuario {user.get_id()} creado exitosamente: {user.get_email()}")
            return user
            
        except (ValidationException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado agregando usuario: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
    
    def add_loan(self, user_id: str, loan: Loan) -> bool:
        """Agrega un préstamo a un usuario específico.
        
        Args:
            user_id: ID del usuario al que se le agregará el préstamo.
            loan (Loan): Préstamo a agregar.
            
        Returns:
            bool: True si la operación fue exitosa.
            
        Raises:
            ValidationException: Si user_id o loan son inválidos.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            if loan is None:
                self.logger.error("Préstamo no puede ser None")
                raise ValidationException("El préstamo no puede ser None")
            
            self.logger.debug(f"Agregando préstamo a usuario {user_id}")
            
            user = self.get_by_id(user_id)
            if user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            user.add_loan(loan)
            
            try:
                self.__user_repository.update(
                    user.get_id(),
                    {"loans": user.get_loans(), "historial": user.get_historial()}
                )
            except Exception as e:
                self.logger.error(f"Error actualizando usuario en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando usuario: {e}")
            
            self.logger.info(f"Préstamo agregado exitosamente al usuario {user_id}")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado agregando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
        
    def add_to_historial(self, user_id: str, type: str, content: str) -> bool:
        """Agrega un registro al historial de un usuario.
        
        Args:
            user_id: ID del usuario.
            type: Tipo de registro (loan, return, update, cancel).
            content: Contenido del registro.
            
        Returns:
            bool: True si la operación fue exitosa.
            
        Raises:
            ValidationException: Si los parámetros son inválidos.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            if not type or not isinstance(type, str):
                self.logger.error(f"Tipo de historial inválido: {type}")
                raise ValidationException(f"Tipo de historial inválido: {type}")
            
            if not content or not isinstance(content, str):
                self.logger.error(f"Contenido de historial inválido: {content}")
                raise ValidationException(f"Contenido de historial inválido: {content}")
            
            self.logger.debug(f"Agregando registro al historial del usuario {user_id}")
            
            user = self.get_by_id(user_id)
            if user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            user.add_to_historial(type, content)
            
            try:
                self.__user_repository.update(
                    user.get_id(),
                    {"historial": user.get_historial()}
                )
            except Exception as e:
                self.logger.error(f"Error actualizando historial en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando historial: {e}")
            
            self.logger.info(f"Registro agregado al historial del usuario {user_id}")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado agregando al historial: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
        
    def get_by_id(self, user_id: str) -> User:
        """Obtiene un usuario específico por su ID.
        
        Args:
            user_id: ID del usuario a buscar.
            
        Returns:
            User: El usuario encontrado.
            
        Raises:
            ValidationException: Si user_id es inválido.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error de repositorio.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            self.logger.debug(f"Buscando usuario {user_id}")
            
            user = self.__user_repository.read(user_id)
            
            if user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            self.logger.debug(f"Usuario {user_id} encontrado: {user.get_email()}")
            return user
            
        except (ValidationException, ResourceNotFoundException):
            raise
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo usuario: {e}")
        
    def get_all(self) -> list[User]:
        """Obtiene todos los usuarios desde el repositorio.
        
        Returns:
            list[User]: Lista de todos los usuarios.
            
        Raises:
            RepositoryException: Si hay error al obtener usuarios.
        """
        try:
            self.logger.debug("Obteniendo todos los usuarios")
            users = self.__user_repository.read_all()
            
            if users is None:
                self.logger.warning("No hay usuarios en el repositorio, retornando lista vacía")
                return []
            
            self.logger.info(f"Obtenidos {len(users)} usuarios")
            return users
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}", exc_info=True)
            raise RepositoryException(f"Error obteniendo usuarios: {e}")

    def update(self, user_id: str, user_data: dict) -> User:
        """Actualiza los datos de un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar.
            user_data: Nuevos datos del usuario.
            
        Returns:
            User: El usuario actualizado.
            
        Raises:
            ValidationException: Si user_id o user_data son inválidos.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            if not user_data or not isinstance(user_data, dict):
                self.logger.error(f"Datos de usuario inválidos: {type(user_data).__name__}")
                raise ValidationException("Los datos del usuario deben ser un diccionario válido")
            
            self.logger.debug(f"Actualizando usuario {user_id} con datos: {user_data.keys()}")
            
            # Verificar que el usuario existe
            existing_user = self.__user_repository.read(user_id)
            if existing_user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado para actualizar")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            try:
                updated_user = self.__user_repository.update(user_id, user_data)
            except Exception as e:
                self.logger.error(f"Error actualizando usuario en repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando usuario: {e}")
            
            if updated_user is None:
                self.logger.critical(f"Repositorio retornó None al actualizar usuario {user_id}")
                raise RepositoryException("El usuario no pudo ser actualizado")
            
            self.__load()
            self.logger.info(f"Usuario {user_id} actualizado exitosamente")
            return updated_user
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado actualizando usuario: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
        
    def delete(self, user_id: str) -> bool:
        """Elimina un usuario del sistema.
        
        Args:
            user_id: ID del usuario a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa.
            
        Raises:
            ValidationException: Si user_id es inválido.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error al eliminar.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            self.logger.debug(f"Eliminando usuario {user_id}")
            
            # Verificar que el usuario existe
            existing_user = self.__user_repository.read(user_id)
            if existing_user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado para eliminar")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            try:
                result = self.__user_repository.delete(user_id)
            except Exception as e:
                self.logger.error(f"Error eliminando usuario del repositorio: {e}", exc_info=True)
                raise RepositoryException(f"Error eliminando usuario: {e}")
            
            if result:
                self.__load()
                self.logger.info(f"Usuario {user_id} eliminado exitosamente")
            else:
                self.logger.error(f"No se pudo eliminar el usuario {user_id}")
                raise RepositoryException(f"No se pudo eliminar el usuario {user_id}")
            
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado eliminando usuario: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")
        
    def delete_loan(self, user_id: str, loan: Loan) -> bool:
        """Elimina un préstamo de un usuario específico.
        
        Args:
            user_id: ID del usuario del que se eliminará el préstamo.
            loan (Loan): Préstamo a eliminar.
            
        Returns:
            bool: True si la operación fue exitosa.
            
        Raises:
            ValidationException: Si user_id o loan son inválidos.
            ResourceNotFoundException: Si el usuario no existe.
            RepositoryException: Si hay error al actualizar.
        """
        try:
            if not user_id or not isinstance(user_id, str):
                self.logger.error(f"ID de usuario inválido: {user_id}")
                raise ValidationException(f"ID de usuario inválido: {user_id}")
            
            if loan is None:
                self.logger.error("Préstamo no puede ser None")
                raise ValidationException("El préstamo no puede ser None")
            
            self.logger.debug(f"Eliminando préstamo del usuario {user_id}")
            
            user = self.get_by_id(user_id)
            if user is None:
                self.logger.warning(f"Usuario {user_id} no encontrado")
                raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
            user.delete_loan(loan)
            
            try:
                self.update(user.get_id(), {"loans": user.get_loans()})
            except Exception as e:
                self.logger.error(f"Error actualizando usuario tras eliminar préstamo: {e}", exc_info=True)
                raise RepositoryException(f"Error actualizando usuario: {e}")
            
            self.logger.info(f"Préstamo eliminado exitosamente del usuario {user_id}")
            return True
            
        except (ValidationException, ResourceNotFoundException, RepositoryException):
            raise
        except Exception as e:
            self.logger.critical(f"Error inesperado eliminando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error inesperado: {e}")