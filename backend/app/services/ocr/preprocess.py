import cv2
import numpy as np


def preprocess(image_bytes):
    """
    Convert bytes to numpy array/opencv image and resize.
    """
    if not image_bytes:
        return None

    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Resize to standard size for comparison
    img = cv2.resize(img, (256, 256))
    return img
