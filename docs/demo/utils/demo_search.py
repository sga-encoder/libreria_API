# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_search.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demostración del comportamiento de `binary_search`.

Este módulo muestra ejemplos sencillos de búsqueda binaria sobre listas
ordenadas de números y de diccionarios (por una clave).

Se recomienda ejecutar desde la raíz del proyecto con:
    python -m docs.demo.utils.demo_search
"""

from app.utils import binary_search


def demo_numbers():
    """Busca un número en una lista ordenada de enteros."""
    arr = [1, 2, 3, 4, 5, 6]
    item = 4
    print("Array:", arr)
    idx = binary_search(arr, key=lambda x: x, item=item)
    print(f"Buscando {item} -> índice: {idx}")


def demo_dicts():
    """Busca por clave en una lista ordenada de diccionarios."""
    users = [
        {"id": "001", "name": "alice"},
        {"id": "002", "name": "bob"},
        {"id": "003", "name": "carol"},
    ]
    # La lista debe estar ordenada según la misma key que usamos en la búsqueda
    target = {"id": "002", "name": "bob"}
    print("Users:", users)
    idx = binary_search(users, key=lambda x: x["id"], item=target)
    print(f"Buscando id={target['id']} -> índice: {idx}")


def demo_not_found():
    """Ejemplo cuando el elemento no se encuentra (devuelve -1)."""
    arr = [10, 20, 30]
    print("Array:", arr)
    print("Buscando 25 ->", binary_search(arr, key=lambda x: x, item=25))


if __name__ == "__main__":
    demo_numbers()
    print()
    demo_dicts()
    print()
    demo_not_found()