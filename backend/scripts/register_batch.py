import os
import sys
import argparse
import json
import time
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# Load environment
load_dotenv(os.path.join(backend_dir, ".env"))

from app.blockchain.web3_client import register_batch as web3_register_batch

# Directory to save brand templates
TEMPLATE_DIR = os.path.join(backend_dir, "data", "brand_templates")
os.makedirs(TEMPLATE_DIR, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Generic Medicine Registration Tool")
    parser.add_argument("--name", required=True, help="Medicine Name (e.g., Aspirin)")
    parser.add_argument("--batch", required=True, help="Batch ID (e.g., B12345)")
    parser.add_argument("--manufacturer", required=True, help="Manufacturer Name")
    parser.add_argument("--expiry", required=True, help="Expiry Date (YYYY-MM-DD)")
    parser.add_argument(
        "--mfg",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Manufacturing Date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--image", help="Path to Master Logo/Packaging Pattern (Generic Image)"
    )

    args = parser.parse_args()

    try:
        # Save image if provided
        if args.image:
            if not os.path.exists(args.image):
                print(f" Image file not found: {args.image}")
                return

            filename = os.path.basename(args.image)
            dest_path = os.path.join(TEMPLATE_DIR, f"{args.batch}_{filename}")
            shutil.copy2(args.image, dest_path)
            print(f" Template saved to: {dest_path}")

        # Convert strings to timestamps
        mfg_ts = int(datetime.strptime(args.mfg, "%Y-%m-%d").timestamp())
        exp_ts = int(datetime.strptime(args.expiry, "%Y-%m-%d").timestamp())

        print(f" Registering {args.name} (Batch: {args.batch}) on Blockchain...")

        result = web3_register_batch(
            batch_id=args.batch,
            medicine_name=args.name,
            manufacturer=args.manufacturer,
            mfg_date=mfg_ts,
            exp_date=exp_ts,
        )

        if result.get("success"):
            print(f" Success! Transaction Hash: {result.get('tx_hash')}")
        else:
            print(f" Registration Failed: {result.get('error')}")
            # Clean up image if failed? optional

    except ValueError as ve:
        print(f" Date format error: {ve}. Please use YYYY-MM-DD.")
    except Exception as e:
        print(f" Unexpected Error: {e}")


if __name__ == "__main__":
    main()
