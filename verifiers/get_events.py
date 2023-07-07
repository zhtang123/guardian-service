import json
from web3 import Web3

class EVMChainHandler:
    def __init__(self, config_file):
        self.chain_config = self.load_chain_config(config_file)

        self.event_signatures = {
            "AddGuardian": Web3.keccak(text="AddGuardian(address,address)").hex(),
            "RevokeGuardian": Web3.keccak(text="RevokeGuardian(address,address)").hex(),
            "ChangeThreshold": Web3.keccak(text="ChangeThreshold(address,uint256)").hex()
        }

    @staticmethod
    def load_chain_config(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)

    def get_chain_info(self, chain_id):
        return self.chain_config.get(str(chain_id))

    def get_transaction_events(self, chain_id, tx_hash):
        chain = self.get_chain_info(chain_id)
        if not chain:
            raise ValueError(f'Unsupported chain ID: {chain_id}')

        w3 = Web3(Web3.HTTPProvider(chain['rpc']))
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

        events = []

        for log in tx_receipt['logs']:
            event_signature = log['topics'][0].hex()
            if event_signature == self.event_signatures['ChangeThreshold']:
                events.append(self.parse_change_threshold(log))
            elif event_signature == self.event_signatures['AddGuardian']:
                events.append(self.parse_add_guardian(log))
            elif event_signature == self.event_signatures['RevokeGuardian']:
                events.append(self.parse_revoke_guardian(log))

        return events

    @staticmethod
    def parse_change_threshold(log):
        data = log['data']

        wallet = Web3.to_checksum_address(data[12:32].hex())
        threshold = int(data[44:64].hex(), 16)

        return {
            'type': "change_threshold",
            'wallet': wallet,
            'threshold': threshold
        }


    @staticmethod
    def parse_add_guardian(log):
        data = log['data']

        wallet = Web3.to_checksum_address(data[12:32].hex())
        guardian = Web3.to_checksum_address(data[44:64].hex())

        return {
            'type': "add",
            'wallet': wallet,
            'guardian': guardian,
        }

    @staticmethod
    def parse_revoke_guardian(log):
        data = log['data']

        wallet = Web3.to_checksum_address(data[12:32].hex())
        guardian = Web3.to_checksum_address(data[44:64].hex())

        return {
            'type': "revoke",
            'wallet': wallet,
            'guardian': guardian,
        }

