import cv2
import numpy as np


def detect_font_anomalies(img):
    """
    Detect font inconsistencies and print quality issues.
    Returns: float score (1.0 = consistent, 0.0 = anomalous)
    """
    if img is None or img.size == 0:
        return 0.0

    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to isolate text
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find text contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) < 5:
            return 0.4  # Too few text elements

        # Analyze text characteristics
        text_heights = []
        text_widths = []
        text_areas = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)

            # Filter out noise (too small) and non-text elements (too large)
            if 10 < area < 5000:
                text_heights.append(h)
                text_widths.append(w)
                text_areas.append(area)

        if not text_heights:
            return 0.3

        # Check font consistency (authentic packaging has uniform text)
        height_variance = np.std(text_heights) / (np.mean(text_heights) + 1e-6)
        consistency_score = 1.0 / (1.0 + height_variance)

        # Check print quality using edge sharpness
        edges = cv2.Canny(gray, 100, 200)
        edge_strength = np.count_nonzero(edges) / edges.size

        # Good print quality has clear, sharp edges
        if 0.05 <= edge_strength <= 0.25:
            quality_score = 1.0
        elif edge_strength < 0.05:
            quality_score = edge_strength / 0.05  # Too blurry
        else:
            quality_score = max(0.3, 1.0 - (edge_strength - 0.25) / 0.25)  # Too noisy

        # Check for text alignment and spacing
        if len(text_areas) > 1:
            area_variance = np.std(text_areas) / (np.mean(text_areas) + 1e-6)
            spacing_score = 1.0 / (1.0 + area_variance * 0.5)
        else:
            spacing_score = 0.5

        # Combined font score
        font_score = consistency_score * 0.4 + quality_score * 0.4 + spacing_score * 0.2

        return round(min(max(font_score, 0.0), 1.0), 2)

    except Exception as e:
        print(f"Font anomaly detection error: {e}")
        return 0.5
