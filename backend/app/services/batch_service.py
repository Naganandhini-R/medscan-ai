from app.blockchain.web3_client import verify_batch as web3_verify

def verify_batch_on_chain(batch_id: str):
    """
    Wrapper service to verify batch on blockchain.
    """
    return web3_verify(batch_id)
