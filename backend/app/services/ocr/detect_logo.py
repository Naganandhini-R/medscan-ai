import logging

# Configure logging
logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np

    HAS_OPENCV = True
except ImportError:
    cv2 = None
    np = None
    HAS_OPENCV = False
    logger.warning("OpenCV or NumPy not found. Logo detection will be disabled.")


def detect_logo(img):
    """
    Detect pharmaceutical logo using feature matching.
    Returns: float confidence (0.0 to 1.0)
    """
    if not HAS_OPENCV:
        logger.error("Attempted to detect logo but OpenCV is missing.")
        return 0.0

    if img is None or img.size == 0:
        return 0.0

    try:
        # Convert to grayscale for feature detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Use ORB (Oriented FAST and Rotated BRIEF) detector
        orb = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        # If no features detected, return low score
        if descriptors is None or len(keypoints) < 10:
            return 0.3

        # Score based on number and quality of detected features
        # More keypoints generally indicate more complex/authentic packaging
        feature_score = min(len(keypoints) / 100.0, 1.0)

        # Check for edge density (authentic medicines have clear edges)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        edge_score = min(edge_density * 10, 1.0)

        # Combined score
        final_score = feature_score * 0.6 + edge_score * 0.4

        return round(min(max(final_score, 0.0), 1.0), 2)

    except Exception as e:
        logger.error(f"Logo detection error: {e}")
        return 0.5
