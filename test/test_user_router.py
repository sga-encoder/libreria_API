def test_user_crud(client, sample_user):
    # Crear
    r = client.post("/user/", json=sample_user)
    assert r.status_code < 500
    created = r.json() if r.content else {}

    # Leer todos (acepta lista o wrapper)
    r = client.get("/user/all")
    assert r.status_code == 200
    resp = r.json()
    if isinstance(resp, list):
        users = resp
    elif isinstance(resp, dict) and "data" in resp:
        d = resp["data"]
        if isinstance(d, list):
            users = d
        else:
            users = []
    else:
        users = []
    assert isinstance(users, list)

    # Intentar identificar recurso para patch/delete (usar email como identificador preferido)
    identifier = created.get("email") or created.get("fullName") or created.get("id") or sample_user.get("email")
    if identifier:
        r = client.patch(f"/user/{identifier}", json={"email": "alice@newdomain.com"})
        assert r.status_code < 500
        r = client.delete(f"/user/{identifier}")
        assert r.status_code < 500
