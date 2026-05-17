import sys
import os
import argparse
from datetime import datetime

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.blockchain.web3_client import register_batch


def main():
    parser = argparse.ArgumentParser(
        description="Register a medicine batch on the blockchain"
    )
    parser.add_argument("--batch", required=True, help="Batch ID (e.g. GF244009)")
    parser.add_argument("--name", required=True, help="Medicine Name")
    parser.add_argument("--manufacturer", required=True, help="Manufacturer Name")
    parser.add_argument(
        "--mfg",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Mfg Date (YYYY-MM-DD)",
    )
    parser.add_argument("--exp", required=True, help="Expiry Date (YYYY-MM-DD)")

    args = parser.parse_args()

    try:
        mfg_ts = int(datetime.strptime(args.mfg, "%Y-%m-%d").timestamp())
        exp_ts = int(datetime.strptime(args.exp, "%Y-%m-%d").timestamp())

        print(f"🚀 Registering {args.name} (Batch: {args.batch}) on blockchain...")

        result = register_batch(
            args.batch, args.name, args.manufacturer, mfg_ts, exp_ts
        )

        if result.get("success"):
            print(f"Success! Transaction Hash: {result.get('tx_hash')}")
        else:
            print(f" Failed: {result.get('error')}")

    except Exception as e:
        print(f" Error: {e}")


if __name__ == "__main__":
    main()
