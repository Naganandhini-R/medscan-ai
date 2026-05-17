import sys
import os
import json
from web3 import Web3
from dotenv import load_dotenv, find_dotenv

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env before importing our modules
load_dotenv(find_dotenv())

from app.blockchain.web3_client import get_contract, get_web3_connection


def list_registered_batches():
    contract = get_contract()
    w3 = get_web3_connection()

    if not contract or not w3:
        print(" Blockchain connection failed. Ensure Ganache/Hardhat is running.")
        return

    print("🔍 Fetching registered batches from blockchain events...")

    try:
        # Using get_logs instead of filters for better reliability on dev nodes
        events = list(contract.events.BatchRegistered.get_logs(from_block=0))

        if not events:
            print("📭 No batches registered yet in the event log.")
            return

        print(f" Found {len(events)} registered batches:\n")
        print(f"{'Batch ID':<15} | {'Medicine Name':<20} | {'Manufacturer':<25}")
        print("-" * 65)

        for event in events:
            batch_id = event.args.batchId
            try:
                name, exp_ts, manufacturer = contract.functions.verifyBatch(
                    batch_id
                ).call()
                print(f"{batch_id:<15} | {name:<20} | {manufacturer:<25}")
            except Exception as e:
                print(f"{batch_id:<15} | Error fetching details: {e}")

    except Exception as e:
        print(f" Error querying blockchain: {e}")


if __name__ == "__main__":
    list_registered_batches()
