from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from app.core.logger import StructuredLogger

logger = StructuredLogger("SanctionAgent")

class SanctionAgent:
    """
    SanctionAgent responsibilities:
    - Issue final loan sanction
    - Generate sanction metadata
    - Reject or approve based on credit decision
    """

    def sanction_loan(self, credit_decision: Dict[str, Any]) -> Dict[str, Any]:
        status = credit_decision.get("status")

        if status not in ["AUTO_APPROVE", "CONDITIONAL_APPROVE"]:
            return {
                "status": "NOT_SANCTIONED",
                "reason": "Loan not eligible for sanction",
                "credit_status": status
            }

        return {
            "status": "SANCTIONED",
            "sanction_id": str(uuid4()),
            "sanction_date": datetime.now(timezone.utc).isoformat(),
            "approved_emi": credit_decision.get("emi"),
            "approved_score": credit_decision.get("score"),
            "terms": {
                "interest_rate": 14,
                "tenure_months": credit_decision.get("tenure"),
            }
        }
