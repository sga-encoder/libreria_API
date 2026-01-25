"""Modelos ORM de SQLAlchemy para la base de datos.

Contiene todas las definiciones de tablas usando declarative_base.
Se importan en app/persistence/database.py para crear las tablas.
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, ForeignKey
from datetime import datetime
from app.core.database import Base

class UserORM(Base):
    __tablename__ = "users"
    
    id = Column(String(17), primary_key=True, index=True)
    fullName = Column(String(50), nullable=False)
    email = Column(String, unique=True, nullable=False,  index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="USER")
    loans = Column(JSON, default=list)
    historial = Column(JSON, default=list)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AdminORM(Base):
    __tablename__ = "admins"
    id = Column(String(17), primary_key=True, index=True)
    fullName = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String, default="ADMIN")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class BookORM(Base):
    __tablename__ = "books"
    
    id_IBSN = Column(String(13), primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    genre = Column(String)
    weight = Column(Float)
    price = Column(Float)
    is_borrowed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class LoanORM(Base):
    __tablename__ = "loans"
    
    id = Column(String(17), primary_key=True, index=True)
    id_user = Column(String(17), ForeignKey("users.id"), index=True)
    id_ISBN_book = Column(String(13), ForeignKey("books.id_IBSN"), index=True)
    loan_date = Column(DateTime, default=datetime.now)
    return_date = Column(DateTime, nullable=True)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)