# kyc_service.py
import base64
import io
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image

app = FastAPI(title="KYC Verification Agent")


# -----------------------------------------------------------
# 1. INPUT MODELS
# -----------------------------------------------------------

class DocumentPayload(BaseModel):
    pan: str | None = None        # base64 PAN image
    aadhaar: str | None = None    # base64 Aadhaar image
    payslip: str | None = None    # base64 Payslip image/PDF


class KYCRequest(BaseModel):
    session_id: str
    documents: DocumentPayload
    expected_name: str | None = None
    expected_pan: str | None = None
    expected_dob: str | None = None


# -----------------------------------------------------------
# 2. UTILITY FUNCTIONS
# -----------------------------------------------------------

def decode_image(base64_str: str):
    """Convert base64 → PIL Image"""
    try:
        image_bytes = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None


# ------- OCR PLACEHOLDERS (replace later with EasyOCR) ------

def extract_pan_details(pan_img):
    """
    THIS IS A SIMULATED PAN OCR FUNCTION.
    Replace with actual OCR when needed.
    """

    # Dummy extraction result
    # TODO: Replace with OCR logic
    return {
        "name": "RAJDEEP DEB",
        "pan_no": "ABCDE1234F",
        "dob": "2004-02-14"
    }


def extract_aadhaar_details(aadhaar_img):
    """
    Simulated Aadhaar OCR extraction.
    """
    return {
        "name": "RAJDEEP DEB",
        "aadhaar_no": "1234-5678-9101",
        "dob": "2004-02-14"
    }


def validate_payslip(payslip_img):
    """
    For PoC: only check if image exists.
    Later: extract employer, salary, date from PDF.
    """
    if payslip_img is None:
        return False
        
    # Simulated validation
    return True


# -----------------------------------------------------------
# 3. KYC VERIFICATION LOGIC
# -----------------------------------------------------------

@app.post("/kyc/verify")
def verify_kyc(req: KYCRequest):

    mismatches = []

    # --------------------------------------
    # Step 1: Decode images
    # --------------------------------------
    pan_img = decode_image(req.documents.pan) if req.documents.pan else None
    aadhaar_img = decode_image(req.documents.aadhaar) if req.documents.aadhaar else None
    payslip_img = decode_image(req.documents.payslip) if req.documents.payslip else None

    # --------------------------------------
    # Step 2: Extract details using OCR
    # --------------------------------------
    if pan_img:
        pan_data = extract_pan_details(pan_img)
    else:
        mismatches.append("PAN not uploaded")
        pan_data = {}

    if aadhaar_img:
        aadhaar_data = extract_aadhaar_details(aadhaar_img)
    else:
        mismatches.append("Aadhaar not uploaded")
        aadhaar_data = {}

    # --------------------------------------
    # Step 3: Verify expected fields
    # (received from Sales/Master)
    # --------------------------------------

    if req.expected_name and pan_data.get("name"):
        if req.expected_name.lower() not in pan_data["name"].lower():
            mismatches.append("Name mismatch")

    if req.expected_pan and pan_data.get("pan_no"):
        if req.expected_pan.upper() != pan_data["pan_no"].upper():
            mismatches.append("PAN number mismatch")

    if req.expected_dob and pan_data.get("dob"):
        if req.expected_dob != pan_data["dob"]:
            mismatches.append("DOB mismatch")

    # --------------------------------------
    # Step 4: Validate payslip
    # --------------------------------------
    if not validate_payslip(payslip_img):
        mismatches.append("Invalid payslip")

    # --------------------------------------
    # Step 5: Final decision
    # --------------------------------------
    kyc_verified = (len(mismatches) == 0)

    # --------------------------------------
    # Step 6: Build response for Master Agent
    # --------------------------------------
    response = {
        "session_id": req.session_id,
        "kyc_verified": kyc_verified,
        "mismatch_reasons": mismatches,
        "extracted_data": {
            "pan": pan_data,
            "aadhaar": aadhaar_data
        }
    }

    # In future:
    # TODO: save this response into Redis for session persistence

    return response
