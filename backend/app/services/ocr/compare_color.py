import cv2
import numpy as np


def compare_color_histogram(img):
    """
    Compare color distribution using histogram analysis.
    Returns: float score (0.0 to 1.0)
    """
    if img is None or img.size == 0:
        return 0.0

    try:
        # Calculate color histograms for each channel
        hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])

        # Normalize histograms
        hist_b = cv2.normalize(hist_b, hist_b).flatten()
        hist_g = cv2.normalize(hist_g, hist_g).flatten()
        hist_r = cv2.normalize(hist_r, hist_r).flatten()

        # Check color distribution quality
        # Authentic medicines typically have consistent, professional color printing

        # Calculate entropy (measure of color diversity)
        def calculate_entropy(hist):
            hist = hist[hist > 0]  # Remove zeros
            return -np.sum(hist * np.log2(hist + 1e-10))

        entropy_b = calculate_entropy(hist_b)
        entropy_g = calculate_entropy(hist_g)
        entropy_r = calculate_entropy(hist_r)

        avg_entropy = (entropy_b + entropy_g + entropy_r) / 3

        # Good entropy range for authentic packaging: 4-7 bits
        # Too low = too uniform (suspicious), too high = too noisy (suspicious)
        if 4.0 <= avg_entropy <= 7.0:
            entropy_score = 1.0
        elif avg_entropy < 4.0:
            entropy_score = avg_entropy / 4.0
        else:
            entropy_score = max(0.3, 1.0 - (avg_entropy - 7.0) / 3.0)

        # Check for color balance (authentic packaging has balanced colors)
        color_means = [np.mean(hist_b), np.mean(hist_g), np.mean(hist_r)]
        color_balance = 1.0 - min(
            np.std(color_means) / (np.mean(color_means) + 1e-6), 1.0
        )

        # Combined color score
        color_score = entropy_score * 0.7 + color_balance * 0.3

        return round(min(max(color_score, 0.0), 1.0), 2)

    except Exception as e:
        print(f"Color histogram error: {e}")
        return 0.5
