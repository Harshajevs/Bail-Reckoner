from tests.conftest import LEGAL_AID


def test_nearest_providers_ranked_by_distance(client):
    client.post("/api/register", json=LEGAL_AID)  # Bengaluru
    far_provider = {
        **LEGAL_AID,
        "email": "delhi@test.com",
        "license_number": "LIC999",
        "working_location": "28.6139,77.2090",  # Delhi
    }
    client.post("/api/register", json=far_provider)

    response = client.post(
        "/api/get-nearest-providers",
        json={"latitude": 12.97, "longitude": 77.59, "maxAdvocateFee": 10000, "minExperience": 2},
    )
    assert response.status_code == 200
    providers = response.json()
    assert len(providers) == 2
    assert providers[0]["email"] == LEGAL_AID["email"]
    assert providers[0]["distance"] < providers[1]["distance"]


def test_nearest_providers_filters(client):
    client.post("/api/register", json=LEGAL_AID)
    response = client.post(
        "/api/get-nearest-providers",
        json={"latitude": 12.97, "longitude": 77.59, "maxAdvocateFee": 100, "minExperience": 0},
    )
    assert response.json() == []

    response = client.post(
        "/api/get-nearest-providers",
        json={"latitude": 12.97, "longitude": 77.59, "minExperience": 50},
    )
    assert response.json() == []


def test_provider_location(client):
    client.post("/api/register", json=LEGAL_AID)
    response = client.get("/api/get-provider-location/1")
    assert response.status_code == 200
    body = response.json()
    assert abs(body["latitude"] - 12.9716) < 1e-6
    assert abs(body["longitude"] - 77.5946) < 1e-6


def test_provider_location_not_found(client):
    assert client.get("/api/get-provider-location/99").status_code == 404
