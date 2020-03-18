import hashlib
import requests
import time
import sys
import json
import random


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block ,sort_keys=True)
    print(f'************** \nPRE MINER PROOF OF WORK: block_string {block_string}\n **************')
    proof = random.randint(0, 10000)
    print(f'************** \nPRE MINER PROOF OF WORK: random proof {block_string}\n **************')
    while valid_proof(block_string, proof) is False:
        proof += 1
        print(f'INVALID HASH: Searching for proof.....\n      next attempted proof: {proof}')
        # print(f'proof: {proof}')

    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print(f'guess_hash: {guess_hash}')

    return guess_hash[:4] == '0000'

if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    coins_mined = 0 
    print(f'**************\nWe started mining\n**************')
    start_time = time.time()

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            break
        print(f'Request Data: {data}')

        # TODO: Get the block from `data` and use it to look for a new proof
        # new_proof = ???
        block = data['last_block']

        # Get New Proof
        
        new_proof = proof_of_work(block)
        print(f'********\nNew Proof: {new_proof}\n********')

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        
        print(f'********\nRESPONSE FROM /mine: {data}\n********')
        breakpoint()

        if data['new_block']:
            end_time = time.time()
            print(f'It took {end_time - start_time} to mine the coin')
            coins_mined += 1
            print(f'Num of coins mined: {coins_mined}')
        else:
            end_time = time.time()
            print(f'It took {end_time - start_time} to FAIL')
            print(data['message'])
        
        print(f'********\n--- END OF LOOP ---\n********')
        breakpoint()
