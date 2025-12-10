from .person import Person
from .enums import PersonRole

class User(Person):
    __loans: list

    def __init__(self, fullName: str, email: str, password: str, loans: list, id: str = "00000000000000000", role: PersonRole = PersonRole.USER, password_is_hashed: bool = False):
        # Aceptamos `role` por compatibilidad con llamadas heredadas
        # (p. ej. si se invoca `Person.from_dict` con `cls=User`).
        super().__init__(fullName, email, password, role, id, password_is_hashed=password_is_hashed)
        self.__set_loans(loans)
        
    @classmethod
    def from_dict(cls, data: dict, password_is_hashed: bool = True):
        # Manejar role si viene en el diccionario (puede ser nombre o PersonRole)
        
        # Crear instancia usando el constructor de Person directamente
        # para aprovechar el parámetro password_is_hashed
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            loans=data.get("loans", []),
            id=data.get("id"),
            role=PersonRole.USER,
            password_is_hashed=password_is_hashed  # ← La contraseña del JSON ya está hasheada
        )

        
    @classmethod
    def from_search_api(cls, id: str):
        return cls(
            fullName="Peppermint Butler",
            email="peppermintButler.aventure@time.cartoon",
            password="adventuretime",
            loans=[],
            id=id
        )
        
    @classmethod
    def default(cls):
        return cls(
            fullName="Finn",
            email="finn.adventure@time.cartoon",
            password="adventuretime",
            loans=[]
        )
        
    def get_loans(self):
        return self.__loans
    
    def __set_loans(self, loans: list):
        self.__loans = loans
        
    def add_loan(self, loan):
        self.__loans.append(loan)
        
    def remove_loan(self, loan):
        self.__loans.remove(loan)
        
    def to_dict(self):
        data = {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "loans": self.__loans,
            "role": self._role.name,
        }
        return data

    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"User: {self._fullName} ({self._email}) - Loans: {len(self.__loans)}"

    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"User(id={self._id}, fullName={self._fullName}, loans={len(self.__loans)})"
            
            