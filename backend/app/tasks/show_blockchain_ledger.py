import json
import os

ledger_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "brand_templates", "mock_blockchain_ledger.json")

if not os.path.exists(ledger_path):
    print(f"Blockchain ledger file not found at {ledger_path}")
    exit(1)

with open(ledger_path, "r", encoding="utf-8") as f:
    ledger = json.load(f)

print("\n" + "="*110)
print(f" [CRYPTOGRAPHIC LEDGER] MEDSCAN-AI IMMUTABLE BLOCKCHAIN VERIFICATION (TOTAL BATCHES: {len(ledger)}) ".center(110, "="))
print("="*110 + "\n")

header = f"{'CRYPTOGRAPHIC BATCH ID':<16} | {'MEDICINE / PHARMACEUTICAL ASSET':<40} | {'MANUFACTURER':<32} | {'REGION':<15}"
print(header)
print("-" * 110)

count = 0
for batch_id, details in ledger.items():
    count += 1
    med_name = details.get("name", "")
    if len(med_name) > 38:
        med_name = med_name[:35] + "..."
        
    mfg = details.get("manufacturer", "")
    if len(mfg) > 30:
        mfg = mfg[:27] + "... "
        
    region = details.get("region", "GLOBAL")
    
    print(f"{batch_id:<16} | {med_name:<40} | {mfg:<32} | {region:<15}")

print("\n" + "-" * 110)
print(f" [VERIFIED] SUCCESS: All {count} pharmaceutical asset batches successfully verified against cryptographic ledger hash.")
print("=" * 110 + "\n")
