from typing import Dict, Any


class MasterAgent:
    """
    MasterAgent responsibilities:
    - Orchestrate Sales, KYC, Credit, and Sanction agents
    - Control execution flow
    - Return final unified response
    """

    def __init__(
        self,
        sales_agent,
        kyc_agent,
        credit_agent,
        sanction_agent,
    ):
        self.sales_agent = sales_agent
        self.kyc_agent = kyc_agent
        self.credit_agent = credit_agent
        self.sanction_agent = sanction_agent

    async def process_loan_application(
        self,
        pan: str,
        loan_amount: float,
        tenure_months: int,
        monthly_income: float,
        is_preapproved: bool = False,
    ) -> Dict[str, Any]:
        """
        End-to-end loan processing pipeline.
        """

        # -----------------------------
        # 1. Sales Agent
        # -----------------------------
        loan_request = self.sales_agent.process_request(
            loan_amount=loan_amount,
            tenure_months=tenure_months,
            monthly_income=monthly_income,
        )

        # -----------------------------
        # 2. KYC Agent
        # -----------------------------
        kyc_result = self.kyc_agent.verify_kyc(pan)

        if kyc_result["status"] == "FAILED":
            return {
                "stage": "KYC",
                "result": kyc_result,
            }

        if kyc_result["status"] == "INCOMPLETE":
            return {
                "stage": "KYC",
                "result": kyc_result,
            }

        documents = kyc_result.get("documents", {})

        # -----------------------------
        # 3. Credit Agent
        # -----------------------------
        score = await self.credit_agent.fetch_credit_score(pan)

        credit_decision = self.credit_agent.evaluate_eligibility(
            score=score,
            loan_amount=loan_request["loan_amount"],
            monthly_income=loan_request["monthly_income"],
            tenure=loan_request["tenure_months"],
            is_preapproved=is_preapproved,
            documents={
                "payslip": documents.get("payslip", False),
                "kyc_verified": True,
            },
        )

        if credit_decision["status"] not in [
            "AUTO_APPROVE",
            "CONDITIONAL_APPROVE",
        ]:
            return {
                "stage": "CREDIT",
                "result": credit_decision,
            }

        # -----------------------------
        # 4. Sanction Agent
        # -----------------------------
        sanction_result = self.sanction_agent.sanction_loan(
            credit_decision
        )

        return {
            "stage": "SANCTION",
            "result": sanction_result,
        }
