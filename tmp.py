from get_events import *

handler = EVMChainHandler('chains.json')
transaction_hash = '0x0dab2eba67434e428de03e3ec957c1acf5cc2577b4186bcc4340059b0b89acef'
print(handler.get_transaction_events("polygon", transaction_hash))