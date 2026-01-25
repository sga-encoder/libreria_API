from .person_service import PersonService
from app.domain.models.enums import PersonRole

class AdminService(PersonService):
    """Servicio para gestionar administradores (tabla: admins)."""
    
    def __init__(self, repo):
        super().__init__(repo, role=PersonRole.ADMIN)