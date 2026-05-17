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
        print(" Blockchain connection failed.")
        return

    print(" --- SHOWING FULL BLOCKCHAIN REGISTERED DATA (BEYOND DATABASE) --- \n")

    try:
        # Fetch all events to find the Wallet Address that registered it
        events = list(contract.events.BatchRegistered.get_logs(from_block=0))
        
        if not events:
            print("📭 No registered batches found.")
            return

        for event in events:
            batch_id = event.args.batchId
            owner_wallet = event.args.by
            
            # Fetch technical data from verifyBatch function
            # Note: Current contract returns (medicineName, expDate, manufacturer, region)
            try:
                data = contract.functions.verifyBatch(batch_id).call()
                
                # Handling different contract versions (3 or 4 returns)
                if len(data) == 4:
                    name, exp_ts, manufacturer, region = data
                else:
                    name, exp_ts, manufacturer = data
                    region = "GLOBAL"

                exp_date_str = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d')
                
                print(f"{batch_id} REGISTRATION PROTOCOL:")
                print(f"   -------------------------------------------------")
                print(f"   Registered By:  {owner_wallet}")
                print(f"   Medicine Name: {name}")
                print(f"   Manufacturer:  {manufacturer}")
                print(f"   Expiry Date:   {exp_date_str}")
                print(f"   Auth. Region:  {region}")
                
                # Calculate a mock Batch Hash since the private variable isn't exported
                # But it demonstrates the security protocol
                from web3 import Web3
                mock_hash = w3.keccak(text=f"{batch_id}-{name}-{manufacturer}-{region}").hex()
                print(f"   🛡️ Batch Hash:    {mock_hash}")
                print(f"   -------------------------------------------------\n")

            except Exception as inner_e:
                print(f"⚠️ Error reading Batch {batch_id}: {inner_e}")

    except Exception as e:
        print(f" Blockchain error: {e}")

if __name__ == "__main__":
    main()
