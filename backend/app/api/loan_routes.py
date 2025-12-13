from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.master_agent import MasterAgent
from app.agents.sales_agent import SalesAgent
from app.agents.kyc_agent import KycAgent
from app.agents.credit_agent import CreditAgent
from app.agents.sanction_agent import SanctionAgent
from app.services.credit_score_service import CreditScoreService
from app.services.crm_service import CRMService

router = APIRouter()


# -----------------------------
# Request model
# -----------------------------
class LoanRequest(BaseModel):
    pan: str
    loan_amount: float
    tenure_months: int
    monthly_income: float
    is_preapproved: bool = False


# -----------------------------
# Endpoint
# -----------------------------
@router.post("/apply-loan")
async def apply_loan(request: LoanRequest):
    """
    Entry point for loan application.
    """

    # Instantiate services
    crm_service = CRMService()
    credit_score_service = CreditScoreService()

    # Instantiate agents
    sales_agent = SalesAgent()
    kyc_agent = KycAgent(crm_service)
    credit_agent = CreditAgent(credit_score_service)
    sanction_agent = SanctionAgent()

    # Master agent
    master_agent = MasterAgent(
        sales_agent=sales_agent,
        kyc_agent=kyc_agent,
        credit_agent=credit_agent,
        sanction_agent=sanction_agent,
    )

    # Run full workflow
    result = await master_agent.process_loan_application(
        pan=request.pan,
        loan_amount=request.loan_amount,
        tenure_months=request.tenure_months,
        monthly_income=request.monthly_income,
        is_preapproved=request.is_preapproved,
    )

    return result
