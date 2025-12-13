from fastapi import APIRouter
from app.schemas.api_response import APIResponse, APIError
from app.agents.master_agent import MasterAgent
from app.agents.sales_agent import SalesAgent
from app.agents.kyc_agent import KycAgent
from app.agents.credit_agent import CreditAgent
from app.agents.sanction_agent import SanctionAgent
from app.services.crm_service import CRMService
from app.services.credit_score_service import CreditScoreService
from pydantic import BaseModel

router = APIRouter()


class LoanRequest(BaseModel):
    pan: str
    loan_amount: float
    tenure_months: int
    monthly_income: float
    is_preapproved: bool = False


@router.post("/apply-loan", response_model=APIResponse)
async def apply_loan(request: LoanRequest):

    master_agent = MasterAgent(
        sales_agent=SalesAgent(),
        kyc_agent=KycAgent(CRMService()),
        credit_agent=CreditAgent(CreditScoreService()),
        sanction_agent=SanctionAgent(),
    )

    result = await master_agent.process_loan_application(
        pan=request.pan,
        loan_amount=request.loan_amount,
        tenure_months=request.tenure_months,
        monthly_income=request.monthly_income,
        is_preapproved=request.is_preapproved,
    )

    stage = result.get("stage")
    payload = result.get("result")

    # -----------------------------
    # SUCCESS CASE
    # -----------------------------
    if stage == "SANCTION":
        return APIResponse(
            status="SUCCESS",
            stage=stage,
            data=payload,
            error=None
        )

    # -----------------------------
    # FAILURE / HOLD / ESCALATE
    # -----------------------------
    return APIResponse(
        status="FAILURE",
        stage=stage,
        data=None,
        error=APIError(
            code=payload.get("status", "UNKNOWN_ERROR"),
            message=payload.get("reason", "Request could not be processed"),
        ),
    )
