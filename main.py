from flask import Flask, request, jsonify
import logging
from database import Database
from verifiers.wallet_verifier import WalletVerifier
from functools import wraps

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.url_map.strict_slashes = False

db = Database()
wallet_verifier = WalletVerifier(db)

def log_and_catch_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Start {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"{func.__name__} executed successfully")
            return jsonify({'code': 0, 'message': 'ok', 'data': result, 'success': True})
        except Exception as e:
            logging.error(f"Error occurred in {func.__name__}: {str(e)}")
            return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500
    return wrapper

@app.route('/create/', methods=['POST'])
@log_and_catch_error
def add_guardian_email():
    data = request.get_json()

    for guardian in data:
        address = guardian['guardian']
        guardian_type = guardian['type']
        guardian_info = guardian['info']
        signature = guardian['signature']

        db.add_guardian(address, guardian_type, guardian_info, signature)
    return None

@app.route('/update/',methods=['POST'])
@log_and_catch_error
def update_guardian_wallet():
    data = request.get_json()
    transaction_hash = data['transaction_hash']
    chain = data['chain']
    wallet_verifier.verify(transaction_hash, chain)
    return None

@app.route('/query/info/', methods=['POST'])
@log_and_catch_error
def query_guardian_email():
    data = request.get_json()
    guardians = data['guardians']

    results = []
    for guardian in guardians:
        address = guardian.strip().lower()
        guardians_info = db.get_guardians_by_address(address)
        for info in guardians_info:
            result = {
                'guardian': info['guardian'],
                'type': info['type'],
                'info': info['info']
            }
            results.append(result)
    return results

@app.route('/query/guardian2wallet/', methods=['POST'])
@log_and_catch_error
def query_wallet_by_guardian():
    data = request.get_json()
    guardian_address = data['address']
    wallets = db.get_wallets_by_guardian(guardian_address)
    return wallets

@app.route('/query/wallet2guardian/', methods=['POST'])
@log_and_catch_error
def query_guardian_by_wallet():
    data = request.get_json()
    wallet_address = data['address']
    chain = data['chain']
    threshold, guardians = db.get_guardians_by_wallet(wallet_address, chain)
    return {'threshold': threshold, 'guardians': guardians}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12001)
