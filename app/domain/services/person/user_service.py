import logging
from app.persistence.repositories import UsersRepositorySQL
from app.domain.models import User, Loan, Person
from app.domain.models.enums import PersonRole
from app.domain.exceptions import ValidationException, ResourceNotFoundException, RepositoryException
from app.domain.algorithms import insertion_sort
from .person_service import PersonService

class UserService(PersonService):
    """Servicio para gestionar usuarios (tabla: users) con lógica extra."""
    def __init__(self, repo):
        super().__init__(repo, role=PersonRole.USER)
        
    def add(self, json: dict) -> User:
        """Crea usuario incluyendo loans/historial."""
        print("UserService.add called with json:", json)
        person = Person.from_dict(json, role=self._role, password_is_hashed=False)
        loans = json.get("loans") or []
        historial = json.get("historial") or []
        try:
            user_orm = self._repository.create(
                id=person.get_id(),
                fullName=person.get_fullName(),
                email=person.get_email(),
                password=person.get_password(),
                role=person.get_role().name,
                loans=loans,
                historial=historial,
                is_active=True,
            )
            user_domain = self._repository.orm_to_domain(user_orm)
            self._people.append(user_domain)
            self._people = insertion_sort(self._people, key=lambda p: p.get_id())
            return user_domain
        except Exception as e:
            raise RepositoryException(f"Error creando usuario: {e}")


    def add_loan(self, user_id: str, loan) -> bool:
        if not user_id or not isinstance(user_id, str):
            raise ValidationException(f"ID de usuario inválido: {user_id}")
        if loan is None:
            raise ValidationException("El préstamo no puede ser None")

        user = self.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")

        user.add_loan(loan)
        try:
            self._repository.update(user.get_id(), loans=user.get_loans(), historial=user.get_historial())
        except Exception as e:
            raise RepositoryException(f"Error actualizando usuario: {e}")
        return True

    def add_to_historial(self, user_id: str, type: str, content: str) -> bool:
        if not user_id or not isinstance(user_id, str):
            raise ValidationException(f"ID de usuario inválido: {user_id}")
        user = self.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
        user.add_to_historial(type, content)
        try:
            self._repository.update(user.get_id(), historial=user.get_historial())
        except Exception as e:
            raise RepositoryException(f"Error actualizando historial: {e}")
        return True

    def delete_loan(self, user_id: str, loan) -> bool:
        if not user_id or not isinstance(user_id, str):
            raise ValidationException(f"ID de usuario inválido: {user_id}")
        if loan is None:
            raise ValidationException("El préstamo no puede ser None")

        user = self.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
        user.delete_loan(loan)
        try:
            self._repository.update(user.get_id(), loans=user.get_loans())
        except Exception as e:
            raise RepositoryException(f"Error actualizando usuario: {e}")
        return True