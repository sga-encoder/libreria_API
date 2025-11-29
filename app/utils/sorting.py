from typing import TypeVar, List, Callable, Any

T = TypeVar('T')

def insert_sort(arr: List[T], key: Callable[[T], Any], item: T = None) -> List[T]:
        """Ordena una lista usando insertion sort y devuelve una nueva lista.

        Parámetros:
        - `arr` (List[T]): Secuencia de entrada (no se modifica).
        - `key` (Callable[[T], Any]): Función que extrae la clave de comparación
            para cada elemento (similar al argumento `key` de `sorted`).
        - `item` (T, opcional): Si se proporciona, se añade a la copia de la
            lista antes de ordenar.

        Retorna:
        - List[T]: Una nueva lista con los elementos ordenados en orden
            ascendente según la clave proporcionada.

        Propiedades:
        - Estable (preserva el orden relativo de elementos con claves iguales).
        - Complejidad temporal: O(n^2) en el peor caso.
        - No muta la lista de entrada; trabaja sobre una copia.

        Ejemplo:
                >> insert_sort([{'v':2},{'v':1}], key=lambda x: x['v'])
                [{'v':1}, {'v':2}]
        """
        result = list(arr)
        if item is not None:
                result.append(item)

        for i in range(1, len(result)):
                current = result[i]
                current_key = key(current)
                j = i - 1

                while j >= 0 and key(result[j]) > current_key:
                        result[j + 1] = result[j]
                        j -= 1

                result[j + 1] = current

        return result