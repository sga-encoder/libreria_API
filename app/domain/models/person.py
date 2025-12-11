"""Módulo `person`.

Contiene la clase `Person` que representa a una persona/usuario del sistema
con validaciones básicas y manejo seguro de contraseñas.
"""

import re

from .enums import PersonRole
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import generate_id


class Person:
    """Representa a una persona en la librería.

    Atributos privados:
    - _id: identificador único (str)
    - _fullName: nombre completo (str)
    - _email: correo electrónico (str)
    - _password: contraseña hasheada (str)
    - _role: rol de la persona (`PersonRole`)

    La clase proporciona métodos de creación (`from_dict`, `default`),
    getters/setters con validación, y utilidades para verificar y cambiar
    la contraseña de forma segura.
    """

    _id: str
    _fullName: str
    _email: str
    _password: str
    _role: PersonRole

    def __init__(self, fullName: str, email: str, password: str, role: PersonRole, id: str = None, password_is_hashed: bool = False):
        """Inicializa una nueva instancia de Person.

        Args:
            fullName (str): Nombre completo de la persona.
            email (str): Correo electrónico de la persona.
            password (str): Contraseña en texto plano.
            role (PersonRole): Rol de la persona.
            id (str, optional): Identificador único. Defaults to None.

        Raises:
            ValueError: Si los argumentos no cumplen las validaciones.
        """
        self.__set_id(id)
        self.set_fullName(fullName)
        self.set_email(email)
        if password_is_hashed:
            self._password = password
        else:
            self.set_password(password)
        self.__set_role(role)

    @classmethod
    def from_dict(cls, data: dict, role: PersonRole = PersonRole.USER ,password_is_hashed: bool = True):
        """Crea una instancia de Person a partir de un diccionario.

        Args:
            data (dict): Diccionario con las claves 'fullName', 'email', 'password', 'role' y 'id' (opcional).

        Returns:
            Person: Nueva instancia de Person.

        Raises:
            KeyError: Si falta alguna clave requerida o el role no es válido.
            ValueError: Si los valores no cumplen las validaciones.
        """
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            role=role,
            id=data.get("id"),
            password_is_hashed=password_is_hashed,
        )
        
    @classmethod
    def from_search_api(cls, id: str):
        """Crea una instancia de Person solo con el id para búsquedas.

        Args:
            id (str): Identificador único.

        Returns:
            Person: Nueva instancia con valores por defecto.
        """
        return cls(
            fullName="Gum Guardians",
            email="gumGuardians.adventure@time.cartoon",
            password="adventuretime",
            role=PersonRole.USER,
            id=id,
        )

    @classmethod
    def default(cls):
        """Devuelve una instancia de Person con valores por defecto para pruebas/demo.

        Returns:
            Person: Nueva instancia con valores por defecto.
        """
        return cls(
            fullName="Jake the Dog",
            email="jakeTheDog.adventure@time.cartoon",
            password="adventuretime",
            role=PersonRole.USER,
            id="00000000000000000",
        )

    def get_id(self):
        """Retorna el identificador único de la persona.

        Returns:
            str: El identificador único.
        """
        return self._id

    def get_fullName(self):
        """Retorna el nombre completo.

        Returns:
            str: El nombre completo.
        """
        return self._fullName

    def get_email(self):
        """Retorna el correo electrónico.

        Returns:
            str: El correo electrónico.
        """
        return self._email

    def get_password(self):
        """Retorna el hash de la contraseña.

        Returns:
            str: El hash de la contraseña.
        """
        return self._password

    def get_role(self):
        """Retorna el rol de la persona.

        Returns:
            PersonRole: El rol de la persona.
        """
        return self._role

    def __set_id(self, id: str):
        """Asigna un id; si es None, lo genera automáticamente.

        Args:
            id (str): El identificador a asignar.
        """
        if id is None:
            self._id = generate_id()
        else:
            self._id = id

    def set_fullName(self, fullName: str):
        """Valida y asigna el nombre completo.

        Args:
            fullName (str): El nombre completo a asignar.

        Raises:
            ValueError: Si no cumple las reglas de validación.
        """
        if not fullName or not fullName.strip():
            raise ValueError("El nombre completo no puede estar vacío.")
        if len(fullName) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres.")
        if len(fullName) > 50:
            raise ValueError("El nombre completo no puede exceder los 50 caracteres.")

        self._fullName = fullName

    def set_email(self, email: str):
        """Valida y asigna el correo electrónico.

        Args:
            email (str): El correo electrónico a asignar.

        Raises:
            ValueError: Si no es un email válido.
        """
        pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

        if not pattern.match(email):
            raise ValueError("El email proporcionado no es válido.")

        self._email = email

    def set_password(self, password: str):
        """Hashea la contraseña y la asigna.

        Args:
            password (str): La contraseña en texto plano.
        """
        self._password = generate_password_hash(password)

    def __set_role(self, role: PersonRole):
        """Asigna el rol de la persona.

        Args:
            role (PersonRole): El rol a asignar.
        """
        if not isinstance(role, PersonRole):
            self._role = PersonRole.USER
        else:
            self._role = role

    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado.

        Args:
            password (str): La contraseña en texto plano a verificar.

        Returns:
            bool: True si coincide, False en caso contrario.
        """
        return check_password_hash(self._password, password)

    def change_password(self, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña si la contraseña actual es correcta.

        Args:
            current_password (str): La contraseña actual en texto plano.
            new_password (str): La nueva contraseña en texto plano.

        Returns:
            bool: True si el cambio fue exitoso, False si la verificación falló.
        """
        if not self.verify_password(current_password):
            return False
        self.set_password(new_password)
        return True

    def to_dict(self):
        """Serializa la instancia a un diccionario.

        Returns:
            dict: Diccionario con los atributos de la persona.
        """
        return {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "role": self._role.name,
        }
        
    def update_from_dict(self, data: dict):
        """Actualiza los atributos de la instancia a partir de un diccionario.

        Args:
            data (dict): Diccionario con los campos a actualizar. Puede incluir 'fullName', 'email', 'new_password', 'role'.
                         Para actualizar la contraseña, debe incluir 'password' (actual) y 'new_password'.

        Raises:
            ValueError: Si los valores no son válidos o falta la contraseña actual para cambiarla.
        """
        if "fullName" in data:
            self.set_fullName(data["fullName"])
        if "email" in data:
            self.set_email(data["email"])
        if "new_password" in data:
            if "password" in data:
                self.change_password(data["password"], data["new_password"])
            else:
                raise ValueError("necesitas la contraseña anterior para actualizar la contraseña")
        if "role" in data:
            self.__set_role(PersonRole[data["role"]])

    def __str__(self):
        """Representación en cadena legible para humanos.

        Returns:
            str: Cadena con información de la persona.
        """
        return f"Person: {self._fullName} ({self._email}) - Role: {self._role.name}"

    def __repr__(self):
        """Representación orientada a debugging.

        Returns:
            str: Cadena para debugging.
        """
        return f"Person(id={self._id}, fullName={self._fullName}, role={self._role.name})"
    
    def __eq__(self, other):
        """Compara la igualdad con otra instancia de Person.

        Regla:
        - Si ambos objetos tienen `id`, se comparan los `id`.
        - Si no, se compara el `email` (se asume único por usuario).
        - Devuelve False si `other` no es una Person.

        Args:
            other: Objeto a comparar.

        Returns:
            bool: True si son iguales, False en caso contrario.
        """
        if self is other:
            return True
        if not isinstance(other, Person):
            return False
        # Si ambos tienen id, usarlo como identidad
    
        # Fallback: comparar por email
        return self._id == other._id
        

