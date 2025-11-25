# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/schemas/demo_schemas.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))
"""Demo que instancia y muestra los schemas en `app.schemas`.

Ejecutar desde la raíz del proyecto:

PowerShell:
; python -m docs.demo.schemas.demo_schemas

"""
from datetime import datetime, timezone

from app.schemas import AuthLogin
from app.schemas import BookCreate, BookUpdate
from app.schemas import LoanCreate, LoanUpdate
from app.schemas import UserCreate, UserUpdate
from app.models.enums import BookGender


def run_demo():
    print("--- AuthLogin ---")
    a = AuthLogin(email='user@example.com', password='s3cret')
    print(a.model_dump())
    print(a.model_dump_json())

    print("\n--- BookCreate / BookUpdate ---")
    b = BookCreate(
        id='978-1', title='Ejemplo', author='Autor',
        gender=BookGender.AVENTURA, weight=0.5, price=9.99, is_borrowed=False
    )
    bu = BookUpdate(title='Nuevo título')
    print(b.model_dump())
    print(b.model_dump_json())
    print(bu.model_dump(exclude_unset=True))

    print("\n--- LoanCreate / LoanUpdate ---")
    l = LoanCreate(user_id='user-1', book_id='978-1', loanDate=datetime.now(timezone.utc))
    lu = LoanUpdate(loanDate=datetime(2025, 12, 1))
    print(l.model_dump())
    print(lu.model_dump(exclude_unset=True))

    print("\n--- UserCreate / UserUpdate ---")
    u = UserCreate(fullName='Alice', email='alice@example.com', password='secret')
    uu = UserUpdate(email='alice@newdomain.com')
    print(u.model_dump())
    print(u.model_dump_json())
    print(uu.model_dump(exclude_unset=True))


if __name__ == '__main__':
    run_demo()
