# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request, render_template, url_for, redirect
import requests
from uuid import uuid4
from urllib.parse import urlparse
from PIL import Image
import sqlite3

with open('ecgdata.csv') as file:
    content = file.read()
    

im = Image.open('C:\\Users\\rajga\\Downloads\\bouquet.jpg')


# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'im':im.show(),
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, data, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'data': data,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5001
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()


# Mining a new block



@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Harsh', amount=1, data='hey ')
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'file': content,
                'im': im,
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return render_template('content.html', content=content)


@app.route('/show', methods=['POST', 'GET'])
def show():
    return render_template('show.html', im = blockchain.chain[0])

# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Checking if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST', 'GET'])
def add_transaction():
    if request.method == 'POST':
        index = blockchain.add_transaction(request.form['sender'], request.form['receiver'], request.form['data'], request.form['amount'])
        response = {'message': f'This transaction will be added to Block {index}'}
        return jsonify(response), 201
    return render_template('add.html')


# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST', 'GET'])
def connect_node():
    if request.method == 'POST':
        nodes = [request.form['name1'], request.form['name2']]
        if nodes is None:
            return "No node", 400
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
        return jsonify(response), 201
    return render_template('connect.html')


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor', methods=['GET', 'POST'])    
def doctor():
    if(request.method == 'POST'):
        with sqlite3.connect("example.db") as conn:
            username = request.form['username']
            password = request.form['password']
            c = conn.cursor()
            t = (username, password, )
            c.execute('SELECT * FROM doctors WHERE username=? AND password=?', t)
            if(c.fetchone() is None):
                return '<h1>Username or password is incorrect</h1>'
            else:
                return render_template('chart.html', content=content)
        
    return render_template('doctor.html')
    
@app.route('/pharmacist', methods=['GET', 'POST'])    
def pharmacist():
    if(request.method == 'POST'):
        with sqlite3.connect("example.db") as conn:
            username = request.form['username']
            password = request.form['password']
            c = conn.cursor()
            t = (username, password, )
            c.execute('SELECT * FROM pharma WHERE username=? AND password=?', t)
            if(c.fetchone() is None):
                return '<h1>Username or password is incorrect</h1>'
            else:
                return render_template('chart.html', content=content)
        
    return render_template('pharmacist.html')

@app.route('/insurance', methods=['GET', 'POST'])    
def insurance():
    if(request.method == 'POST'):
        with sqlite3.connect("example.db") as conn:
            username = request.form['username']
            password = request.form['password']
            c = conn.cursor()
            t = (username, password, )
            c.execute('SELECT * FROM insurance WHERE username=? AND password=?', t)
            if(c.fetchone() is None):
                return '<h1>Username or password is incorrect</h1>'
            else:
                return render_template('chart.html', content=content)
        
    return render_template('insurance.html')
    
@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    if(request.method == 'POST'):
        with sqlite3.connect("example.db") as conn:
            username = request.form['username']
            password = request.form['password']
            user = request.form['user']
            c = conn.cursor()
            t = (1, username, password)
            if(user == 'doctor'):
                c.execute('INSERT INTO doctors VALUES (?, ?, ?)', t)
                return redirect(url_for('doctor'))
            elif(user == 'pharmacist'):
                c.execute('INSERT INTO pharma VALUES (?, ?, ?)', t)
                return redirect(url_for('pharmacist'))
            else:
                c.execute('INSERT INTO insurance VALUES (?, ?, ?)', t)
                return redirect(url_for('insurance'))
                
    return render_template('new_user.html')

# Running the app
app.run(debug=True, port=5002)
