# app/services/crm_service.py

#What will it do?
#Given PAN / customer_id → return KYC info
#No Approval logic

class CRMService:
    def fetch_kyc(self, pan: str):
        mock_db = {
            "ABCDE1234F": {
                "kyc_verified": True,
                "documents": {
                    "payslip": True,
                    "aadhaar": True,
                }
            },
            "PQRSX9999Z": {
                "kyc_verified": True,
                "documents": {
                    "payslip": False,
                    "aadhaar": True,
                }
            },
        }
        return mock_db.get(
            pan,
            {"kyc_verified": False, "documents": {}}
        )
