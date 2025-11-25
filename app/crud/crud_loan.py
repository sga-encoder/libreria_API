from app.crud.interface import ICrud
from app.models import Loan
class CRUDLoan(ICrud[Loan]):
    def __init__(self, loansRecords: list[Loan], resevacionQueue) -> None:
        self.__loans = loansRecords
        self.__resevacionQueue = resevacionQueue
        
    def create(self, json: dict) -> Loan:
        print("implementando create en CRUDLoan")
        # Aceptar tanto dicts como modelos Pydantic (BookCreate)
        # Preferir model_dump() (Pydantic v2), caer a dict() si no existe
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        return Loan.from_dict(data)
    
    def read(self, id: str):
        print("implementando read en CRUDLoan")
        return id
    
    def read_all(self):
        print("implementando read_all en CRUDLoan")
        return self.__loans
    
    def update(self, id: str, json: dict) -> Loan:
        print("implementando update en CRUDLoan")
        # Aceptar tanto dicts como modelos Pydantic (BookCreate)
        if hasattr(json, "model_dump"):
            data = json.model_dump()
        elif hasattr(json, "dict"):
            data = json.dict()
        else:
            data = json
        data["id"] = id
        return Loan.from_dict(data)
    
    def delete(self, id: str) -> bool:
        print("implementando delete en CRUDLoan")
        return True