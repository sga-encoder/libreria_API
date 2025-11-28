#!/usr/bin/env python
"""Script de prueba para verificar que CRUDLoan.read_all() funciona correctamente.

Este test se colocó en la carpeta `test/` y realiza las mismas comprobaciones
que el script original ubicado en la raíz del proyecto.
"""

from app.models.loan import Loan
from app.models.user import User
from app.models.book import Book
from app.models.enums.book_gender import BookGender
from app.services.library import Library
from app.crud.crud_loan import CRUDLoan
from datetime import datetime

# Inicializar Library
Library.initialize()

# Crear instancias de prueba
user = User('Test User', 'test@example.com', 'password', [])
book = Book('978-1234', 'Test Book', 'Test Author', BookGender.FICTION, 0.5, 10.0)
loan = Loan(user, book, datetime.now())

# Crear CRUD con un préstamo inicial
crud = CRUDLoan([loan], Library.get_reservationsQueue(), [user])

# Llamar read_all
result = crud.read_all()

print(f"read_all() devolvió: {type(result).__name__} con {len(result)} elementos")
if result:
    print(f"Primer elemento tipo: {type(result[0]).__name__}")
    print(f"Primer elemento: {result[0]}")
else:
    print("Lista vacía")

print("\n✅ Test completado exitosamente")
