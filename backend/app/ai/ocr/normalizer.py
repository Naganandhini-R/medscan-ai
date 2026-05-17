# backend/app/ai/ocr/normalizer.py boilerplate
import re
from typing import Dict

def normalize_ocr_text(text: str) -> Dict[str, str]:
    """
    Normalize OCR text and extract structured medicine data
    """
    clean_text = text.lower()

    batch_pattern = r"(batch|lot)[\s:]*([a-z0-9\-]+)"
    expiry_pattern = r"(exp|expiry)[\s:]*([0-9]{2}[\/\-][0-9]{2,4})"

    batch_match = re.search(batch_pattern, clean_text)
    expiry_match = re.search(expiry_pattern, clean_text)

    return {
        "batch_id": batch_match.group(2).upper() if batch_match else None,
        "expiry": expiry_match.group(2) if expiry_match else None,
    }
