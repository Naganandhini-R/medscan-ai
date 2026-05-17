from web3 import Web3
import os

GANACHE_URL = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.is_connected():
    print(f"Connected to {GANACHE_URL}")
    print(f"Chain ID: {w3.eth.chain_id}")
    print(f"Latest Block: {w3.eth.block_number}")
    accounts = w3.eth.accounts
    if accounts:
        print(f"First Account: {accounts[0]}")
        print(f"Balance: {w3.from_wei(w3.eth.get_balance(accounts[0]), 'ether')} ETH")

    # Check if code exists at the address
    addr = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    code = w3.eth.get_code(addr)
    print(
        f"Code at {addr}: {'Present' if len(code) > 2 else 'EMPTY (Not a contract or wrong network)'}"
    )
else:
    print(f"❌ Failed to connect to {GANACHE_URL}")
