from verifiers.get_events import EVMChainHandler
from verifiers.get_transaction import Block, UserOp
import logging
import requests
import json
import os


class WalletVerifier:

    def __init__(self, database, max_block_number=0):
        self.events_handler = EVMChainHandler("./verifiers/chains.json")
        self.database = database
        self.max_block_number = {}

    def verify(self, transaction_hash, chain):

        logging.info("parse event start")
        ops = self.events_handler.get_transaction_events(transaction_hash, chain)
        logging.info("parse event done")
        for op in ops:
            if op['type'] == 'change_threshold':
                self.database.change_threshold(op['wallet'], op['threshold'], chain)
            elif op['type'] == 'add':
                self.database.add_wallet_guardian(op['guardian'], op['wallet'], chain)
            elif op['type'] == 'revoke':
                self.database.del_wallet_guardian(op['guardian'], op['wallet'], chain)
            elif op['type'] == 'change_guardian_status':
                self.database.change_guardian_status(op['wallet'], op['status'], chain)

        logging.info("update db done")




