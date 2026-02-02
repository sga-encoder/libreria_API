from sqlalchemy.orm import Session
from app.persistence.models import AdminORM
from .base_repository import BaseRepository
from app.domain.models import Admin
from app.domain.models.enums import PersonRole

class AdminsRepositorySQL(BaseRepository[AdminORM]):
    def __init__(self, db: Session):
        super().__init__(db, AdminORM)

    def read_by_email(self, email: str) -> AdminORM | None:
        return self.db.query(AdminORM).filter(AdminORM.email == email).first()

    def read_active(self) -> list[AdminORM]:
        return self.db.query(AdminORM).filter(AdminORM.is_active == True).all()

    def deactivate_admin(self, admin_id: str) -> bool:
        admin = self.read(admin_id)
        if admin:
            admin.is_active = False
            self.db.commit()
            return True
        return False
    
    def orm_to_domain(self, orm_admin: AdminORM) -> Admin:
        """Convierte AdminORM → User del dominio (sin loans/historial)."""
        return Admin(
            fullName=orm_admin.fullName,
            email=orm_admin.email,
            password=orm_admin.password,
            id=orm_admin.id,
            password_is_hashed=True,
        )
    
    
    def domain_to_orm(self, admin: Admin) -> AdminORM:
        """Convierte User del dominio → AdminORM."""
        return AdminORM(
            id=admin.get_id(),
            fullName=admin.get_fullName(),
            email=admin.get_email(),
            password=admin.get_password(),
            is_active=True
        )
        
    def __str__(self):
        return f"AdminsRepositorySQL(total_admins={len(self.read_all())})"
    
    def __repr__(self):
        return f"AdminsRepositorySQL(total_admins={len(self.read_all())})"