"""Utilidad: implementación simple de una pila LIFO.

Proporciona una clase genérica Stack con operaciones O(1) para push, pop y peek,
implementada sobre collections.deque. Incluye iteración desde el tope hacia abajo
y conversión a lista con el elemento superior en la primera posición.
"""
from collections import deque
from typing import Generic, TypeVar, Optional, Iterator

T = TypeVar('T')

class Stack(Generic[T]):
    """Pila LIFO genérica.

    Ejemplo de uso:
        s = Stack[int]()
        s.push(1)
        s.push(2)
        top = s.peek()  # 2
        x = s.pop()     # 2

    Métodos principales:
        - push(item): añade un elemento al tope.
        - pop(): elimina y devuelve el elemento del tope; devuelve None si está vacía.
        - peek(): devuelve el elemento del tope sin extraerlo; None si está vacía.
        - is_empty(): True si la pila está vacía.
        - __len__(): número de elementos.
        - __iter__(): itera desde el tope hacia abajo.
        - to_list(): devuelve una lista con el tope en la posición 0.
    """
    _stack: deque[T]
    
    def __init__(self) -> None:
        """Inicializa una pila vacía."""
        self._stack = deque()

    def push(self, item: T) -> None:
        """Añade `item` al tope de la pila.

        Args:
            item: valor a apilar.
        """
        self._stack.append(item)

    def pop(self) -> Optional[T]:
        """Elimina y devuelve el elemento del tope.

        Returns:
            El elemento eliminado, o None si la pila está vacía.
        """
        return self._stack.pop() if self._stack else None

    def peek(self) -> Optional[T]:
        """Devuelve el elemento del tope sin eliminarlo.

        Returns:
            El elemento en el tope, o None si la pila está vacía.
        """
        return self._stack[-1] if self._stack else None

    def is_empty(self) -> bool:
        """Indica si la pila está vacía.

        Returns:
            True si no contiene elementos.
        """
        return not self._stack

    def __len__(self) -> int:
        """Devuelve el número de elementos en la pila."""
        return len(self._stack)

    def __iter__(self) -> Iterator[T]:
        """Iterador que recorre los elementos en orden LIFO.

        Permite iterar con: for x in stack: ...
        """
        # itera desde el tope (último añadido) hacia abajo
        return iter(reversed(self._stack))
    
    def __repr__(self):
        """Devuelve una representación de la pila."""
        return f"Stack({list(self._stack)})"
    
    def __str__(self) -> str:
        """Representación con cada elemento en su propia línea (tope primero)."""
        if not self._stack:
            return "Stack()"
        return "Stack:(\n" + "\n".join(str(x) for x in reversed(self._stack))

    def to_list(self) -> list[T]:
        """Devuelve una lista con el tope en la posición 0.

        La lista es una copia de los elementos actuales de la pila.
        """
        # lista con top primero
        return list(reversed(self._stack))