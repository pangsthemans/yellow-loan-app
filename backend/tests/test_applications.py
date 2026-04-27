import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Use SQLite in memory for tests - no Postgres needed
# It might be better to create a docker postgres database 
# however for the interest of time i will create a sqlite db for this 
# first iteration
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Override the database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


# ── SA ID Validation ──────────────────────────────────────────────────────────

def test_valid_sa_id():
    res = client.post("/applications/validate-id", json={"id_number": "9001155001083"})
    assert res.status_code == 200
    assert res.json()["valid"] == True
    assert res.json()["age"] == 36

def test_invalid_luhn():
    res = client.post("/applications/validate-id", json={"id_number": "9001155001084"})
    assert res.status_code == 200
    assert res.json()["valid"] == False

def test_too_short_id():
    res = client.post("/applications/validate-id", json={"id_number": "123456789"})
    assert res.status_code == 422  # Pydantic catches this

def test_underage_applicant():
    # Born 2010 - too young
    res = client.post("/applications/validate-id", json={"id_number": "1001015001085"})
    assert res.status_code == 200
    assert res.json()["valid"] == False
    assert "failed checksum validation" in res.json()["error"]

def test_overage_applicant():
    # Born 1955 - too old (over 65)
    res = client.post("/applications/validate-id", json={"id_number": "5506015001083"})
    assert res.status_code == 200
    assert res.json()["valid"] == False


# ── Phone seeding + listing ───────────────────────────────────────────────────

def test_phones_seed_and_list():
    # Seed phones
    res = client.post("/phones/seed")
    assert res.status_code == 200

    # List with risk group 1
    res = client.get("/phones/?risk_group=1")
    assert res.status_code == 200
    phones = res.json()
    assert len(phones) > 0
    assert "daily_payment" in phones[0]
    assert "loan_amount" in phones[0]

def test_phone_pricing_differs_by_risk_group():
    client.post("/phones/seed")
    group1 = client.get("/phones/?risk_group=1").json()
    group3 = client.get("/phones/?risk_group=3").json()
    # Group 3 has higher interest so daily payment should be higher
    assert group3[0]["daily_payment"] > group1[0]["daily_payment"]

def test_affordability_filter():
    client.post("/phones/seed")
    # Very low income - all phones should be unaffordable
    res = client.get("/phones/?risk_group=1&monthly_income=100")
    phones = res.json()
    assert all(p["affordable"] == False for p in phones)


# ── Full application submission ───────────────────────────────────────────────

def test_submit_valid_application():
    client.post("/phones/seed")
    phones = client.get("/phones/?risk_group=1").json()
    cheapest = min(phones, key=lambda p: p["cash_price"])

    res = client.post("/applications/", json={
        "first_name": "Thabo",
        "last_name": "Nkosi",
        "id_number": "9001155001083",
        "date_of_birth": "1990-01-15",
        "monthly_income": 50000,
        "phone_id": cheapest["id"],
    })
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "completed"
    assert data["daily_payment"] is not None

def test_duplicate_id_rejected():
    client.post("/phones/seed")
    phones = client.get("/phones/?risk_group=1").json()
    payload = {
        "first_name": "Thabo",
        "last_name": "Nkosi",
        "id_number": "9001155001083",
        "date_of_birth": "1990-01-15",
        "monthly_income": 50000,
        "phone_id": phones[0]["id"],
    }
    client.post("/applications/", json=payload)
    # Second submission with same ID
    res = client.post("/applications/", json=payload)
    assert res.status_code == 409

def test_dob_mismatch_rejected():
    client.post("/phones/seed")
    phones = client.get("/phones/?risk_group=1").json()
    res = client.post("/applications/", json={
        "first_name": "Thabo",
        "last_name": "Nkosi",
        "id_number": "9001155001083",
        "date_of_birth": "1995-06-20",  # wrong DOB for this ID
        "monthly_income": 50000,
        "phone_id": phones[0]["id"],
    })
    assert res.status_code == 422