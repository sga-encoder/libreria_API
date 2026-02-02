from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime
from app.domain.models import Loan
from app.persistence.models import LoanORM
from .base_repository import BaseRepository


class LoansRepositorySQL(BaseRepository[LoanORM]):
    """Repositorio SQL para gestionar préstamos."""
    
    def __init__(self, db: Session):
        super().__init__(db, LoanORM)
    
    def read_all(self) -> List[LoanORM]:
        """Lee todos los préstamos."""
        return self.db.query(LoanORM).all()
    
    def read(self, loan_id: str) -> Optional[LoanORM]:
        """Obtiene un préstamo por ID (sobrescribe BaseRepository)."""
        return self.db.query(LoanORM).filter(LoanORM.id == loan_id).first()
    
    def read_with_relations(self, loan_id: str) -> Optional[LoanORM]:
        """Obtiene un préstamo por ID con usuario y libro cargados."""
        return self.db.query(LoanORM)\
            .options(joinedload(LoanORM.user), joinedload(LoanORM.book))\
            .filter(LoanORM.id == loan_id)\
            .first()
    
    def read_all_with_relations(self) -> List[LoanORM]:
        """Lee todos los préstamos con usuario y libro cargados."""
        return self.db.query(LoanORM)\
            .options(joinedload(LoanORM.user), joinedload(LoanORM.book))\
            .all()
    
    def read_by_user(self, id_user: str) -> List[LoanORM]:
        """Obtiene todos los préstamos de un usuario."""
        return self.db.query(LoanORM).filter(LoanORM.id_user == id_user).all()
    
    def read_by_book(self, id_ISBN: str) -> List[LoanORM]:
        """Obtiene todos los préstamos de un libro."""
        return self.db.query(LoanORM).filter(LoanORM.id_ISBN_book == id_ISBN).all()
    
    def read_active(self) -> List[LoanORM]:
        """Obtiene solo los préstamos activos (status=True)."""
        return self.db.query(LoanORM).filter(LoanORM.status == True).all()
    
    def read_active_by_book(self, id_ISBN: str) -> Optional[LoanORM]:
        """Obtiene el préstamo activo de un libro (si existe)."""
        return self.db.query(LoanORM).filter(
            LoanORM.id_ISBN_book == id_ISBN,
            LoanORM.status == True
        ).first()
    
    def read_active_by_user(self, id_user: str) -> List[LoanORM]:
        """Obtiene los préstamos activos de un usuario."""
        return self.db.query(LoanORM).filter(
            LoanORM.id_user == id_user,
            LoanORM.status == True
        ).all()
    
    def update(self, loan_id: str, **kwargs) -> Optional[LoanORM]:
        """Actualiza un préstamo por ID (sobrescribe BaseRepository)."""
        loan = self.read(loan_id)
        if loan:
            for key, value in kwargs.items():
                if hasattr(loan, key):
                    setattr(loan, key, value)
            self.db.commit()
            self.db.refresh(loan)
        return loan
    
    def delete(self, loan_id: str) -> bool:
        """Elimina un préstamo por ID (sobrescribe BaseRepository)."""
        loan = self.read(loan_id)
        if loan:
            self.db.delete(loan)
            self.db.commit()
            return True
        return False
    
    def deactivate(self, loan_id: str) -> bool:
        """Marca un préstamo como inactivo sin eliminarlo (soft delete)."""
        loan = self.read(loan_id)
        if loan:
            loan.status = False
            loan.return_date = datetime.now()
            self.db.commit()
            self.db.refresh(loan)
            return True
        return False
    
    def orm_to_domain(self, orm_loan: LoanORM, user_service=None, book_service=None) -> Loan:
        """Convierte un LoanORM a un Loan del dominio."""
        if not orm_loan:
            return None
        
        return Loan(
            id_user=orm_loan.id_user,
            id_book=orm_loan.id_ISBN_book,
            loan_date=orm_loan.loan_date,
            id=orm_loan.id,
            status=orm_loan.status,
            searching=True,  # ✅ Solo cargar IDs, no validar
            user_service=user_service,
            book_service=book_service
        )
    
    def domain_to_orm(self, loan: Loan) -> LoanORM:
        """Convierte un Loan del dominio a un LoanORM."""
        if not loan:
            return None
        
        return LoanORM(
            id=loan.get_id(),
            id_user=loan.get_user().get_id() if hasattr(loan.get_user(), 'get_id') else loan.get_user(),
            id_ISBN_book=loan.get_book().get_id_IBSN() if hasattr(loan.get_book(), 'get_id_IBSN') else loan.get_book(),
            loan_date=loan.get_loan_date(),
            status=loan.get_status()
        )
    
    def orm_to_dict_with_relations(self, orm_loan: LoanORM) -> dict:
        """Convierte un LoanORM con relaciones a diccionario completo."""
        if not orm_loan:
            return None
        
        return {
            "id": orm_loan.id,
            "id_user": orm_loan.id_user,
            "id_ISBN_book": orm_loan.id_ISBN_book,
            "loan_date": orm_loan.loan_date.isoformat() if orm_loan.loan_date else None,
            "return_date": orm_loan.return_date.isoformat() if orm_loan.return_date else None,
            "status": orm_loan.status,
            "user": {
                "id": orm_loan.user.id,
                "fullName": orm_loan.user.fullName,
                "email": orm_loan.user.email,
                "is_active": orm_loan.user.is_active
            } if orm_loan.user else None,
            "book": {
                "id_IBSN": orm_loan.book.id_IBSN,
                "title": orm_loan.book.title,
                "author": orm_loan.book.author,
                "gender": orm_loan.book.gender,
                "price": orm_loan.book.price,
                "is_borrowed": orm_loan.book.is_borrowed
            } if orm_loan.book else None
        }
        
    def __str__(self):
        return f"LoansRepositorySQL(total_loans={len(self.read_all())})"
    
    def __repr__(self):
        return f"LoansRepositorySQL(total_loans={len(self.read_all())})"
