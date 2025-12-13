import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_apply_loan_happy_path():
    """
    Full API test:
    HTTP → FastAPI → MasterAgent → response
    """

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

    assert data["stage"] == "SANCTION"
    assert data["result"]["status"] == "SANCTIONED"
    assert "sanction_id" in data["result"]
    
def test_apply_loan_kyc_failure():
    """
    API should stop processing if KYC fails.
    """

    payload = {
        "pan": "BADKYC9999",
        "loan_amount": 100000,
        "tenure_months": 24,
        "monthly_income": 60000
    }

    response = client.post("/api/apply-loan", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["stage"] == "KYC"
    assert data["result"]["status"] in ["FAILED", "INCOMPLETE"]
