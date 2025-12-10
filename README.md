
**Introducción**
- **Proyecto**: `library_api` — API ligera para gestión de una biblioteca (libros, estantes, préstamos, usuarios).
- **Descripción breve**: Este repositorio contiene la estructura inicial de una API para gestionar una pequeña librería/inventario. Por ahora tenemos la estructura del proyecto y varios módulos en desarrollo; la intención es seguir construyendo las capas de `models`, `schemas`, `routers` y `services` para exponer la funcionalidad vía HTTP.

**Estado del Proyecto**
- **Progreso aproximado**: 15% del 100% total — el repositorio contiene la estructura inicial y módulos en desarrollo.
- **Módulos terminados**: `Utils` (incluye `file_manager`, `queue`, `stack`) — **100%**.
- **Módulos en avance**: `Routers` — **75%** (faltaría integrar el sistema de `auth`/autenticación dentro de las rutas).

**Estructura de carpetas (actual)**
```markdown
 # library_api

 Proyecto `library_api`: API ligera para gestionar una biblioteca (libros, estantes, préstamos y usuarios).

 Resumen: este repositorio contiene la estructura y módulos iniciales para construir una API en Python. Se incluyen las capas de `models`, `schemas`, `routers`, `services`, utilidades y ejemplos en `docs/demo`.

 **Estado**: trabajo en progreso — utilidades y demos disponibles; routers y autenticación parcialmente implementados.

 **Quick start (Windows / PowerShell)**

 - Asegúrate de tener Python 3.10+ instalado.
 - Crear y activar un entorno virtual (opcional, recomendado):

 ```powershell
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1
 ```

 - Instalar dependencias:

 ```powershell
 python -m pip install --upgrade pip
 python -m pip install -r requirements.txt
 ```

 - Ejecutar los scripts provistos:

 ```powershell
 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
 .\install.ps1
 .\run.ps1
 ```

 Si el proyecto usa `uvicorn` y hay un objeto `app` en `main.py`, se puede ejecutar manualmente:

 ```powershell
 python -m uvicorn main:app --reload
 ```

 Tests (si están presentes):

 ```powershell
 python -m pytest -q
 ```

 **Estadísticas de Contribuidores**

 Para ver cuántas líneas de código ha agregado y eliminado cada contribuidor:

 ```powershell
 python contributor_stats.py
 ```

 Ver la [documentación completa](docs/ContributorStats.md) para más detalles.

 **Instrucciones básicas de Git**

 He inicializado el repositorio localmente y añadido un `.gitignore` básico (ver archivo en la raíz). Para subir (push) los cambios a un repositorio remoto necesitas configurar un `remote` llamado `origin` con la URL de tu repo en GitHub/GitLab/Bitbucket.

 Ejemplo para añadir remoto y subir:

 ```powershell
 git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
 git branch -M main
 git push -u origin main
 ```

 Si prefieres, puedo crear el repositorio remoto en GitHub usando la CLI `gh` (si la tienes instalada) y hacer el push por ti; indícame si quieres que lo haga y dame el nombre del repo o la URL remota.

 **Estructura principal (resumen)**

 - `main.py` — punto de entrada.
 - `requirements.txt` — dependencias.
 - `app/` — código fuente: `models/`, `schemas/`, `routers/`, `services/`, `utils/`, `crud/`.
 - `data/` — ficheros JSON/CSV de ejemplo.
 - `docs/` — documentación y demos.
 - `test/` — pruebas unitarias.

 ---

 Si quieres que suba los cambios automáticamente, por favor comparte la URL del repositorio remoto o autoriza crear uno en tu cuenta de GitHub (puedo usar `gh` si está disponible). Si prefieres no compartir credenciales, puedo explicar los pasos para que lo subas localmente.
  .\install.ps1
  ```

  - Si el script no instala paquetes, puede instalar manualmente las dependencias con:

  ```powershell
  python -m pip install -r requirements.txt
  ```

**Ejecución**

- Para iniciar la aplicación usando el script provisto:

  ```powershell
  .\run.ps1
  ```

- Alternativa (si usa `uvicorn`/FastAPI y hay un `main.py` con `app`):

  ```powershell
  & .\venv\Scripts\Activate.ps1
  python -m uvicorn main:app --reload
  ```

**Clonar desde GitHub**

- (Espacio reservado) Antes de ejecutar `install.ps1`, clone el repo y sitúese en la carpeta del proyecto:

  ```powershell
  git clone <REPO_URL>
  cd library_api
  ```

  Sustituya `<REPO_URL>` por la URL real del repositorio.

**Carpeta `docs/demo` — dinámica y uso**
- **Propósito**: Contiene ejemplos de uso y demos para probar módulos concretos sin arrancar el servidor.
- **Contenido clave**:
  - `docs/demo/models/demo_models.py`: script de demostración para las clases de `models` (se ejecuta con `python`).
  - `docs/demo/routers/demo_requests.http`: colección de peticiones de ejemplo (útil con extensiones HTTP client en editores o para referencia).
  - `docs/demo/result_demos/`: resultados esperados/ejemplos (`demo.csv`, `demo.json`).
  - `docs/demo/utils/`: versiones demostrativas de `file_manager`, `queue`, `stack` usadas en los demos.
- **Cómo usar**:

  ```powershell
  python docs/demo/models/demo_models.py
  ```

  Esto ejecutará el demo y generará/mostrará resultados similares a los que están en `docs/demo/result_demos/`.

**Tabla de Contenidos (links a `docs/`)**

| Sección | Archivo |
|---|---:|
| Grud | [docs/Grud.md](docs/Grud.md) |
| Models | [docs/Models.md](docs/Models.md) |
| Routers | [docs/Routers.md](docs/Routers.md) |
| Schemas | [docs/Schemas.md](docs/Schemas.md) |
| Services | [docs/Services.md](docs/Services.md) |
| Utils | [docs/Utils.md](docs/Utils.md) |
| Contributor Stats | [docs/ContributorStats.md](docs/ContributorStats.md) |

---