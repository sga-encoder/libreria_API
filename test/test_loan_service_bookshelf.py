"""
Tests para LoanService con integración de BookShelf.

Prueba:
1. create_loan - con y sin bookcase
2. update_loan - con y sin bookcase
3. delete_loan - con y sin bookcase
4. Verificación de is_borrowed
5. Verificación de inventario ordenado
6. Verificación de cola de reservas
"""

import pytest
from app.domain.services.loan_service import LoanService
from app.domain.services.inventory_service import InventoryService
from app.domain.structures import Queue, Stack
from app.domain.models import Book, User, Loan, BookCase, BookShelf
from app.domain.models.enums import TypeOrdering
from app.domain.repositories import LoansRepository, BooksRepository, UsersRepository
from datetime import datetime


@pytest.fixture
def books_repository(tmp_path):
    """Crea un repositorio de libros temporal para testing."""
    # Usar ruta temporal
    return BooksRepository(str(tmp_path / "books.json"))


@pytest.fixture
def loans_repository(tmp_path):
    """Crea un repositorio de préstamos temporal para testing."""
    return LoansRepository(str(tmp_path / "loans.json"))


@pytest.fixture
def users_repository(tmp_path):
    """Crea un repositorio de usuarios temporal para testing."""
    return UsersRepository(str(tmp_path / "users.json"))


@pytest.fixture
def inventory_service(books_repository):
    """Crea un servicio de inventario con libros de prueba."""
    service = InventoryService(str(books_repository._BooksRepository__url))
    return service


@pytest.fixture
def sample_books():
    """Crea libros de prueba."""
    return [
        Book(
            id_IBSN="978-0001",
            title="Libro 1",
            author="Autor 1",
            gender=1,
            weight=0.5,
            price=9.99,
            is_borrowed=False
        ),
        Book(
            id_IBSN="978-0002",
            title="Libro 2",
            author="Autor 2",
            gender=2,
            weight=0.6,
            price=12.99,
            is_borrowed=False
        ),
        Book(
            id_IBSN="978-0003",
            title="Libro 3",
            author="Autor 3",
            gender=3,
            weight=0.7,
            price=14.99,
            is_borrowed=False
        ),
    ]


@pytest.fixture
def sample_users():
    """Crea usuarios de prueba."""
    return [
        User(
            id="user-001",
            name="Usuario 1",
            email="user1@test.com",
            password="pass123",
            role=1
        ),
        User(
            id="user-002",
            name="Usuario 2",
            email="user2@test.com",
            password="pass123",
            role=1
        ),
    ]


@pytest.fixture
def bookcase_deficient():
    """Crea un bookcase con ordenamiento DEFICIENT."""
    return BookCase(
        stands=BookShelf(books=[]),
        TypeOrdering=TypeOrdering.DEFICIENT,
        weighCapacity=2.0,  # Capacidad limitada
        capacityStands=3,
        store=[]
    )


@pytest.fixture
def bookcase_optimum():
    """Crea un bookcase con ordenamiento OPTIMOUM."""
    return BookCase(
        stands=BookShelf(books=[]),
        TypeOrdering=TypeOrdering.OPTIMOUM,
        weighCapacity=2.0,
        capacityStands=3,
        store=[]
    )


class TestLoanServiceWithoutBookcase:
    """Tests de LoanService SIN bookcase."""

    def test_create_loan_sin_bookcase(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba crear un préstamo sin bookcase."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None  # SIN bookcase
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Acción
        loan = service.create(user, book)
        
        # Verificaciones
        assert loan is not None, "El préstamo debería haberse creado"
        assert loan.get_user() == user, "El usuario debería coincidir"
        assert loan.get_book() == book, "El libro debería coincidir"
        assert book.get_is_borrowed() == True, "El libro debería marcarse como prestado"
        print("✓ create_loan sin bookcase funciona correctamente")

    def test_update_loan_sin_bookcase(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba actualizar un préstamo sin bookcase."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        old_book = sample_books[0]
        new_book = sample_books[1]
        
        # Crear préstamo inicial
        loan = service.create(user, old_book)
        assert loan is not None
        loan_id = loan.get_id()
        
        # Acción: Actualizar préstamo
        updated_loan = service.update(loan_id, new_book)
        
        # Verificaciones
        assert updated_loan is not None, "El préstamo actualizado debería existir"
        assert updated_loan.get_book() == new_book, "El nuevo libro debería estar en el préstamo"
        assert new_book.get_is_borrowed() == True, "El nuevo libro debería estar prestado"
        assert old_book.get_is_borrowed() == False, "El libro antiguo debería estar disponible"
        print("✓ update_loan sin bookcase funciona correctamente")

    def test_delete_loan_sin_bookcase(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba eliminar un préstamo sin bookcase."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Crear préstamo
        loan = service.create(user, book)
        assert loan is not None
        loan_id = loan.get_id()
        assert book.get_is_borrowed() == True
        
        # Acción: Eliminar préstamo
        result = service.delete(loan_id)
        
        # Verificaciones
        assert result == True, "La eliminación debería retornar True"
        assert book.get_is_borrowed() == False, "El libro debería volver a estar disponible"
        print("✓ delete_loan sin bookcase funciona correctamente")


class TestLoanServiceWithBookcase:
    """Tests de LoanService CON bookcase."""

    def test_create_loan_con_bookcase_deficient(self, loans_repository, inventory_service, sample_books, sample_users, bookcase_deficient, capsys):
        """Prueba crear un préstamo con bookcase DEFICIENT."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=bookcase_deficient
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Acción
        loan = service.create(user, book)
        
        # Verificaciones
        assert loan is not None, "El préstamo debería haberse creado"
        assert book.get_is_borrowed() == True, "El libro debería marcarse como prestado"
        
        # Verificar que se aplicó el ordenamiento
        captured = capsys.readouterr()
        assert "DEFICIENT" in captured.out or "organizados" in captured.out or "Libros" in captured.out, \
            "El algoritmo DEFICIENT debería haberse aplicado"
        print("✓ create_loan con bookcase DEFICIENT funciona correctamente")

    def test_create_loan_con_bookcase_optimum(self, loans_repository, inventory_service, sample_books, sample_users, bookcase_optimum, capsys):
        """Prueba crear un préstamo con bookcase OPTIMOUM."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=bookcase_optimum
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Acción
        loan = service.create(user, book)
        
        # Verificaciones
        assert loan is not None, "El préstamo debería haberse creado"
        assert book.get_is_borrowed() == True
        
        # Verificar que se aplicó el ordenamiento
        captured = capsys.readouterr()
        assert "OPTIMOUM" in captured.out or "óptimo" in captured.out or "Valor" in captured.out, \
            "El algoritmo OPTIMOUM debería haberse aplicado"
        print("✓ create_loan con bookcase OPTIMOUM funciona correctamente")

    def test_update_loan_con_bookcase(self, loans_repository, inventory_service, sample_books, sample_users, bookcase_deficient, capsys):
        """Prueba actualizar un préstamo con bookcase."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=bookcase_deficient
        )
        
        user = sample_users[0]
        old_book = sample_books[0]
        new_book = sample_books[1]
        
        # Crear préstamo inicial
        loan = service.create(user, old_book)
        assert loan is not None
        loan_id = loan.get_id()
        
        # Limpiar captura previa
        capsys.readouterr()
        
        # Acción: Actualizar préstamo
        updated_loan = service.update(loan_id, new_book)
        
        # Verificaciones
        assert updated_loan is not None
        assert updated_loan.get_book() == new_book
        
        # Verificar que se aplicó el ordenamiento (dos veces: agregar antiguo y remover nuevo)
        captured = capsys.readouterr()
        count = captured.out.count("DEFICIENT")
        assert count >= 2 or "organizados" in captured.out, \
            "El algoritmo debería haberse aplicado al menos dos veces"
        print("✓ update_loan con bookcase funciona correctamente")

    def test_delete_loan_con_bookcase(self, loans_repository, inventory_service, sample_books, sample_users, bookcase_deficient, capsys):
        """Prueba eliminar un préstamo con bookcase."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=bookcase_deficient
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Crear préstamo
        loan = service.create(user, book)
        assert loan is not None
        loan_id = loan.get_id()
        
        # Limpiar captura previa
        capsys.readouterr()
        
        # Acción: Eliminar préstamo
        result = service.delete(loan_id)
        
        # Verificaciones
        assert result == True
        assert book.get_is_borrowed() == False
        
        # Verificar que se aplicó el ordenamiento
        captured = capsys.readouterr()
        assert "DEFICIENT" in captured.out or "organizados" in captured.out or "Libros" in captured.out, \
            "El algoritmo DEFICIENT debería haberse aplicado"
        print("✓ delete_loan con bookcase funciona correctamente")


class TestLoanServiceInventoryManagement:
    """Tests para verificar la gestión del inventario ordenado."""

    def test_inventario_ordenado_se_actualiza_create(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba que el inventario ordenado se actualiza al crear préstamo."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Estado inicial del inventario
        initial_count = len(inventory_service.get_order_inventary())
        
        # Acción
        loan = service.create(user, book)
        
        # Verificación
        final_count = len(inventory_service.get_order_inventary())
        assert final_count < initial_count, "El libro debería removerse del inventario ordenado"
        assert book not in inventory_service.get_order_inventary(), "El libro no debería estar en inventario"
        print("✓ Inventario ordenado se actualiza correctamente en create_loan")

    def test_inventario_ordenado_se_actualiza_delete(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba que el inventario ordenado se actualiza al eliminar préstamo."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Crear préstamo
        loan = service.create(user, book)
        loan_id = loan.get_id()
        count_after_create = len(inventory_service.get_order_inventary())
        
        # Acción: Eliminar préstamo
        service.delete(loan_id)
        
        # Verificación
        count_after_delete = len(inventory_service.get_order_inventary())
        assert count_after_delete > count_after_create, "El libro debería añadirse al inventario ordenado"
        assert book in inventory_service.get_order_inventary(), "El libro debería estar en inventario"
        print("✓ Inventario ordenado se actualiza correctamente en delete_loan")


class TestLoanServiceUserLoans:
    """Tests para verificar la gestión de préstamos del usuario."""

    def test_usuario_tiene_prestamo_after_create(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba que el usuario tiene el préstamo después de crear."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Acción
        loan = service.create(user, book)
        
        # Verificación
        assert loan in user.get_loans(), "El préstamo debería estar en la lista del usuario"
        print("✓ Usuario tiene el préstamo después de create_loan")

    def test_usuario_no_tiene_prestamo_after_delete(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba que el usuario no tiene el préstamo después de eliminar."""
        # Setup
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Crear préstamo
        loan = service.create(user, book)
        loan_id = loan.get_id()
        assert loan in user.get_loans()
        
        # Acción: Eliminar préstamo
        service.delete(loan_id)
        
        # Verificación
        assert loan not in user.get_loans(), "El préstamo no debería estar en la lista del usuario"
        print("✓ Usuario no tiene el préstamo después de delete_loan")


class TestLoanServiceWaitingQueue:
    """Tests para verificar la cola de reservas."""

    def test_libro_prestado_va_a_cola_de_espera(self, loans_repository, inventory_service, sample_books, sample_users):
        """Prueba que un libro prestado se añade a la cola de espera."""
        # Setup
        reservations_queue = Queue()
        service = LoanService(
            url_history_loans=str(loans_repository._LoansRepository__url),
            reservations_queue=reservations_queue,
            users=sample_users,
            inventory_service=inventory_service,
            bookcase=None
        )
        
        user1 = sample_users[0]
        user2 = sample_users[1]
        book = sample_books[0]
        
        # Crear primer préstamo
        loan1 = service.create(user1, book)
        assert loan1 is not None
        assert book.get_is_borrowed() == True
        
        # Acción: Intentar prestar el mismo libro a otro usuario
        loan2 = service.create(user2, book)
        
        # Verificación
        assert loan2 is None, "No debería crearse el segundo préstamo"
        queue_items = reservations_queue.to_list()
        assert len(queue_items) > 0, "Debería haber items en la cola de espera"
        assert (user2, book) in queue_items, "El usuario y libro deberían estar en la cola de espera"
        print("✓ Cola de espera funciona correctamente")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
