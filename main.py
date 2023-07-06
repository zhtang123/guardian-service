from flask import Flask, request, jsonify
import logging
from database import Database
from verifiers.wallet_verifier import WalletVerifier

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.url_map.strict_slashes = False

db = Database()
wallet_verifier = WalletVerifier(db)
@app.route('/create/', methods=['POST'])
def add_guardian_email():
    try:
        data = request.get_json()

        for guardian in data:
            address = guardian['guardian']
            guardian_type = guardian['type']
            guardian_info = guardian['info']
            signature = guardian['signature']

            db.add_guardian(address, guardian_type, guardian_info, signature)

        return jsonify({'code': 0, 'message': 'ok', 'data': None, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'insert_fail', 'data': None, 'success': False}), 500

@app.route('/update/<transaction_hash>',methods=['GET'])
def update_guardian_wallet(transaction_hash):
    logging.info("start update guardian <--> wallet")
    try:
        wallet_verifier.verify(transaction_hash, 'polygon')
        return jsonify({'code': 0, 'message': 'ok', 'success': True})
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'success': False}), 500


@app.route('/query/info', methods=['POST'])
def query_guardian_email():
    try:
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

        return jsonify({'code': 0, 'message': 'ok', 'data': results, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500

@app.route('/query/guardian2wallet/<guardian_address>/', methods=['GET'])
def query_wallet_by_guardian(guardian_address):
    try:
        wallets = db.get_wallets_by_guardian(guardian_address)
        return jsonify({'code': 0, 'message': 'ok', 'data': wallets, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500

@app.route('/query/wallet2guardian/<wallet_address>/', methods=['GET'])
def query_guardian_by_wallet(wallet_address):
    try:
        threshold, guardians = db.get_guardians_by_wallet(wallet_address)
        return jsonify({'code': 0, 'message': 'ok', 'threshold': threshold, 'data': guardians, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12001)
