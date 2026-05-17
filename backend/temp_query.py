import sys, os
sys.path.append(os.path.abspath(r'c:\Users\HP\OneDrive\Desktop\medscan-ai\backend'))
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(r'c:\Users\HP\OneDrive\Desktop\medscan-ai\.env'))

from app.blockchain.web3_client import get_contract
contract = get_contract()
batches = ['INC2570', 'GF244009', 'AMX260315B', 'PARA260402X', 'CPL50576']
from datetime import datetime
for b in batches:
    try:
        name, exp_ts, mfg, region = contract.functions.verifyBatch(b).call()
        print('Batch:', b)
        print('Name:', name)
        print('Mfg:', mfg)
        print('Exp:', datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d'))
        print('Region:', region)
        print('-'*30)
    except Exception as e:
        pass
