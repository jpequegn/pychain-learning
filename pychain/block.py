import hashlib
import json
import time


class Block:
    """
    A single block in the blockchain.

    Attributes:
        index (int): Position of the block in the chain (0 for genesis block)
        timestamp (float): Unix timestamp of when the block was created
        data (any): The data/payload stored in this block (can be string, dict, or list)
        previous_hash (str): Hash of the previous block in the chain
        difficulty (int): Number of leading zeros required in hash (Proof of Work)
        nonce (int): Counter used in mining to find valid hash
        hash (str): SHA-256 hash of this block
    """

    def __init__(self, index, timestamp, data, previous_hash, difficulty=2):
        """
        Initialize a new Block.

        Args:
            index (int): Position of the block in the chain
            timestamp (float): Unix timestamp of block creation
            data (any): Data to be stored in the block
            previous_hash (str): Hash of the previous block
            difficulty (int): Mining difficulty (default: 2)
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate the SHA-256 hash of this block.

        Concatenates index, timestamp, data (as string), previous_hash, and nonce,
        then generates a SHA-256 hash.

        Returns:
            str: Hexadecimal digest of the block's hash
        """
        # Convert data to string representation
        # Use JSON for dicts/lists to ensure consistent serialization
        if isinstance(self.data, (dict, list)):
            data_string = json.dumps(self.data, sort_keys=True)
        else:
            data_string = str(self.data)

        # Concatenate all block components (including nonce for PoW)
        block_string = f"{self.index}{self.timestamp}{data_string}{self.previous_hash}{self.nonce}"

        # Encode to bytes and hash
        block_bytes = block_string.encode()
        hash_object = hashlib.sha256(block_bytes)

        return hash_object.hexdigest()

    def mine_block(self):
        """
        Mine the block by finding a nonce that produces a hash
        meeting the difficulty requirement.

        The mining process increments the nonce until a hash is found
        that starts with 'difficulty' number of zeros.

        Returns:
            float: Time taken to mine the block in seconds
        """
        start_time = time.time()

        # Target: hash must start with 'difficulty' number of zeros
        target = "0" * self.difficulty

        # Keep trying different nonces until we find a valid hash
        while self.hash[:self.difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        end_time = time.time()
        mining_time = end_time - start_time

        print(f"Block mined! Nonce: {self.nonce}, Hash: {self.hash}")
        print(f"Mining time: {mining_time:.2f} seconds")

        return mining_time
