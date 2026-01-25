 # Contexto Completo: Migración de Library API a SQLAlchemy

## 📋 Objetivo del Proyecto

Migrar una API de biblioteca de FastAPI que actualmente usa archivos JSON para persistencia de datos hacia una base de datos SQLite usando SQLAlchemy como ORM.

---

## 🏗️ Estructura Actual del Proyecto

```
library_api/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py          ✅ CREADO - Configuración SQLAlchemy
│   │   ├── logging_config.py
│   │   └── security.py
│   ├── domain/
│   │   ├── models/              (Modelos de dominio - independientes de BD)
│   │   ├── services/            (Lógica de negocio)
│   │   ├── repositories/        (Actualmente usa archivos JSON - A MIGRAR)
│   │   ├── algorithms/
│   │   ├── structures/
│   │   └── exceptions/
│   ├── persistence/             ✅ NUEVA CARPETA
│   │   ├── models.py           ✅ CREADO - Modelos ORM (UserORM, BookORM, LoanORM)
│   │   └── repositories/       ✅ CREADO - Repositorios SQL
│   │       ├── base_repository.py
│   │       └── users_repository.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       ├── users/
│   │       ├── books/
│   │       ├── loans/
│   │       └── admin/
│   ├── dependencies.py
│   └── integrations/
├── data/
│   ├── json/
│   │   ├── users.json          (Datos actuales - A MIGRAR)
│   │   ├── books.json
│   │   └── loans.json
│   └── csv/
├── scripts/
│   └── migrate_users.py        ✅ CREADO - Script de migración
├── test/
├── main.py
├── requirements.txt
├── .env
└── run.ps1
```

---

## 📦 Dependencias Instaladas

### Archivo `requirements.txt` actualizado:

```txt
# Framework
fastapi==0.121.3
uvicorn==0.38.0
starlette==0.50.0

# Base de datos y ORM
SQLAlchemy==2.0.23
alembic==1.13.1

# Autenticación
python-jose[cryptography]
passlib[bcrypt]
bcrypt

# Validación
pydantic==2.12.4
marshmallow==3.20.1

# Testing
pytest==9.0.1
pytest-cov==4.1.0

# Utilidades
python-dotenv==1.2.1
requests==2.32.5
Werkzeug==3.1.3

# Otros
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.11.0
certifi==2025.11.12
charset-normalizer==3.4.4
click==8.3.1
colorama==0.4.6
dotenv==0.9.9
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
iniconfig==2.3.0
MarkupSafe==3.0.3
packaging==25.0
pluggy==1.6.0
pydantic_core==2.41.5
Pygments==2.19.2
sniffio==1.3.1
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.5.0
```

**Comando de instalación ejecutado:**
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuración de Variables de Entorno

### Archivo `.env`:

```env
# Servicios externos
GOOGLE_BOOKS_API_KEY=AIzaSyAYYluDm76drpDC-9XgPTTOs5YlJ0Upt94

# Base de datos
DATABASE_URL=sqlite:///./library.db

# JWT
SECRET_KEY=FV9q3WkPs1rA8dMZ4uT2Lxh7Be0QnJgC5vSypRNDmHGoUjKXfbiVztEawOYcLp6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=100000000

# Configuración
DEBUG=True
API_VERSION=v1
```

---

## 💾 Código Implementado

### 1. Configuración de Base de Datos (`app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import settings

# Crear el motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependencia para obtener sesión de BD en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa todas las tablas en la BD"""
    from app.persistence.models import UserORM
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")
```

**Explicación:**
- `engine`: Motor SQLAlchemy que conecta con SQLite
- `SessionLocal`: Factory para crear sesiones de BD
- `Base`: Clase base para modelos ORM
- `get_db()`: Generador para inyección de dependencias en FastAPI
- `init_db()`: Crea todas las tablas automáticamente

---

### 2. Modelos ORM (`app/persistence/models.py`)

```python
"""Modelos ORM de SQLAlchemy para la base de datos."""

from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from app.core.database import Base

class UserORM(Base):
    """Modelo ORM para la tabla de usuarios."""
    __tablename__ = "users"
    
    # Columnas principales
    id = Column(String(50), primary_key=True, index=True)
    fullName = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Ya hasheada
    role = Column(String(20), default="USER")
    
    # Campos de auditoría
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Características:**
- `__tablename__`: Nombre de la tabla en la BD
- `Column()`: Define columnas con tipos de datos
- Índices automáticos en `id` y `email`
- `unique=True` en email para evitar duplicados
- Campos de auditoría (`created_at`, `updated_at`)

---

### 3. Repositorio Base con Genéricos (`app/persistence/repositories/base_repository.py`)

```python
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model
    
    def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def read(self, id: str) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def read_all(self) -> List[T]:
        return self.db.query(self.model).all()
    
    def update(self, id: str, **kwargs) -> Optional[T]:
        obj = self.read(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj
    
    def delete(self, id: str) -> bool:
        obj = self.read(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
```

**Explicación de Genéricos:**
- `T = TypeVar("T")`: Variable de tipo genérica
- `Generic[T]`: Clase que puede trabajar con cualquier tipo
- Permite reutilización: un repositorio base para todos los modelos
- Type safety: Tu IDE sabe qué tipo retorna cada método

**Ejemplo de uso:**
```python
# T se reemplaza por UserORM
class UsersRepositorySQL(BaseRepository[UserORM]):
    def __init__(self, db: Session):
        super().__init__(db, UserORM)

# Ahora el IDE sabe que repo.read() retorna UserORM
repo = UsersRepositorySQL(db)
user = repo.read("123")  # user es tipo UserORM
```

---

### 4. Repositorio de Usuarios (`app/persistence/repositories/users_repository.py`)

```python
"""Repositorio SQL para operaciones con usuarios."""

from sqlalchemy.orm import Session
from typing import Optional, List
from app.persistence.models import UserORM
from app.persistence.repositories.base_repository import BaseRepository

class UsersRepositorySQL(BaseRepository[UserORM]):
    """Repositorio SQL para gestionar usuarios."""
    
    def __init__(self, db: Session):
        super().__init__(db, UserORM)
    
    def read_by_email(self, email: str) -> Optional[UserORM]:
        """Busca un usuario por email."""
        return self.db.query(UserORM).filter(
            UserORM.email == email
        ).first()
    
    def read_active_users(self) -> List[UserORM]:
        """Obtiene todos los usuarios activos."""
        return self.db.query(UserORM).filter(
            UserORM.is_active == True
        ).all()
    
    def deactivate_user(self, user_id: str) -> bool:
        """Desactiva un usuario (soft delete)."""
        user = self.read(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
```

**Métodos heredados de BaseRepository:**
- `create(**kwargs)`: Crear usuario
- `read(id)`: Leer por ID
- `read_all()`: Leer todos
- `update(id, **kwargs)`: Actualizar
- `delete(id)`: Eliminar

**Métodos específicos:**
- `read_by_email()`: Buscar por email (para login)
- `read_active_users()`: Solo usuarios activos
- `deactivate_user()`: Soft delete

---

### 5. Script de Migración (`scripts/migrate_users.py`)

```python
"""Script para migrar usuarios desde JSON a SQLite."""

import json
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.persistence.models import UserORM
from app.core.config import settings

def migrate_users_from_json():
    """Migra usuarios desde data/json/users.json a la BD."""
    
    # Inicializar tablas
    init_db()
    
    # Leer JSON
    json_path = Path(settings.DATA_PATH_USERS)
    
    if not json_path.exists():
        print(f"❌ Archivo no encontrado: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    db = SessionLocal()
    migrated = 0
    skipped = 0
    
    try:
        for user_dict in users_data:
            # Verificar si ya existe
            existing = db.query(UserORM).filter(
                UserORM.email == user_dict.get('email')
            ).first()
            
            if existing:
                print(f"⚠️  Usuario ya existe: {user_dict.get('email')}")
                skipped += 1
                continue
            
            # Crear nuevo usuario
            new_user = UserORM(
                id=user_dict.get('id'),
                fullName=user_dict.get('fullName'),
                email=user_dict.get('email'),
                password=user_dict.get('password'),  # Ya hasheada
                role=user_dict.get('role', 'USER'),
                is_active=True
            )
            
            db.add(new_user)
            migrated += 1
            print(f"✓ Migrado: {user_dict.get('email')}")
        
        db.commit()
        print(f"\n✅ Migración completada:")
        print(f"   - Usuarios migrados: {migrated}")
        print(f"   - Usuarios omitidos: {skipped}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante migración: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users_from_json()
```

**Funcionalidad:**
1. Lee `data/json/users.json`
2. Verifica si cada usuario ya existe en BD (por email)
3. Inserta usuarios nuevos
4. Mantiene contraseñas ya hasheadas
5. Muestra reporte de migración

---

### 6. Actualización de Dependencias (`app/dependencies.py`)

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.persistence.repositories.users_repository import UsersRepositorySQL

# Nueva función para inyectar repositorio SQL
def get_users_repository(db: Session = Depends(get_db)) -> UsersRepositorySQL:
    """Inyecta el repositorio de usuarios con sesión de BD."""
    return UsersRepositorySQL(db)
```

**Uso en routers:**
```python
@router.post("/")
def create_user(
    user: UserCreate,
    repo: UsersRepositorySQL = Depends(get_users_repository)
):
    # repo ya tiene la sesión de BD inyectada
    user_orm = repo.create(...)
    return user_orm
```

---

### 7. Ejemplo de Router Actualizado (`app/api/v1/users/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_users_repository
from app.persistence.repositories.users_repository import UsersRepositorySQL

user_router = APIRouter(prefix="/api/v1/user", tags=["user"])

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    repo: UsersRepositorySQL = Depends(get_users_repository)
):
    """Crear un nuevo usuario."""
    # Verificar si el email ya existe
    existing = repo.read_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Generar ID único
    import uuid
    user_id = str(uuid.uuid4())
    
    # Hashear contraseña
    from app.domain.models.person import Person
    hashed_password = Person._Person__hash_password(user.password)
    
    # Crear usuario en BD
    user_orm = repo.create(
        id=user_id,
        fullName=user.fullName,
        email=user.email,
        password=hashed_password,
        role="USER"
    )
    
    return {
        "message": "Usuario creado exitosamente",
        "data": {
            "id": user_orm.id,
            "fullName": user_orm.fullName,
            "email": user_orm.email,
            "role": user_orm.role
        }
    }

@user_router.get("/")
def read_all_users(
    repo: UsersRepositorySQL = Depends(get_users_repository)
):
    """Obtener todos los usuarios activos."""
    users = repo.read_active_users()
    
    return {
        "message": f"Se encontraron {len(users)} usuarios",
        "data": [
            {
                "id": u.id,
                "fullName": u.fullName,
                "email": u.email,
                "role": u.role
            }
            for u in users
        ]
    }
```

---

### 8. Main.py con Inicialización de BD

```python
from fastapi import FastAPI
from app.core.database import init_db
from app.api.v1 import auth_router, user_router, book_router, loan_router

app = FastAPI(
    title="Library API",
    description="API para gestión de biblioteca",
    version="2.0.0"
)

@app.on_event("startup")
def startup_event():
    """Inicializar BD al arrancar el servidor."""
    print("🚀 Iniciando aplicación...")
    init_db()
    print("✅ Base de datos inicializada")

# Registrar routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(book_router)
app.include_router(loan_router)

@app.get("/")
def root():
    return {
        "message": "Library API v2.0",
        "database": "SQLite",
        "status": "running"
    }
```

---

## 🔄 Flujo Completo de Trabajo

### 1. **Crear Base de Datos (Automático)**

Cuando ejecutas `uvicorn main:app --reload`:
- Se ejecuta `startup_event()`
- Llama a `init_db()`
- SQLAlchemy lee todos los modelos ORM
- Genera SQL automáticamente:
  ```sql
  CREATE TABLE IF NOT EXISTS users (
      id VARCHAR(50) PRIMARY KEY,
      fullName VARCHAR(255) NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      password VARCHAR(255) NOT NULL,
      role VARCHAR(20) DEFAULT 'USER',
      is_active BOOLEAN DEFAULT 1,
      created_at DATETIME,
      updated_at DATETIME
  );
  ```
- Ejecuta el SQL en `library.db`

### 2. **Migrar Datos Existentes**

```bash
python scripts/migrate_users.py
```

Salida esperada:
```
✓ Tablas creadas exitosamente
✓ Migrado: starchy.adventure@time.cartoon
✓ Migrado: crunchy.adventure@time.cartoon
✓ Migrado: drdonut.adventure@time.cartoon

✅ Migración completada:
   - Usuarios migrados: 3
   - Usuarios omitidos: 0
```

### 3. **Hacer Request a la API**

```http
POST http://localhost:8000/api/v1/user/
Content-Type: application/json

{
  "fullName": "Test User",
  "email": "test@example.com",
  "password": "secure123"
}
```

**Flujo interno:**
1. FastAPI recibe request
2. Ejecuta `get_users_repository()`
3. `get_db()` crea sesión de BD
4. Se pasa al repositorio
5. `repo.create()` inserta en BD
6. Se hace commit automático
7. Retorna objeto creado

---

## 🎯 Conceptos Clave Aprendidos

### 1. **Inyección de Dependencias en FastAPI**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # ← Genera la sesión
    finally:
        db.close()  # ← Siempre cierra

# FastAPI ejecuta get_db() automáticamente
@router.get("/")
def endpoint(db: Session = Depends(get_db)):
    # db ya está lista para usar
```

### 2. **Genéricos en Python**

```python
T = TypeVar("T")  # Variable de tipo

class BaseRepository(Generic[T]):
    def read(self) -> T:  # Retorna tipo T
        pass

# T = UserORM
class UsersRepo(BaseRepository[UserORM]):
    pass

# Ahora IDE sabe que read() retorna UserORM
```

### 3. **ORM (Object-Relational Mapping)**

**Antes (SQL manual):**
```python
cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (id, name, email))
```

**Después (SQLAlchemy ORM):**
```python
user = UserORM(id=id, fullName=name, email=email)
db.add(user)
db.commit()
```

**Ventajas:**
- Menos propenso a errores
- Type safety
- Más legible
- Independiente del motor de BD

### 4. **Sesiones de Base de Datos**

```python
db = SessionLocal()  # Abre conexión
try:
    db.add(objeto)
    db.commit()      # Guarda cambios
except:
    db.rollback()    # Revierte si hay error
finally:
    db.close()       # Siempre cierra
```

---

## 📊 Datos de Ejemplo (users.json)

```json
[
  {
    "id": "17653216386410001",
    "fullName": "Starchy",
    "email": "starchy.adventure@time.cartoon",
    "password": "pbkdf2:sha256:1000000$93k88Ut5Gc36il4Y$aa19a962df82a5d72796abd23db4ede2a8d0005e3259f12364da686c9ad49d32",
    "loans": ["17682495938710004"],
    "historial": [
      {"type": "loan", "id": "17682495836280001"},
      {"type": "loan", "id": "17682495938710004"}
    ],
    "role": "USER"
  },
  {
    "id": "17653218466160001",
    "fullName": "Crunchy",
    "email": "crunchy.adventure@time.cartoon",
    "password": "pbkdf2:sha256:1000000$IdwTSQJajj5oe3QM$33c4ea9f5ad8ec5f04289555aeca46448eae2bd3532148fa6a332542d100e977",
    "loans": ["17682495891830002"],
    "historial": [
      {"type": "loan", "id": "17682495891830002"}
    ],
    "role": "USER"
  },
  {
    "id": "17653362689770001",
    "fullName": "Dr. Donut",
    "email": "drdonut.adventure@time.cartoon",
    "password": "pbkdf2:sha256:1000000$CqaHLWzEbNoDMLf7$cd2236296f2190b7b059b9831cb770ca5dcbff03b25f12df7e2988931e87018e",
    "loans": ["17682495915150003"],
    "historial": [
      {"type": "loan", "id": "17682495915150003"}
    ],
    "role": "USER"
  }
]
```

---

## ✅ Estado Actual del Proyecto

### Completado:
- ✅ Instalación de dependencias (SQLAlchemy, Alembic, etc.)
- ✅ Configuración de `.env` con DATABASE_URL
- ✅ Creación de `app/core/database.py`
- ✅ Creación de modelo ORM `UserORM`
- ✅ Implementación de `BaseRepository` con genéricos
- ✅ Implementación de `UsersRepositorySQL`
- ✅ Script de migración `migrate_users.py`
- ✅ Actualización de dependencias para inyectar repositorio SQL
- ✅ Ejemplo de router actualizado

### Pendiente:
- ⏳ Ejecutar migración de usuarios
- ⏳ Probar endpoints con BD SQLite
- ⏳ Crear modelos ORM para `BookORM` y `LoanORM`
- ⏳ Implementar repositorios para libros y préstamos
- ⏳ Migrar datos de books.json y loans.json
- ⏳ Actualizar servicios de dominio para usar repositorios SQL
- ⏳ Configurar Alembic para migraciones
- ⏳ Crear tests unitarios para repositorios
- ⏳ Eliminar repositorios legacy de archivos JSON

---

## 🚀 Comandos de Ejecución

### Iniciar el servidor:
```powershell
.\run.ps1
```

O manualmente:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### Migrar datos:
```powershell
python scripts/migrate_users.py
```

### Ver base de datos:
```powershell
sqlite3 library.db
.tables
SELECT * FROM users;
.quit
```

### Instalar dependencias:
```powershell
pip install -r requirements.txt
```

---

## 🏛️ Arquitectura de Capas

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)            │
│  - Routers (endpoints HTTP)             │
│  - Schemas (validación Pydantic)        │
│  - Dependencies (inyección)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Service Layer (Domain)           │
│  - Lógica de negocio                    │
│  - Algoritmos                           │
│  - Validaciones de dominio              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Repository Layer (Persistence)       │
│  - UsersRepositorySQL                   │
│  - BooksRepositorySQL (pendiente)       │
│  - LoansRepositorySQL (pendiente)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          ORM Layer (SQLAlchemy)         │
│  - UserORM, BookORM, LoanORM            │
│  - Mapeo objeto-relacional              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Database (SQLite)                │
│  - library.db                           │
└─────────────────────────────────────────┘
```

---

## 🔍 Decisiones de Diseño

### ¿Por qué SQLite?
- ✅ Simple para desarrollo y prototipado
- ✅ No requiere servidor separado
- ✅ Archivo único fácil de manejar
- ✅ Ideal para aplicaciones pequeñas/medianas
- ⚠️ Para producción considerar PostgreSQL/MySQL

### ¿Por qué SQLAlchemy?
- ✅ ORM maduro y robusto
- ✅ Soporta múltiples BD (migración fácil)
- ✅ Type hints y autocompletado
- ✅ Manejo automático de conexiones
- ✅ Previene SQL injection

### ¿Por qué BaseRepository?
- ✅ DRY (Don't Repeat Yourself)
- ✅ Un lugar para cambios en CRUD
- ✅ Métodos comunes heredados
- ✅ Métodos específicos en repositorios hijos

### ¿Por qué separar `domain` y `persistence`?
- ✅ **Domain**: Lógica de negocio independiente de BD
- ✅ **Persistence**: Implementación específica de almacenamiento
- ✅ Permite cambiar BD sin tocar lógica de negocio
- ✅ Facilita testing (mocks de repositorios)

---

## 📚 Recursos y Referencias

### SQLAlchemy:
- Documentación: https://docs.sqlalchemy.org/
- Tutorial ORM: https://docs.sqlalchemy.org/en/20/tutorial/

### FastAPI con BD:
- https://fastapi.tiangolo.com/tutorial/sql-databases/

### Alembic (Migraciones):
- https://alembic.sqlalchemy.org/

### Patrones:
- Repository Pattern: https://martinfowler.com/eaaCatalog/repository.html
- Dependency Injection: https://fastapi.tiangolo.com/tutorial/dependencies/

---

## 🎓 Conceptos para Investigar Más

1. **Alembic Migrations**: Sistema de versionado de esquemas de BD
2. **Unit of Work Pattern**: Gestión de transacciones
3. **Lazy Loading vs Eager Loading**: Optimización de queries
4. **N+1 Query Problem**: Problema común con ORM
5. **Database Indexing**: Optimización de búsquedas
6. **Connection Pooling**: Reutilización de conexiones
7. **Soft Delete**: Marcar como eliminado sin borrar físicamente

---

## 💡 Próximos Pasos Recomendados

1. **Ejecutar migración de usuarios**
   ```bash
   python scripts/migrate_users.py
   ```

2. **Probar endpoints actualizados**
   - POST /api/v1/user/ (crear)
   - GET /api/v1/user/ (listar)
   - GET /api/v1/user/{id} (detalle)

3. **Implementar BookORM y LoanORM**
   - Seguir mismo patrón que UserORM
   - Crear repositorios correspondientes

4. **Configurar Alembic**
   ```bash
   alembic init migrations
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

5. **Crear tests**
   ```python
   # test/test_users_repository.py
   def test_create_user(db_session):
       repo = UsersRepositorySQL(db_session)
       user = repo.create(...)
       assert user.id is not None
   ```

6. **Eliminar código legacy**
   - Quitar repositorios de archivos JSON
   - Limpiar imports no usados

---

## 🐛 Troubleshooting Común

### Error: "No such table: users"
**Solución:** Ejecutar `init_db()` antes de hacer queries
```python
from app.core.database import init_db
init_db()
```

### Error: "database is locked"
**Causa:** Múltiples conexiones simultáneas en SQLite
**Solución:** Usar `StaticPool` (ya configurado)

### Error: "password is None"
**Causa:** Olvidar hashear contraseña
**Solución:** 
```python
from app.domain.models.person import Person
hashed = Person._Person__hash_password(password)
```

### IDE no autocompleta atributos ORM
**Solución:** Agregar type hints
```python
user: UserORM = repo.read("123")
print(user.email)  # Ahora funciona autocompletado
```

---

## 📝 Notas Importantes

- Las contraseñas en JSON ya están hasheadas con `pbkdf2:sha256`
- Los campos `loans` y `historial` se manejarán con relaciones después
- `is_active` permite soft delete (no borrar físicamente)
- `created_at` y `updated_at` son automáticos
- Todos los métodos de repositorio manejan transacciones

---

## 🎯 Resumen Ejecutivo

**Problema:** API usando archivos JSON, difícil de escalar y consultar

**Solución:** Migrar a SQLite + SQLAlchemy

**Beneficios:**
- ✅ Queries más rápidas
- ✅ Integridad referencial
- ✅ Transacciones ACID
- ✅ Mejor escalabilidad
- ✅ Menos bugs con type safety

**Estado:** Infraestructura lista, usuarios implementados, pendiente libros y préstamos

---

## 📞 Preguntas Frecuentes Anticipadas

**P: ¿Se pierden los datos JSON al migrar?**
R: No, el script de migración los copia a BD, puedes mantener JSON como backup

**P: ¿Puedo volver a usar JSON?**
R: Sí, solo comenta las líneas de BD y descomenta el código legacy

**P: ¿Cómo hago búsquedas complejas?**
R: Con SQLAlchemy query:
```python
users = db.query(UserORM).filter(
    UserORM.email.like("%@example.com")
).all()
```

**P: ¿Cómo manejo relaciones (foreign keys)?**
R: Con `relationship()` en SQLAlchemy:
```python
class User(Base):
    loans = relationship("Loan", back_populates="user")
```

**P: ¿Qué pasa si cambio el modelo después?**
R: Usa Alembic para crear migraciones que actualicen la BD sin perder datos

---

**Fecha de este contexto:** 23 de enero de 2026  
**Versión del proyecto:** 2.0.0 (en desarrollo)  
**Estado:** Migración de usuarios completada, pendiente libros y préstamos
