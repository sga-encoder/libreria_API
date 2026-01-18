from typing import TypeVar, List, Callable, Any, Union

T = TypeVar('T')

def linear_search(arr: List[T], key: Callable[[T], Any], item: Union[T, Any]) -> int:
    """Realiza una búsqueda lineal en `arr` usando `key`.

    Parámetros:
    - arr (List[T]): Lista de elementos donde se realizará la búsqueda.
      No necesita estar ordenada (a diferencia de búsqueda binaria).
    - key (Callable[[T], Any]): Función que, dada una entrada de tipo `T`,
      devuelve una clave comparable (por ejemplo, un número o string) usada
      para comparar elementos.
    - item (Union[T, Any]): Puede ser:
      1) Un elemento del mismo tipo que `arr` (se aplicará `key(item)` para obtener el valor)
      2) Un valor directo a buscar (string, int, etc.) que se comparará directamente
      
      La función detecta automáticamente si `item` es un valor directo o necesita
      aplicar `key()` intentando aplicar `key(item)` primero.

    Retorna:
    - int: Índice de la primera ocurrencia del elemento encontrado dentro de `arr`.
      Si el elemento no se encuentra, se devuelve `-1`.

    Excepciones:
    - IndexError: Si `arr` es una lista vacía, se lanza `IndexError`.
    
    Ejemplos:
    >>> # Búsqueda en lista de diccionarios con valor directo
    >>> loans = [{"id": "001"}, {"id": "002"}]
    >>> linear_search(loans, key=lambda x: x["id"], item="002")  # item es valor directo
    1
    
    >>> # Búsqueda con objeto completo
    >>> linear_search(loans, key=lambda x: x["id"], item={"id": "002"})  # item es dict
    1
    """

    if arr is None or len(arr) == 0:
        raise IndexError("La lista proporcionada está vacía.")

    # Intentar aplicar key() al item para obtener el valor a buscar
    # Si falla (porque item ya es un valor directo), usar item directamente
    try:
        target_key = key(item)
    except (KeyError, TypeError, AttributeError):
        # item es un valor directo (string, int, etc.), no un objeto complejo
        target_key = item

    for index, element in enumerate(arr):
        if key(element) == target_key:
            return index

    return -1