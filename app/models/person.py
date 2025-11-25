from .enums import PersonRole

class Person:
    _id: str
    _fullName: str
    _email: str
    _password: str
    _role: PersonRole
    
    def __init__(self,  fullName: str, email: str, password: str, role: PersonRole):
        self.__set_id('000000')
        self.set_fullName(fullName)
        self.set_email(email)
        self.set_password(password)
        self.__set_role(role)
        
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            fullName=data["fullName"],
            email=data["email"],
            password=data["password"],
            role=PersonRole[data["role"]]
        )
        
    def get_id(self):
        return self._id
    def get_fullName(self):
        return self._fullName
    def get_email(self):
        return self._email
    def get_password(self):
        return self._password
    def get_role(self):
        return self._role
    
    def __set_id(self, id: str):
        self._id = id
    def set_fullName(self, fullName: str):
        self._fullName = fullName
    def set_email(self, email: str):
        self._email = email
    def set_password(self, password: str):
        self._password = password
    def __set_role(self, role: PersonRole):
        self._role = role 
           
    def to_dict(self):
        return {
            "id": self._id,
            "fullName": self._fullName,
            "email": self._email,
            "password": self._password,
            "role": self._role.name
        }
        
    def __str__(self):
        """Sobreescribe la representación en string"""
        return f"Person: {self._fullName} ({self._email}) - Role: {self._role.name}"
    
    def __repr__(self):
        """Sobreescribe la representación para debugging"""
        return f"Person(id={self._id}, fullName={self._fullName}, role={self._role.name})"
        

