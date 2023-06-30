from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)

db = Database()

@app.route('/guardians', methods=['POST'])
def add_guardian():
    data = request.get_json()
    address = data['address']
    guardian_type = data['type']
    guardian_info = data['info']

    db.add_guardian(address, guardian_type, guardian_info)

    return jsonify({'message': 'Guardian added successfully.'})

@app.route('/guardians/address/<address>', methods=['GET'])
def get_guardians_by_address(address):
    guardians = db.get_guardians_by_address(address)

    return jsonify({'guardians': guardians})

@app.route('/addresses/guardian', methods=['GET'])
def get_addresses_by_guardian():
    guardian_type = request.args.get('type')
    addresses = db.get_addresses_by_guardian(guardian_type)

    return jsonify({'addresses': addresses})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12001)
