def test_index_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_all_pages_served(client):
    for page in ("login", "register", "home", "about", "guest", "find_advocate",
                 "undertrial_prisoner", "legal_aid_provider", "judicial_authority",
                 "historical_cases", "risk_assignment"):
        response = client.get(f"/{page}")
        assert response.status_code == 200, page


def test_unknown_page_404(client):
    assert client.get("/no-such-page").status_code == 404


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
