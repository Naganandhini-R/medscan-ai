from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

if w3.is_connected():
    print("Connected to Blockchain")
    print(f"Chain ID: {w3.eth.chain_id}")

    accounts = w3.eth.accounts
    print(f"Found {len(accounts)} accounts")

    for i, acc in enumerate(accounts):
        balance = w3.eth.get_balance(acc)
        eth_balance = w3.from_wei(balance, "ether")
        print(f"[{i}] {acc}: {eth_balance} ETH")

        # Check current .env address
        current_pk_addr = (
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # derived from 0xac09...
        )
        if acc.lower() == current_pk_addr.lower():
            print(f"   -> MATCHES your current private key!")
else:
    print("❌ Failed to connect to Blockchain")
