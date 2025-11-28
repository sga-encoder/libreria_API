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
from app.models.enums.person_role import PersonRole


def run_demo():
    print("--- Person ---")
    p1 = Person(fullName='Alice', email='alice@example.com', password='pw', role=PersonRole.USER)
    p2 = Person.from_dict(p1.to_dict())
    print("p1", p1)
    print('p2',p2 )
    print('p1',p1.to_dict())
    print('p2',p2.to_dict())
    print(f"p1 == p2: {p1 == p2}")
    

    print("\n--- User ---")
    u1 = User(fullName='Bob', email='bob@example.com', password='pw', loans=[])   
    print("u1", u1.to_dict())
     
    u2 = User.from_dict(u1.to_dict())
    
    print(f"u1 == u2: {u1 == u2}")
    
    print("u1", u1)
    print("u2", u2)
    print("u1", u1.to_dict())
    print("u2", u2.to_dict())

    print("\n--- Book ---")
    b = Book(id_IBSN='978-1', title='Ejemplo', author='Autor', gender='AVENTURA', weight=0.5, price=9.99)
    print(b)
    print(b.to_dict())

    print("\n--- Loan ---")
    loan = Loan( user=u1, book=b, loanDate=datetime.now(timezone.utc))
    print(loan)
    print(loan.to_dict())


if __name__ == '__main__':
    run_demo()
