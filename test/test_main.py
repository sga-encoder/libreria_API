def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    # La app devuelve un mensaje de bienvenida en español
    assert isinstance(response.json(), dict)
    assert "message" in response.json()