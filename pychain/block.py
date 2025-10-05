import hashlib
import json
import time


class Block:
    """
    A single block in the blockchain.

    Attributes:
        index (int): Position of the block in the chain (0 for genesis block)
        timestamp (float): Unix timestamp of when the block was created
        transactions (list): List of Transaction objects stored in this block
        data (any): Legacy data field (for backward compatibility)
        previous_hash (str): Hash of the previous block in the chain
        difficulty (int): Number of leading zeros required in hash (Proof of Work)
        nonce (int): Counter used in mining to find valid hash
        hash (str): SHA-256 hash of this block
    """

    def __init__(self, index, timestamp, data, previous_hash, difficulty=2):
        """
        Initialize a new Block.

        Supports both legacy 'data' format and new 'transactions' format.
        If data is a list of Transaction objects, stores them as transactions.
        Otherwise, stores data in legacy format for backward compatibility.

        Args:
            index (int): Position of the block in the chain
            timestamp (float): Unix timestamp of block creation
            data (any): Data or list of Transaction objects to store
            previous_hash (str): Hash of the previous block
            difficulty (int): Mining difficulty (default: 2)
        """
        self.index = index
        self.timestamp = timestamp

        # Support both transactions and legacy data
        # Check if data is a list of Transaction objects
        if isinstance(data, list) and len(data) > 0 and hasattr(data[0], 'transaction_id'):
            self.transactions = data
            self.data = None  # No legacy data
        else:
            self.data = data
            self.transactions = None  # No transactions

        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate the SHA-256 hash of this block.

        Handles both transaction-based blocks and legacy data blocks.
        For transactions, serializes all transaction data to JSON.
        For legacy data, uses the original serialization method.

        Returns:
            str: Hexadecimal digest of the block's hash
        """
        # Handle transaction-based blocks
        if self.transactions is not None:
            # Serialize transactions to JSON
            transactions_data = json.dumps(
                [tx.to_dict() for tx in self.transactions],
                sort_keys=True
            )
            data_string = transactions_data
        else:
            # Legacy data handling
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

    def get_transaction_count(self):
        """
        Get the number of transactions in this block.

        Returns:
            int: Number of transactions (0 if block uses legacy data format)
        """
        if self.transactions is not None:
            return len(self.transactions)
        return 0

    def get_total_amount(self):
        """
        Calculate total transaction amount in this block.

        Returns:
            float: Sum of all transaction amounts (0 if block uses legacy data format)
        """
        if self.transactions is not None:
            return sum(tx.amount for tx in self.transactions)
        return 0

    def __str__(self):
        """
        String representation of the block.

        Returns:
            str: Human-readable block description
        """
        if self.transactions is not None:
            return f"Block {self.index} with {len(self.transactions)} transactions"
        else:
            return f"Block {self.index} with data: {self.data}"
