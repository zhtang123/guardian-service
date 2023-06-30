from flask import Flask, request, jsonify
import logging
from database import Database

app = Flask(__name__)

db = Database()

@app.route('/guardian-wallet/email', methods=['POST'])
def add_guardian_email():
    try:
        data = request.get_json()

        for guardian in data:
            address = guardian['guardian']
            guardian_type = guardian['type']
            guardian_info = guardian['info']
            signature = guardian['signature']

            db.add_guardian(address, guardian_type, guardian_info, signature)

        return jsonify({'code': 0, 'message': '处理成功', 'data': None, 'success': True})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'code': 1, 'message': '处理失败', 'data': None, 'success': False}), 500

@app.route('/guardian-wallet/email/query', methods=['POST'])
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
        return jsonify({'code': 1, 'message': '处理失败', 'data': None, 'success': False}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12001)
