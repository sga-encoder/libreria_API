from .person import Person
from .enums import PersonRole

class User(Person):
    __loans: list

    def __init__(self, fullName: str, email: str, password: str, loans: list, id: str = "00000000000000000", role: PersonRole = PersonRole.USER):
        # Aceptamos `role` por compatibilidad con llamadas heredadas
        # (p. ej. si se invoca `Person.from_dict` con `cls=User`).
        super().__init__(fullName, email, password, role, id)
        self.__set_loans(loans)
        
    @classmethod
    def from_dict(cls, data: dict):
        # Manejar role si viene en el diccionario (puede ser nombre o PersonRole)
        role_value = data.get("role", "USER")
        if isinstance(role_value, PersonRole):
            role = role_value
        else:
            try:
                role = PersonRole[role_value]
            except Exception:
                role = PersonRole.USER
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            loans=data.get("loans", []),
            id=data.get("id"),
            role=role,
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
            
            