import sys
import os
from datetime import datetime

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.blockchain.web3_client import verify_batch


def check_medicine(batch_id):
    print(f"🔍 Checking batch: {batch_id}")
    result = verify_batch(batch_id)
    if result.get("valid"):
        print(f"FOUND ON BLOCKCHAIN")
        print(f"Medicine Name: {result['name']}")
        print(f"Expiry Date:   {result['expiry']}")
        print(f"Manufacturer:  {result['manufacturer']}")
    else:
        print(f" NOT FOUND or error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    batch = sys.argv[1] if len(sys.argv) > 1 else "GF244009"
    check_medicine(batch)
