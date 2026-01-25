from abc import ABC, abstractmethod
from app.domain.models import Person, User
from app.domain.models.enums import PersonRole
from app.domain.algorithms import insertion_sort
from app.domain.exceptions import ValidationException, RepositoryException
import logging

class PersonService(ABC):
    """Servicio base abstracto para gestionar personas (usuarios y admins)."""
    
    def __init__(self, repo, role: PersonRole = PersonRole.USER):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if repo is None:
            raise ValidationException(f"Repositorio no puede ser None")
        
        self._repository = repo
        self._role = role
        self._people = []
        self.__load()
        self.logger.info(f"{self.__class__.__name__} inicializado con rol {role.name}")
    
    def __load(self) -> None:
        """Carga y ordena personas desde el repositorio."""
        try:
            self.logger.debug(f"Iniciando carga de {self._role.name}s...")
            people_orm = self._repository.read_all()
            
            if people_orm is None:
                self.logger.warning(f"No hay {self._role.name}s en la BD")
                self._people = []
            else:
                self._people = [
                    self._repository.orm_to_domain(orm_person) 
                    for orm_person in people_orm
                ]
                self._people = insertion_sort(self._people, key=lambda p: p.get_id())
                self.logger.info(f"{len(self._people)} {self._role.name}s cargados y ordenados")
                
        except Exception as e:
            self.logger.error(f"Error cargando {self._role.name}s: {e}", exc_info=True)
            raise RepositoryException(f"Error crítico al cargar {self._role.name}s: {e}")
    
    def add(self, json: dict) -> User:
        """Crea una nueva persona."""
        try:
            # Crear persona del dominio
            person = Person.from_dict(json, role=self._role, password_is_hashed=False)
            
            # Persistir en BD con tabla específica (users o admins)
            person_orm = self._repository.create(
                id=person.get_id(),
                fullName=person.get_fullName(),
                email=person.get_email(),
                password=person.get_password(),
                role=person.get_role().name,
                is_active=True,
            )
            
            # Convertir a dominio
            person_domain = self._repository.orm_to_domain(person_orm)
            self._people.append(person_domain)
            self._people = insertion_sort(self._people, key=lambda p: p.get_id())
            
            self.logger.info(f"{self._role.name} {person_domain.get_id()} creado: {person_domain.get_email()}")
            return person_domain
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error creando {self._role.name}: {e}", exc_info=True)
            raise RepositoryException(f"Error creando {self._role.name}: {e}")
    
    def get_all(self) -> list[User]:
        """Obtiene todos los {role}s."""
        try:
            people_orm = self._repository.read_all()
            if people_orm is None:
                return []
            return [self._repository.orm_to_domain(orm_p) for orm_p in people_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo {self._role.name}s: {e}")
            raise RepositoryException(f"Error obteniendo {self._role.name}s: {e}")
    
    def get_by_id(self, person_id: str) -> User | None:
        """Obtiene una persona por ID."""
        try:
            person_orm = self._repository.read(person_id)
            if not person_orm:
                return None
            return self._repository.orm_to_domain(person_orm)
        except Exception as e:
            self.logger.error(f"Error obteniendo {self._role.name}: {e}")
            raise RepositoryException(f"Error obteniendo {self._role.name}: {e}")
    
    def get_by_email(self, email: str):
        """Obtiene una persona por email."""
        try:
            orm_person = self._repository.read_by_email(email)
            if not orm_person:
                return None
            return self._repository.orm_to_domain(orm_person)
        except Exception as e:
            self.logger.error(f"Error obteniendo {self._role.name} por email: {e}")
            raise RepositoryException(f"Error obteniendo {self._role.name} por email: {e}")

    def update(self, person_id: str, person_data: dict) -> User | None:
        """Actualiza una persona."""
        try:
            updated_orm = self._repository.update(person_id, **person_data)
            if updated_orm is None:
                return None
            self.__load()
            self.logger.info(f"{self._role.name} {person_id} actualizado")
            return self._repository.orm_to_domain(updated_orm)
        except Exception as e:
            self.logger.error(f"Error actualizando {self._role.name}: {e}")
            raise RepositoryException(f"Error actualizando {self._role.name}: {e}")
    
    def delete(self, user_id: str) -> dict:
        """Elimina un usuario (soft delete - marca como inactivo)."""
        try:
            result = self._repository.soft_delete(user_id)
            if result:
                return {"success": True}
            raise RepositoryException(f"{self._role.name} {user_id} no encontrado")
        except Exception as e:
            raise RepositoryException(f"Error eliminando {self._role.name}: {e}")

    def activate(self, email: str) -> dict:
        """Activa un usuario (is_active=True)."""
        try:
            result = self._repository.activate(email)
            if result:
                return {"success": True}
            raise RepositoryException(f"{self._role.name} {email} no encontrado")
        except Exception as e:
            raise RepositoryException(f"Error activando {self._role.name}: {e}")