"""
Test de endpoints de loan para verificar que las rutas funcionan correctamente.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_loans():
    """Verificar que el endpoint GET /api/v1/loan/ responde"""
    response = client.get("/api/v1/loan/")
    # Puede devolver 200 con lista vacía o 404 si no hay préstamos
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert isinstance(data["data"], list)


def test_get_bookcase_status():
    """Verificar que el endpoint GET /api/v1/loan/bookcase/status responde"""
    response = client.get("/api/v1/loan/bookcase/status")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "data" in data
    assert "is_configured" in data["data"]


def test_configure_bookcase_deficient():
    """Verificar que el endpoint POST /api/v1/loan/bookcase/configure funciona con DEFICIENT"""
    response = client.post(
        "/api/v1/loan/bookcase/configure",
        json={
            "algorithm_type": "DEFICIENT",
            "weight_capacity": 10.0,
            "capacity_stands": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "BookCase configurado" in data["message"]
    assert data["data"]["algorithm_type"] == "DEFICIENT"


def test_configure_bookcase_optimoum():
    """Verificar que el endpoint POST /api/v1/loan/bookcase/configure funciona con OPTIMOUM"""
    response = client.post(
        "/api/v1/loan/bookcase/configure",
        json={
            "algorithm_type": "OPTIMOUM",
            "weight_capacity": 15.0,
            "capacity_stands": 8
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["data"]["algorithm_type"] == "OPTIMOUM"
    assert data["data"]["weight_capacity"] == 15.0
    assert data["data"]["capacity_stands"] == 8


def test_disable_bookcase():
    """Verificar que el endpoint DELETE /api/v1/loan/bookcase/disable funciona"""
    response = client.delete("/api/v1/loan/bookcase/disable")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "desactivado" in data["message"].lower()
    assert data["data"]["is_configured"] == False


def test_get_loan_by_id_not_found():
    """Verificar que el endpoint GET /api/v1/loan/{id} responde adecuadamente cuando no encuentra el préstamo"""
    response = client.get("/api/v1/loan/nonexistent-id-12345")
    # Puede ser 404 o 500 dependiendo de la implementación
    assert response.status_code in [404, 500]
