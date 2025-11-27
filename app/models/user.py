from .person import Person
from .enums import PersonRole

class User(Person):
    __loans: list
    
    def __init__(self, fullName: str, email: str, password: str, loans: list):
        super().__init__(fullName, email, password, PersonRole.USER)
        self.__set_loans(loans)
        
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            fullName=data["fullName"],
            email=data["email"],
            password=data["password"],
            loans=data.get("loans", [])
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
        data = super().to_dict()
        data.update({
            "loans": self.__loans
        })
        return data

    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"User: {self._fullName} ({self._email}) - Loans: {len(self.__loans)}"

    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"User(id={self._id}, fullName={self._fullName}, loans={len(self.__loans)})"
            
            