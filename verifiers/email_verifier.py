from web3 import Web3, exceptions
from eth_utils import to_checksum_address

class CustomerException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
        super().__init__(self.error_code)

class MyClass:
    def __init__(self, email, signature, guardian):
        self.email = email
        self.signature = signature
        self.guardian = guardian

    def inner_get_msg_hash(self):
        try:
            message_hash = Web3.keccak(text=self.email).hex()
            return message_hash
        except Exception as e:
            raise CustomerException("BAD_SIGN_ERROR")

    def check(self):
        message_hash = self.inner_get_msg_hash()
        try:
            r = int(self.signature[:64], 16)
            s = int(self.signature[64:128], 16)
            v = 27 + int(self.signature[128:130], 16) # 把 v 的值调整到 27 或 28
            signature = bytes([v]) + r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
            recovered_address = Web3().eth.account._recover_hash(bytes.fromhex(message_hash[2:]), signature=signature)
            print(recovered_address)
            if to_checksum_address(recovered_address) != self.guardian:
                raise CustomerException("BAD_SIGN_ERROR")
        except (exceptions.InvalidAddress, exceptions.BadFunctionCallOutput) as e:
            print(e)
            raise CustomerException("BAD_SIGN_ERROR")
