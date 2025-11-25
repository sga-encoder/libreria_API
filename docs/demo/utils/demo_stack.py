# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_stack.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demostración del comportamiento de `Stack`.

Este módulo contiene dos demos pequeñas:
- `demo_basic()`: muestra `push`, `peek`, `pop`, `len` y `is_empty`.
- `demo_iteration()`: muestra la iteración LIFO y cómo vaciar la pila.

Se recomienda ejecutar desde la raíz del proyecto con:
    python -m docs.demo.utils.demo_stack

Los prints muestran el estado relevante tras cada operación.
"""


from app.utils import Stack


def demo_basic():
    """Operaciones básicas: push, peek, pop, len, is_empty, to_list."""
    s = Stack()

    print("Estado inicial:", s.to_list(), "is_empty:", s.is_empty())

    # Apilar varios elementos
    s.push("alice")
    s.push("bob")
    s.push("carol")
    print("Tras push: ", s.to_list)

    # Consultar el tope sin extraer
    print("peek() ->", s.peek())

    # Extraer un elemento
    print("pop() ->", s.pop())
    print("Tras pop:", s)

    # Comprobar longitud y estado
    print("len ->", len(s))
    print("is_empty ->", s.is_empty())


def demo_iteration():
    """Demuestra iteración LIFO y vaciado con pop."""
    s = Stack()
    for name in ("dave", "eve", "frank"):
        s.push(name)

    print("Pila inicial:", s)

    # Iteración (no consume la pila)
    print("Iterando (tope -> abajo):")
    for item in s:
        print(" -", item)

    # Vaciar la pila con pop hasta que esté vacía
    print("Vaciando con pop():")
    while not s.is_empty():
        print("pop ->", s.pop())

    print("Estado final:", s.to_list(), "is_empty:", s.is_empty())


if __name__ == "__main__":
    demo_basic()
    print()
    demo_iteration()
