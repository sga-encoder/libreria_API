"""
Tests unitarios simples para LoanService con BookShelf.
Sin dependencias de repositorios reales.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from app.domain.services.loan_service import LoanService
from app.domain.structures import Queue
from app.domain.models import Book, User, Loan, BookCase, BookShelf
from app.domain.models.enums import TypeOrdering


@pytest.fixture
def mock_inventory_service():
    """Mock del InventoryService."""
    mock = Mock()
    mock.get_order_inventary.return_value = []
    mock.get_inventary.return_value = Mock()
    mock.get_inventary.return_value.to_list.return_value = []
    return mock


@pytest.fixture
def mock_loans_repository():
    """Mock del LoansRepository."""
    mock = Mock()
    # Simular que los préstamos se guardan
    stored_loans = {}
    
    def create_loan(data):
        loan = Mock(spec=Loan)
        loan.get_id.return_value = "loan-123"
        loan.get_user.return_value = data["user"]
        loan.get_book.return_value = data["book"]
        stored_loans["loan-123"] = loan
        return loan
    
    def read_loan(id):
        return stored_loans.get(id)
    
    def delete_loan(id):
        if id in stored_loans:
            del stored_loans[id]
            return True
        return False
    
    mock.create.side_effect = create_loan
    mock.read.side_effect = read_loan
    mock.delete.side_effect = delete_loan
    return mock


@pytest.fixture
def sample_books():
    """Libros de prueba."""
    books = []
    for i in range(3):
        book = Mock(spec=Book)
        book.get_id_IBSN.return_value = f"ISBN-{i}"
        book.get_title.return_value = f"Libro {i}"
        book.get_weight.return_value = 0.5 + i * 0.1
        book.get_is_borrowed.return_value = False
        book.set_is_borrowed = Mock()
        books.append(book)
    return books


@pytest.fixture
def sample_users():
    """Usuarios de prueba."""
    users = []
    for i in range(2):
        user = Mock(spec=User)
        user.get_id.return_value = f"user-{i}"
        user.get_loans.return_value = []
        user.add_loan = Mock()
        user.remove_loan = Mock()
        users.append(user)
    return users


@pytest.fixture
def bookcase_deficient():
    """BookCase tipo DEFICIENT."""
    bookcase = Mock(spec=BookCase)
    bookcase.get_TypeOrdering.return_value = TypeOrdering.DEFICIENT
    bookcase.get_weighOrdering.return_value = 2.0
    return bookcase


@pytest.fixture
def bookcase_optimum():
    """BookCase tipo OPTIMOUM."""
    bookcase = Mock(spec=BookCase)
    bookcase.get_TypeOrdering.return_value = TypeOrdering.OPTIMOUM
    bookcase.get_weighOrdering.return_value = 2.0
    return bookcase


class TestCreateLoanWithoutBookcase:
    """Tests para create_loan sin BookCase."""
    
    def test_create_loan_sin_bookcase(self, mock_loans_repository, mock_inventory_service, sample_books, sample_users):
        """Verifica que create_loan funciona sin BookCase."""
        # Setup
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        book.get_is_borrowed.return_value = False
        
        # Acción
        loan = service.create_loan(user, book)
        
        # Verificaciones
        assert loan is not None
        book.set_is_borrowed.assert_called_with(True)
        user.add_loan.assert_called_once()
        print("✓ create_loan sin bookcase funciona")
    
    def test_create_loan_libro_ya_prestado(self, mock_loans_repository, mock_inventory_service, sample_books, sample_users):
        """Verifica que no se crea préstamo si libro está prestado."""
        # Setup
        reservations_queue = Queue()
        service = LoanService(
            url="test",
            reservations_queue=reservations_queue,
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        book.get_is_borrowed.return_value = True  # Libro ya prestado
        
        # Acción
        loan = service.create_loan(user, book)
        
        # Verificaciones
        assert loan is None, "No debería crear préstamo de libro prestado"
        queue_items = reservations_queue.to_list()
        assert len(queue_items) == 1, "Debería estar en cola de espera"
        print("✓ Libro prestado va a cola de espera")


class TestCreateLoanWithBookcase:
    """Tests para create_loan con BookCase."""
    
    @patch('app.domain.services.loan_service.DeficientOrganizer')
    def test_create_loan_con_bookcase_deficient(self, mock_deficient, mock_loans_repository, mock_inventory_service, 
                                                 sample_books, sample_users, bookcase_deficient, capsys):
        """Verifica que se aplica algoritmo DEFICIENT."""
        # Setup
        mock_organizer_instance = Mock()
        mock_organizer_instance.organize.return_value = (Mock(), [])
        mock_deficient.return_value = mock_organizer_instance
        
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=bookcase_deficient
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        book.get_is_borrowed.return_value = False
        
        # Acción
        loan = service.create_loan(user, book)
        
        # Verificaciones
        assert loan is not None
        mock_deficient.assert_called_once_with(2.0)
        mock_organizer_instance.organize.assert_called_once()
        print("✓ create_loan con DEFICIENT aplica ordenamiento")
    
    @patch('app.domain.services.loan_service.estanteria_optima')
    def test_create_loan_con_bookcase_optimum(self, mock_optima, mock_loans_repository, mock_inventory_service,
                                               sample_books, sample_users, bookcase_optimum):
        """Verifica que se aplica algoritmo OPTIMOUM."""
        # Setup
        mock_optima.return_value = (0, None)
        
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=bookcase_optimum
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        book.get_is_borrowed.return_value = False
        
        # Acción
        loan = service.create_loan(user, book)
        
        # Verificaciones
        assert loan is not None
        mock_optima.assert_called_once()
        print("✓ create_loan con OPTIMOUM aplica ordenamiento")


class TestUpdateLoan:
    """Tests para update_loan."""
    
    def test_update_loan_sin_bookcase(self, mock_loans_repository, mock_inventory_service, sample_books, sample_users):
        """Verifica que update_loan funciona sin BookCase."""
        # Setup
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        old_book = sample_books[0]
        new_book = sample_books[1]
        
        # Crear préstamo inicial
        old_loan = Mock(spec=Loan)
        old_loan.get_user.return_value = user
        old_loan.get_book.return_value = old_book
        old_loan.get_id.return_value = "loan-old"
        
        mock_loans_repository.read.return_value = old_loan
        new_book.get_is_borrowed.return_value = False
        
        # Acción
        new_loan = service.update_loan("loan-old", new_book)
        
        # Verificaciones
        assert new_loan is not None
        assert old_book.set_is_borrowed.called
        assert new_book.set_is_borrowed.called
        print("✓ update_loan sin bookcase funciona")


class TestDeleteLoan:
    """Tests para delete_loan."""
    
    def test_delete_loan_sin_bookcase(self, mock_loans_repository, mock_inventory_service, sample_books, sample_users):
        """Verifica que delete_loan funciona sin BookCase."""
        # Setup
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        
        # Mock del préstamo a eliminar
        loan = Mock(spec=Loan)
        loan.get_user.return_value = user
        loan.get_book.return_value = book
        loan.get_id.return_value = "loan-123"
        
        mock_loans_repository.read.return_value = loan
        mock_loans_repository.delete.return_value = True
        
        # Acción
        result = service.delete_loan("loan-123")
        
        # Verificaciones
        assert result == True
        assert book.set_is_borrowed.called
        mock_loans_repository.delete.assert_called_once_with("loan-123")
        print("✓ delete_loan sin bookcase funciona")


class TestSetBookcase:
    """Tests para set_bookcase."""
    
    def test_set_bookcase(self, mock_loans_repository, mock_inventory_service, sample_users, bookcase_deficient):
        """Verifica que se puede establecer bookcase."""
        # Setup
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        
        # Verificar que inicia sin bookcase
        assert service._LoanService__bookcase is None
        
        # Acción
        service.set_bookcase(bookcase_deficient)
        
        # Verificación
        assert service._LoanService__bookcase == bookcase_deficient
        print("✓ set_bookcase funciona correctamente")


class TestUserLoans:
    """Tests para gestión de préstamos del usuario."""
    
    def test_user_add_loan_on_create(self, mock_loans_repository, mock_inventory_service, sample_books, sample_users):
        """Verifica que el usuario recibe el préstamo."""
        # Setup
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user = sample_users[0]
        book = sample_books[0]
        book.get_is_borrowed.return_value = False
        
        # Acción
        loan = service.create_loan(user, book)
        
        # Verificación
        user.add_loan.assert_called_once_with(loan)
        print("✓ Usuario recibe el préstamo en create_loan")


class TestWaitingQueue:
    """Tests para cola de espera."""
    
    def test_waiting_queue_on_borrowed_book(self, mock_loans_repository, mock_inventory_service, 
                                           sample_books, sample_users):
        """Verifica que la cola de espera se llena correctamente."""
        # Setup
        reservations_queue = Queue()
        service = LoanService(
            url="test",
            reservations_queue=reservations_queue,
            users=sample_users,
            inventory_service=mock_inventory_service,
            bookcase=None
        )
        service._LoanService__loans_repository = mock_loans_repository
        
        user1 = sample_users[0]
        user2 = sample_users[1]
        book = sample_books[0]
        
        # Crear primer préstamo
        book.get_is_borrowed.return_value = False
        loan1 = service.create_loan(user1, book)
        assert loan1 is not None
        
        # Intentar prestar el mismo libro
        book.get_is_borrowed.return_value = True
        loan2 = service.create_loan(user2, book)
        
        # Verificaciones
        assert loan2 is None, "No debe crearse segundo préstamo"
        queue_items = reservations_queue.to_list()
        assert len(queue_items) == 1, "Debe haber 1 item en cola"
        assert queue_items[0] == (user2, book), "Debe ser el usuario2 y libro correcto"
        print("✓ Cola de espera funciona correctamente")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
