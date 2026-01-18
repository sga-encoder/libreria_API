"""
Módulo que define el modelo de dominio `Book`.

Contiene la clase Book que representa un libro en la aplicación de biblioteca.
Proporciona fábrica desde diccionarios, conversión a diccionario, getters/setters
y utilidades de comparación/representación.
"""
from typing import Optional
from app.domain.exceptions import ValidationException

class Book:
    """
    Modelo de dominio para un libro.

    Atributos privados:
    - __id_IBSN (str): Identificador ISBN del libro (debe tener exactamente 13 caracteres).
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
        
        Raises:
            ValidationException: Si algún parámetro no cumple las validaciones.
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
            
        Raises:
            ValidationException: Si data no es un diccionario o faltan campos obligatorios.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"El parámetro 'data' debe ser un diccionario, recibido: {type(data).__name__}"
            )
        
        # Validar campos obligatorios
        required_fields = ["id_IBSN", "title", "author"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationException(
                f"Faltan campos obligatorios en el diccionario: {', '.join(missing_fields)}"
            )
        
        # Normalizar el campo 'gender' para aceptar str o None
        raw_gender = data.get("gender")
        gender = raw_gender if raw_gender is not None else None

        return cls(
            id_IBSN=data.get("id_IBSN"),
            title=data.get("title"),
            author=data.get("author"),
            gender=gender,
            weight=data.get("weight", 0.0),
            price=data.get("price", 0.0),
            description=data.get("description", ""),
            frond_page_url=data.get("frond_page_url", ""),
            is_borrowed=data.get("is_borrowed", False),
        )
        
    @classmethod
    def from_search_api(cls, id: str = "0000000000000", title: str = "Gum Guardians Story", author: str = "Adventure Time"):
        """
        Crea una instancia de Book a partir de datos de API externa.

        Parámetros opcionales para crear un libro de prueba.

        Devuelve:
            Book
            
        Raises:
            ValidationException: Si los parámetros no son válidos.
        """
        if not id or not isinstance(id, str):
            raise ValidationException(
                f"El ID debe ser una cadena no vacía, recibido: {type(id).__name__}"
            )
        
        if not title or not isinstance(title, str):
            raise ValidationException(
                f"El título debe ser una cadena no vacía, recibido: {type(title).__name__}"
            )
        
        if not author or not isinstance(author, str):
            raise ValidationException(
                f"El autor debe ser una cadena no vacía, recibido: {type(author).__name__}"
            )
        
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
        Establece el ID ISBN privado con validación.

        Parámetros:
        - id_IBSN (str): ISBN del libro (debe tener exactamente 13 caracteres).
        
        Raises:
            ValidationException: Si id_IBSN no es válido.
        """
        if not id_IBSN or not isinstance(id_IBSN, str):
            raise ValidationException(
                f"El ISBN debe ser una cadena no vacía, recibido: {type(id_IBSN).__name__}"
            )
        
        id_IBSN_stripped = id_IBSN.strip()
        
        if not id_IBSN_stripped:
            raise ValidationException("El ISBN no puede estar vacío o contener solo espacios")
        
        if len(id_IBSN_stripped) != 13:
            raise ValidationException(
                f"El ISBN debe tener exactamente 13 caracteres, recibido: {len(id_IBSN_stripped)}"
            )
        
        # Validar que sean solo dígitos (opcional, dependiendo de tu estándar ISBN)
        if not id_IBSN_stripped.isdigit():
            raise ValidationException(
                f"El ISBN debe contener solo dígitos, recibido: '{id_IBSN_stripped}'"
            )
        
        self.__id_IBSN = id_IBSN_stripped
    
    def set_title(self, title: str):
        """
        Establece el título del libro.
        
        Raises:
            ValidationException: Si title no es válido.
        """
        if not title or not isinstance(title, str):
            raise ValidationException(
                f"El título debe ser una cadena no vacía, recibido: {type(title).__name__}"
            )
        
        title_stripped = title.strip()
        
        if not title_stripped:
            raise ValidationException("El título no puede estar vacío o contener solo espacios")
        
        if len(title_stripped) < 1:
            raise ValidationException("El título debe tener al menos 1 carácter")
        
        if len(title_stripped) > 500:
            raise ValidationException(
                f"El título no puede exceder 500 caracteres, recibido: {len(title_stripped)}"
            )
        
        self.__title = title_stripped
    
    def set_author(self, author: str):
        """
        Establece el autor del libro.
        
        Raises:
            ValidationException: Si author no es válido.
        """
        if not author or not isinstance(author, str):
            raise ValidationException(
                f"El autor debe ser una cadena no vacía, recibido: {type(author).__name__}"
            )
        
        author_stripped = author.strip()
        
        if not author_stripped:
            raise ValidationException("El autor no puede estar vacío o contener solo espacios")
        
        if len(author_stripped) < 2:
            raise ValidationException(
                f"El autor debe tener al menos 2 caracteres, recibido: {len(author_stripped)}"
            )
        
        if len(author_stripped) > 200:
            raise ValidationException(
                f"El autor no puede exceder 200 caracteres, recibido: {len(author_stripped)}"
            )
        
        self.__author = author_stripped
    
    def set_gender(self, gender: Optional[str]):
        """
        Establece el género/categoría del libro.
        
        Raises:
            ValidationException: Si gender no es válido (cuando no es None).
        """
        if gender is not None:
            if not isinstance(gender, str):
                raise ValidationException(
                    f"El género debe ser una cadena o None, recibido: {type(gender).__name__}"
                )
            
            gender_stripped = gender.strip()
            
            if not gender_stripped:
                # Si es string vacío, tratarlo como None
                self.__gender = None
                return
            
            if len(gender_stripped) > 100:
                raise ValidationException(
                    f"El género no puede exceder 100 caracteres, recibido: {len(gender_stripped)}"
                )
            
            self.__gender = gender_stripped
        else:
            self.__gender = None
    
    def set_weight(self, weight: float):
        """
        Establece el peso del libro.
        
        Raises:
            ValidationException: Si weight no es válido.
        """
        try:
            weight_float = float(weight)
        except (TypeError, ValueError):
            raise ValidationException(
                f"El peso debe ser un número, recibido: {type(weight).__name__}"
            )
        
        if weight_float < 0:
            raise ValidationException(
                f"El peso no puede ser negativo, recibido: {weight_float}"
            )
        
        if weight_float > 100:
            raise ValidationException(
                f"El peso no puede exceder 100 kg, recibido: {weight_float}"
            )
        
        self.__weight = weight_float
    
    def set_price(self, price: float):
        """
        Establece el precio del libro.
        
        Raises:
            ValidationException: Si price no es válido.
        """
        try:
            price_float = float(price)
        except (TypeError, ValueError):
            raise ValidationException(
                f"El precio debe ser un número, recibido: {type(price).__name__}"
            )
        
        if price_float < 0:
            raise ValidationException(
                f"El precio no puede ser negativo, recibido: {price_float}"
            )
        
        self.__price = price_float
    
    def set_description(self, description: str):
        """
        Establece la descripción del libro.
        
        Raises:
            ValidationException: Si description no es válido.
        """
        if description is None:
            self.__description = ""
            return
        
        if not isinstance(description, str):
            raise ValidationException(
                f"La descripción debe ser una cadena, recibido: {type(description).__name__}"
            )
        
        # Permitir descripción vacía
        if len(description) > 5000:
            raise ValidationException(
                f"La descripción no puede exceder 5000 caracteres, recibido: {len(description)}"
            )
        
        self.__description = description
    
    def set_frond_page_url(self, frond_page_url: str):
        """
        Establece la URL de la portada.
        
        Raises:
            ValidationException: Si frond_page_url no es válido.
        """
        if frond_page_url is None:
            self.__frond_page_url = ""
            return
        
        if not isinstance(frond_page_url, str):
            raise ValidationException(
                f"La URL de portada debe ser una cadena, recibido: {type(frond_page_url).__name__}"
            )
        
        # Permitir URL vacía
        if len(frond_page_url) > 1000:
            raise ValidationException(
                f"La URL de portada no puede exceder 1000 caracteres, recibido: {len(frond_page_url)}"
            )
        
        self.__frond_page_url = frond_page_url
    
    def set_is_borrowed(self, is_borrowed: bool):
        """
        Marca el libro como prestado o no.
        
        Raises:
            ValidationException: Si is_borrowed no es válido.
        """
        if not isinstance(is_borrowed, bool):
            raise ValidationException(
                f"is_borrowed debe ser booleano, recibido: {type(is_borrowed).__name__}"
            )
        
        self.__is_borrowed = is_borrowed

    def update_from_dict(self, data: dict):
        """
        Actualiza atributos del libro a partir de un diccionario.

        Valida y convierte tipos básicos. Solo se actualizan las claves presentes en `data`.
        
        Raises:
            ValidationException: Si data no es válido o algún campo tiene formato incorrecto.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"El parámetro 'data' debe ser un diccionario, recibido: {type(data).__name__}"
            )
        
        if not data:
            raise ValidationException("El diccionario de actualización no puede estar vacío")

        def _to_float(value, name):
            """Convierte a float con validación."""
            try:
                return float(value)
            except (TypeError, ValueError):
                raise ValidationException(f"El campo '{name}' debe ser convertible a número")

        def _to_bool(value):
            """Convierte a bool con validación."""
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                v = value.strip().lower()
                if v in ("true", "1", "yes", "y"):
                    return True
                if v in ("false", "0", "no", "n"):
                    return False
                raise ValidationException(
                    f"El campo 'is_borrowed' debe ser true/false, recibido: '{value}'"
                )
            if isinstance(value, (int, float)):
                return bool(value)
            raise ValidationException(
                f"El campo 'is_borrowed' debe ser booleano o convertible, recibido: {type(value).__name__}"
            )

        # Actualizar campos uno por uno (los setters ya tienen validaciones)
        if "id_IBSN" in data:
            self.__set_id_IBSN(data["id_IBSN"])

        if "title" in data:
            self.set_title(str(data["title"]) if data["title"] is not None else "Untitled")

        if "author" in data:
            self.set_author(str(data["author"]) if data["author"] is not None else "Unknown")

        if "gender" in data:
            self.set_gender(data["gender"])

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