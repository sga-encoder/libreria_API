# Módulo `domain`

Resumen
- `domain/` contiene el dominio de la aplicación: modelos, repositorios, servicios, estructuras y algoritmos.

Estructura relevante
- `domain/models/` - Clases de datos: `book.py`, `user.py`, `loan.py`, `bookcase.py`, `bookshelf.py`, `person.py`.
- `domain/repositories/` - Implementaciones in-memory o basadas en ficheros para datos.
- `domain/services/` - Lógica de negocio (ej. `inventory_service.py`, `loan_service.py`).
- `domain/algorithms/` - Algoritmos de apoyo (búsqueda, ordenamiento).
- `domain/structures/` - Estructuras de datos auxiliares (`queue.py`, `stack.py`).

Demos
- Los demos de modelos y estructuras están en `docs/demo/models/` y `docs/demo/utils/`.

Consejos
- Si cambias modelos, actualiza los schemas en `app/api/v1/*/schemas.py` y los repositorios.
