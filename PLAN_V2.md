# 📋 Plan de Desarrollo - Versión 2.0

**Fecha de Inicio:** 17 de enero de 2026  
**Objetivo:** Migrar arquitectura de persistencia JSON/CSV a PostgreSQL con SQLAlchemy

---

## 🎯 Opción Seleccionada

- **BD:** PostgreSQL
- **ORM:** SQLAlchemy
- **Hosting:** Vercel, Railway o Render
- **Migraciones:** Alembic

---

## 📦 Fase 1: Preparación (Semana 1)

### 1.1 Instalar Dependencias
```bash
pip install sqlalchemy psycopg2-binary alembic python-dotenv
```

### 1.2 Crear Estructura de Persistencia
```
app/
├── persistence/              # NUEVA CAPA
│   ├── __init__.py
│   ├── database.py           # Motor de BD
│   ├── models_orm.py         # Modelos SQLAlchemy
│   └── repositories/
│       ├── __init__.py
│       ├── base_repository.py
│       ├── books_repository.py
│       ├── users_repository.py
│       └── loans_repository.py
```

### 1.3 Configurar Variables de Entorno
Crear `.env`:
```env
# Desarrollo Local
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/library_db

# O usar SQLite para desarrollo rápido
# DATABASE_URL=sqlite:///./library.db

# Variables de seguridad (mantener)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

### 1.4 Inicializar Alembic
```bash
alembic init alembic
```

---

## 🗄️ Fase 2: Modelado de Datos (Semana 1-2)

### 2.1 Crear Modelos ORM
**Archivo:** `app/persistence/models_orm.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class BookORM(Base):
    __tablename__ = "books"
    
    id_IBSN = Column(String(20), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    weight = Column(Float)
    price = Column(Float)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    loans = relationship("LoanORM", back_populates="book", cascade="all, delete-orphan")

class UserORM(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, index=True)
    fullName = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255))
    role = Column(String(20), default="USER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    loans = relationship("LoanORM", back_populates="user", cascade="all, delete-orphan")

class LoanORM(Base):
    __tablename__ = "loans"
    
    id = Column(String(50), primary_key=True, index=True)
    id_user = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    id_ISBN_book = Column(String(20), ForeignKey("books.id_IBSN"), nullable=False, index=True)
    loan_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime)
    due_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserORM", back_populates="loans")
    book = relationship("BookORM", back_populates="loans")
```

### 2.2 Crear Motor de BD
**Archivo:** `app/persistence/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./library.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crear tablas al iniciar"""
    from app.persistence.models_orm import Base
    Base.metadata.create_all(bind=engine)
```

### 2.3 Crear Repositorio Base
**Archivo:** `app/persistence/repositories/base_repository.py`

```python
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, List, Optional

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

---

## 📚 Fase 3: Repositorios Específicos (Semana 2)

### 3.1 Books Repository
**Archivo:** `app/persistence/repositories/books_repository.py`

```python
from sqlalchemy.orm import Session
from app.persistence.models_orm import BookORM
from app.persistence.repositories.base_repository import BaseRepository

class BooksRepository(BaseRepository[BookORM]):
    def __init__(self, db: Session):
        super().__init__(db, BookORM)
    
    def read_by_title(self, title: str) -> list[BookORM]:
        return self.db.query(BookORM).filter(
            BookORM.title.ilike(f"%{title}%")
        ).all()
    
    def read_by_author(self, author: str) -> list[BookORM]:
        return self.db.query(BookORM).filter(
            BookORM.author.ilike(f"%{author}%")
        ).all()
```

### 3.2 Users Repository
**Archivo:** `app/persistence/repositories/users_repository.py`

```python
from sqlalchemy.orm import Session
from app.persistence.models_orm import UserORM
from app.persistence.repositories.base_repository import BaseRepository

class UsersRepository(BaseRepository[UserORM]):
    def __init__(self, db: Session):
        super().__init__(db, UserORM)
    
    def read_by_email(self, email: str) -> UserORM | None:
        return self.db.query(UserORM).filter(UserORM.email == email).first()
    
    def read_active(self) -> list[UserORM]:
        return self.db.query(UserORM).filter(UserORM.is_active == True).all()
```

### 3.3 Loans Repository
**Archivo:** `app/persistence/repositories/loans_repository.py`

```python
from sqlalchemy.orm import Session
from app.persistence.models_orm import LoanORM
from app.persistence.repositories.base_repository import BaseRepository

class LoansRepository(BaseRepository[LoanORM]):
    def __init__(self, db: Session):
        super().__init__(db, LoanORM)
    
    def read_by_user(self, user_id: str) -> list[LoanORM]:
        return self.db.query(LoanORM).filter(
            LoanORM.id_user == user_id,
            LoanORM.is_active == True
        ).all()
    
    def read_active_loans(self) -> list[LoanORM]:
        return self.db.query(LoanORM).filter(
            LoanORM.is_active == True
        ).all()
```

---

## 🔄 Fase 4: Actualizar Servicios (Semana 2-3)

### 4.1 Inyectar Dependencias
**Actualizar:** `app/dependencies.py`

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.persistence.database import get_db
from app.persistence.repositories.books_repository import BooksRepository
from app.persistence.repositories.users_repository import UsersRepository
from app.persistence.repositories.loans_repository import LoansRepository

def get_books_repo(db: Session = Depends(get_db)) -> BooksRepository:
    return BooksRepository(db)

def get_users_repo(db: Session = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db)

def get_loans_repo(db: Session = Depends(get_db)) -> LoansRepository:
    return LoansRepository(db)
```

### 4.2 Actualizar Servicios de Dominio
Los servicios que usaban `FileManager` ahora usan repositorios:

```python
# Antes
from app.utils.file_manager import FileManager

# Ahora
from app.persistence.repositories.books_repository import BooksRepository

class BookCaseService:
    def __init__(self, repository: BooksRepository):
        self.repository = repository
```

---

## 🚀 Fase 5: Actualizar Endpoints (Semana 3)

### 5.1 Rutas de Libros
**Actualizar:** `app/api/v1/books/routes.py`

```python
from fastapi import APIRouter, Depends
from app.persistence.repositories.books_repository import BooksRepository

router = APIRouter()

@router.get("/")
async def get_all_books(repo: BooksRepository = Depends(get_books_repo)):
    return repo.read_all()

@router.get("/{id}")
async def get_book(id: str, repo: BooksRepository = Depends(get_books_repo)):
    book = repo.read(id)
    if not book:
        raise HTTPException(status_code=404)
    return book

@router.post("/")
async def create_book(data: BookSchema, repo: BooksRepository = Depends(get_books_repo)):
    return repo.create(**data.dict())
```

---

## 📊 Fase 6: Migraciones de Datos (Semana 3-4)

### 6.1 Script de Migración
**Crear:** `scripts/migrate_data.py`

```python
import json
from app.persistence.database import SessionLocal
from app.persistence.models_orm import BookORM, UserORM, LoanORM

def migrate_books():
    with open("data/json/books.json", "r") as f:
        books = json.load(f)
    
    db = SessionLocal()
    for book in books:
        existing = db.query(BookORM).filter(
            BookORM.id_IBSN == book["id_IBSN"]
        ).first()
        if not existing:
            db.add(BookORM(**book))
    db.commit()

def migrate_users():
    # Similar a migrate_books
    pass

def migrate_loans():
    # Similar a migrate_books
    pass

if __name__ == "__main__":
    migrate_books()
    migrate_users()
    migrate_loans()
    print("✅ Migración completada")
```

---

## 🧪 Fase 7: Testing (Semana 4)

### 7.1 Fixtures para Testing
**Actualizar:** `test/conftest.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.persistence.models_orm import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
```

---

## ☁️ Fase 8: Deployment (Semana 4)

### 8.1 Preparar para Producción

#### Opción A: Vercel
```bash
# Crear vercel.json
{
  "buildCommand": "pip install -r requirements.txt",
  "devCommand": "uvicorn app.main:app --reload",
  "outputDirectory": "."
}
```

#### Opción B: Railway
```bash
# Conectar repo
railway login
railway link
railway up
```

#### Opción C: Render
```bash
# Crear build.sh
#!/bin/bash
pip install -r requirements.txt
alembic upgrade head
```

### 8.2 Actualizar requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
python-dotenv==1.0.0
pydantic==2.5.0
```

### 8.3 Variables de Entorno en Servidor
```
DATABASE_URL=postgresql://user:pass@host:5432/library_db
SECRET_KEY=your-production-secret-key
ALGORITHM=HS256
```

---

## 📝 Checklist Final

- [ ] Estructura de persistencia creada
- [ ] Modelos ORM definidos
- [ ] Repositorios implementados
- [ ] Dependencias actualizadas
- [ ] Endpoints migrando a BD
- [ ] Tests con BD en memoria
- [ ] Datos migrados desde JSON/CSV
- [ ] Variables de entorno configuradas
- [ ] Alembic configurado
- [ ] Desplegado en servidor gratuito
- [ ] Documentación actualizada

---

## 🔗 Referencias Útiles

- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Alembic:** https://alembic.sqlalchemy.org/
- **PostgreSQL:** https://www.postgresql.org/
- **Vercel:** https://vercel.com
- **Railway:** https://railway.app
- **Render:** https://render.com

---

**Estimación Total:** 2-3 semanas de desarrollo

**Próximos Pasos:** Crear rama `develop` → `feature/sql-migration` → Implementar Fase 1
