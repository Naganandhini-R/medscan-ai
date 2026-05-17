import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compare_layout(img):
    """
    Compare image layout using structural analysis.
    Returns: float score (0.0 to 1.0)
    """
    if img is None or img.size == 0:
        return 0.0

    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect text regions using morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morph = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

        # Threshold to get text regions
        _, thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours (text blocks)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Analyze layout structure
        if len(contours) < 3:
            return 0.4  # Too few text regions - suspicious

        # Calculate layout metrics
        areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 50]

        if not areas:
            return 0.3

        # Check for consistent text block sizes (authentic packaging has organized layout)
        area_variance = np.std(areas) / (np.mean(areas) + 1e-6)
        consistency_score = 1.0 / (1.0 + area_variance)

        # Check for proper spacing and alignment
        bounding_boxes = [
            cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50
        ]
        if len(bounding_boxes) > 1:
            y_coords = [box[1] for box in bounding_boxes]
            alignment_score = 1.0 - min(np.std(y_coords) / 100.0, 1.0)
        else:
            alignment_score = 0.5

        # Combined layout score
        layout_score = consistency_score * 0.6 + alignment_score * 0.4

        return round(min(max(layout_score, 0.0), 1.0), 2)

    except Exception as e:
        print(f"Layout comparison error: {e}")
        return 0.5
