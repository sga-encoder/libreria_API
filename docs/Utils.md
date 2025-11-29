[⬆ Volver al inicio](#top)
# Utils
Este documento resume las utilidades del paquete `app.utils`, con firmas de
funciones, comportamiento detallado y ejemplos extraídos de los demos
locales

**Objetivo**: referencia rápida por módulo (qué hace, cómo se comporta,
métodos disponibles y ejemplos de uso). ✅

---

## FileManager 🧾

### Qué hace
`FileManager` gestiona archivos en formato JSON y CSV: leer, escribir,
anexar y eliminar. Implementa una estrategia sencilla de `append` basada en
leer, combinar en memoria y reescribir. ⚙️

### Cómo se comporta (detalle) 🔍
- Si el archivo no existe, `read()` devuelve la caché interna si existe (permite
	operar en memoria antes de escribir). 🧠
- Para JSON, siempre escribe una lista de diccionarios; convierte `dict` ->
	`[dict]`. 📝
- Para CSV, `write()` acepta `list[dict]` (filas) o `list[str]` (cabeceras).
- `append()` combina en memoria y delega a `write()` para persistir. 🔁
- En CSV, `append()` valida incompatibilidades (por ejemplo, no mezclar cabeceras
	con filas existentes). ⚠️

### Métodos / firmas (extraídos del código) 📋
- `FileManager(url: str, file_type: FileType, csv_headers: list[str] | None = None) -> None`  
	Inicializa el gestor. Si `file_type` es `CSV` y `csv_headers` se pasan, crea
	el archivo con la cabecera si no existe. 🏗️
- `read() -> dict | list[dict] | None`  
	Lee y devuelve el contenido (JSON: dict o list; CSV: list[dict]) o la caché
	interna si no existe archivo. 📥
- `write(content: dict | list[dict]) -> None`  
	Sobrescribe el archivo según el tipo (JSON o CSV). Lanza `ValueError` si el
	contenido no es válido para el formato. 💾
- `append(content: dict | list[dict]) -> dict | list[dict] | None`  
	Anexa datos usando la estrategia read+merge+write. Devuelve la caché
	actualizada (útil en tests). ➕🔁
- `delete() -> None`  
	Elimina el archivo gestionado y limpia la caché interna. 🗑️

Métodos privados útiles (no parte de la API pública):
- `__get_path() -> str` — normaliza la ruta y añade sufijo según `FileType`.
- `__read_json(file_path)` / `__read_csv(file_path)` — lecturas específicas.
- `__write_json(file_path, content)` / `__write_csv(file_path, content)` —
	escritura específica con normalizaciones y validaciones.
- `__apppend_json(...)` y `__append_csv(...)` — helpers de append. 🔧

### Ejemplo breve (JSON) 🧪
```python
from app.utils import FileManager, FileType
fm = FileManager("docs/result_demos/demo.json", FileType.JSON)
fm.write({"sample": "value"})
print(fm.read())  # -> [{'sample': 'value'}]
fm.append({"another": "entry"})
print(fm.read())  # -> [{'sample': 'value'}, {'another': 'entry'}]
```

---

## Queue 🟢

### Qué hace
`Queue` es una cola FIFO ligera sobre `collections.deque` con operaciones
comunes de encolado y desencolado. ✅

### Cómo se comporta (detalle) 🔍
- `push(item)`: añade `item` al final (tail). ➕
- `pop()`: elimina y devuelve el elemento del frente (head). Devuelve `None`
	si la cola está vacía. 📤
- `peek()`: devuelve el elemento del frente sin extraerlo; `None` si vacía. 👀
- `__iter__()` recorre los elementos en orden FIFO sin consumir la cola. 🔁
- `to_list()` devuelve una copia en forma de lista con el frente en la
	posición 0. 📋

### Métodos / firmas 📋
- `push(item: T) -> None`  
- `pop() -> Optional[T]`  
- `peek() -> Optional[T]`  
- `is_empty() -> bool`  
- `__len__() -> int`  
- `__iter__() -> Iterator[T]`  
- `to_list() -> list[T]`  
- `__repr__() -> str`

### Ejemplo (rápido) 🧪
```python
from app.utils import Queue
q = Queue()
q.push('alice')
q.push('bob')
print(q.peek())   # -> 'alice'
print(q.pop())    # -> 'alice'
print(q.to_list())# -> ['bob']
```

---

## Stack 🔵

### Qué hace
`Stack` es una pila LIFO implementada con `collections.deque`. Permite operaciones
rápidas de push/pop y soporta iteración desde el tope. 🧠

### Cómo se comporta (detalle) 🔍
- `push(item)`: añade al tope. ➕
- `pop()`: extrae y devuelve el tope; `None` si vacía. 📤
- `peek()`: devuelve el tope sin extraer. 👀
- `__iter__()` itera desde el tope hacia abajo (LIFO). 🔁
- `to_list()` devuelve una lista con el tope en primera posición. 📋

### Métodos / firmas 📋
- `push(item: T) -> None`  
- `pop() -> Optional[T]`  
- `peek() -> Optional[T]`  
- `is_empty() -> bool`  
- `__len__() -> int`  
- `__iter__() -> Iterator[T]`  
- `to_list() -> list[T]`  
- `__repr__() -> str`

### Ejemplo (rápido) 🧪
```python
from app.utils import Stack
s = Stack()
s.push('alice')
s.push('bob')
print(s.peek())  # -> 'bob'
print(s.pop())   # -> 'bob'
print(s.to_list())# -> ['alice']
```

---

## Sorting 🟡

### Qué hace
`insert_sort` implementa el algoritmo de ordenamiento por inserción
adaptado para aceptar una función `key` (como `sorted`) y la opción de
añadir un elemento adicional (`item`) que será incluido antes de ordenar.

### Cómo se comporta (detalle) 🔍
- No modifica la lista original; devuelve una nueva lista ordenada.
- Orden ascendente según la clave devuelta por `key`.
- Si `item` se pasa, se añade a la copia antes de ordenar.

### Firma
- `insert_sort(arr: list[T], key: Callable[[T], Any], item: T | None = None) -> list[T]`

### Propiedades
- Estable: preserva el orden relativo de elementos con la misma clave.
- Complejidad temporal: O(n^2) en el peor caso.

### Ejemplo (rápido) 🧪
```python
from app.utils import insert_sort

# Números
print(insert_sort([3, 1, 2], key=lambda x: x))  # -> [1, 2, 3]

# Lista de dicts por clave
items = [{'v': 2}, {'v': 1}, {'v': 3}]
print(insert_sort(items, key=lambda x: x['v']))  # -> [{'v':1}, {'v':2}, {'v':3}]

# Usando el parámetro `item`
print(insert_sort([1, 4], key=lambda x: x, item=2))  # -> [1, 2, 4]
```

---

## Search 🟣

### Qué hace
Proporciona dos algoritmos de búsqueda:

- `binary_search`: búsqueda binaria recursiva para listas **ordenadas**. Acepta una función `key` (como `sorted`) para extraer la clave de comparación de cada elemento.
- `linear_search`: búsqueda lineal secuencial que funciona sobre listas **no ordenadas** y devuelve la primera ocurrencia que coincida según la `key`.

### Cómo se comporta (detalle) 🔍

**Binary Search (búsqueda binaria):**
- Requiere que la lista esté ordenada según la misma `key` usada en la búsqueda.
- Implementación recursiva que busca en el rango [`0`, `len(arr)-1`].
- Devuelve el índice del elemento encontrado, o `-1` si no existe.
- Complejidad temporal: O(log n) en promedio.
- Lanza `IndexError` si la lista proporcionada está vacía.

**Linear Search (búsqueda lineal):**
- No requiere lista ordenada; itera de forma secuencial y devuelve el índice de la primera coincidencia.
- Devuelve `-1` si no encuentra ninguna coincidencia.
- Complejidad temporal: O(n).
- Lanza `IndexError` si la lista proporcionada está vacía.

### Firmas
- `binary_search(arr: list[T], key: Callable[[T], Any], item: T) -> int`
- `linear_search(arr: list[T], key: Callable[[T], Any], item: T) -> int`

### Ejemplo (rápido) 🧪
```python
from app.utils import binary_search
# Busqueda Binaria
print(binary_search([1,2,3,4], key=lambda x: x, item=3))  # -> 2
users = [{'id':'001'},{'id':'002'},{'id':'003'}]
print(binary_search(users, key=lambda x: x['id'], item={'id':'002'}))  # -> 1

# Búsqueda lineal
unordered = [5, 2, 8, 1, 9]
print(linear_search(unordered, key=lambda x: x, item=8))  # -> 2
```

---

## Lexicographical ID 🟤

### Qué hace
El módulo `lexicographical_id` expone `generate_id()`, que crea IDs
como cadenas con formato `{epoch_ms:013d}{suffix:04d}`. El prefijo de
timestamp en milisegundos garantiza que comparar las IDs como cadenas
respecte el orden temporal (orden lexicográfico).

### Cómo se comporta (detalle) 🔍
- El sufijo de 4 dígitos evita colisiones al generar múltiples IDs en
	rápida sucesión dentro del mismo proceso (usa un lock para seguridad
	en entornos multihilo).
- Para unicidad entre procesos use ULID/KSUID o un coordinador externo.

### Firma
- `generate_id() -> str`

### Ejemplo (rápido) 🧪
```python
from app.utils import generate_id

print(generate_id())
ids = [generate_id() for _ in range(3)]
print(sorted(ids))  # orden lexicográfico == orden temporal
```

## Ejecutar los demos ▶️

Los demos se encuentran en `docs/demo/utils/` y están pensados para ejecutarse
desde la raíz del proyecto. Ejemplos (PowerShell):

- **Ejecutar (desde la raíz del proyecto, PowerShell):**

```powershell
; python -m docs.demo.utils.demo_filemanager
; python -m docs.demo.utils.demo_queue
; python -m docs.demo.utils.demo_stack
; python -m docs.demo.utils.demo_sorting
; python -m docs.demo.utils.demo_search
; python -m docs.demo.utils.demo_lexicographical_id
```

[⬆ Volver al inicio](#top)