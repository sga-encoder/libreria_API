from .enums import BookGender

class Book:
    __id_IBSN: str
    __title: str
    __author: str
    __gender: BookGender
    __weight: float
    __price: float
    __is_borrowed: bool
    
    def __init__(self, id_IBSN: str, title: str, author: str, gender: BookGender, weight: float, price: float, is_borrowed: bool = False):
        self.__set_id_IBSN(id_IBSN)
        self.set_title(title)
        self.set_author(author)
        self.set_gender(gender)
        self.set_weight(weight)
        self.set_price(price)
        self.set_is_borrowed(is_borrowed)
        
    @classmethod
    def from_dict(cls, data: dict):
        # Normalizar el campo 'gender' para aceptar str, int o BookGender
        raw_gender = data.get("gender")
        # Evita pasar None a BookGender — permite actualizaciones parciales
        gender = BookGender(raw_gender) if raw_gender is not None else None

        return cls(
            id_IBSN=data.get("id_IBSN"),
            title=data.get("title"),
            author=data.get("author"),
            gender=gender,
            weight=data.get("weight"),
            price=data.get("price"),
            is_borrowed=data.get("is_borrowed", False),
        )
        
    @classmethod
    def default(cls):
        return cls(
            id_IBSN="000-0",
            title="Default Title",
            author="Default Author",
            gender=BookGender.OTHER,
            weight=0.0,
            price=0.0,
            is_borrowed=False
        )
        
        
        
    def get_id_IBSN(self):
        return self.__id_IBSN
    def get_title(self):
        return self.__title
    def get_author(self):
        return self.__author
    def get_gender(self):
        return self.__gender
    def get_weight(self):
        return self.__weight
    def get_price(self):
        return self.__price
    def get_is_borrowed(self):
        return self.__is_borrowed
    
    def __set_id_IBSN(self, id_IBSN: str):
        self.__id_IBSN = id_IBSN
    def set_title(self, title: str):
        self.__title = title
    def set_author(self, author: str):
        self.__author = author
    def set_gender(self, gender: BookGender):
        self.__gender = gender
    def set_weight(self, weight: float):
        self.__weight = weight
    def set_price(self, price: float):
        self.__price = price
    def set_is_borrowed(self, is_borrowed: bool):
        self.__is_borrowed = is_borrowed
        
    def to_dict(self):
        return {
            "id_IBSN": self.__id_IBSN,
            "title": self.__title,
            "author": self.__author,
            "gender": self.__gender.name if self.__gender is not None else None,
            "weight": self.__weight,
            "price": self.__price,
            "is_borrowed": self.__is_borrowed
        }
        
    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"ISBN: {self.__id_IBSN} - Book: {self.__title} by {self.__author}"
    
    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"Book(id_IBSN={self.__id_IBSN}, title={self.__title}, author={self.__author})"