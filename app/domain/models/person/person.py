"""Módulo `person`.

Contiene la clase `Person` que representa a una persona/usuario del sistema
con validaciones básicas y manejo seguro de contraseñas.
"""

import re

from ..enums import PersonRole
from app.domain.exceptions import ValidationException
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
    _historial: list
    

    def __init__(self, fullName: str, email: str, password: str, role: PersonRole, id: str = None, password_is_hashed: bool = False):
        """Inicializa una nueva instancia de Person.

        Args:
            fullName (str): Nombre completo de la persona.
            email (str): Correo electrónico de la persona.
            password (str): Contraseña en texto plano o hasheada.
            role (PersonRole): Rol de la persona.
            id (str, optional): Identificador único. Defaults to None.
            password_is_hashed (bool, optional): Si la contraseña ya está hasheada. Defaults to False.

        Raises:
            ValidationException: Si fullName, email o password no cumplen las validaciones.
            ValidationException: Si role no es una instancia de PersonRole.
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
            data (dict): Diccionario con las claves 'fullName', 'email', 'password' y 'id' (opcional).
            role (PersonRole): Rol de la persona. Defaults to PersonRole.USER.
            password_is_hashed (bool): Si la contraseña ya está hasheada. Defaults to True.

        Returns:
            Person: Nueva instancia de Person.

        Raises:
            ValidationException: Si data no es un diccionario o falta alguna clave requerida.
            ValidationException: Si los valores no cumplen las validaciones.
        """
        # print(data)
        if not isinstance(data, dict):
            raise ValidationException("Los datos deben ser un diccionario válido")
        
        # Validar campos requeridos
        required_fields = ["fullName", "email", "password"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise ValidationException(
                f"Faltan campos requeridos: {', '.join(missing_fields)}"
            )
        
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
            ValidationException: Si fullName es None, vacío o no cumple las reglas de longitud.
        """
        if not fullName or not isinstance(fullName, str):
            raise ValidationException(
                f"El nombre completo debe ser una cadena no vacía, recibido: {type(fullName).__name__}"
            )
        
        fullName_stripped = fullName.strip()
        
        if not fullName_stripped:
            raise ValidationException("El nombre completo no puede estar vacío o contener solo espacios")
        
        if len(fullName_stripped) < 3:
            raise ValidationException(
                f"El nombre completo debe tener al menos 3 caracteres, recibido: {len(fullName_stripped)}"
            )
        
        if len(fullName_stripped) > 50:
            raise ValidationException(
                f"El nombre completo no puede exceder los 50 caracteres, recibido: {len(fullName_stripped)}"
            )

        self._fullName = fullName_stripped

    def set_email(self, email: str):
        """Valida y asigna el correo electrónico.

        Args:
            email (str): El correo electrónico a asignar.

        Raises:
            ValidationException: Si email es None, vacío o no tiene formato válido.
        """
        if not email or not isinstance(email, str):
            raise ValidationException(
                f"El email debe ser una cadena no vacía, recibido: {type(email).__name__}"
            )
        
        # Patrón más estricto para validación de email
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

        if not pattern.match(email):
            raise ValidationException(
                f"El email '{email}' no tiene un formato válido. "
                f"Debe ser del tipo 'usuario@dominio.com'"
            )

        self._email = email # Normalizar a minúsculas

    def set_password(self, password: str):
        """Hashea la contraseña y la asigna.

        Args:
            password (str): La contraseña en texto plano.
            
        Raises:
            ValidationException: Si password es None, vacío o muy corta.
        """
        if not password or not isinstance(password, str):
            raise ValidationException(
                f"La contraseña debe ser una cadena no vacía, recibido: {type(password).__name__}"
            )
        
        if len(password) < 6:
            raise ValidationException(
                f"La contraseña debe tener al menos 6 caracteres, recibido: {len(password)}"
            )
        
        if len(password) > 100:
            raise ValidationException(
                f"La contraseña no puede exceder los 100 caracteres, recibido: {len(password)}"
            )
        
        self._password = generate_password_hash(password)

    def __set_role(self, role: PersonRole):
        """Asigna el rol de la persona.

        Args:
            role (PersonRole): El rol a asignar.
            
        Raises:
            ValidationException: Si role no es una instancia de PersonRole.
        """
        if not isinstance(role, PersonRole):
            raise ValidationException(
                f"El rol debe ser una instancia de PersonRole, recibido: {type(role).__name__}"
            )
        
        self._role = role
            
    def add_historial(self, item: str):
        """Agrega un ítem al historial de la persona.

        Args:
            item (str): El ítem a agregar al historial.
            
        Raises:
            ValidationException: Si item no es una cadena válida.
        """
        if not item or not isinstance(item, str):
            raise ValidationException(
                f"El ítem del historial debe ser una cadena no vacía, recibido: {type(item).__name__}"
            )
        
        if not hasattr(self, '_historial'):
            self._historial = []
        
        self._historial.append(item)

    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado.

        Args:
            password (str): La contraseña en texto plano a verificar.

        Returns:
            bool: True si coincide, False en caso contrario.
            
        Raises:
            ValidationException: Si password es None o vacío.
        """
        if not password or not isinstance(password, str):
            raise ValidationException(
                f"La contraseña a verificar debe ser una cadena no vacía, recibido: {type(password).__name__}"
            )
        
        return check_password_hash(self._password, password)

    def change_password(self, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña si la contraseña actual es correcta.

        Args:
            current_password (str): La contraseña actual en texto plano.
            new_password (str): La nueva contraseña en texto plano.

        Returns:
            bool: True si el cambio fue exitoso.
            
        Raises:
            ValidationException: Si current_password o new_password son inválidos.
            ValidationException: Si la contraseña actual no coincide.
            ValidationException: Si la nueva contraseña es igual a la actual.
        """
        if not current_password or not isinstance(current_password, str):
            raise ValidationException(
                "La contraseña actual debe ser una cadena no vacía"
            )
        
        if not new_password or not isinstance(new_password, str):
            raise ValidationException(
                "La nueva contraseña debe ser una cadena no vacía"
            )
        
        if current_password == new_password:
            raise ValidationException(
                "La nueva contraseña debe ser diferente a la contraseña actual"
            )
        
        if not self.verify_password(current_password):
            raise ValidationException(
                "La contraseña actual proporcionada es incorrecta"
            )
        
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
            "historial": getattr(self, '_historial', []),
        }
        
    def update_from_dict(self, data: dict):
        """Actualiza los atributos de la instancia a partir de un diccionario.

        Args:
            data (dict): Diccionario con los campos a actualizar. Puede incluir 'fullName', 'email', 'new_password', 'role'.
                         Para actualizar la contraseña, debe incluir 'password' (actual) y 'new_password'.

        Raises:
            ValidationException: Si data no es un diccionario.
            ValidationException: Si los valores no son válidos.
            ValidationException: Si se intenta cambiar contraseña sin proporcionar la actual.
            ValidationException: Si el rol proporcionado no es válido.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"Los datos deben ser un diccionario, recibido: {type(data).__name__}"
            )
        
        if not data:
            raise ValidationException("No hay datos para actualizar")
        
        if "fullName" in data:
            self.set_fullName(data["fullName"])
        
        if "email" in data:
            self.set_email(data["email"])
        
        if "new_password" in data:
            if "password" not in data:
                raise ValidationException(
                    "Necesitas proporcionar la contraseña actual ('password') "
                    "para actualizar a la nueva contraseña ('new_password')"
                )
            self.change_password(data["password"], data["new_password"])
        
        if "role" in data:
            try:
                role_enum = PersonRole[data["role"]]
                self.__set_role(role_enum)
            except KeyError:
                valid_roles = ", ".join([r.name for r in PersonRole])
                raise ValidationException(
                    f"Rol '{data['role']}' no válido. Roles válidos: {valid_roles}"
                )
        
        if "historial" in data:
            if not isinstance(data["historial"], list):
                raise ValidationException(
                    f"El historial debe ser una lista, recibido: {type(data['historial']).__name__}"
                )
            self._historial = data["historial"]

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
        

