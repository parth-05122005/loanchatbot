from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_apply_loan_happy_path():
    payload = {
        "pan": "ABCDE1234F",
        "loan_amount": 100000,
        "tenure_months": 24,
        "monthly_income": 60000,
        "is_preapproved": False
    }

    response = client.post("/api/apply-loan", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["stage"] == "SANCTION"
    assert data["data"]["status"] == "SANCTIONED"


def test_apply_loan_kyc_failure():
    payload = {
        "pan": "BADKYC9999",
        "loan_amount": 100000,
        "tenure_months": 24,
        "monthly_income": 60000
    }

    response = client.post("/api/apply-loan", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "FAILURE"
    assert data["stage"] == "KYC"
    assert data["error"]["code"] in ["FAILED", "INCOMPLETE"]
