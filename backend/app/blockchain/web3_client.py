from web3 import Web3
import json
import os
import time
from dotenv import load_dotenv, find_dotenv

# Explicitly load .env from project root
script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up: app/blockchain -> app -> backend -> root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
env_path = os.path.join(project_root, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"env file not found at {env_path}, trying find_dotenv...")
    load_dotenv(find_dotenv())

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

ETH_PRIVATE_KEY = os.getenv("ETH_PRIVATE_KEY")

if ETH_PRIVATE_KEY:
    print(
        f"Loaded Merchant Private Key: {ETH_PRIVATE_KEY[:6]}...{ETH_PRIVATE_KEY[-4:]}"
    )
else:
    print("Merchant Private Key NOT loaded!")

if CONTRACT_ADDRESS:
    print(f"Contract Address: {CONTRACT_ADDRESS}")
else:
    print("Contract Address NOT loaded!")


def get_web3_connection():
    # Optimistic connection check
    w3_conn = Web3(Web3.HTTPProvider(GANACHE_URL, request_kwargs={"timeout": 10}))
    try:
        if w3_conn.is_connected():
            print(
                f"Connected to Blockchain {GANACHE_URL} (Chain ID: {w3_conn.eth.chain_id})"
            )
            return w3_conn
        else:
            print(f"Connection failed to {GANACHE_URL}")
    except Exception as e:
        print(f"Connection error to {GANACHE_URL}: {e}")
    return None


_w3 = None
_contract = None


def get_contract():
    global _w3, _contract
    if _contract:
        return _contract

    if _w3 is None:
        _w3 = get_web3_connection()

    if _w3:
        try:
            abi_path = os.path.join(os.path.dirname(__file__), "contract_abi.json")
            if not os.path.exists(abi_path):
                print(f"⚠ ABI file missing at {abi_path}")
                return None

            with open(abi_path) as f:
                abi_data = json.load(f)
                # Handle cases where ABI is wrapped in artifacts (Hardhat output)
                if isinstance(abi_data, dict) and "abi" in abi_data:
                    abi = abi_data["abi"]
                else:
                    abi = abi_data

            if not CONTRACT_ADDRESS:
                print("CONTRACT_ADDRESS environment variable missing")
                return None

            _contract = _w3.eth.contract(
                address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi
            )
            print("Blockchain contract initialized")
            return _contract

        except Exception as e:
            print(f"Web3 initialization error: {e}")
            return None
    return None


# For backward compatibility if needed, but preferred to use get_contract()
contract = None


def verify_batch(batch_no: str):
    # Try local mock ledger first or as a fallback
    def check_local_ledger(b_id):
        try:
            import json
            # path: app/blockchain/web3_client.py -> up 3 levels -> backend root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            p_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            ledger_path = os.path.join(p_root, "backend", "data", "brand_templates", "mock_blockchain_ledger.json")
            if not os.path.exists(ledger_path):
                # Alternate path inside container
                ledger_path = os.path.join(p_root, "data", "brand_templates", "mock_blockchain_ledger.json")
            
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as f:
                    ledger = json.load(f)
                if b_id in ledger:
                    b_data = ledger[b_id]
                    print(f"⚠️ Ganache down/unreachable. Using local mock blockchain ledger fallback for batch {b_id}!")
                    return {
                        "valid": True,
                        "name": b_data["name"],
                        "expiry": b_data["expiry_date"],
                        "manufacturer": b_data["manufacturer"],
                        "region": b_data["region"]
                    }
        except Exception as err:
            print(f"Local ledger check failed: {err}")
        return None

    # Security: Sanitize input to prevent generic attacks
    if not batch_no:
        return {"valid": False, "error": "Invalid batch ID"}

    clean_batch = str(batch_no).strip()

    # 1. Try real blockchain first
    contract_inst = get_contract()
    if contract_inst:
        try:
            # ABI: verifyBatch(string) returns (string, uint256, string, string)
            name, expiry_timestamp, manufacturer, region = contract_inst.functions.verifyBatch(
                clean_batch
            ).call()
            from datetime import datetime
            expiry_date = datetime.fromtimestamp(expiry_timestamp).strftime("%Y-%m-%d")
            return {
                "valid": True,
                "name": name,
                "expiry": expiry_date,
                "manufacturer": manufacturer,
                "region": region,
            }
        except Exception as e:
            print(f"Blockchain verification error ({clean_batch}): {e}")
            # Fallback to local ledger
            local_res = check_local_ledger(clean_batch)
            if local_res:
                return local_res
            return {"valid": False}
    else:
        # 2. Fallback to local ledger if blockchain is unavailable
        local_res = check_local_ledger(clean_batch)
        if local_res:
            return local_res
        return {"valid": False, "error": "Blockchain unavailable"}


def register_batch(
    batch_id, medicine_name, manufacturer, mfg_date, exp_date, region="GLOBAL"
):
    """
    Registers a new medicine batch on the blockchain with an authorized region.
    Dates should be Unix timestamps (int).
    """
    contract_inst = get_contract()
    if not contract_inst or not _w3:
        return {"success": False, "error": "Blockchain unavailable"}

    if not ETH_PRIVATE_KEY:
        return {"success": False, "error": "Merchant private key not configured"}

    try:
        t0 = time.time()
        print(f"Start registration for {batch_id}...")

        # Account init
        account = _w3.eth.account.from_key(ETH_PRIVATE_KEY)

        # Generate a simple hash for the batch
        batch_hash = _w3.keccak(
            text=f"{batch_id}-{medicine_name}-{manufacturer}-{region}"
        )

        # Build transaction
        nonce = _w3.eth.get_transaction_count(account.address)

        # Build function call
        # ABI: registerBatch(string,string,string,uint256,uint256,string,bytes32)
        tx_func = contract_inst.functions.registerBatch(
            batch_id,
            medicine_name,
            manufacturer,
            int(mfg_date),
            int(exp_date),
            region,
            batch_hash,
        )

        # Estimate gas
        print("Estimating gas...")
        gas_estimate = tx_func.estimate_gas({"from": account.address})
        print(f"Gas estimated ({time.time()-t0:.2f}s)")

        transaction = tx_func.build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "gas": gas_estimate + 10000,
                "gasPrice": _w3.eth.gas_price,
                "chainId": _w3.eth.chain_id,
            }
        )

        # Sign and send
        print("Signing and sending...")
        signed_tx = _w3.eth.account.sign_transaction(transaction, ETH_PRIVATE_KEY)
        
        # Support both web3 v5 and v6 property names
        raw_tx = getattr(signed_tx, "raw_transaction", getattr(signed_tx, "rawTransaction", None))
        tx_hash = _w3.eth.send_raw_transaction(raw_tx)
        print(f"Sent! Hash: {tx_hash.hex()} ({time.time()-t0:.2f}s)")

        # Wait for receipt
        print("Waiting for receipt...")
        receipt = _w3.eth.wait_for_transaction_receipt(tx_hash, timeout=15)
        print(f"Mined! Total time: {time.time()-t0:.2f}s")

        if receipt.status == 1:
            return {"success": True, "tx_hash": tx_hash.hex()}
        else:
            return {"success": False, "error": "Transaction failed"}

    except Exception as e:
        print(f"Blockchain registration error: {e}")
        if "Batch exists" in str(e):
            return {"success": False, "error": "Batch already registered on blockchain"}
        return {"success": False, "error": str(e)}


def get_recent_batches(limit=10, manufacturer=None):
    contract_inst = get_contract()
    if not contract_inst or not _w3:
        return {"status": "error", "message": "Blockchain unavailable"}

    try:
        # Fetch BatchRegistered events
        logs = contract_inst.events.BatchRegistered.get_logs(from_block=0)

        batches = []
        # Reverse to get latest first and filter
        for log in reversed(logs):
            if len(batches) >= limit:
                break

            batch_id = log.args.batchId
            # Verify to get full details
            details = verify_batch(batch_id)
            if details.get("valid"):
                m_name = details.get("manufacturer", "").upper()

                # Apply filter if provided (case-insensitive partial match)
                if manufacturer:
                    target = manufacturer.strip().upper()
                    if target not in m_name:
                        continue

                batches.append(
                    {
                        "batch_id": batch_id,
                        "medicine_name": details.get("name"),
                        "manufacturer": m_name,
                        "expiry": details.get("expiry"),
                        "region": details.get("region"),
                        "tx_hash": log.transactionHash.hex(),
                        "block_number": log.blockNumber,
                    }
                )

        return {"status": "success", "data": batches}
    except Exception as e:
        print(f"Error fetching recent batches: {e}")
        return {"status": "error", "message": str(e)}
