from pydantic import BaseModel

class AuthLogin(BaseModel):
    email: str
    password: str
    