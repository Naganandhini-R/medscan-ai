# backend/app/ai/ocr/extractor.py boilerplate
import pytesseract
import cv2
import numpy as np

def run_ocr(image_bytes: bytes) -> str:
    """
    Run OCR on an image and return raw extracted text
    """
    np_img = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    text = pytesseract.image_to_string(blur, config="--psm 6")

    return text.strip()
