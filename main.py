import hashlib
import json
from time import time, sleep
import matplotlib.pyplot as plt
import random
from threading import Thread


class Blockchain:
    def __init__(self, node_id):
        self.chain = []
        self.current_transactions = []
        self.node_id = node_id

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        # Creates a new block and adds it to the chain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'node_id': self.node_id,
            'parent_block': self.chain[-1]['index'] if len(self.chain) > 0 else None
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, product_id, location, event):
        # Adds a new transaction to the blockchain
        self.current_transactions.append({
            'product_id': product_id,
            'location': location,
            'event': event,
            'timestamp': time(),
            'node_id': self.node_id
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        # Simple Proof of Work Algorithm
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Define event types
event_types = ['Received', 'Shipped', 'Defect Identified', 'Quality Check in Process']


# Function to simulate a node adding transactions and mining blocks
def node_simulation(blockchain, num_transactions, sleep_interval):
    for i in range(num_transactions):
        product_id = f'Product-{random.randint(1, 100)}'
        location = f'Location-{random.randint(1, 5)}'
        event = random.choice(event_types)

        blockchain.new_transaction(product_id, location, event)

        # Simulate mining the block
        last_proof = blockchain.last_block['proof']
        proof = blockchain.proof_of_work(last_proof)
        blockchain.new_block(proof)

        # Simulate random delay
        sleep(random.uniform(0.5, sleep_interval))


# Create 10 nodes (blockchains) to simulate distribution
nodes = [Blockchain(node_id=f'Node-{i + 1}') for i in range(10)]

# Run node simulations in parallel using threading
num_transactions_per_node = 5
threads = []

# Create threads for each node
for node in nodes:
    threads.append(Thread(target=node_simulation, args=(node, num_transactions_per_node, 2)))

# Start all threads
for thread in threads:
    thread.start()

# Join all threads to ensure they complete
for thread in threads:
    thread.join()

# Merge blocks from all nodes to represent the tree structure
all_blocks = []
for node in nodes:
    all_blocks += node.chain

all_blocks = sorted(all_blocks, key=lambda x: x['timestamp'])

# Prepare data for tree visualization
block_indices = [block['index'] for block in all_blocks]
parent_blocks = [block['parent_block'] for block in all_blocks]
nodes_ids = [block['node_id'] for block in all_blocks]

# Assign Y values based on node_id for better visual separation
unique_nodes = list(set(nodes_ids))
node_to_y = {node: i + 1 for i, node in enumerate(unique_nodes)}
y_values = [node_to_y[block['node_id']] for block in all_blocks]

# Create the figure and axis
plt.figure(figsize=(14, 10))

# Plot the tree structure
for i in range(len(block_indices)):
    plt.scatter(block_indices[i], y_values[i], color='blue', s=100)

    if parent_blocks[i] is not None:
        parent_idx = block_indices.index(parent_blocks[i])
        plt.plot([block_indices[parent_idx], block_indices[i]], [y_values[parent_idx], y_values[i]], color='black')

# Annotate with node names
for i in range(len(block_indices)):
    plt.text(block_indices[i], y_values[i], f'{nodes_ids[i]}', fontsize=10, ha='right')

# Add labels and title
plt.title('Blockchain Tree Structure with 10 Node Forks')
plt.xlabel('Block Index (Sequence of Block Creation)')
plt.ylabel('Nodes')

# Adjust the layout and show the plot
plt.tight_layout()
plt.show()
