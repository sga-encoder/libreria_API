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

    def __init__(self, fullName: str, email: str, password: str, role: PersonRole, id: str = None):
        """Inicializa una nueva instancia de `Person`.

        fullName: nombre completo; se valida longitud y que no esté vacío.
        email: correo electrónico; se valida con una expresión regular simple.
        password: contraseña en texto plano; se almacenará como hash.
        role: miembro de la enumeración `PersonRole`.
        id: identificador opcional; si no se provee se genera con `generate_id()`.
        """
        self.__set_id(id)
        self.set_fullName(fullName)
        self.set_email(email)
        self.set_password(password)
        self.__set_role(role)

    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia de `Person` a partir de un diccionario.

        Se espera que `data` contenga las claves: `fullName`, `email`, `password`,
        `role` (nombre del enum) e `id` (opcional).
        """
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            role=PersonRole[data.get("role")],
            id=data.get("id"),
        )

    @classmethod
    def default(cls):
        """Devuelve una instancia `Person` con valores por defecto (uso de pruebas/demo)."""
        return cls(
            fullName="Jake the Dog",
            email="jakeTheDog.adventure@time.cartoon",
            password="adventuretime",
            role=PersonRole.USER,
        )

    def get_id(self):
        """Retorna el identificador único de la persona."""
        return self._id

    def get_fullName(self):
        """Retorna el nombre completo."""
        return self._fullName

    def get_email(self):
        """Retorna el correo electrónico."""
        return self._email

    def get_password(self):
        """Retorna el hash de la contraseña (no el texto plano)."""
        return self._password

    def get_role(self):
        """Retorna el rol (`PersonRole`)."""
        return self._role

    def __set_id(self, id: str):
        """Asigna un `id`; si es `None`, lo genera automáticamente."""
        if id is None:
            self._id = generate_id()
        else:
            self._id = id

    def set_fullName(self, fullName: str):
        """Valida y asigna el nombre completo.

        Reglas:
        - No puede estar vacío ni solo espacios.
        - Longitud mínima 3 y máxima 50 caracteres.
        """
        if not fullName or not fullName.strip():
            raise ValueError("El nombre completo no puede estar vacío.")
        if len(fullName) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres.")
        if len(fullName) > 50:
            raise ValueError("El nombre completo no puede exceder los 50 caracteres.")

        self._fullName = fullName

    def set_email(self, email: str):
        """Valida y asigna el correo electrónico usando una regex simple.

        Se verifica la estructura básica `local@dominio.tld`.
        """
        pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

        if not pattern.match(email):
            raise ValueError("El email proporcionado no es válido.")

        self._email = email

    def set_password(self, password: str):
        """Hash de la contraseña y asignación.

        Recibe la contraseña en texto plano y almacena su hash seguro.
        """
        self._password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

    def __set_role(self, role: PersonRole):
        """Asigna el rol de la persona (método interno)."""
        self._role = role

    def verify_password(self, password: str) -> bool:
        """Verifica si `password` coincide con el hash almacenado.

        Retorna `True` si coinciden, `False` en caso contrario.
        """
        return check_password_hash(self._password, password)

    def change_password(self, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña si `current_password` es correcta.

        - Verifica la contraseña actual con `verify_password`.
        - Si es correcta, reemplaza el hash por el hash de `new_password`.
        - Retorna `True` si el cambio tuvo éxito, `False` si la verificación falló.
        """
        if not self.verify_password(current_password):
            return False
        self.set_password(new_password)
        return True

    def to_dict(self):
        """Serializa la instancia a un diccionario apto para persistencia/JSON.

        Nota: `password` contendrá el hash.
        """
        return {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "role": self._role.name,
        }
        
    def __eq__(self, other):
        """Comparación de igualdad entre instancias de Person.

        Regla:
        - Si ambos objetos tienen `id`, se comparan los `id`.
        - Si no, se compara el `email` (se asume único por usuario).
        - Devuelve False si `other` no es una Person.
        """
        if self is other:
            return True
        if not isinstance(other, Person):
            return False
        # Si ambos tienen id, usarlo como identidad
        if getattr(self, "_id", None) and getattr(other, "_id", None):
            return self._id == other._id
        # Fallback: comparar por email
        return self._email == other._email

    def __str__(self):
        """Representación en cadena legible para humanos."""
        return f"Person: {self._fullName} ({self._email}) - Role: {self._role.name}"

    def __repr__(self):
        """Representación orientada a debugging."""
        return f"Person(id={self._id}, fullName={self._fullName}, role={self._role.name})"
        

