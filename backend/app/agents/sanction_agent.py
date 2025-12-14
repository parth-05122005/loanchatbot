from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
import os

from app.core.logger import StructuredLogger

logger = StructuredLogger("SanctionAgent")


class SanctionAgent:
    """
    SanctionAgent responsibilities:
    - Issue final loan sanction
    - Generate sanction metadata
    - Generate sanction letter artifact
    """

    OUTPUT_DIR = "app/static/outputs"

    def sanction_loan(self, credit_decision: Dict[str, Any]) -> Dict[str, Any]:
        status = credit_decision.get("status")

        if status not in ["AUTO_APPROVE", "CONDITIONAL_APPROVE"]:
            logger.info("Loan not eligible for sanction", credit_status=status)
            return {
                "status": "NOT_SANCTIONED",
                "reason": "Loan not eligible for sanction",
                "credit_status": status
            }

        sanction_id = str(uuid4())
        sanction_date = datetime.now(timezone.utc).isoformat()

        file_name = f"sanction_{sanction_id}.txt"
        file_path = os.path.join(self.OUTPUT_DIR, file_name)

        self._generate_sanction_letter(
            file_path=file_path,
            credit_decision=credit_decision,
            sanction_id=sanction_id,
            sanction_date=sanction_date,
        )

        logger.info(
            "Loan sanctioned",
            sanction_id=sanction_id,
            credit_status=status
        )

        return {
            "status": "SANCTIONED",
            "sanction_id": sanction_id,
            "sanction_date": sanction_date,
            "approved_emi": credit_decision.get("emi"),
            "approved_score": credit_decision.get("score"),
            "terms": {
                "interest_rate": 14,
                "tenure_months": credit_decision.get("tenure"),
            },
            "document": {
                "type": "SANCTION_LETTER",
                "file_name": file_name,
                "download_url": f"/static/outputs/{file_name}"
            }
        }

    def _generate_sanction_letter(
        self,
        file_path: str,
        credit_decision: Dict[str, Any],
        sanction_id: str,
        sanction_date: str,
    ) -> None:
        """
        Mock sanction letter generation.
        (Can be replaced with real PDF later)
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(
                f"""
SANCTION LETTER
===========================

Sanction ID   : {sanction_id}
Sanction Date : {sanction_date}

Approved Loan Details
---------------------
Loan Amount   : {credit_decision.get("loan_amount", "N/A")}
Tenure        : {credit_decision.get("tenure", "N/A")} months
Interest Rate : 14%
EMI           : {credit_decision.get("emi")}
Credit Score  : {credit_decision.get("score")}

This loan has been sanctioned based on automated credit assessment.

-- AI Loan Processing System
"""
            )
