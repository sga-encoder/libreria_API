from .person import Person
from .enums import PersonRole

class User(Person):
    __loans: list
    __historial: list  # Historial completo de préstamos (activos + devueltos)

    def __init__(self, fullName: str, email: str, password: str, loans: list, id: str = "00000000000000000", role: PersonRole = PersonRole.USER, password_is_hashed: bool = False, historial: list = None):
        # Aceptamos `role` por compatibilidad con llamadas heredadas
        # (p. ej. si se invoca `Person.from_dict` con `cls=User`).
        super().__init__(fullName, email, password, role, id, password_is_hashed=password_is_hashed)
        self.__set_loans(loans)
        self.__set_historial(historial if historial is not None else [])
        
    @classmethod
    def from_dict(cls, data: dict, password_is_hashed: bool = True):
        # Manejar role si viene en el diccionario (puede ser nombre o PersonRole)
        
        # Crear instancia usando el constructor de Person directamente
        # para aprovechar el parámetro password_is_hashed
        return cls(
            fullName=data.get("fullName"),
            email=data.get("email"),
            password=data.get("password"),
            loans=data.get("loans", []),
            id=data.get("id"),
            role=PersonRole.USER,
            password_is_hashed=password_is_hashed,  # ← La contraseña del JSON ya está hasheada
            historial=data.get("historial", [])
        )

        
    @classmethod
    def from_search_api(cls, id: str):
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
        return cls(
            fullName="Finn",
            email="finn.adventure@time.cartoon",
            password="adventuretime",
            loans=[],
            historial=[]
        )
        
    def get_loans(self):
        return self.__loans
    
    def get_historial(self):
        """Obtiene el historial completo de préstamos del usuario."""
        return self.__historial
    
    def __set_loans(self, loans: list):
        self.__loans = loans
    
    def __set_historial(self, historial: list):
        """Establece el historial de préstamos."""
        self.__historial = historial
        
    def add_loan(self, loan):
        """Agrega un préstamo activo y lo registra en el historial.
        
        Args:
            loan: Puede ser un objeto Loan (se guardará completo en historial y solo ID en loans)
                  o un ID de préstamo (string).
        """
        loan_id = loan.get_id() if hasattr(loan, 'get_id') else str(loan)
        self.__loans.append(loan_id)
        
        # Agregar al historial como objeto completo si no está ya
        existing_ids = [h.get('id') if isinstance(h, dict) else h for h in self.__historial]
        if loan_id not in existing_ids:
            loan_dict = loan.to_dict() if hasattr(loan, 'to_dict') else {'id': str(loan)}
            self.__historial.append(loan_dict)
        
    def add_to_historial(self, loan):
        """Agrega un préstamo completo al historial sin modificar los préstamos activos.
        
        Este método se usa cuando se elimina o actualiza un préstamo para
        asegurar que quede registrado en el historial antes de removerlo
        de los préstamos activos. Guarda el objeto completo serializado para
        mantener un registro histórico completo (usuario, libro, fecha, etc.).
        
        Args:
            loan: Objeto Loan a agregar al historial.
        """
        # Convertir el loan a diccionario para guardarlo en el historial
        loan_dict = loan.to_dict() if hasattr(loan, 'to_dict') else loan
        loan_id = loan.get_id() if hasattr(loan, 'get_id') else (loan_dict.get('id') if isinstance(loan_dict, dict) else str(loan))
        
        # Verificar si ya existe en el historial (comparando por ID)
        existing_ids = [h.get('id') if isinstance(h, dict) else h for h in self.__historial]
        if loan_id not in existing_ids:
            self.__historial.append(loan_dict)
    
    def remove_loan(self, loan):
        """Remueve un préstamo activo (no lo elimina del historial)."""
        loan_id = loan.get_id() if hasattr(loan, 'get_id') else str(loan)
        if loan_id in self.__loans:
            self.__loans.remove(loan_id)
        # El préstamo permanece en el historial
    
    def update_from_dict(self, data: dict):
        """Actualiza los atributos del usuario a partir de un diccionario.

        Args:
            data (dict): Diccionario con los campos a actualizar. 
                         Puede incluir 'fullName', 'email', 'new_password', 'role', 'loans', 'historial'.
        """
        # Llamar al método de la clase padre para actualizar campos comunes
        super().update_from_dict(data)
        
        # Actualizar el campo específico de User: loans
        if "loans" in data:
            self.__set_loans(data["loans"])
        
        # Actualizar el historial si está presente
        if "historial" in data:
            self.__set_historial(data["historial"])
        
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
            if isinstance(loan, str):
                loan_ids.append(loan)
            elif hasattr(loan, 'get_id'):
                loan_ids.append(loan.get_id())
            else:
                loan_ids.append(str(loan))
        
        # El historial debe conservar los objetos completos (dicts)
        # para mantener registro histórico de usuario, libro y fecha
        historial_data = []
        for hist in self.__historial:
            if isinstance(hist, dict):
                # Ya es un diccionario, conservarlo
                historial_data.append(hist)
            elif isinstance(hist, str):
                # Es un ID antiguo, mantenerlo como está por compatibilidad
                historial_data.append(hist)
            elif hasattr(hist, 'to_dict'):
                # Es un objeto Loan, convertirlo a dict
                historial_data.append(hist.to_dict())
            else:
                # Fallback: guardar como string
                historial_data.append(str(hist))
        
        data = {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "loans": loan_ids,
            "historial": historial_data,  # Objetos completos, no solo IDs
            "role": self._role.name,
        }
        return data

    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"User: {self._fullName} ({self._email}) - Loans: {len(self.__loans)}"

    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"User(id={self._id}, fullName={self._fullName}, loans={len(self.__loans)})"
            
            