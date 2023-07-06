import requests
import json
import os

class Block:
    def __init__(self, block_number, block_hash, transaction_hash):
        self.block_number = block_number
        self.block_hash = block_hash
        self.transaction_hash = transaction_hash

class UserOp:
    def __init__(self, user_operation_hash, chain):
        self.user_operation_hash = user_operation_hash
        self.endpoint = os.environ.get('BLOCK_API_URL') + f"/bundler/{chain}"

    def get_transaction(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getUserOperationByHash",
            "params": [self.user_operation_hash]
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            result = response.json().get('result', {})
            return Block(
                block_number=result.get('blockNumber', None),
                block_hash=result.get('blockHash', None),
                transaction_hash=result.get('transactionHash', None),
            )
        else:
            return None
