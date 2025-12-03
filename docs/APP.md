# Módulo `app`

Resumen
- `app/` contiene la capa de aplicación: routers, dependencias y puntos de entrada.

Estructura relevante
- `app/api/v1/` - Routers por recurso: `auth/`, `books/`, `loans/`, `users/`.
- `app/dependencies.py` - Dependencias de FastAPI (inyección, auth helpers).

Archivos clave
- `app/api/v1/auth/router.py` - Endpoints de autenticación y token.
- `app/api/v1/books/router.py` - Endpoints para gestionar libros.
- `app/api/v1/loans/router.py` - Endpoints para préstamos.

Demos y pruebas
- Ver `docs/demo/routers/demo_requests.http` para ejemplos de peticiones.

Ejecutar servidor
```powershell
python -m uvicorn main:app --reload
```

Notas
- Actualiza este README si cambias rutas o nombres de routers.
