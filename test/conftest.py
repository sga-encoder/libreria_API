import pytest
from fastapi.testclient import TestClient
from main import app
from uuid import uuid4


@pytest.fixture(scope="session")
def client():
    """TestClient compartido para la sesión de tests."""
    return TestClient(app)


@pytest.fixture
def unique_id():
    """Genera un id único para evitar colisiones entre tests."""
    return str(uuid4())


@pytest.fixture
def sample_book(unique_id):
    return {
        "id_IBSN": f"978-{unique_id[:8]}",
        "title": "Ejemplo",
        "author": "Autor",
        "gender": 1,
        "weight": 0.5,
        "price": 9.99,
        "is_borrowed": False,
    }


@pytest.fixture
def sample_user(unique_id):
    return {
        "id": f"user-{unique_id[:8]}",
        "name": "Test User",
        "email": f"test-{unique_id[:8]}@example.com",
        "password": "password123",
    }


@pytest.fixture
def sample_loan():
    return {
        # formato mínimo; los tests que lo usen deben completar campos necesarios
        "loanDate": None,
        "dueDate": None,
    }
