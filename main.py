from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4
import json

import argparse

# ------------------------
# Command-line argument for port
# ------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=5001, help="Port to run the server")
args = parser.parse_args()
PORT = args.port

# ------------------------
# Flask App Setup
# ------------------------
app = Flask(__name__)
node_address = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# ------------------------
# Routes
# ------------------------
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(sender=node_address, receiver='MoByte', amount=1)
    block = blockchain.create_block(proof, prev_hash)
    return jsonify({
        'message': 'Block mined!',
        'index': block['index'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    return jsonify({'message': 'Blockchain valid!' if valid else 'Blockchain invalid!'}), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    keys = ['sender', 'receiver', 'amount']
    if not all(k in data for k in keys):
        return 'Missing transaction fields', 400
    index = blockchain.add_transaction(data['sender'], data['receiver'], data['amount'])
    return jsonify({'message': f'Transaction added to block {index}'}), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    data = request.get_json()
    nodes = data.get('nodes')
    if not nodes:
        return 'No nodes provided', 400
    for node in nodes:
        blockchain.add_node(node)
    return jsonify({'message': 'Nodes connected', 'total_nodes': list(blockchain.nodes)}), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    replaced = blockchain.replace_chain()
    return jsonify({'message': 'Chain replaced' if replaced else 'Chain is longest', 
                    'chain': blockchain.chain}), 200

# ------------------------
# Run Server
# ------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
