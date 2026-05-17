from web3 import Web3
import json
import os
import time
from dotenv import load_dotenv, find_dotenv

# Automatically load environment variables
load_dotenv(find_dotenv())

GANACHE_URL = os.getenv("GANACHE_URL", "http://localhost:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")


def run():
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        print(" Could not connect to blockchain")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    abi_path = os.path.join(backend_dir, "app", "blockchain", "contract_abi.json")
    with open(abi_path) as f:
        abi = json.load(f)

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    accounts = w3.eth.accounts
    owner = accounts[0]

    # Load batches from external JSON file to keep code clean and real-time
    json_path = os.path.join(backend_dir, "data", "seed_medicines.json")
    if not os.path.exists(json_path):
        print(f" Data file not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        batches_data = json.load(f)

    for b in batches_data:
        batch_id = b.get("batchId")
        if not batch_id:
            continue

        print(f"Registering {b['name']} (ID: {batch_id})...")

        # Convert dates to timestamps from JSON
        try:
            mfg_ts = int(time.mktime(time.strptime(b["mfg"], "%Y-%m-%d")))
            exp_ts = int(time.mktime(time.strptime(b["exp"], "%Y-%m-%d")))
        except Exception:
            # Fallback if dates are missing in JSON
            mfg_ts = int(time.time()) - 86400 * 30
            exp_ts = int(time.time()) + 86400 * 365

        # Generate hash
        dummy_hash = w3.keccak(text=batch_id + b["manufacturer"])

        try:
            tx_hash = contract.functions.registerBatch(
                batch_id, b["name"], b["manufacturer"], mfg_ts, exp_ts, "GLOBAL", dummy_hash
            ).transact({"from": owner})

            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Success!")
        except Exception as e:
            if "Batch exists" in str(e):
                print(f"Batch {batch_id} already exists.")
            else:
                print(f"Failed to register {batch_id}: {e}")


if __name__ == "__main__":
    run()
