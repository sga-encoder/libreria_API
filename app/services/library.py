from app.models import Book, User, Loan
from app.utils import Stack, Queue


class Library:
    """Clase estática que expone colecciones y utilidades de la biblioteca.

    No puede instanciarse. Todos los atributos y métodos son de clase.
    """
    __inventary: Stack[Book] = Stack()
    __order_inventary: list[Book] = []
    __resevationsQueue: Queue[tuple[User, Book]] = Queue()
    __user: list[User] = []
    __loanRecords: list[Loan] = []
    __bookcase: list[Book] = []
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        raise TypeError("Library es una clase estática y no se puede instanciar.")

    @classmethod
    def initialize(cls) -> None:
        """falta implementarlo"""
        if not cls._initialized:
            cls.__inventary = Stack()
            cls.__order_inventary = []
            cls.__resevationsQueue = Queue()
            cls.__user = []
            cls.__loanRecords = []
            cls.__bookcase = []
            cls._initialized = True

    @classmethod
    def get_inventary(cls) -> Stack[Book]:
        cls.initialize()
        return cls.__inventary

    @classmethod
    def get_order_inventary(cls) -> list[Book]:
        cls.initialize()
        return cls.__order_inventary

    @classmethod
    def get_reservationsQueue(cls) -> Queue[tuple[User, Book]]:
        cls.initialize()
        return cls.__resevationsQueue

    @classmethod
    def get_user(cls) -> list[User]:
        cls.initialize()
        return cls.__user

    @classmethod
    def get_loanRecords(cls) -> list[Loan]:
        cls.initialize()
        return cls.__loanRecords

    @classmethod
    def get_bookcase(cls) -> list[Book]:
        cls.initialize()
        return cls.__bookcase

    @classmethod
    def set_inventary(cls, inventary: Stack[Book]) -> None:
        cls.__inventary = inventary

    @classmethod
    def set_order_inventary(cls, order_inventary: list[Book]) -> None:
        cls.__order_inventary = order_inventary

    @classmethod
    def set_reservationsQueue(cls, resevationsQueue: Queue[tuple[User, Book]]) -> None:
        cls.__resevationsQueue = resevationsQueue

    @classmethod
    def set_user(cls, user: list[User]) -> None:
        cls.__user = user

    @classmethod
    def set_loanRecords(cls, loanRecords: list[Loan]) -> None:
        cls.__loanRecords = loanRecords

    @classmethod
    def set_bookcase(cls, bookcase: list[Book]) -> None:
        cls.__bookcase = bookcase
        
    @classmethod
    def push_inventary(cls, value: Book ) -> None :
        """Aplica una función modificadora al inventario de libros."""
        cls.__inventary.push(value)
            


# Inicializar al importar el módulo para mantener comportamiento previo
Library.initialize()
    
    