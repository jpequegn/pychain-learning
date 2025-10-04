import hashlib
import json


class Block:
    """
    A single block in the blockchain.

    Attributes:
        index (int): Position of the block in the chain (0 for genesis block)
        timestamp (float): Unix timestamp of when the block was created
        data (any): The data/payload stored in this block (can be string, dict, or list)
        previous_hash (str): Hash of the previous block in the chain
        hash (str): SHA-256 hash of this block
    """

    def __init__(self, index, timestamp, data, previous_hash):
        """
        Initialize a new Block.

        Args:
            index (int): Position of the block in the chain
            timestamp (float): Unix timestamp of block creation
            data (any): Data to be stored in the block
            previous_hash (str): Hash of the previous block
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate the SHA-256 hash of this block.

        Concatenates index, timestamp, data (as string), and previous_hash,
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

        # Concatenate all block components
        block_string = f"{self.index}{self.timestamp}{data_string}{self.previous_hash}"

        # Encode to bytes and hash
        block_bytes = block_string.encode()
        hash_object = hashlib.sha256(block_bytes)

        return hash_object.hexdigest()
