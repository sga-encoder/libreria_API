[⬆ Volver al inicio](#top)

# Pruebas (Tests) 🧪

Guía práctica y plantilla para crear, ejecutar y depurar tests en el proyecto `library_api`. Pensada para colaboradores que no conocen el código.

---

## Requisitos ⚙️

- Activa el entorno virtual (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

- Instala dependencias:

```powershell
python -m pip install -r requirements.txt
# o, si sólo quieres pytest y httpx
python -m pip install pytest httpx
```

---

## Ejecutar los tests ▶️

- Ejecutar toda la suite (raíz del repo):

```powershell
pytest -q
```

- Ejecutar un archivo concreto:

```powershell
pytest test/test_book_router.py -q
```

- Ejecutar una única prueba (función):

```powershell
pytest test/test_book_router.py::test_book_crud -q
```

- Filtrar por nombre / más verbosidad:

```powershell
pytest -k <expresión> -q
pytest -v
```

---

## Estructura recomendada ✅

- Un archivo de tests por router o por responsabilidad (`test_book_router.py`, `test_user_router.py`, ...).
- Importar la app con `from app.main import app` y crear `TestClient(app)`.
- Flujo típico dentro de un test: preparar datos → crear recurso → leer → actualizar → borrar.

---

## Uso de `TestClient` — ejemplos prácticos 📁

Crear el cliente:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
```

POST con JSON (crear recurso):

```python
payload = {"id_IBSN": "978-1", "title": "Ejemplo"}
resp = client.post("/book/", json=payload)
assert resp.status_code in (200, 201)
```

GET básico y extracción segura del cuerpo (soporte para wrapper `{message,data}`):

```python
resp = client.get("/book/978-1")
assert resp.status_code == 200
body = resp.json()
resource = body.get("data") if isinstance(body, dict) and "data" in body else body
```

PATCH / PUT / DELETE:

```python
resp = client.patch("/book/978-1", json={"title": "Nuevo"})
resp = client.put("/book/978-1", json={...})
resp = client.delete("/book/978-1")
```

Enviar headers / autenticación:

```python
headers = {"Authorization": "Bearer <token>"}
resp = client.get("/protected/", headers=headers)
```

Subir archivos (multipart):

```python
files = {"file": ("test.txt", b"contenido", "text/plain")}
resp = client.post("/upload/", files=files)
```

---

## Fixtures recomendadas (pytest) 🧩

Crear `test/conftest.py` para compartir `TestClient` y datos comunes:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_book():
    return {
        "id_IBSN": "978-1",
        "title": "Ejemplo",
        "author": "Autor",
        "gender": 1,
        "weight": 0.5,
        "price": 9.99,
        "is_borrowed": False,
    }
```

Uso en tests:

```python
def test_book_crud(client, sample_book):
    r = client.post("/book/", json=sample_book)
    assert r.status_code < 500
```

---

## Plantilla rápida para nuevo test 📝

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_<recurso>_flow():
    # 1) Preparar
    payload = {...}

    # 2) Crear
    r = client.post("/<recurso>/", json=payload)
    assert r.status_code in (200, 201)

    # 3) Leer
    r = client.get("/<recurso>/<id>")
    assert r.status_code == 200

    # 4) Actualizar
    r = client.patch("/<recurso>/<id>", json={"campo": "valor"})
    assert r.status_code < 500

    # 5) Borrar
    r = client.delete("/<recurso>/<id>")
    assert r.status_code < 500
```

---

## Manejo de Pydantic y compatibilidad 🔧

Cuando los routers reciben modelos Pydantic, normaliza antes de pasarlos a la capa CRUD:

```python
if hasattr(obj, "model_dump"):
    data = obj.model_dump()
elif hasattr(obj, "dict"):
    data = obj.dict()
else:
    data = obj
```

Esto evita advertencias en Pydantic v2 y mantiene compatibilidad con v1.

---

## Depuración de fallos 🐛

- Imprime la respuesta dentro del test para inspeccionar: `print(resp.status_code, resp.text)`.
- Ejecuta la prueba individualmente para reproducir rápido:

```powershell
pytest test/test_book_router.py::test_book_crud -q
```

- Si el error es del servidor, arranca `uvicorn` y reproduce la petición para ver el stacktrace:

```powershell
uvicorn app.main:app --reload
```

Error habitual: `AttributeError: 'str' object has no attribute 'to_dict'` → indica que el `crud` devolvió un tipo inesperado; revisa la implementación o ajusta el test si el endpoint aún es un stub.

---

## Ejemplo de salida ✅

```text
(venv) PS C:\Users\ASUS\code\library_api> pytest -q
.....
5 passed in 0.40s
```

---

## Buenas prácticas 📌

- Aisla el estado entre tests: crear y limpiar recursos dentro del propio test.
- Usa identificadores únicos para evitar colisiones (p. ej. `f"test-{uuid4()}"`).
- Añade tests para respuestas de error (400, 404, 500).
- Integra los tests en CI (GitHub Actions / GitLab CI).

---


Fin del documento.