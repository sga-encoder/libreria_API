[⬆ Volver al inicio](#top)
# CRUD
Resumen del módulo `app.crud`: interfaz genérica `ICrud` y las
implementaciones concretas (`CRUDBook`, `CRUDLoan`, `CRUDUser`). Incluye
firmas, comportamiento actual y recomendaciones para robustecer la capa CRUD.

**Objetivo**: referencia rápida para desarrolladores sobre cómo funcionan las
operaciones CRUD en memoria y qué revisar antes de mover lógica a producción.

> **Nota importante**: Las implementaciones actuales de `CRUDBook`,
> `CRUDLoan` y `CRUDUser` son ejemplos y stubs creados únicamente para
> establecer la estructura inicial del proyecto y facilitar el desarrollo
> temprano. No están pensadas para uso en producción: contienen comportamientos
> simulados (prints, retornos estáticos) y requieren las correcciones y
> validaciones  antes de ser usadas en un entorno real.


---

## Interfaz `ICrud` 🧩

### Qué hace
`ICrud` define la API que deben implementar las clases CRUD: `create`,
`read`, `read_all`, `update` y `delete`. Está parametrizada con un tipo
genérico `T` para indicar la entidad que maneja cada implementación.

### Firma (resumen)
- `create(json: dict) -> T`
- `read(id: str) -> Optional[T]`
- `read_all() -> List[T]`
- `update(id: str, json: dict) -> Optional[T]`
- `delete(id: str) -> bool`

> Nota: la interfaz documenta el comportamiento esperado; las
implementaciones actuales en `app.crud` son simples stubs orientados a demo.

---

## Implementaciones actuales

Las implementaciones concretas se encuentran en `app/crud/`:
- `CRUDBook` — maneja libros
- `CRUDLoan` — maneja préstamos
- `CRUDUser` — maneja usuarios

Todas las clases siguen la firma de `ICrud` pero, en el código actual, su
comportamiento es mayormente de demo: imprimen mensajes y devuelven valores
simulados (`to_dict` aplicado a dicts, `True`, o simplemente el id recibido).

### CRUDBook
Estado actual tras la última actualización del módulo `CRUDBook`:

- Constructor: ahora recibe una URL de archivo y usa `FileManager(url, FileType.JSON)`; llama a `load()` para poder inicializar el inventario.
- `load()`: lee todos los libros desde el archivo (vía `FileManager`), crea objetos `Book` y:
  - carga el inventario en `Library` (`Library.set_inventary(...)`),
  - crea y guarda un inventario ordenado usando `insert_sort(...)` por `book.get_id_IBSN()`.
- `create(json)`: acepta dicts o modelos Pydantic, crea un `Book` con `Book.from_dict`, añade la entrada al archivo (`FileManager.append(...)`), actualiza el inventario en `Library` y recalcula el inventario ordenado con `insert_sort`.
- `read_all()`: implementado; lee todos los libros del archivo y los devuelve como `Stack[Book]`.

Pendientes (stubs actualmente)
- `read(id)`: método presente pero no implementado — actualmente imprime y retorna el id.
- `update(id, json)`: método presente pero no implementado — actualmente transforma el payload y construye un `Book` temporal sin persistir ni actualizar estructuras.
- `delete(id)`: método presente pero no implementado — actualmente imprime y retorna `True`.

Motivo de la falta de implementación completa
- Estas operaciones (`read`, `update`, `delete`) requieren localizar un libro concreto dentro del inventario persistido en archivo o en la estructura `Stack[Book]`. Falta por integrar el algoritmo de búsqueda lineal solicitado (búsqueda por `id_IBSN`) que permita:
  - localizar la posición/objeto para lectura,
  - modificar y persistir cambios (update),
  - eliminar la entrada del archivo y del inventario (delete).

Recomendación breve
- Implementar una función `linear_search(collection, key, target) -> Optional[index/object]` en el módulo de utilidades (por ejemplo `app.utils` o `algorithms/search.py`) y usarla desde `CRUDBook.read/update/delete` para localizar el libro por `id_IBSN`.
- Tras localizar el registro:
  - `read` debe devolver el `Book` encontrado o `None`,
  - `update` debe aplicar cambios, persistir el archivo y actualizar `Library` y el inventario ordenado,
  - `delete` debe eliminar del archivo y actualizar `Library` y el inventario ordenado.


### CRUDLoan
- Constructor: `CRUDLoan(loansRecords: list[Loan], resevacionQueue)`
- Comportamiento actual similar: métodos imprimen, `create`/`update` llaman
  `Loan.to_dict(json)` y `read_all()` devuelve la lista interna.

### CRUDUser
- Constructor: `CRUDUser(users: list[User])`
- Comportamiento: stubs que imprimen y retornan `User.to_dict(json)` o listas
  internas.
---

```
[⬆ Volver al inicio](#top)
