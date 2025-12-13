from typing import Optional, Dict, Any

class CreditAgent:
    """
    Handles:
    - Fetching credit score (via credit_score_service)
    - Calculating EMI
    - Applying approval rules (score-based + income-based)
    - Document completeness checks
    """

    def __init__(self, credit_score_service):
        self.credit_score_service = credit_score_service

    # -----------------------------
    # Fetch Score
    # -----------------------------
    async def fetch_credit_score(self, pan: str) -> Optional[int]:
        """
        Returns credit score from mock credit bureau.
        """
        score = await self.credit_score_service.get_score(pan)
        return score

    # -----------------------------
    # EMI Calculator
    # -----------------------------
    def calculate_emi(self, loan_amount: float, roi: float, tenure_months: int) -> float:
        """
        Standard EMI formula:
            E = P * r * (1+r)^n / ((1+r)^n - 1)
        """
        r = roi / (12 * 100)
        n = tenure_months

        if r == 0:  # Zero interest edge case
            return loan_amount / n

        emi = loan_amount * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return round(emi, 2)

    # -----------------------------
    # Eligibility Evaluation
    # -----------------------------
    def evaluate_eligibility(
        self,
        score: int,
        loan_amount: float,
        monthly_income: float,
        tenure: int,
        is_preapproved: bool,
        documents: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Implements approval logic:
        - Score >= 750 → Auto-approve (if income supports EMI)
        - 700–749 → Conditional approve (manual docs required)
        - < 700 → Reject
        - EMI must be ≤ 50% income
        - Missing payslips → hold request
        - Missing KYC → escalate
        """

        # -----------------------------
        # 1. Score based approval rules
        # -----------------------------
        if score >= 750:
            decision = "AUTO_APPROVE"
        elif 700 <= score <= 749:
            decision = "CONDITIONAL_APPROVE"
        else:
            return {
                "status": "REJECT",
                "reason": f"Low credit score ({score}). Needs remediation.",
                "score": score,
            }

        # -----------------------------
        # 2. EMI calculation
        # -----------------------------
        roi = 14  # fixed mock interest rate
        emi = self.calculate_emi(loan_amount, roi, tenure)

        if emi > 0.5 * monthly_income:
            return {
                "status": "REJECT",
                "reason": f"EMI ({emi}) exceeds 50% of salary ({monthly_income}).",
                "emi": emi,
                "score": score,
            }

        # -----------------------------
        # 3. Document Completeness Check
        # -----------------------------
        missing_docs = []
        if not documents.get("payslip"):
            missing_docs.append("payslip")

        if not documents.get("kyc_verified"):
            return {
                "status": "ESCALATE",
                "reason": "KYC mismatch — manual verification required.",
                "missing_documents": ["kyc_verified"],
                "score": score,
                "emi": emi,
            }

        if missing_docs and decision == "CONDITIONAL_APPROVE":
            return {
                "status": "HOLD",
                "reason": "Missing required documents.",
                "missing_documents": missing_docs,
                "score": score,
                "emi": emi,
            }

        # -----------------------------
        # 4. Pre-approved logic
        # -----------------------------
        if is_preapproved and loan_amount <= monthly_income * 2:
            return {
                "status": "AUTO_APPROVE",
                "reason": "Pre-approved loan within limit.",
                "score": score,
                "emi": emi,
            }

        if loan_amount > monthly_income * 2:
            return {
                "status": "REJECT",
                "reason": "Requested loan exceeds 2× income limit.",
                "score": score,
                "emi": emi,
            }

        # -----------------------------
        # Final approval
        # -----------------------------
        return {
            "status": decision,
            "score": score,
            "emi": emi,
            "message": "Eligible for loan",
        }

