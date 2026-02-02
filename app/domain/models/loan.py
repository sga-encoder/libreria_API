from datetime import datetime
from . import User
from .book import Book
from app.utils import generate_id
from app.domain.exceptions import BookAlreadyBorrowedException, ValidationException, ResourceNotFoundException



class Loan:
    __id: str
    __user: User
    __book: Book
    __loan_date: datetime
    __status: bool
    
    def __init__(self, id_user: str, id_book: str, loan_date: datetime, id: str = None, 
                 status: bool = True, searching: bool = False, skip_validation: bool = False,
                 user_service=None, book_service=None):  # ✅ Agregar servicios opcionales
        """Inicializa un préstamo validando usuario y libro."""
        self._user_service = user_service  # ✅ Guardar referencias
        self._book_service = book_service
        
        self.__set_id(id)
        
        if searching or skip_validation:
            self.__set_user(id_user, searching=True)
            self.__set_book(id_book, searching=True)
        else:
            self.__set_user(id_user)
            self.__set_book(id_book)
        
        self.__set_loan_date(loan_date)
        self.__set_status(status)
    
    @classmethod
    def from_dict(cls, json: dict, skip_validation: bool = False, user_service=None, book_service=None):  # ✅ Agregar
        """Crea una instancia de Loan a partir de un diccionario.

        Args:
            json (dict): Diccionario con los datos del préstamo.
            skip_validation (bool): Si True, no valida existencia de usuario/libro (para uso con SQL).

        Returns:
            Loan: Instancia creada.
        """
        id = json.get("id", None)
        id_user = json["id_user"]
        id_book = json["id_ISBN_book"]
        
        # loan_date es opcional, si no viene usar fecha actual
        loan_date_str = json.get("loan_date")
        if loan_date_str:
            loan_date = datetime.fromisoformat(loan_date_str)
        else:
            loan_date = datetime.now()
        
        status = json.get("status", True)
        
        return cls(id_user=id_user, id_book=id_book, loan_date=loan_date, id=id, 
                   status=status, skip_validation=skip_validation,
                   user_service=user_service, book_service=book_service)  # ✅ Pasar servicios
    
    @classmethod
    def from_search_api(cls, id: str):
        return cls(
            id_user="0000000000000",
            id_book="0000000000000",
            loan_date=datetime.now(),
            id=id,
            searching=True
        )
    
    def get_id(self):
        return self.__id
    def get_user(self):
        # ✅ Solo resolver si se pasó el servicio
        if self._user_service and isinstance(self.__user, str):
            self.__user = self._user_service.get_by_id(self.__user)
        return self.__user
    def get_book(self):
        # ✅ Solo resolver si se pasó el servicio
        if self._book_service and isinstance(self.__book, str):
            self.__book = self._book_service.get_by_isbn(self.__book)
        return self.__book
    def get_loan_date(self):
        return self.__loan_date
    def get_status(self):
        return self.__status
    def set_status(self, status: bool):
        self.__set_status(status)
    
    def __set_id(self, id: str):
        """Asigna un `id`; si es `None`, lo genera automáticamente."""
        if id is None:
            self.__id = generate_id()
        else:
            self.__id = id
            
    def __set_user(self, id_user: str, searching: bool = False):
        if searching:
            self.__user = id_user
            return
        if not id_user:
            raise ValidationException(f"ID no debe estar vacío, valor recibido: {id_user}")
        
        # ✅ Si tiene servicio inyectado, usarlo
        if self._user_service:
            user = self._user_service.get_by_id(id_user)
            if user is None:
                raise ResourceNotFoundException(f"Usuario con ID {id_user} no encontrado")
            self.__user = user
        else:
            # ✅ Sin servicio, solo guardar el ID (lazy loading)
            self.__user = id_user
                
            if user is None:
                raise ResourceNotFoundException(f"Usuario con ID {id_user} no encontrado")
            self.__user = user
    
    def __set_book(self, id_book: str, inizialize: bool = False, searching: bool = False):
        if searching:
            self.__book = id_book
            return
        if not id_book:
            raise ValidationException(f"ID ISBN no debe estar vacío")
        
        # ✅ Si tiene servicio inyectado, usarlo
        if self._book_service:
            book = self._book_service.get_by_isbn(id_book)
            if book is None:
                raise ValidationException(f"Libro con ISBN {id_book} no encontrado")
            
            if book.get_is_borrowed():
                raise BookAlreadyBorrowedException(f"Libro ya está prestado")
            
            self.__book = book
        else:
            # ✅ Sin servicio, solo guardar el ISBN (lazy loading)
            self.__book = id_book
        
    def __set_loan_date(self, loan_date: datetime):
        self.__loan_date = loan_date
        
    def __set_status(self, status: bool):
        if not isinstance(status, bool):
                raise ValidationException(f"El estado del préstamo debe ser booleano (True/False), recibido: {type(status).__name__}")
        self.__status = status
        
    def get_user_id(self):
        """Retorna solo el ID del usuario."""
        if isinstance(self.__user, str):
            return self.__user  # ✅ Ya es un string (ID)
        return self.__user.get_id()  # ✅ Es un objeto User

    def get_book_isbn(self):
        """Retorna solo el ISBN del libro."""
        if isinstance(self.__book, str):
            return self.__book  # ✅ Ya es un string (ISBN)
        return self.__book.get_id_IBSN()  # ✅ Es un objeto Book
            
    def update_from_dict(self, json: dict):
        """Actualiza los atributos del préstamo a partir de un diccionario.

        Args:
            json (dict): Diccionario con los campos a actualizar. 
                         Puede incluir 'user', 'book', 'loan_date'.
        """

        if "id_ISBN_book" in json:
            self.__set_book( json.get("id_ISBN_book"))
        if "status" in json:
            self.__set_status(json.get("status"))
        
    def to_dict(self):
        """Convierte el préstamo a diccionario para la API."""
        return {
            "id": self.__id,
            "user": self.get_user_id(),  # ✅ Siempre retorna string
            "book": self.get_book_isbn(),  # ✅ Siempre retorna string
            "loan_date": self.__loan_date.isoformat(),
            "status": self.__status
        }
        
    def to_dict_with_objects(self):
        return {
            "id": self.__id,
            "user": self.__user.to_dict(),
            "book": self.__book.to_dict(),
            "loan_date": self.__loan_date.isoformat(),
            "status": self.__status
        }
        
    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"Loan: {self.__id} - User: {self.__user.get_fullName()} - Book: {self.__book.get_title()} - Date: {self.__loan_date.strftime('%Y-%m-%d')}"
    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"Loan(id={self.__id}, user={self.__user.get_id()}, book={self.__book.get_id_IBSN()}, loan_date={self.__loan_date.isoformat()}, status={self.__status})"
    
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

