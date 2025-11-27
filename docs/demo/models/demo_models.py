# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/models/demo_models.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))
"""Demo que instancia los modelos de `app.models` y muestra `to_dict()`.

Ejecutar desde la raíz del proyecto:

PowerShell:
; python -m docs.demo.models.demo_models

"""
from datetime import datetime, timezone

from app.models import Person, User, Book, Loan
from app.models.enums.book_gender import BookGender
from app.models.enums.person_role import PersonRole


def run_demo():
    print("--- Person ---")
    p = Person(fullName='Alice', email='alice@example.com', password='pw', role=PersonRole.USER)
    print(p)
    print(p.to_dict())

    print("\n--- User ---")
    u = User(fullName='Bob', email='bob@example.com', password='pw', loans=[])
    u2 = User( fullName='Bob', email='bob@example.com', password='pw', loans=[])
    print(f"u == u2: {u == u2}")
    u.add_loan({'id': 'loan-1'})
    print(u)
    print(u.to_dict())

    print("\n--- Book ---")
    b = Book(id_IBSN='978-1', title='Ejemplo', author='Autor', gender=BookGender.AVENTURA, weight=0.5, price=9.99)
    print(b)
    print(b.to_dict())

    print("\n--- Loan ---")
    loan = Loan( user=u, book=b, loanDate=datetime.now(timezone.utc))
    print(loan)
    print(loan.to_dict())


if __name__ == '__main__':
    run_demo()
