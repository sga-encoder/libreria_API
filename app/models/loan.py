from datetime import datetime
from .user import User
from .book import Book
from app.utils import generate_id

class Loan:
    _id: str
    _user: User
    _book: Book
    _loanDate: datetime
    
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
        return self._id
    def get_user(self):
        return self._user
    def get_book(self):
        return self._book
    def get_loanDate(self):
        return self._loanDate
    
    def __set_id(self, id: str):
        """Asigna un `id`; si es `None`, lo genera automáticamente."""
        if id is None:
            self._id = generate_id()
        else:
            self._id = id
        
    def set_user(self, user: User):
        self._user = user
    def set_book(self, book: Book):
        self._book = book
    def set_loanDate(self, loanDate: datetime):
        self._loanDate = loanDate
        
    def to_dict(self):
        return {
            "id": self._id,
            "user": self._user.to_dict(),
            "book": self._book.to_dict(),
            "loanDate": self._loanDate.isoformat()
        }
        
    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"Loan: {self._id} - User: {self._user.get_fullName()} - Book: {self._book.get_title()} - Date: {self._loanDate.strftime('%Y-%m-%d')}"
    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"Loan(id={self._id}, user={self._user.get_id()}, book={self._book.get_id_IBSN()}, loanDate={self._loanDate.isoformat()})"
    