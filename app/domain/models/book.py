"""
Módulo que define el modelo de dominio `Book`.

Contiene la clase Book que representa un libro en la aplicación de biblioteca.
Proporciona fábrica desde diccionarios, conversión a diccionario, getters/setters
y utilidades de comparación/representación.
"""
from typing import Optional

class Book:
    """
    Modelo de dominio para un libro.

    Atributos privados:
    - __id_IBSN (str): Identificador ISBN del libro (nota: el método de validación actual
      lanza ValueError si la longitud es 13 — revisar lógica si se desea otra validación).
    - __title (str)
    - __author (str)
    - __gender (Optional[str])
    - __weight (float)
    - __price (float)
    - __description (str)
    - __frond_page_url (str)
    - __is_borrowed (bool)

    Uso típico:
        book = Book.from_dict({...})
        book.set_title("Nuevo título")
        data = book.to_dict()
    """

    __id_IBSN: str
    __title: str
    __author: str
    __gender: Optional[str]
    __weight: float
    __price: float
    __description: str
    __frond_page_url: str
    __is_borrowed: bool

    def __init__(self, id_IBSN: str, title: str, author: str, gender: Optional[str], weight: float, price: float, description: str, frond_page_url: str, is_borrowed: bool = False):
        """
        Inicializa una instancia de Book.

        Parámetros:
        - id_IBSN (str): Identificador ISBN del libro.
        - title (str): Título del libro.
        - author (str): Autor del libro.
        - gender (Optional[str]): Género o categoría del libro.
        - weight (float): Peso del libro.
        - price (float): Precio del libro.
        - description (str): Descripción del libro.
        - frond_page_url (str): URL de la portada.
        - is_borrowed (bool): Indica si el libro está prestado (por defecto False).
        """
        self.__set_id_IBSN(id_IBSN)
        self.set_title(title)
        self.set_author(author)
        self.set_gender(gender)
        self.set_weight(weight)
        self.set_price(price)
        self.set_description(description)
        self.set_frond_page_url(frond_page_url)
        self.set_is_borrowed(is_borrowed)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Crea una instancia de Book a partir de un diccionario.

        El diccionario puede contener las claves:
        "id_IBSN", "title", "author", "gender", "weight", "price",
        "description", "frond_page_url", "is_borrowed".

        Normaliza 'gender' para aceptar str o None.

        Devuelve:
            Book
        """
        # Normalizar el campo 'gender' para aceptar str o None
        raw_gender = data.get("gender")
        gender = raw_gender if raw_gender is not None else None

        return cls(
            id_IBSN=data.get("id_IBSN"),
            title=data.get("title"),
            author=data.get("author"),
            gender=gender,
            weight=data.get("weight"),
            price=data.get("price"),
            description=data.get("description", ""),
            frond_page_url=data.get("frond_page_url", ""),
            is_borrowed=data.get("is_borrowed", False),
        )
        
    @classmethod
    def from_search_api(cls, id: str ="0000000000000", title: str = "Gum Guardians Story", author: str = "Adventure Time"):
        """
        Crea una instancia de Book a partir de un diccionario obtenido
        de una API externa (por ejemplo, Google Books API).

        Mapea los campos del diccionario externo a los atributos de Book.

        Devuelve:
            Book
        """
        return cls(
            id,
            title,
            author,
            "Fiction",
            4.0,
            100000.0,
            "las aventuras de de los guardianes del chicle",
            "las fotos son para las locas",
            False
        )
            

    @classmethod
    def default(cls):
        """
        Fábrica que devuelve una instancia por defecto de Book con valores iniciales.
        Útil para pruebas o valores placeholder.
        """
        return cls(
            id_IBSN="0000000000000",
            title="Aventure Time",
            author="Cartoon Network",
            gender="Fiction",
            weight=4.0,
            price=100000.0,
            description="el mejor libro del mundo",
            frond_page_url="las fotos son para las locas",
            is_borrowed=False
        )

    def get_id_IBSN(self):
        """Devuelve el ISBN del libro (str)."""
        return self.__id_IBSN
    def get_title(self):
        """Devuelve el título del libro (str)."""
        return self.__title
    def get_author(self):
        """Devuelve el autor del libro (str)."""
        return self.__author
    def get_gender(self):
        """Devuelve el género/categoría del libro (str|None)."""
        return self.__gender
    def get_weight(self):
        """Devuelve el peso del libro (float)."""
        return self.__weight
    def get_price(self):
        """Devuelve el precio del libro (float)."""
        return self.__price
    def get_description(self):
        """Devuelve la descripción del libro (str)."""
        return self.__description
    def get_frond_page_url(self):
        """Devuelve la URL de la portada (str)."""
        return self.__frond_page_url
    def get_is_borrowed(self):
        """Indica si el libro está prestado (bool)."""
        return self.__is_borrowed

    def __set_id_IBSN(self, id_IBSN: str):
        """
        Establece el ID ISBN privado con validación mínima.

        Actualmente lanza ValueError si la longitud de `id_IBSN` es 13
        """
        if len(id_IBSN) != 13:
            raise ValueError("ISBN must be 13 characters long")
        self.__id_IBSN = id_IBSN
    def set_title(self, title: str):
        """Establece el título del libro."""
        self.__title = title
    def set_author(self, author: str):
        """Establece el autor del libro."""
        self.__author = author
    def set_gender(self, gender: Optional[str]):
        """Establece el género/categoría del libro."""
        self.__gender = gender
    def set_weight(self, weight: float):
        """Establece el peso del libro."""
        self.__weight = weight
    def set_price(self, price: float):
        """Establece el precio del libro."""
        self.__price = price
    def set_description(self, description: str):
        """Establece la descripción del libro."""
        self.__description = description
    def set_frond_page_url(self, frond_page_url: str):
        """Establece la URL de la portada."""
        self.__frond_page_url = frond_page_url
    def set_is_borrowed(self, is_borrowed: bool):
        """Marca el libro como prestado o no."""
        self.__is_borrowed = is_borrowed

    def update_from_dict(self, data: dict):
        """
        Actualiza atributos del libro a partir de un diccionario.

        Valida y convierte tipos básicos. Solo se actualizan las claves presentes en `data`.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        def _to_float(value, name):
            try:
                return float(value)
            except (TypeError, ValueError):
                raise ValueError(f"{name} must be convertible to float")

        def _to_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                v = value.strip().lower()
                if v in ("true", "1", "yes", "y"):
                    return True
                if v in ("false", "0", "no", "n"):
                    return False
                raise ValueError("is_borrowed string must be true/false")
            if isinstance(value, (int, float)):
                return bool(value)
            raise ValueError("is_borrowed must be a bool-like value")

        if "id_IBSN" in data:
            # usa la validación ya definida en __set_id_IBSN
            self.__set_id_IBSN(data["id_IBSN"])

        if "title" in data:
            self.set_title(str(data["title"]) if data["title"] is not None else "")

        if "author" in data:
            self.set_author(str(data["author"]) if data["author"] is not None else "")

        if "gender" in data:
            self.set_gender(data["gender"] if data["gender"] is not None else None)

        if "weight" in data:
            self.set_weight(_to_float(data["weight"], "weight"))

        if "price" in data:
            self.set_price(_to_float(data["price"], "price"))

        if "description" in data:
            self.set_description(str(data["description"]) if data["description"] is not None else "")

        if "frond_page_url" in data:
            self.set_frond_page_url(str(data["frond_page_url"]) if data["frond_page_url"] is not None else "")

        if "is_borrowed" in data:
            self.set_is_borrowed(_to_bool(data["is_borrowed"]))

    def to_dict(self):
        """
        Convierte la instancia a un diccionario serializable.

        Devuelve las claves:
        id_IBSN, title, author, gender, weight, price, description, frond_page_url, is_borrowed
        """
        return {
            "id_IBSN": self.__id_IBSN,
            "title": self.__title,
            "author": self.__author,
            "gender": self.__gender if self.__gender is not None else None,
            "weight": self.__weight,
            "price": self.__price,
            "description": self.__description,
            "frond_page_url": self.__frond_page_url,
            "is_borrowed": self.__is_borrowed
        }


    def __str__(self):
        """Representación legible del libro para impresión."""
        return f"ISBN: {self.__id_IBSN} - Book: {self.__title} by {self.__author}"

    def __repr__(self):
        """Representación útil para debugging."""
        return f"Book(id_IBSN={self.__id_IBSN}, title={self.__title}, author={self.__author})"

    def __eq__(self, other):
        """
        Comparación de igualdad entre instancias de Book.

        Reglas:
        - Si `self` y `other` son la misma instancia, devuelve True.
        - Si `other` no es instancia de Book, devuelve False.
        - Devuelve True si al menos uno de los siguientes coincide: id_IBSN, title, author.
        """
        if self is other:
            return True
        if not isinstance(other, Book):
            return False

        return (self.__id_IBSN == other.__id_IBSN or
                self.__title == other.__title or
                self.__author == other.__author)