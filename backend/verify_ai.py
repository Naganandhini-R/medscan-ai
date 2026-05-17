# backend/verify_ai.py
import sys
import os
import torch
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Testing AI Vision Pipeline Components...")
    from app.ai.vision.logo_detection import detect_logo
    from app.ai.vision.layout_matching import compare_layout
    from app.ai.vision.text_analysis import check_font_issues
    from app.tasks.scan_pipeline import run_vision_pipeline

    # Mock image (random noise)
    dummy_image = bytes(
        np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8).tobytes()
    )

    # Needs a real image encoding (e.g. cv2.imencode) to work with our preprocess stub completely
    # but let's see if imports work first.
    print("AI Vision imports successful")

except Exception as e:
    # We expect some failures because I used different module names in my plan vs the file system
    # Let me check what I actually created vs what scan_pipeline imports
    print(f"⚠ Import failed: {e}")

try:
    print("\nTesting GAN Generator...")
    from app.ai.gan.generator import Generator

    gen = Generator()
    z = torch.randn(1, 100)
    img = gen(z)
    if img.shape == (1, 3, 64, 64):
        print(" GAN Generator operational")
    else:
        print(f"GAN Output mismatch: {img.shape}")
except Exception as e:
    print(f"GAN Generator failed: {e}")
