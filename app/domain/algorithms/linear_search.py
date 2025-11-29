from typing import TypeVar, List, Callable, Any

T = TypeVar('T')

def linear_search(arr: List[T], key: Callable[[T], Any], item: T) -> int:
    """Realiza una búsqueda lineal en `arr` usando `key`.

    Parámetros:
    - arr (List[T]): Lista de elementos donde se realizará la búsqueda.
      No necesita estar ordenada (a diferencia de búsqueda binaria).
    - key (Callable[[T], Any]): Función que, dada una entrada de tipo `T`,
      devuelve una clave comparable (por ejemplo, un número o string) usada
      para comparar elementos.
    - item (T): Elemento a buscar. No debe ser `None`; si se pasa `None`, la
      llamada a `key(item)` puede provocar una excepción en tiempo de ejecución.

    Retorna:
    - int: Índice de la primera ocurrencia del elemento encontrado dentro de `arr`.
      Si el elemento no se encuentra, se devuelve `-1`.

    Excepciones:
    - IndexError: Si `arr` es una lista vacía, se lanza `IndexError`.
    """

    if arr is None or len(arr) == 0:
        raise IndexError("La lista proporcionada está vacía.")

    target_key = key(item)

    for index, element in enumerate(arr):
        if key(element) == target_key:
            return index

    return -1