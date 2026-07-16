from tests.conftest import COMPLETED_CASE, LEGAL_AID, ONGOING_CASE


def add_ongoing(client, headers, **overrides):
    return client.post(
        "/api/add-ongoing-case", json={**ONGOING_CASE, **overrides}, headers=headers
    )


def test_add_and_list_ongoing_case(client, auth_headers):
    assert add_ongoing(client, auth_headers).status_code == 201
    response = client.get("/api/ongoing-cases", headers=auth_headers)
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 1
    assert cases[0]["case_number"] == ONGOING_CASE["case_number"]
    assert cases[0]["opinion"] is None


def test_add_completed_and_historical_search(client, auth_headers):
    response = client.post(
        "/api/add-completed-case", json=COMPLETED_CASE, headers=auth_headers
    )
    assert response.status_code == 201

    response = client.post(
        "/api/historical-cases", json={"ipcs": ["IPC_420"]}, headers=auth_headers
    )
    matches = response.json()["matching_cases"]
    assert len(matches) == 1
    assert matches[0]["judgement"] == COMPLETED_CASE["judgement"]

    response = client.post(
        "/api/historical-cases", json={"ipcs": ["IPC_999"]}, headers=auth_headers
    )
    assert response.json() == {"message": "No historical cases found for the provided IPCs."}


def test_validate_aadhar_returns_case(client, auth_headers):
    add_ongoing(client, auth_headers)
    response = client.get(
        f"/api/validate-aadhar/{ONGOING_CASE['aadhar_number']}", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["case_number"] == ONGOING_CASE["case_number"]
    assert body["charges"] == ONGOING_CASE["charges"]


def test_validate_aadhar_unknown_prisoner(client, auth_headers):
    response = client.get("/api/validate-aadhar/000000000000", headers=auth_headers)
    assert response.status_code == 400


def test_counts_and_all_cases(client, auth_headers):
    add_ongoing(client, auth_headers)
    client.post("/api/add-completed-case", json=COMPLETED_CASE, headers=auth_headers)

    aadhar = ONGOING_CASE["aadhar_number"]
    assert client.get(f"/api/ongoing-cases/{aadhar}", headers=auth_headers).json() == {"count": 1}
    assert client.get(f"/api/completed-cases/{aadhar}", headers=auth_headers).json() == {"count": 1}

    body = client.get(f"/api/all-cases/{aadhar}", headers=auth_headers).json()
    assert len(body["ongoing_cases"]) == 1
    assert len(body["completed_cases"]) == 1


def test_take_up_case_assigns_provider_id(client, auth_headers):
    client.post("/api/register", json=LEGAL_AID)
    add_ongoing(client, auth_headers)

    response = client.post(
        "/api/take-up-case/1",
        json={"prisoner_lawyer": LEGAL_AID["full_name"], "license_number": "LIC123"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    pending = client.get("/api/pending-cases", headers=auth_headers).json()
    assert pending == []

    case = client.get("/api/ongoing-cases", headers=auth_headers).json()[0]
    # Provider *id* is stored, not the license string (legacy type bug fixed)
    assert case["legal_aid_provider_id"] == 1
    assert case["prisoner_lawyer"] == LEGAL_AID["full_name"]


def test_take_up_case_unknown_license(client, auth_headers):
    add_ongoing(client, auth_headers)
    response = client.post(
        "/api/take-up-case/1",
        json={"prisoner_lawyer": "Nobody", "license_number": "NOPE"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_opinion_flow(client, auth_headers):
    add_ongoing(client, auth_headers)

    pending = client.get("/api/pending-opinions", headers=auth_headers).json()
    assert len(pending) == 1

    response = client.post(
        "/api/submit-opinion/1", json={"opinion": "Grant bail"}, headers=auth_headers
    )
    assert response.status_code == 200

    assert client.get("/api/pending-opinions", headers=auth_headers).json() == []
    case = client.get("/api/ongoing-cases", headers=auth_headers).json()[0]
    assert case["opinion"] == "Grant bail"


def test_suggestion_flow(client, auth_headers):
    add_ongoing(client, auth_headers)
    response = client.post(
        "/api/suggestion/1", json={"suggestion": "Collect witness affidavits"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    case = client.get("/api/ongoing-cases", headers=auth_headers).json()[0]
    assert case["suggestions"] == "Collect witness affidavits"
