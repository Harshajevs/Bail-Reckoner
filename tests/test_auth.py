from tests.conftest import JUDICIAL, LEGAL_AID, PRISONER


def test_register_all_roles(client):
    for payload in (PRISONER, LEGAL_AID, JUDICIAL):
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201, response.text
        assert response.json() == {"message": "Registration successful"}


def test_register_duplicate_email_rejected(client):
    assert client.post("/api/register", json=PRISONER).status_code == 201
    response = client.post("/api/register", json=PRISONER)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_invalid_role_rejected(client):
    response = client.post("/api/register", json={**PRISONER, "role": "hacker"})
    assert response.status_code == 400


def test_register_missing_role_fields_rejected(client):
    payload = {k: v for k, v in LEGAL_AID.items() if k != "working_location"}
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
    assert "working_location" in response.json()["detail"]


def test_login_returns_token_and_profile(client):
    client.post("/api/register", json=PRISONER)
    response = client.post(
        "/api/login",
        json={"email": PRISONER["email"], "password": PRISONER["password"], "role": "prisoner"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Login successful"
    assert body["name"] == PRISONER["full_name"]
    assert body["role"] == "prisoner"
    assert body["access_token"]


def test_login_wrong_password_rejected(client):
    client.post("/api/register", json=PRISONER)
    response = client.post(
        "/api/login",
        json={"email": PRISONER["email"], "password": "wrong", "role": "prisoner"},
    )
    assert response.status_code == 401


def test_login_role_alias_accepted(client):
    client.post("/api/register", json=LEGAL_AID)
    response = client.post(
        "/api/login",
        json={"email": LEGAL_AID["email"], "password": LEGAL_AID["password"], "role": "legalAid"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "legal_aid"


def test_protected_endpoint_requires_token(client):
    assert client.get("/api/pending-cases").status_code == 401


def test_protected_endpoint_rejects_bad_token(client):
    response = client.get(
        "/api/pending-cases", headers={"Authorization": "Bearer not-a-token"}
    )
    assert response.status_code == 401
