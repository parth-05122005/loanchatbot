import pytest

from app.agents.credit_agent import CreditAgent
from app.services.credit_score_service import CreditScoreService


@pytest.mark.asyncio
async def test_auto_approve_high_score():
    """
    Credit score >= 750
    EMI within limits
    All documents present
    """
    agent = CreditAgent(CreditScoreService())

    score = await agent.fetch_credit_score("ABCDE1234F")

    result = agent.evaluate_eligibility(
        score=score,
        loan_amount=100000,
        monthly_income=60000,
        tenure=24,
        is_preapproved=False,
        documents={
            "payslip": True,
            "kyc_verified": True
        },
    )

    assert result["status"] == "AUTO_APPROVE"


@pytest.mark.asyncio
async def test_conditional_approve_missing_payslip():
    """
    Credit score between 700–749
    Missing payslip → HOLD
    """
    agent = CreditAgent(CreditScoreService())

    score = await agent.fetch_credit_score("PQRSX9999Z")

    result = agent.evaluate_eligibility(
        score=score,
        loan_amount=150000,
        monthly_income=50000,
        tenure=24,
        is_preapproved=False,
        documents={
            "payslip": False,
            "kyc_verified": True
        },
    )

    assert result["status"] == "HOLD"
    assert "payslip" in result["missing_documents"]


@pytest.mark.asyncio
async def test_reject_low_credit_score():
    """
    Credit score < 700 → REJECT
    """
    agent = CreditAgent(CreditScoreService())

    score = await agent.fetch_credit_score("LOWSC0000X")

    result = agent.evaluate_eligibility(
        score=score,
        loan_amount=100000,
        monthly_income=50000,
        tenure=24,
        is_preapproved=False,
        documents={
            "payslip": True,
            "kyc_verified": True
        },
    )

    assert result["status"] == "REJECT"


@pytest.mark.asyncio
async def test_reject_high_emi():
    """
    EMI > 50% of salary → REJECT
    """
    agent = CreditAgent(CreditScoreService())

    score = await agent.fetch_credit_score("ABCDE1234F")

    result = agent.evaluate_eligibility(
        score=score,
        loan_amount=1000000,  # very high loan
        monthly_income=30000,
        tenure=24,
        is_preapproved=False,
        documents={
            "payslip": True,
            "kyc_verified": True
        },
    )

    assert result["status"] == "REJECT"
