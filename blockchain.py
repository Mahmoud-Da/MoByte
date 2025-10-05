import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000':
                return new_proof
            new_proof += 1

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        for block_index in range(1, len(chain)):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            prev_proof = previous_block['proof']
            proof = block['proof']
            hash_op = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_op[:4] != '0000':
                return False
            previous_block = block
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount})
        return self.get_previous_block()['index'] + 1

    def add_node(self, address):
        parsed = urlparse(address)
        self.nodes.add(parsed.netloc)

    def replace_chain(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            try:
                response = requests.get(f'http://{node}/get_chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']
                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        longest_chain = chain
            except:
                pass
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
