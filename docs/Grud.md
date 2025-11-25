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
- Constructor: `CRUDBook(books: list[Book], orderBooks: list[Book])`
- Comportamiento actual:
  - `create(json)` — imprime y devuelve `Book.to_dict(json)` (posible bug:
    `Book.to_dict` es un método de instancia, no un factory estático).
  - `read(id)` — imprime y devuelve `id`.
  - `read_all()` — devuelve la lista interna `__books`.
  - `update(id, json)` — añade `id` al json y devuelve `Book.to_dict(json)`.
  - `delete(id)` — imprime y devuelve `True`.

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
