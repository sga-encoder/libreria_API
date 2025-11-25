from app.crud.interface import ICrud
from app.models import User

class CRUDUser(ICrud):
    def __init__(self, users: list[User]) -> None:
        self.__users = users

    def create(self, json: dict):
        print("implementando create en CRUDUser")
        # Aceptar tanto dicts como modelos Pydantic (BookCreate)
        # Preferir model_dump() (Pydantic v2), caer a dict() si no existe
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        return User.from_dict(data)
    

    def read(self, id: str):
        print("implementando read en CRUDUser")
        return id

    def read_all(self):
        print("implementando read_all en CRUDUser")
        return self.__users

    def update(self, id: str, json: dict):
        print("implementando update en CRUDUser")
        # Aceptar tanto dicts como modelos Pydantic (BookUpdate)
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        data["id"] = id
        return User.from_dict(data)

    def delete(self, id: str) -> bool:
        print("implementando delete en CRUDUser")
        return True