from typing import TYPE_CHECKING
from .person import Person
from .enums import PersonRole
from app.domain.exceptions import ValidationException

if TYPE_CHECKING:
    from .loan import Loan
    
class User(Person):
    __loans: list
    __historial: list  # Historial completo de préstamos (activos + devueltos)

    def __init__(self, fullName: str, email: str, password: str, loans: list, id: str = "00000000000000000", role: PersonRole = PersonRole.USER, password_is_hashed: bool = False, historial: list = None):
        """Inicializa un usuario con sus datos y préstamos.
        
        Args:
            fullName: Nombre completo del usuario.
            email: Email del usuario.
            password: Contraseña (plana o hasheada según password_is_hashed).
            loans: Lista de IDs de préstamos activos.
            id: ID único del usuario (por defecto genera uno nuevo).
            role: Rol del usuario (por defecto USER).
            password_is_hashed: Indica si la contraseña ya está hasheada.
            historial: Historial de préstamos (por defecto lista vacía).
            
        Raises:
            ValidationException: Si loans o historial no son listas válidas.
        """
        # Validar loans antes de llamar al constructor padre
        if loans is None:
            raise ValidationException("El parámetro 'loans' no puede ser None. Use [] para lista vacía.")
        
        if not isinstance(loans, list):
            raise ValidationException(
                f"El parámetro 'loans' debe ser una lista, recibido: {type(loans).__name__}"
            )
        
        # Validar historial
        if historial is not None and not isinstance(historial, list):
            raise ValidationException(
                f"El parámetro 'historial' debe ser una lista o None, recibido: {type(historial).__name__}"
            )
        
        # Llamar al constructor de Person (este ya valida fullName, email, password)
        super().__init__(fullName, email, password, role, id, password_is_hashed=password_is_hashed)
        
        self.__set_loans(loans)
        self.__set_historial(historial if historial is not None else [])
        
    @classmethod
    def from_dict(cls, data: dict, password_is_hashed: bool = True):
        """Crea un usuario desde un diccionario.
        
        Args:
            data: Diccionario con los datos del usuario.
            password_is_hashed: Indica si la contraseña en data ya está hasheada.
            
        Returns:
            User: Nueva instancia de usuario.
            
        Raises:
            ValidationException: Si data no es un diccionario o faltan campos obligatorios.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"El parámetro 'data' debe ser un diccionario, recibido: {type(data).__name__}"
            )
        
        # Validar campos obligatorios
        required_fields = ["fullName", "email", "password"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationException(
                f"Faltan campos obligatorios en el diccionario: {', '.join(missing_fields)}"
            )
        
        # Crear instancia
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            loans=data.get("loans", []),
            id=data.get("id"),
            role=PersonRole.USER,
            password_is_hashed=password_is_hashed,
            historial=data.get("historial", [])
        )

        
    @classmethod
    def from_search_api(cls, id: str):
        """Crea un usuario de prueba para búsquedas API.
        
        Args:
            id: ID único para el usuario.
            
        Returns:
            User: Usuario de prueba.
            
        Raises:
            ValidationException: Si id no es válido.
        """
        if not id or not isinstance(id, str):
            raise ValidationException(
                f"El ID debe ser una cadena no vacía, recibido: {type(id).__name__}"
            )
        
        return cls(
            fullName="Peppermint Butler",
            email="peppermintButler.aventure@time.cartoon",
            password="adventuretime",
            loans=[],
            id=id,
            historial=[]
        )
        
    @classmethod
    def default(cls):
        """Crea un usuario con valores por defecto para testing."""
        return cls(
            fullName="Finn",
            email="finn.adventure@time.cartoon",
            password="adventuretime",
            loans=[],
            historial=[]
        )
        
    def get_loans(self):
        """Obtiene la lista de IDs de préstamos activos."""
        return self.__loans
    
    def get_historial(self):
        """Obtiene el historial completo de préstamos del usuario."""
        return self.__historial
    
    def __set_loans(self, loans: list):
        """Establece la lista de préstamos activos.
        
        Args:
            loans: Lista de IDs de préstamos.
            
        Raises:
            ValidationException: Si loans no es una lista.
        """
        if not isinstance(loans, list):
            raise ValidationException(
                f"loans debe ser una lista, recibido: {type(loans).__name__}"
            )
        
        # Validar que todos los elementos sean strings o tengan get_id()
        for i, loan in enumerate(loans):
            if not isinstance(loan, str) and not hasattr(loan, 'get_id'):
                raise ValidationException(
                    f"Elemento {i} en loans no es válido. Debe ser string o tener método get_id()"
                )
        
        self.__loans = loans
    
    def __set_historial(self, historial: list):
        """Establece el historial de préstamos.
        
        Args:
            historial: Lista de registros históricos.
            
        Raises:
            ValidationException: Si historial no es una lista.
        """
        if not isinstance(historial, list):
            raise ValidationException(
                f"historial debe ser una lista, recibido: {type(historial).__name__}"
            )
        
        self.__historial = historial
        
    def add_loan(self, loan):
        """Agrega un préstamo activo y lo registra en el historial.
        
        Args:
            loan: Objeto Loan o ID de préstamo (string).
            
        Raises:
            ValidationException: Si loan no es válido o es None.
        """
        if loan is None:
            raise ValidationException("No se puede agregar un préstamo None")
        
        # Extraer ID del préstamo
        if isinstance(loan, str):
            loan_id = loan
        elif hasattr(loan, 'get_id'):
            loan_id = loan.get_id()
        else:
            raise ValidationException(
                f"El préstamo debe ser un string (ID) o tener método get_id(), "
                f"recibido: {type(loan).__name__}"
            )
        
        # Validar que no esté duplicado
        if loan_id in self.__loans:
            raise ValidationException(
                f"El préstamo con ID '{loan_id}' ya existe en los préstamos activos del usuario"
            )
        
        # Agregar a préstamos activos
        self.__loans.append(loan_id)
        
        # Agregar al historial
        self.__historial.append({"type": "loan", "id": loan_id})
        
    def add_to_historial(self, type: str, content: str):
        """Agrega un registro al historial sin modificar préstamos activos.
        
        Este método se usa cuando se elimina o actualiza un préstamo para
        asegurar que quede registrado en el historial antes de removerlo
        de los préstamos activos.
        
        Args:
            type: Tipo de registro ("loan", "return", "update", etc.).
            content: ID o contenido del registro.
            
        Raises:
            ValidationException: Si type o content son inválidos.
        """
        if not type or not isinstance(type, str):
            raise ValidationException(
                f"El tipo debe ser una cadena no vacía, recibido: {type(type).__name__}"
            )
        
        if not content or not isinstance(content, str):
            raise ValidationException(
                f"El contenido debe ser una cadena no vacía, recibido: {type(content).__name__}"
            )
        
        # Validar tipos permitidos
        valid_types = ["loan", "return", "update", "cancel"]
        if type not in valid_types:
            raise ValidationException(
                f"Tipo de registro inválido: '{type}'. Tipos válidos: {', '.join(valid_types)}"
            )
        
        self.__historial.append({"type": type, "id": content})
    
    def delete_loan(self, loan):
        """Remueve un préstamo activo (no lo elimina del historial).
        
        Args:
            loan: Objeto Loan o ID de préstamo (string).
            
        Raises:
            ValidationException: Si loan no es válido.
        """
        if loan is None:
            raise ValidationException("No se puede eliminar un préstamo None")
        
        # Extraer ID del préstamo
        if isinstance(loan, str):
            loan_id = loan
        elif hasattr(loan, 'get_id'):
            loan_id = loan.get_id()
        else:
            raise ValidationException(
                f"El préstamo debe ser un string (ID) o tener método get_id(), "
                f"recibido: {type(loan).__name__}"
            )
        
        # Intentar remover (no lanzar excepción si no existe, solo advertir)
        if loan_id in self.__loans:
            self.__loans.remove(loan_id)
        # El préstamo permanece en el historial para auditoría
    
    def update_from_dict(self, data: dict):
        """Actualiza los atributos del usuario a partir de un diccionario.

        Args:
            data: Diccionario con los campos a actualizar. 
                  Puede incluir 'fullName', 'email', 'new_password', 'role', 'loans', 'historial'.
                  
        Raises:
            ValidationException: Si data no es un diccionario válido.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"El parámetro 'data' debe ser un diccionario, recibido: {type(data).__name__}"
            )
        
        if not data:
            raise ValidationException("El diccionario de actualización no puede estar vacío")
        
        # Llamar al método de la clase padre para actualizar campos comunes
        super().update_from_dict(data)
        
        # Actualizar loans si está presente
        if "loans" in data:
            loans_data = data["loans"]
            if not isinstance(loans_data, list):
                raise ValidationException(
                    f"El campo 'loans' debe ser una lista, recibido: {type(loans_data).__name__}"
                )
            self.__set_loans(loans_data)
        
        # Actualizar historial si está presente
        if "historial" in data:
            historial_data = data["historial"]
            if not isinstance(historial_data, list):
                raise ValidationException(
                    f"El campo 'historial' debe ser una lista, recibido: {type(historial_data).__name__}"
                )
            self.__set_historial(historial_data)
        
    def to_dict(self):
        """Serializa el usuario a diccionario.
        
        Returns:
            dict: Diccionario con los datos del usuario donde:
                - loans contiene solo IDs de préstamos activos
                - historial contiene objetos completos de préstamos (para auditoría)
        """
        # Asegurarse de que loans solo contenga IDs (strings), no objetos Loan completos
        loan_ids = []
        for loan in self.__loans:
            try:
                if isinstance(loan, str):
                    loan_ids.append(loan)
                elif hasattr(loan, 'get_id'):
                    loan_ids.append(loan.get_id())
                else:
                    # Fallback: convertir a string
                    loan_ids.append(str(loan))
            except Exception:
                # Si hay error, omitir este préstamo
                continue
        
        # El historial debe conservar los objetos completos (dicts)
        historial_data = []
        for hist in self.__historial:
            try:
                if isinstance(hist, dict):
                    historial_data.append(hist)
                elif isinstance(hist, str):
                    historial_data.append(hist)
                elif hasattr(hist, 'to_dict'):
                    historial_data.append(hist.to_dict())
                else:
                    historial_data.append(str(hist))
            except Exception:
                # Si hay error, omitir este registro
                continue
        
        data = {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "loans": loan_ids,
            "historial": historial_data,
            "role": self._role.name,
        }
        return data

    def __str__(self):
        """Representación en string para mostrar información básica."""
        return f"User: {self._fullName} ({self._email}) - Loans: {len(self.__loans)}"

    def __repr__(self):
        """Representación para debugging con información detallada."""
        return f"User(id={self._id}, fullName={self._fullName}, loans={len(self.__loans)})"

