import pytest

from app.agents.sales_agent import SalesAgent


def test_valid_loan_request():
    """
    Valid loan inputs should return a structured loan request.
    """
    agent = SalesAgent()

    result = agent.process_request(
        loan_amount=200000,
        tenure_months=24,
        monthly_income=50000,
    )

    assert result["loan_amount"] == 200000
    assert result["tenure_months"] == 24
    assert result["monthly_income"] == 50000
    assert result["loan_type"] == "personal_loan"


def test_invalid_loan_amount():
    """
    Loan amount must be positive.
    """
    agent = SalesAgent()

    with pytest.raises(ValueError, match="Loan amount must be positive"):
        agent.process_request(
            loan_amount=-10000,
            tenure_months=24,
            monthly_income=50000,
        )


def test_invalid_tenure():
    """
    Tenure must be positive.
    """
    agent = SalesAgent()

    with pytest.raises(ValueError, match="Tenure must be positive"):
        agent.process_request(
            loan_amount=100000,
            tenure_months=0,
            monthly_income=50000,
        )


def test_invalid_monthly_income():
    """
    Monthly income must be positive.
    """
    agent = SalesAgent()

    with pytest.raises(ValueError, match="Monthly income must be positive"):
        agent.process_request(
            loan_amount=100000,
            tenure_months=24,
            monthly_income=0,
        )


def test_no_matching_product():
    """
    Loan amount outside supported product range should fail.
    """
    agent = SalesAgent()

    with pytest.raises(ValueError, match="No suitable loan product found"):
        agent.process_request(
            loan_amount=5000000,  # exceeds max_amount
            tenure_months=24,
            monthly_income=100000,
        )
