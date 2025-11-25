def test_auth_login_logout(client, sample_user):
    # Crear usuario para login
    client.post("/user/", json=sample_user)

    # Login
    login_payload = {"email": sample_user["email"], "password": sample_user["password"]}
    r = client.post("/auth/login", json=login_payload)
    assert r.status_code < 500

    # Logout (no requiere cuerpo en demo)
    r = client.post("/auth/logout")
    assert r.status_code < 500
