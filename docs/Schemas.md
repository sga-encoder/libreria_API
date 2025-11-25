[⬆ Volver al inicio](#top)
# Schemas
Este documento resume los schemas Pydantic del paquete `app.schemas`, con
firmas, comportamiento esperado y ejemplos de uso para los modelos de entrada
(POST/PATCH) usados por los routers.

**Objetivo**: referencia rápida por schema (qué valida, campos requeridos vs
opcionales, y ejemplos de creación). ✅

---

## Auth 🔐

### Qué hace
Schemas para autenticación de usuarios. Validan credenciales en las rutas de
login.

### Modelo / firma
- `AuthLogin(BaseModel)`
	- `email: str`
	- `password: str`

### Ejemplo breve 🧪
```python
from app.schemas.auth import AuthLogin

data = AuthLogin(email='user@example.com', password='s3cret')
print(data.dict())
```

---

## Book 📗

### Qué hace
Schemas para crear y actualizar libros. El schema de creación exige todos los
campos relevantes; el de actualización hace la mayoría opcionales para
parcheos (PATCH).

### Modelos / firmas
- `BookCreate(BaseModel)` (POST completo):
	- `id_IBSN: str`
	- `title: str`
	- `author: str`
	- `gender: BookGender` (enum en `app.models.enums`)
	- `weight: float`
	- `price: float`
	- `is_borrowed: bool`

- `BookUpdate(BaseModel)` (PATCH parcial):
	- `title: Optional[str] = None`
	- `author: Optional[str] = None`
	- `gender: Optional[BookGender] = None`
	- `weight: Optional[float] = None`
	- `price: Optional[float] = None`
	- `is_borrowed: Optional[bool] = None`

### Ejemplo breve 🧪
```python
from app.schemas.book import BookCreate, BookUpdate
from app.models.enums import BookGender

create = BookCreate(
		id_IBSN='978-1', title='Ejemplo', author='Autor',
		gender=BookGender.NOVEL, weight=0.5, price=9.99, is_borrowed=False
)

update = BookUpdate(title='Nuevo título')
print(create.dict())
print(update.dict(exclude_unset=True))
```

> Nota: ajuste `BookGender` según los valores definidos en `app.models.enums`.

---

## Loan 📝

### Qué hace
Schemas para crear y actualizar registros de préstamo. Usan IDs para evitar
serializar objetos de dominio complejos dentro de los esquemas.

### Modelos / firmas
- `LoanCreate(BaseModel)`:
	- `user: str`
	- `book: str`
	- `loanDate: datetime`

- `LoanUpdate(BaseModel)` (PATCH parcial):
	- `user: Optional[str] = None`
	- `book: Optional[str] = None`
	- `loanDate: Optional[datetime] = None`

### Ejemplo breve 🧪
```python
from datetime import datetime
from app.schemas.loan import LoanCreate, LoanUpdate

loan = LoanCreate(user='user-1', book='978-1', loanDate=datetime.utcnow())
update = LoanUpdate(loanDate=datetime(2025, 12, 1))
print(loan.dict())
```

---

## User 👤

### Qué hace
Schemas para creación y actualización de usuarios. El schema de creación
requiere los campos básicos; el de actualización los hace opcionales.

### Modelos / firmas
- `UserCreate(BaseModel)` (POST completo):
	- `fullName: str`
	- `email: str`
	- `password: str`

- `UserUpdate(BaseModel)` (PATCH parcial):
	- `fullName: Optional[str] = None`
	- `email: Optional[str] = None`
	- `password: Optional[str] = None`

### Ejemplo breve 🧪
```python
from app.schemas.user import UserCreate, UserUpdate

u = UserCreate(fullName='Alice', email='alice@example.com', password='secret')
patch = UserUpdate(email='alice@newdomain.com')
print(u.json())
```

---

## Buenas prácticas y notas ⚠️
- Use `BaseModel` directamente para validación de inputs en routers y para
	documentar los tipos en OpenAPI.


---

## Ejecutar los demos ▶️

Los demos se encuentran en `docs/demo/schemas/` y están pensados para ejecutarse
desde la raíz del proyecto. Ejemplos (PowerShell):

- **Ejecutar (desde la raíz del proyecto, PowerShell):**

```powershell
; python -m docs.demo.schemas.demo_schemas
```
[⬆ Volver al inicio](#top)