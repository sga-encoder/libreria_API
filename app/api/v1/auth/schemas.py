from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Schema para solicitud de login."""
    email: str
    password: str

class UserIn(BaseModel):
    """Schema para entrada de usuario."""
    fullName: str
    email: str
    password: str
    
class TokenResponse(BaseModel):
    """Schema para respuesta de token."""
    access_token: str
    token_type: str
