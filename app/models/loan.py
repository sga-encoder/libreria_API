from datetime import datetime
from .user import User
from .book import Book
from app.utils import generate_id

class Loan:
    __id: str
    __user: User
    __book: Book
    __loanDate: datetime
    
    def __init__(self, user: User, book: Book, loanDate: datetime, id: str = None):
        self.__set_id(id)
        self.set_user(user)
        self.set_book(book)
        self.set_loanDate(loanDate)
        
    @classmethod
    def from_dict(cls, data: dict):
        # esto es temporal hasta implementar bien User y Book
        # Manejar loanDate que puede ser str (incluida la 'Z') o datetime
        loan_date_raw = data.get("loanDate")
        if isinstance(loan_date_raw, datetime):
            loan_date = loan_date_raw
        elif isinstance(loan_date_raw, str):
            s = loan_date_raw
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            loan_date = datetime.fromisoformat(s)
        else:
            loan_date = None
            
        return cls(
            user= User.default(),
            book= Book.default(),
            loanDate=loan_date
        )
        # return cls(
        #     user=User.from_dict(data["user"]),
        #     book=Book.from_dict(data["book"]),
        #     loanDate=datetime.fromisoformat(data["loanDate"])
        # )
        
    def get_id(self):
        return self.__id
    def get_user(self):
        return self.__user
    def get_book(self):
        return self.__book
    def get_loanDate(self):
        return self.__loanDate
    
    def __set_id(self, id: str):
        """Asigna un `id`; si es `None`, lo genera automáticamente."""
        if id is None:
            self.__id = generate_id()
        else:
            self.__id = id
        
    def set_user(self, user: User):
        self.__user = user
    def set_book(self, book: Book):
        self.__book = book
    def set_loanDate(self, loanDate: datetime):
        self.__loanDate = loanDate
        
    def to_dict(self):
        return {
            "id": self.__id,
            "user": self.__user.to_dict(),
            "book": self.__book.to_dict(),
            "loanDate": self.__loanDate.isoformat()
        }
        
    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"Loan: {self.__id} - User: {self.__user.get_fullName()} - Book: {self.__book.get_title()} - Date: {self.__loanDate.strftime('%Y-%m-%d')}"
    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"Loan(id={self.__id}, user={self.__user.get_id()}, book={self.__book.get_id_IBSN()}, loanDate={self.__loanDate.isoformat()})"
    
    def __eq__(self, other):
        """Comparación de igualdad entre instancias de Person.

        Regla:
        - Si ambos objetos tienen `id`, se comparan los `id`.
        - Devuelve False si `other` no es una Prestamo.
        """
        if self is other:
            return True
        if not isinstance(other, Loan):
            return False
        # Si ambos tienen id, usarlo como identidad
        if getattr(self, "__id", None) and getattr(other, "__id", None):
            return self.__id == other.__id

    