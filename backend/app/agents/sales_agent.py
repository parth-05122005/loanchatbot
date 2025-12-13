from typing import Dict, Any


class SalesAgent:
    """
    SalesAgent responsibilities:
    - Collect and validate raw loan requirements
    - Perform basic sanity checks
    - Structure the loan request
    - Hand off clean data to downstream agents
    """

    def __init__(self, supported_products: Dict[str, Dict[str, Any]] | None = None):
        # Mock loan products (can be replaced by a service later)
        self.supported_products = supported_products or {
            "personal_loan": {
                "min_amount": 50000,
                "max_amount": 2000000,
                "min_tenure": 6,
                "max_tenure": 60,
            }
        }

    # -----------------------------
    # 1. Validate raw input
    # -----------------------------
    def validate_input(
        self,
        loan_amount: float,
        tenure_months: int,
        monthly_income: float,
    ) -> None:
        if loan_amount <= 0:
            raise ValueError("Loan amount must be positive")

        if tenure_months <= 0:
            raise ValueError("Tenure must be positive")

        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")

    # -----------------------------
    # 2. Match loan product
    # -----------------------------
    def match_product(
        self,
        loan_amount: float,
        tenure_months: int,
    ) -> str:
        for product, rules in self.supported_products.items():
            if (
                rules["min_amount"] <= loan_amount <= rules["max_amount"]
                and rules["min_tenure"] <= tenure_months <= rules["max_tenure"]
            ):
                return product

        raise ValueError("No suitable loan product found")

    # -----------------------------
    # 3. Build structured request
    # -----------------------------
    def build_loan_request(
        self,
        loan_amount: float,
        tenure_months: int,
        monthly_income: float,
    ) -> Dict[str, Any]:
        self.validate_input(loan_amount, tenure_months, monthly_income)

        product = self.match_product(loan_amount, tenure_months)

        return {
            "loan_amount": loan_amount,
            "tenure_months": tenure_months,
            "monthly_income": monthly_income,
            "loan_type": product,
        }

    # -----------------------------
    # 4. Public entry point
    # -----------------------------
    def process_request(
        self,
        loan_amount: float,
        tenure_months: int,
        monthly_income: float,
    ) -> Dict[str, Any]:
        """
        Main method called by MasterAgent or API.
        """
        return self.build_loan_request(
            loan_amount=loan_amount,
            tenure_months=tenure_months,
            monthly_income=monthly_income,
        )
