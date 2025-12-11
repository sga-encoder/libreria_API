import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.security import create_access_token
from app.domain.models.enums import PersonRole
from app.core import settings
import os

# Configurar SECRET_KEY para tests
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
settings.SECRET_KEY = 'test-secret-key-for-testing-only'

client = TestClient(app)


def test_create_bookcase_without_auth():
    """Debe fallar sin autenticación"""
    response = client.post(
        "/api/v1/admin/bookcase",
        json={
            "typeOrdering": "OPTIMOUM",
            "weighCapacity": 500.0,
            "capacityStands": 5
        }
    )
    assert response.status_code == 401


def test_create_bookcase_with_admin_auth():
    """Debe crear bookcase con autenticación de admin"""
    # Crear token de admin
    token = create_access_token(
        data={"sub": "admin@test.com", "role": PersonRole.ADMIN.name}
    )
    
    response = client.post(
        "/api/v1/admin/bookcase",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "typeOrdering": "OPTIMOUM",
            "weighCapacity": 500.0,
            "capacityStands": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Bookcase creado satisfactoriamente"
    assert data["data"]["typeOrdering"] == "OPTIMOUM"
    assert data["data"]["weighCapacity"] == 500.0
    assert data["data"]["capacityStands"] == 5


def test_create_bookcase_deficient():
    """Debe crear bookcase con ordenamiento DEFICIENT"""
    token = create_access_token(
        data={"sub": "admin@test.com", "role": PersonRole.ADMIN.name}
    )
    
    response = client.post(
        "/api/v1/admin/bookcase",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "typeOrdering": "DEFICIENT",
            "weighCapacity": 300.0,
            "capacityStands": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["typeOrdering"] == "DEFICIENT"


def test_create_bookcase_invalid_type():
    """Debe fallar con tipo de ordenamiento inválido"""
    token = create_access_token(
        data={"sub": "admin@test.com", "role": PersonRole.ADMIN.name}
    )
    
    response = client.post(
        "/api/v1/admin/bookcase",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "typeOrdering": "INVALIDO",
            "weighCapacity": 400.0,
            "capacityStands": 4
        }
    )
    
    assert response.status_code == 400
    assert "typeOrdering debe ser" in response.json()["detail"]


def test_create_bookcase_with_user_token():
    """Debe fallar con token de usuario normal (no admin)"""
    token = create_access_token(
        data={"sub": "user@test.com", "role": PersonRole.USER.name}
    )
    
    response = client.post(
        "/api/v1/admin/bookcase",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "typeOrdering": "OPTIMOUM",
            "weighCapacity": 500.0,
            "capacityStands": 5
        }
    )
    
    assert response.status_code == 403  # Forbidden
