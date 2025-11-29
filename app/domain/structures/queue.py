"""Utilidad: implementación simple de una cola FIFO.

Proporciona una clase genérica `Queue` con operaciones O(1) para
`enqueue`, `dequeue` y `peek`, implementada sobre `collections.deque`.
Incluye iteración en orden FIFO y conversión a lista con el elemento
frontal en la primera posición.
"""

from collections import deque
from typing import Generic, TypeVar, Optional, Iterator

T = TypeVar('T')


class Queue(Generic[T]):
    """Cola FIFO genérica.

    Ejemplo de uso:
        q = Queue[int]()
        q.enqueue(1)
        q.enqueue(2)
        front = q.peek()   # 1
        x = q.dequeue()    # 1

    Métodos principales:
        - push(item): añade un elemento al final.
        - pop(): elimina y devuelve el elemento del frente; devuelve None si está vacía.
        - peek(): devuelve el elemento del frente sin extraerlo; None si está vacía.
        - is_empty(): True si la cola está vacía.
        - __len__(): número de elementos.
        - __iter__(): itera en orden FIFO.
        - to_list(): devuelve una lista con el frontal en la posición 0.
    """

    _queue: deque[T]
    
    def __init__(self) -> None:
        """Inicializa una cola vacía."""
        self._queue = deque()

    def push(self, item: T) -> None:
        """Añade `item` al final de la cola.

        Args:
            item: elemento a encolar.
        """
        self._queue.append(item)

    def pop(self) -> Optional[T]:
        """Elimina y devuelve el elemento del frente.

        Returns:
            El elemento eliminado, o None si la cola está vacía.
        """
        return self._queue.popleft() if self._queue else None

    def peek(self) -> Optional[T]:
        """Devuelve el elemento del frente sin eliminarlo.

        Returns:
            El elemento en el frente, o None si la cola está vacía.
        """
        return self._queue[0] if self._queue else None

    def is_empty(self) -> bool:
        """Indica si la cola está vacía.

        Returns:
            True si no contiene elementos.
        """
        return not self._queue

    def __len__(self) -> int:
        """Devuelve el número de elementos en la cola."""
        return len(self._queue)

    def __iter__(self) -> Iterator[T]:
        """Iterador que recorre los elementos en orden FIFO.

        Permite iterar con: for x in queue: ...
        """
        return iter(self._queue)
    
    def __repr__(self):
        """Devuelve una representación de la cola."""
        return f"Queue({list(self._queue)})"

    def to_list(self) -> list[T]:
        """Devuelve una lista con el elemento frontal en la posición 0.

        La lista es una copia de los elementos actuales de la cola.
        """
        return list(self._queue)