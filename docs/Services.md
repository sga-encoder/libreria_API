[⬆ Volver al inicio](#top)
# Services
Este documento resume los servicios del paquete `app.services`, con firmas de
funciones, comportamiento detallado y ejemplos de uso centrados en la clase
estática `Library`.

**Objetivo**: referencia rápida por módulo (qué hace, cómo se comporta,
métodos disponibles y ejemplos de uso). ✅

---

## Library 📚

### Qué hace
`Library` actúa como una clase estática que expone las colecciones y utilidades
principales de la biblioteca en memoria: inventario (pila), cola de reservas,
usuarios, registros de préstamos y estantería. No está pensada para
instanciarse; todos sus atributos y métodos son de clase y se inicializan al
importar el módulo. ✅

### Cómo se comporta (detalle) 🔍
- Es una clase estática: intentar instanciarla lanza `TypeError`.
- Inicializa sus estructuras internas la primera vez que se accede (método
	`initialize()`), y el módulo invoca `Library.initialize()` al importarse para
	preservar comportamiento previo.
- Mantiene varias colecciones en memoria:
	- `__inventary`: `Stack[Book]` — pila que representa el inventario.
	- `__order_inventary`: `list[Book]` — lista con orden explícito de inventario.
	- `__resevationsQueue`: `Queue[tuple[User, Book]]` — cola de reservas.
	- `__user`: `list[User]` — usuarios de la librería.
	- `__loanRecords`: `list[Loan]` — registros de préstamos.
	- `__bookcase`: `list[Book]` — estantería / colección persistente en memoria.
- Proporciona getters y setters de clase para acceder o reemplazar estas
	colecciones desde otras partes de la aplicación.

### Métodos / firmas (extraídos del código) 📋
- `initialize() -> None`  : Inicializa las estructuras internas si no existen.
- `get_inventary() -> Stack[Book]` : Devuelve la `Stack` del inventario.
- `get_order_inventary() -> list[Book]` : Devuelve la lista de inventario ordenado.
- `get_reservationsQueue() -> Queue[tuple[User, Book]]` : Devuelve la cola de reservas.
- `get_user() -> list[User]` : Devuelve la lista de usuarios.
- `get_loanRecords() -> list[Loan]` : Devuelve los registros de préstamos.
- `get_bookcase() -> list[Book]` : Devuelve la estantería/colección.

Setters:
- `set_inventary(inventary: Stack[Book]) -> None`
- `set_order_inventary(order_inventary: list[Book]) -> None`
- `set_reservationsQueue(resevationsQueue: Queue[tuple[User, Book]]) -> None`
- `set_user(user: list[User]) -> None`
- `set_loanRecords(loanRecords: list[Loan]) -> None`
- `set_bookcase(bookcase: list[Book]) -> None`

> Nota: la implementación actual inicializa las colecciones al importar el
módulo (`Library.initialize()` se ejecuta al final de `app.services.library`).

### Ejemplo breve (uso) 🧪
```python
from app.services import Library
from app.utils import Stack
from app.models import Book, User

# Obtener la pila del inventario (Stack) y trabajar sobre ella
inventary = Library.get_inventary()
inventary.push(Book(title='Ejemplo', author='Autor'))

# Acceder a la cola de reservas
queue = Library.get_reservationsQueue()
# queue.push((User(...), Book(...)))

# Reemplazar la lista de usuarios (p. ej. al cargar desde un fichero)
Library.set_user([User(name='Admin')])

print(Library.get_user())
```

Este ejemplo es ilustrativo: adapte la construcción de `Book` y `User` a las
firmas reales en `app.models`.

---

## Buenas prácticas y notas ⚠️
- `Library` guarda el estado en memoria: si la aplicación debe persistir datos
  entre ejecuciones, combine estos servicios con `app.utils.FileManager` u
  otra capa de persistencia.
- Evite instanciar `Library` (no es instanciable). Use siempre métodos de clase.
- Reemplazar colecciones con los setters es la forma prevista para cargar
  estados completos (p. ej. desde JSON) en lugar de manipular atributos
  privados directamente.

---

## Ejecutar ejemplos / comprobaciones ▶️

Comandos PowerShell de ejemplo (ejecutar desde la raíz del proyecto):

```powershell
; python -c "from app.services import Library; print(Library.get_inventary())"
; python -c "from app.services import Library; print(Library.get_user())"
```
[⬆ Volver al inicio](#top)



