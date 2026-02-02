"""Servicio SQL para gestión de préstamos de libros."""
from __future__ import annotations  # ✅ Agregar
from typing import TYPE_CHECKING  # ✅ Agregar
import logging

from app.persistence.repositories import LoansRepositorySQL
from app.domain.models import Loan
from app.domain.exceptions import ValidationException, RepositoryException, ResourceNotFoundException

# ✅ Importar solo para type hints (no en runtime)
if TYPE_CHECKING:
    from app.domain.services.person.user_service import UserService
    from app.domain.services.book_service import BookService


class LoanService:
    """Servicio para gestionar préstamos con lógica de negocio."""
    
    def __init__(self, repo: LoansRepositorySQL, 
                 user_service: UserService,
                 book_service: BookService): 
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if repo is None:
            raise ValidationException("Repositorio no puede ser None")
        
        self._repository = repo
        self.user_service = user_service
        self.book_service = book_service
        self.logger.info("LoanService inicializado")
    
    def create(self, json: dict) -> Loan:
        """Crea un nuevo préstamo y actualiza usuario + inventario."""
        try:
            # ✅ Crear préstamo con validación
            loan = Loan.from_dict(json, skip_validation=False,
                                  user_service=self.user_service,
                                  book_service=self.book_service)
            
            # ✅ Persistir préstamo
            loan_orm = self._repository.create(
                id=loan.get_id(),
                id_user=loan.get_user_id(),
                id_ISBN_book=loan.get_book_isbn(),
                loan_date=loan.get_loan_date(),
                status=loan.get_status()
            )
            
            loan_domain = self._repository.orm_to_domain(loan_orm,
                                                         user_service=self.user_service,
                                                         book_service=self.book_service)
            
            # ✅ AGREGAR: Actualizar usuario con el préstamo
            user = self.user_service.get_by_id(loan.get_user_id())
            if user:
                user.add_loan(loan_domain)
                self.user_service.update(user.get_id(), {
                    "loans": user.get_loans(),
                    "historial": user.get_historial()
                })
                self.logger.info(f"Usuario {user.get_id()} actualizado con préstamo {loan_domain.get_id()}")
            
            # ✅ AGREGAR: Marcar libro como prestado
            self.book_service.mark_borrowed(loan.get_book_isbn())
            self.logger.info(f"Libro {loan.get_book_isbn()} marcado como prestado")
            
            self.logger.info(f"Préstamo {loan_domain.get_id()} creado exitosamente")
            return loan_domain
            
        except ValidationException:
            raise
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Error creando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error creando préstamo: {e}")
    
    def get_all(self) -> list[Loan]:
        """Obtiene todos los préstamos."""
        try:
            loans_orm = self._repository.read_all()
            if loans_orm is None:
                return []
            return [self._repository.orm_to_domain(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos: {e}")
            raise RepositoryException(f"Error obteniendo préstamos: {e}")
    
    def get_by_id(self, loan_id: str) -> Loan | None:
        """Obtiene un préstamo por ID."""
        try:
            loan_orm = self._repository.read(loan_id)
            if not loan_orm:
                return None
            return self._repository.orm_to_domain(loan_orm)
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamo: {e}")
            raise RepositoryException(f"Error obteniendo préstamo: {e}")
    
    def get_by_id_with_details(self, loan_id: str) -> dict | None:
        """Obtiene un préstamo con usuario y libro completos."""
        try:
            loan_orm = self._repository.read_with_relations(loan_id)
            if not loan_orm:
                return None
            return self._repository.orm_to_dict_with_relations(loan_orm)
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamo con detalles: {e}")
            raise RepositoryException(f"Error obteniendo préstamo: {e}")
    
    def get_all_with_details(self) -> list[dict]:
        """Obtiene todos los préstamos con usuario y libro completos."""
        try:
            loans_orm = self._repository.read_all_with_relations()
            if not loans_orm:
                return []
            return [self._repository.orm_to_dict_with_relations(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos con detalles: {e}")
            raise RepositoryException(f"Error obteniendo préstamos: {e}")
    
    def get_by_user(self, id_user: str) -> list[Loan]:
        """Obtiene todos los préstamos de un usuario."""
        try:
            loans_orm = self._repository.read_by_user(id_user)
            if not loans_orm:
                return []
            return [self._repository.orm_to_domain(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos del usuario: {e}")
            raise RepositoryException(f"Error obteniendo préstamos: {e}")
    
    def get_by_book(self, id_ISBN: str) -> list[Loan]:
        """Obtiene todos los préstamos de un libro."""
        try:
            loans_orm = self._repository.read_by_book(id_ISBN)
            if not loans_orm:
                return []
            return [self._repository.orm_to_domain(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos del libro: {e}")
            raise RepositoryException(f"Error obteniendo préstamos: {e}")
    
    def get_active(self) -> list[Loan]:
        """Obtiene todos los préstamos activos."""
        try:
            loans_orm = self._repository.read_active()
            if not loans_orm:
                return []
            return [self._repository.orm_to_domain(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos activos: {e}")
            raise RepositoryException(f"Error obteniendo préstamos activos: {e}")
    
    def get_active_by_book(self, id_ISBN: str) -> Loan | None:
        """Obtiene el préstamo activo de un libro."""
        try:
            loan_orm = self._repository.read_active_by_book(id_ISBN)
            if not loan_orm:
                return None
            return self._repository.orm_to_domain(loan_orm)
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamo activo del libro: {e}")
            raise RepositoryException(f"Error obteniendo préstamo: {e}")
    
    def get_active_by_user(self, id_user: str) -> list[Loan]:
        """Obtiene los préstamos activos de un usuario."""
        try:
            loans_orm = self._repository.read_active_by_user(id_user)
            if not loans_orm:
                return []
            return [self._repository.orm_to_domain(orm_l) for orm_l in loans_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo préstamos activos del usuario: {e}")
            raise RepositoryException(f"Error obteniendo préstamos: {e}")
    
    def update(self, loan_id: str, loan_data: dict) -> Loan | None:
        """Actualiza un préstamo."""
        try:
            updated_orm = self._repository.update(loan_id, **loan_data)
            if updated_orm is None:
                return None
            self.logger.info(f"Préstamo {loan_id} actualizado")
            return self._repository.orm_to_domain(updated_orm)
        except Exception as e:
            self.logger.error(f"Error actualizando préstamo: {e}")
            raise RepositoryException(f"Error actualizando préstamo: {e}")
    
    def delete(self, loan_id: str) -> dict:
        """Desactiva (soft delete) un préstamo y revierte cambios en usuario e inventario."""
        try:
            # Obtener préstamo antes de desactivarlo
            loan = self.get_by_id(loan_id)
            if not loan:
                raise ResourceNotFoundException(f"Préstamo {loan_id} no encontrado")

            # ✅ Quitar de préstamos activos del usuario (sin agregar historial de retorno)
            user = self.user_service.get_by_id(loan.get_user_id())
            if user:
                user.delete_loan(loan_id)
                self.user_service.update(user.get_id(), {
                    "loans": user.get_loans(),
                    "historial": user.get_historial()
                })

            # ✅ Marcar libro como disponible
            self.book_service.mark_available(loan.get_book_isbn())

            # ✅ Soft delete (desactivar préstamo, NO eliminar)
            result = self._repository.deactivate(loan_id)
            if not result:
                raise RepositoryException(f"Préstamo {loan_id} no encontrado")

            self.logger.info(f"Préstamo {loan_id} desactivado exitosamente")
            return {"success": True, "message": f"Préstamo {loan_id} desactivado"}

        except Exception as e:
            self.logger.error(f"Error desactivando préstamo: {e}", exc_info=True)
            raise RepositoryException(f"Error desactivando préstamo: {e}")
