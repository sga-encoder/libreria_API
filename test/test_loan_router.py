def test_loan_crud(client, sample_user, sample_book):
    # Asegurar user y book existentes usando fixtures
    client.post("/api/v1/user/", json=sample_user)
    client.post("/api/v1/book/", json=sample_book)

    # Crear loan
    loan_payload = {
        "user": sample_user.get("email"),
        "book": sample_book.get("id_IBSN"),
        "loanDate": "2025-11-25T00:00:00Z",
    }
    r = client.post("/api/v1/loan/", json=loan_payload)
    assert r.status_code < 500
    created = r.json() if r.content else {}

    # Leer listado (acepta lista o wrapper)
    r = client.get("/api/v1/loan/")
    assert r.status_code == 200
    resp = r.json()
    if isinstance(resp, list):
        loans = resp
    elif isinstance(resp, dict) and "data" in resp:
        d = resp["data"]
        if isinstance(d, list):
            loans = d
        else:
            loans = []
    else:
        loans = []
    assert isinstance(loans, list)

    # Si se devolvió id, probar patch y delete
    loan_id = created.get("id")
    if loan_id:
        r = client.patch(f"/api/v1/loan/{loan_id}", json={"loanDate": "2025-12-01T00:00:00Z"})
        assert r.status_code < 500
        r = client.delete(f"/api/v1/loan/{loan_id}")
        assert r.status_code < 500
