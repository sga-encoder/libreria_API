from . import Person
from ..enums import PersonRole

class Admin(Person):
    """Modelo de dominio para administradores (sin loans ni historial)."""
    
    def __init__(
        self,
        fullName: str,
        email: str,
        password: str,
        id: str = None,
        password_is_hashed: bool = False
    ):
        super().__init__(
            fullName=fullName,
            email=email,
            password=password,
            id=id,
            role=PersonRole.ADMIN,
            password_is_hashed=password_is_hashed
        )
    
    def to_dict(self) -> dict:
        """Serializa admin SIN loans ni historial."""
        return {
            "id": self.get_id(),
            "fullName": self.get_fullName(),
            "email": self.get_email(),
            "password": self.get_password(),
            "role": self.get_role().name
        }