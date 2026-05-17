# backend/app/ai/ocr/validator.py boilerplate
from datetime import datetime
from typing import Dict

def validate_medicine_data(data: Dict[str, str]) -> Dict[str, object]:
    """
    Validate extracted medicine details
    """
    is_valid = True
    reason = []

    # Batch validation
    if not data.get("batch_id"):
        is_valid = False
        reason.append("Batch ID not found")

    # Expiry validation
    expiry = data.get("expiry")
    if expiry:
        try:
            exp_date = datetime.strptime(expiry, "%m/%Y")
            if exp_date < datetime.utcnow():
                is_valid = False
                reason.append("Medicine expired")
        except ValueError:
            is_valid = False
            reason.append("Invalid expiry format")
    else:
        is_valid = False
        reason.append("Expiry date missing")

    return {"valid": is_valid, "reasons": reason}
