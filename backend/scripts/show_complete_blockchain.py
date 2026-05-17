import sys
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env
load_dotenv(find_dotenv())

from app.blockchain.web3_client import get_contract, get_web3_connection

def main():
    contract = get_contract()
    w3 = get_web3_connection()

    if not contract or not w3:
        print(" Connection failed.")
        return

    print("🔍 Fetching ALL registered medicines from the blockchain...\n")

    try:
        # Fetch verification events to find all ever-registered batches
        events = list(contract.events.BatchRegistered.get_logs(from_block=0))
        
        if not events:
            print("📭 No data found on blockchain.")
            return

        print(f" Found {len(events)} uniquely registered items.\n")

        for event in events:
            batch_id = event.args.batchId
            
            # The current ABI defines verifyBatch as returning (name, expDate, manufacturer)
            # We call it and unpack carefully
            try:
                data = contract.functions.verifyBatch(batch_id).call()
                name, exp_ts, manufacturer = data
                
                exp_date = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d')
                
                print(f"BATCH ID: {batch_id}")
                print(f" Medicine:     {name}")
                print(f" Manufacturer: {manufacturer}")
                print(f" Expiry:       {exp_date}")
                print(f" Registered by: {event.args.by}")
                print("-" * 50)
            except Exception as inner_e:
                print(f"Could not fetch details for {batch_id}: {inner_e}")

    except Exception as e:
        print(f" Error during blockchain query: {e}")
if __name__ == "__main__":
    main()
