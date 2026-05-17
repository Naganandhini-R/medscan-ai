import sys
import os
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.blockchain.web3_client import register_batch

def interactive_register():
    print("--- MedScan-AI Merchant Portal --- ")
    print("Enter medicine details to register on Blockchain.\n")

    try:
        # Get user input
        batch_id = input("Enter Batch ID: ").strip()
        med_name = input("Enter Medicine Name: ").strip()
        mfg_name = input("Enter Manufacturer Name: ").strip()
        exp_date_str = input("Enter Expiry Date (YYYY-MM-DD): ").strip()
        region = (
            input("Enter Authorized Region (e.g., TAMIL NADU, DELHI): ").strip().upper()
            or "GLOBAL"
        )

        if not all([batch_id, med_name, mfg_name, exp_date_str]):
            print("Error: All fields are required.")
            return

        # Prepare dates
        mfg_ts = int(datetime.now().timestamp())
        exp_ts = int(datetime.strptime(exp_date_str, "%Y-%m-%d").timestamp())

        print(
            f"\n🔗 Registering {med_name} (Batch: {batch_id}) for region {region} on blockchain..."
        )

        result = register_batch(
            batch_id, med_name, mfg_name, mfg_ts, exp_ts, region=region
        )

        if result.get("success"):
            print(f" Registered! TX Hash: {result.get('tx_hash')}")
        else:
            print(f" Failed: {result.get('error')}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    interactive_register()
