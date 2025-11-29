# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_sorting.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demostración del comportamiento de `insert_sort`.

Este módulo contiene tres demos pequeñas:
- `demo_numbers()`: ordena una lista de números.
- `demo_dicts()`: ordena una lista de dicts con una clave específica.
- `demo_with_item()`: muestra el uso del parámetro opcional `item`.

Se recomienda ejecutar desde la raíz del proyecto con:
    python -m docs.demo.utils.demo_sorting

Los prints muestran los resultados de las operaciones.
"""


from app.utils import insert_sort


def demo_numbers():
    """Ordena una lista simple de enteros."""
    data = [5, 1, 4, 3, 2]
    print("Original:", data)
    print("Ordenado:", insert_sort(data, key=lambda x: x))


def demo_dicts():
    """Ordena una lista de diccionarios usando una clave."""
    items = [
        {"name": "alice", "score": 30},
        {"name": "bob", "score": 25},
        {"name": "carol", "score": 40},
    ]
    print("Original:", items)
    sorted_items = insert_sort(items, key=lambda x: x["score"])
    print("Ordenado por 'score':", sorted_items)


def demo_with_item():
    """Muestra que `item` se puede añadir y ordenar junto con la lista."""
    base = [1, 4, 5]
    print("Base:", base)
    print("Con item=3 ->", insert_sort(base, key=lambda x: x, item=3))


if __name__ == "__main__":
    demo_numbers()
    print()
    demo_dicts()
    print()
    demo_with_item()
