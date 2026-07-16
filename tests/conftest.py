import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.seed import seed_legal_sections
from app.db.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_legal_sections(session)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # No context manager: lifespan is skipped so startup doesn't touch the
    # real database file.
    yield TestClient(app)
    app.dependency_overrides.clear()


PRISONER = {
    "role": "prisoner",
    "full_name": "Test Prisoner",
    "dob": "1990-01-01",
    "aadhar_number": "123456789012",
    "gender": "Male",
    "email": "prisoner@test.com",
    "password": "secret123",
    "address": "Test Lane",
    "phone_number": "9999999999",
    "occupation": "Labourer",
    "father_name": "Father",
    "father_aadhar": "111111111111",
    "mother_name": "Mother",
    "mother_aadhar": "222222222222",
}

LEGAL_AID = {
    "role": "legalAid",
    "full_name": "Adv Kumar",
    "dob": "1985-05-05",
    "aadhar_number": "333333333333",
    "gender": "Male",
    "email": "legal@test.com",
    "password": "secret123",
    "address": "Court Road",
    "designation": "Advocate",
    "license_number": "LIC123",
    "experience": 8,
    "contact_number": "8888888888",
    "working_location": "12.9716,77.5946",
    "legal_fee": 5000,
    "languages_known": "English,Hindi",
}

JUDICIAL = {
    "role": "judicial",
    "full_name": "Judge Rao",
    "dob": "1970-03-03",
    "aadhar_number": "444444444444",
    "gender": "Female",
    "email": "judge@test.com",
    "password": "secret123",
    "address": "High Court",
    "designation": "Judge",
    "license_number": "JLIC1",
    "experience": 20,
    "contact_number": "7777777777",
}

ONGOING_CASE = {
    "prisoner_id": 1,
    "aadhar_number": "123456789012",
    "case_number": "CASE001",
    "arrest_conditions": "Arrested at home",
    "charges": "IPC_379",
    "offense_date": "2024-01-10",
    "arrest_date": "2024-01-12",
    "bail_status": "Pending",
    "case_status": "Ongoing",
    "court_hearing_date": "2025-02-01",
    "case_summary": "Alleged theft",
}

COMPLETED_CASE = {
    "prisoner_id": 1,
    "aadhar_number": "123456789012",
    "case_number": "OLD1",
    "arrest_conditions": "NA",
    "charges": "IPC_420",
    "offense_date": "2020-01-01",
    "arrest_date": "2020-01-02",
    "bail_status": "Granted",
    "case_status": "Closed",
    "court_hearing_date": "2021-01-01",
    "judgement": "Acquitted for lack of evidence",
}


@pytest.fixture()
def prisoner_token(client):
    client.post("/api/register", json=PRISONER)
    response = client.post(
        "/api/login",
        json={"email": PRISONER["email"], "password": PRISONER["password"], "role": "prisoner"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(prisoner_token):
    return {"Authorization": f"Bearer {prisoner_token}"}
