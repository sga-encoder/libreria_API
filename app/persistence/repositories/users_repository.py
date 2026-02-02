from sqlalchemy.orm import Session
from app.domain.models import User
from app.persistence.models import UserORM
from .base_repository import BaseRepository

class UsersRepositorySQL(BaseRepository[UserORM]):
    def __init__(self, db: Session):
        super().__init__(db, UserORM)
        
    def read_all(self) -> list[UserORM] | None:
        """Lee todos los usuarios ACTIVOS."""
        return self.db.query(UserORM).filter(UserORM.is_active == True).all()
        
    def read_by_email(self, email: str) -> UserORM | None:
        """Obtiene un usuario ACTIVO por email."""
        return (
            self.db.query(UserORM)
            .filter(UserORM.email == email, UserORM.is_active == True)
            .first()
        )
    
    def read_active(self) -> list[UserORM]:
        return self.db.query(UserORM).filter(UserORM.is_active == True).all()
    
    def soft_delete(self, user_id: str) -> bool:
        """Desactiva un usuario (soft delete)."""
        user = self.read(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
    
    def activate(self, email: str) -> bool:
        """Activa un usuario (revierte el soft delete)."""
        user = self.db.query(UserORM).filter(UserORM.email == email).first()
        if user:
            user.is_active = True
            self.db.commit()
            return True
        return False
    
    def orm_to_domain(self, orm_user: UserORM) -> User:
        """Convierte un UserORM a un User del dominio."""
        if not orm_user:
            return None
        
        from app.domain.models.enums import PersonRole
        
        # Convertir string de BD a enum PersonRole
        role_enum = PersonRole[orm_user.role] if isinstance(orm_user.role, str) else orm_user.role
        
        return User(
            fullName=orm_user.fullName,
            email=orm_user.email,
            password=orm_user.password,
            loans=orm_user.loans or [],
            id=orm_user.id,
            role=role_enum,
            password_is_hashed=True,
            historial=orm_user.historial or []
        )
        
    def domain_to_orm(self, user: User) -> UserORM:
        """Convierte un User del dominio a un UserORM."""
        if not user:
            return None
        
        return UserORM(
            id=user.get_id(),
            fullName=user.get_fullName(),
            email=user.get_email(),
            password=user.get_password(),
            loans=user.get_loans(),
            historial=user.get_historial(),
            role=user.get_role().name,
            is_active=True
        )
        
    def __str__(self):
        return f"UsersRepositorySQL(total_users={len(self.read_all())})"
    
    def __repr__(self):
        return f"UsersRepositorySQL(total_users={len(self.read_all())})"