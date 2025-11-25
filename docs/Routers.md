[⬆ Volver al inicio](#top)
# Routers
Resumen de los routers expuestos en `app.routers`. Incluye rutas, métodos
HTTP, schemas de entrada y ejemplos de uso rápido.

**Objetivo**: referencia rápida de endpoints (qué reciben, qué devuelven y
cómo probarlos). ✅

---

## Visión general
Los routers se registran en la aplicación principal y exponen prefijos:
- `/auth` — autenticación
- `/book` — operaciones sobre libros
- `/loan` — operaciones sobre préstamos
- `/user` — operaciones sobre usuarios

Todas las respuestas siguen un patrón simple: `{"message": str, "data": ...}`
cuando aplicable.

---

## Auth (`/auth`) 🔐

Rutas principales:
- `POST /auth/login` — body: `AuthLogin` (`email`, `password`) -> devuelve
  `{"message": str, "data": AuthLogin}` (actualmente devuelve el body sin
  procesar).
- `POST /auth/logout` — no body -> devuelve `{"message": str}`.

Ejemplo (REST Client):

```http
POST {{host}}/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "s3cret"
}
```

Nota: el endpoint de login actualmente devuelve el objeto `AuthLogin` tal
como llega; hay una implementación pendiente de la lógica de autenticación.

---

## Book (`/book`) 📗

Prefijo: `/book` — tags: `book`.

Schemas usados:
- `BookCreate` (body de `POST /book/`)
- `BookUpdate` (body de `PATCH /book/{id_IBSN}`)

Endpoints:
- `POST /book/` — crea un libro; body `BookCreate`.
- `GET /book/{id_IBSN}` — lectura por ISBN (path param `id_IBSN`).
- `GET /book/` — lista todos los libros.
- `PATCH /book/{id_IBSN}` — actualiza campos parciales con `BookUpdate`.
- `DELETE /book/{id_IBSN}` — elimina libro por ISBN.

Ejemplo (REST Client):

```http
POST {{host}}/book/
Content-Type: application/json

{
  "id": "978-1",
  "title": "Ejemplo",
  "author": "Autor",
  "gender": 1,
  "weight": 0.5,
  "price": 9.99,
  "is_borrowed": false
}
```

Notas y observaciones:
- Las rutas devuelven objetos `data` creados/consultados por la capa CRUD.
- Revisa la implementación de `DELETE /book/{id_IBSN}`: el código usa una
  variable `id` internamente que podría ser un error (debería usar
  `id_IBSN`).

---

## Loan (`/loan`) 📝

Prefijo: `/loan` — tags: `loan`.

Schemas usados:
- `LoanCreate` (body de `POST /loan/`)
- `LoanUpdate` (body de `PATCH /loan/{id}`)

Endpoints:
- `POST /loan/` — crea un préstamo; body `LoanCreate`.
- `GET /loan/{id}` — obtiene préstamo por id.
- `GET /loan/` — lista todos los préstamos.
- `PATCH /loan/{id}` — actualiza préstamo parcial con `LoanUpdate`.
- `DELETE /loan/{id}` — elimina préstamo por id.

Ejemplo (REST Client):

```http
POST {{host}}/loan/
Content-Type: application/json

{
  "user_id": "user-1",
  "book_id": "978-1",
  "loanDate": "2025-11-25T00:00:00Z"
}
```

Notas y observaciones:
- En el archivo `app/routers/loan.py` la inicialización del CRUD usa
  `Library.get_loanRecords` (sin paréntesis) lo que pasa la función en lugar
  del valor retornado; conviene revisar si la intención era pasar la lista
  (`Library.get_loanRecords()`).

---

## User (`/user`) 👤

Prefijo: `/user` — tags: `user`.

Schemas usados:
- `UserCreate` (body de `POST /user/`)
- `UserUpdate` (body de `PATCH /user/{id}`)

Endpoints:
- `GET /user/` — lista todos los usuarios.
- `GET /user/{id}` — obtiene usuario por id.
- `POST /user/` — crea usuario; body `UserCreate`.
- `PATCH /user/{id}` — actualiza usuario parcial con `UserUpdate`.
- `DELETE /user/{id}` — elimina usuario por id.

Ejemplo (REST Client):

```http
POST {{host}}/user/
Content-Type: application/json

{
  "fullName": "Alice",
  "email": "alice@example.com",
  "password": "secret"
}
```

---

## Probar localmente

```powershell
; uvicorn main:app --reload
```
Para más información sobre cómo usar el cliente REST, añade el siguiente
subapartado para usar el plugin **REST Client** en VS Code y ejecutar las
peticiones definidas en `docs/demo/routers/demo_requests.http`.

### Uso del plugin REST Client (VS Code)

- Instalación: busca e instala la extensión `REST Client` (publisher:
  `humao.rest-client`) en Visual Studio Code.
- Abrir peticiones: abre `docs/demo/routers/demo_requests.http`.
- Ejecutar: pulsa en el enlace `Send Request` que aparece encima de cada
  petición o usa `Alt+Ctrl+R` / `Ctrl+Alt+R` según tu configuración.
- Variables: el fichero demo usa una variable `{{host}}` definida al inicio
  del archivo para apuntar a `http://localhost:8000`.

El archivo demo incluye peticiones de ejemplo para `/auth`, `/book`, `/loan`
y `/user`. Asegúrate de iniciar la aplicación (`uvicorn main:app --reload`) y
luego enviar las peticiones desde el REST Client.

[⬆ Volver al inicio](#top)