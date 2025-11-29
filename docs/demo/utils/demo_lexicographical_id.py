
# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_lexicographical_id.py`).
from pathlib import Path
import sys
import time

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demostración del generador de IDs lexicográficos (`generate_id`).

Genera una serie de IDs y muestra que el orden lexicográfico de las cadenas
coincide con el orden temporal (timestamp + sufijo).

Se recomienda ejecutar desde la raíz del proyecto con:
    python -m docs.demo.utils.demo_lexicographical_id
"""

from app.utils import generate_id


def demo_generate_sequential(n=5, delay=0.001):
    """Genera `n` IDs en rápida sucesión mostrando sufijo incremental."""
    ids = []
    for _ in range(n):
        ids.append(generate_id())
        time.sleep(delay)
    print("Generados:")
    for i in ids:
        print(" -", i)


def demo_lexicographic_order():
    """Comprueba que ordenar las cadenas mantiene el orden temporal."""
    ids = [generate_id() for _ in range(3)]
    # pequeña espera para asegurar cambio de timestamp en caso necesario
    time.sleep(0.01)
    ids += [generate_id() for _ in range(2)]

    print("Generados:", ids)
    print("Orden lexicográfico ->", sorted(ids))


if __name__ == "__main__":
    demo_generate_sequential()
    print()
    demo_lexicographic_order()
