import requests
import os

URL = "http://localhost:8000/api/v1/medicine/register"
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test.jpg")

# Ensure a test image exists
if not os.path.exists(IMAGE_PATH):
    with open(IMAGE_PATH, "wb") as f:
        f.write(
            b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01"
        )  # minimal jpg header


def test_register():
    data = {
        "batch_id": "TEST_BATCH_999",
        "medicine_name": "Test Medicine",
        "manufacturer": "Test Pharma",
        "mfg_date": "2023-01-01",
        "exp_date": "2025-01-01",
        "region": "GLOBAL",
    }

    files = {"file": ("logo.jpg", open(IMAGE_PATH, "rb"), "image/jpeg")}

    try:
        print(f"Sending POST request to {URL}...")
        response = requests.post(URL, data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    test_register()
