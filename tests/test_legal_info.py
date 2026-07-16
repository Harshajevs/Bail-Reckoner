from app.services.ai.base import ProviderError, SectionFacts
from app.services.ai.rule_based import RuleBasedProvider


def test_bail_info_known_section(client):
    response = client.post("/api/get-bail-status", json={"charges": "IPC_302"})
    assert response.status_code == 200
    body = response.json()
    assert body["found_in_database"] is True
    assert body["provider"] == "rule_based"
    assert "IPC Section: IPC_302" in body["content"]
    assert "Bail Status: No" in body["content"]


def test_bail_info_bailable_section(client):
    response = client.post("/api/get-bail-status", json={"charges": "IPC_323"})
    body = response.json()
    assert body["found_in_database"] is True
    assert "Bail Status: Yes" in body["content"]
    assert "bailable" in body["content"].lower()


def test_bail_info_lowercase_input_normalized(client):
    response = client.post("/api/get-bail-status", json={"charges": "ipc_302"})
    assert response.status_code == 200
    assert response.json()["found_in_database"] is True


def test_bail_info_invalid_format_rejected(client):
    response = client.post("/api/get-bail-status", json={"charges": "Section 302"})
    assert response.status_code == 400


def test_bail_info_unknown_section_still_answers(client):
    response = client.post("/api/get-bail-status", json={"charges": "IPC_9999"})
    assert response.status_code == 200
    body = response.json()
    assert body["found_in_database"] is False
    assert body["content"]


def test_rule_based_provider_needs_facts():
    provider = RuleBasedProvider()
    facts = SectionFacts(
        section="IPC_302",
        bns_section="BNS_103",
        offense_type="Murder",
        bailable=False,
        bail_eligibility="Non-bailable",
        punishment="Life imprisonment",
    )
    text = provider.generate(facts, "IPC_302")
    assert "Life imprisonment" in text
    assert "non-bailable" in text.lower()

    try:
        provider.generate(None, "IPC_9999")
        raised = False
    except ProviderError:
        raised = True
    assert raised
