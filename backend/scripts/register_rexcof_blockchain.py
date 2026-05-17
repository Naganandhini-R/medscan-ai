import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.blockchain.web3_client import register_batch

def register_rexcof():
    batch_id = "RXCF2603"
    medicine_name = "Rexcof DX Cough Syrup"
    manufacturer = "Cipla Limited"
    
    # Mfg date: 2024-09-01, Exp date: 2026-09-30
    mfg_ts = int(datetime.strptime("2024-09-01", "%Y-%m-%d").timestamp())
    exp_ts = int(datetime.strptime("2026-09-30", "%Y-%m-%d").timestamp())
    
    print(f"Registering Rexcof DX batch {batch_id} on the blockchain...")
    
    result = register_batch(
        batch_id=batch_id,
        medicine_name=medicine_name,
        manufacturer=manufacturer,
        mfg_date=mfg_ts,
        exp_date=exp_ts
    )
    
    if result.get("success"):
        print(f"Success! Registered on blockchain with tx: {result.get('tx_hash')}")
    else:
        print(f"Failed to register on blockchain: {result.get('error')}")

if __name__ == "__main__":
    register_rexcof()
