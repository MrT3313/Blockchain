import hashlib
import json
from time import time
from uuid import uuid4
import random

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof, 
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        # Reset the current list of transactions
        self.current_transactions = [] # Transactions are stored ON THE SIDE until a proof id found for the last block on the chain and a new block is and filled with thos transactions
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block


    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        

        # TODO: Create the block_string
        string_block = json.dumps(block,sort_keys=True).encode()
        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(string_block)        # RETURNS AN OBJECT

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand
        hex_hash = raw_hash.hexdigest()

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):       # DONT OFFLOAD THIS!! YOU NEED THE VARIFICATIO ON BOTH SIDES
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f'{block_string}{proof}'.encode()
        print(f'********\n/mine\nINSIDE valid_proof(): encoded guess {guess}\n********')

        guess_hash = hashlib.sha256(guess).hexdigest()
        print(f'********\n/mine\nINSIDE valid_proof(): guess hash {guess_hash}\n********')

        return guess_hash[:4] == '0000'

    def new_transaction(self, sender, recipient, amount):
        '''
            :param sender: <str> Address of the Recipient
            :param recipient: <str> Address of the Recipient
            :param amount: <int> Amount
            :return: <int> The index of the `block` that will hold this transaction
        '''
        print(f'NEW TRANSACTION - pre: len = {len(self.current_transactions)}')

        # Prepare Transactoin
        prep_new_transaction = {
            'sender': sender, 
            'recipient': recipient,
            'amount': amount
        }
        print(f'********\nNew Transaction {prep_new_transaction}\n********')

        # Append transaction
        # ❗️WHY IS IT ADDING IT TO THE ROOT BLOCK!!!!!
        self.current_transactions.append(prep_new_transaction)
        print(f'********\nUPDATED current_transactions {self.current_transactions}\n********')
        breakpoint()

        return self.last_block['index'] + 1



# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/last_block', methods=['GET'])
def return_last_block():
    response = {
        'last_block': blockchain.last_block
    }

    return jsonify(response), 200

@app.route('/mine', methods=['POST'])
def mine():
    # Check for non JSON values
    try:
        values = request.get_json()
    except ValueError:
        response = {'Error': 'Error:  Non-json response'}
        return jsonify(response), 400

    # Check for appropriate values have been passed to /mine
    required = ['proof', 'id']
    if not all (k in values for k in required):
        response = {'Error': 'Missing Values'}
        return jsonify(response), 400
    submitted_proof = values['proof']
    miner_id = values['id']

    # get last block
    last_block = blockchain.last_block
    print(f'********\n/mine endpoint:\nLast Block {last_block}\n{type(last_block)}\n********')

    # Turn into block_string
    block_string = json.dumps(last_block, sort_keys=True)
    print(f'********\n/mine endpoint:\nBlock String {block_string}\n{type(block_string)}\n********')

    if blockchain.valid_proof(block_string, submitted_proof):
        print(f'********\n/Proof is VALID\n********')
        breakpoint()
        # ❗️NEEDS TO BE BEFORE FORGING THE NEW BLOCK -- the current_transactions (on the SIDE) need to be updated to put INTO new block
        # Reward the miner!!
        blockchain.new_transaction(sender='THE COIN GODS', recipient=miner_id, amount=1)

        # Get previous hash
        previous_hash = blockchain.hash(blockchain.last_block)
        # Forge new block
        forged_block = blockchain.new_block(submitted_proof, previous_hash)
        print(f'********\n/mine endpoint:\nProof is VALID: Forged Block {forged_block}\n********')
        breakpoint()



        # Prepare Response
        # ❗️❗️❗️❗️
        # TODO: Send a JSON response with the new block
        # ❗️❗️❗️❗️
        # response = {
        #     'message': "New Block Forged",
        #     'index': forged_block['index'],
        #     'transactions': forged_block['transactions'],
        #     'proof': forged_block['proof'],
        #     'previous_hash': forged_block['previous_hash'],
        # }
        response = {
            'new_block': forged_block
        }

        return jsonify(response), 200
    else:
        print(f'********\n/Proof is NOT valid\n********')
        breakpoint()
        response = {
            'message': 'Proof Either Invalid or Late'
        }
        return jsonify(response), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain' : blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)