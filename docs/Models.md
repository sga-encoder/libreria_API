[⬆ Volver al inicio](#top)
# Models
Resumen de los modelos de dominio en `app.models`: clases, campos,
métodos útiles y ejemplos de uso.

**Objetivo**: referencia rápida de las clases del dominio (qué representan,
cómo crearlas y cómo serializarlas). ✅

---

## Person 👤

### Qué hace
`Person` es la clase base para entidades humanas (usuarios y administradores).
Provee campos básicos (`id`, `fullName`, `email`, `password`, `role`) y
utilidades de creación/serialización y gestión segura de contraseñas.

### Campos / firma
- `__init__(fullName: str, email: str, password: str, role: PersonRole, id: str = None)`

Propiedades principales accesibles vía getters:
- `get_id()`
- `get_fullName()`
- `get_email()`
- `get_password()`  : retorna el hash de la contraseña, no el texto plano.
- `get_role()`

### Comportamiento / validaciones
- **Nombre (`fullName`)**: no puede estar vacío ni solo espacios; longitud mínima 3 y máxima 50.
- **Email**: validado con una regex simple (`local@domain.tld`).
- **Password**: se guarda como hash usando `werkzeug.security.generate_password_hash`.

### Métodos importantes
- `from_dict(data: dict) -> Person` — construye desde un diccionario. El campo `role` debe ser el nombre del enum (ej. `"USER"`) ya que internamente se hace `PersonRole[data.get("role")]`.
- `to_dict() -> dict` — serializa a dict; `password` contiene el hash y `role` se exporta con `role.name`.
- `verify_password(password: str) -> bool` — verifica un password contra el hash almacenado.
- `change_password(current_password: str, new_password: str) -> bool` — cambia el password si la verificación es correcta.
- `__str__()` / `__repr__()` — representaciones legibles para logging/debug.

### Ejemplo 🧪
```python
from app.models import Person
from app.models.enums import PersonRole

p = Person(fullName='Alice', email='alice@example.com', password='pw', role=PersonRole.USER)
print(p.get_fullName())
print(p.to_dict())
```

---

## User 👥

### Qué hace
`User` hereda de `Person` e incorpora la lista de préstamos (`loans`). Mantiene
préstamos en memoria como una lista y añade utilidades para gestionarlos.

### Campos / firma
- `__init__(fullName: str, email: str, password: str, loans: list, id: str = None)`

Comportamiento y detalles:
- Los `loans` se almacenan en un atributo privado (`__loans`) y pueden ser accedidos con `get_loans()`.
- `add_loan(loan)` y `remove_loan(loan)` modifican la lista en memoria.
- `from_dict(data: dict) -> User` — construye un `User` desde un diccionario (espera `loans` opcionalmente).
- `to_dict()` incluye el campo `loans` tal como está en memoria (útil para persistencia simple).
- Se sobreescriben `__str__()` y `__repr__()` para mostrar información concisa del usuario y la cantidad de préstamos.

### Ejemplo 🧪
```python
from app.models import User

u = User(fullName='Bob', email='bob@example.com', password='pw', loans=[])
u.add_loan({'id':'loan-1'})
print(u.get_loans())
```

Nota: los schemas (p. ej. `UserCreate`) usan campos de entrada diferentes
para las rutas (por ejemplo no requieren `id` al crear); la conversión entre
schemas y modelos de dominio se realiza en la capa CRUD/routers.

---

## Book 📗

### Qué hace
`Book` representa la entidad libro: identificador (ISBN), título, autor,
género (enum), peso, precio y estado de préstamo.

### Campos / firma
- `__init__(id_IBSN: str, title: str, author: str, gender: BookGender, weight: float, price: float)`

Getters principales:
- `get_id_IBSN()`, `get_title()`, `get_author()`, `get_gender()`,
  `get_weight()`, `get_price()`, `get_is_borrowed()`

Métodos interesantes:
- `from_dict(data: dict) -> Book`
- `to_dict() -> dict` — serializa `gender` usando `gender.name`.
- `set_is_borrowed(bool)` para marcar estado de préstamo.

### Ejemplo 🧪
```python
from app.models import Book
from app.models.enums import BookGender

b = Book(id_IBSN='978-1', title='Ejemplo', author='Autor', gender=BookGender.AVENTURA, weight=0.5, price=9.99)
print(b.get_title())
print(b.to_dict())
```

---

## Loan 📝

### Qué hace
`Loan` modela un préstamo: id, referencia al `User`, referencia al `Book` y
la fecha del préstamo. En el dominio mantiene referencias a objetos (no
solo IDs).

### Campos / firma
- `__init__(id: str, user: User, book: Book, loanDate: datetime)`

Getters:
- `get_id()`, `get_user()`, `get_book()`, `get_loanDate()`

Otros métodos:
- `from_dict(data: dict) -> Loan` — construye desde dict (convierte user y
  book usando `User.from_dict()` / `Book.from_dict()`).
- `to_dict() -> dict` — serializa `loanDate` con `isoformat()` y anida
  `user.to_dict()` / `book.to_dict()`.

### Ejemplo 🧪
```python
from datetime import datetime, timezone
from app.models import Loan, User, Book

loan = Loan(id='loan-1', user=User.from_dict({'id':'u1','fullName':'A','email':'a@x','password':'p','loans':[]}), book=Book.from_dict({'id_IBSN':'978-1','title':'T','author':'A','gender':'AVENTURA','weight':1.0,'price':5.0,'is_borrowed':False}), loanDate=datetime.now(timezone.utc))
print(loan.to_dict())
```

---

## BookCase & BookShelf

### Qué hacen
`BookCase` y `BookShelf` están definidos como clases placeholder en el
repositorio actual (sin implementación). Se incluyen en `app.models` para
completar el espacio de nombres y poder extenderlas en el futuro.

---

## Enums útiles

- `app.models.enums.BookGender` — géneros disponibles (ej: `AVENTURA`,
  `ROMANCE`, `TERROR`, ...).
- `app.models.enums.PersonRole` — roles (`ADMIN`, `USER`).

---

## Demo ejecutable ✅

- **Archivo**: `docs/demo/models/demo_models.py` — instancias de ejemplo de
  `Person`, `User`, `Book` y `Loan` que imprimen la salida de `to_dict()`.
- **README**: `docs/demo/models/README.md` con instrucciones rápidas.

- **Ejecutar (desde la raíz del proyecto, PowerShell):**

```powershell
; python -m docs.demo.models.demo_models
```

[⬆ Volver al inicio](#top)


