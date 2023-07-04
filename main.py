from flask import Flask, request, jsonify
import logging
from database import Database

app = Flask(__name__)
app.url_map.strict_slashes = False

db = Database()

@app.route('/guardian-wallet/email/', methods=['POST'])
def add_guardian_email():
    try:
        data = request.get_json()

        for guardian in data:
            address = guardian['guardian']
            wallet_address = guardian['wallet']
            guardian_type = guardian['type']
            guardian_info = guardian['info']
            signature = guardian['signature']

            db.add_guardian(address, guardian_type, guardian_info, signature)
            db.add_wallet_guardian(address,wallet_address)

        return jsonify({'code': 0, 'message': 'ok', 'data': None, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'insert_fail', 'data': None, 'success': False}), 500

@app.route('/guardian-wallet/email/query/', methods=['POST'])
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

@app.route('/guardian-wallet/get-wallet/<guardian_address>/', methods=['GET'])
def query_wallet_by_guardian(guardian_address):
    try:
        wallets = db.get_wallets_by_guardian(guardian_address)
        return jsonify({'code': 0, 'message': 'ok', 'data': wallets, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500

@app.route('/guardian-wallet/get-guardian/<wallet_address>/', methods=['GET'])
def query_guardian_by_wallet(wallet_address):
    try:
        guardians = db.get_guardians_by_wallet(wallet_address)
        return jsonify({'code': 0, 'message': 'ok', 'data': guardians, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': 'query_fail', 'data': None, 'success': False}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12001)
