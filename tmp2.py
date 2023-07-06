from eth_account.messages import defunct_hash_message
from eth_account.account import Account
from eth_abi import encode
import struct

def encode_utf8_string(string_value):
    encoded_string = string_value.encode('utf-8')
    encoded_length = len(encoded_string)
    encoded_length_bytes = struct.pack('>I', encoded_length)
    encoded_value = encoded_length_bytes + encoded_string
    return encoded_value

def encode_dynamic_struct(email):
    encoded_email = encode_utf8_string(email)
    encoded_struct = encode_utf8_string('String') + encode_utf8_string('email') + encoded_email
    return encoded_struct




message = "google:jmingwei6@gmail.com"
signature = '0x2600512e2394c9936955174f646193a0d4d7f9b7275df7cb15d5ddb3737322f5367a223b98b977d75a279af99d74778ac96cdd72985adf7cc6a47a942ee956451b'

message = encode_dynamic_struct(message)
print(message)
message_hash = defunct_hash_message(message)
print(str(message_hash))
public_key = Account._recover_hash(message_hash, signature=signature)

print(public_key)
