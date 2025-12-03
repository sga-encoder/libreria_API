# API v1 - Resumen de endpoints

Rutas principales en `app/api/v1/`:

- `/api/v1/auth` - Autenticación y tokens.
- `/api/v1/book` - CRUD de libros.
- `/api/v1/loan` - Operaciones sobre préstamos.
- `/api/v1/user` - Gestión de usuarios.

Schemas
- Cada router tiene su `schemas.py` que define los modelos Pydantic usados en requests/responses.

Protección de rutas
- Algunas rutas requieren autorización por token (Bearer JWT). Usa el endpoint de `auth` para obtener token.

Ejemplo de uso
- Ver `docs/demo/routers/demo_requests.http` para ejemplos de peticiones con variables y token.
