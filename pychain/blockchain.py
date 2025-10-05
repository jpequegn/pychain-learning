import time
from pychain.block import Block


class Blockchain:
    """
    A blockchain that manages a chain of blocks.

    The blockchain automatically creates a genesis block upon initialization
    and provides methods to manage the chain.

    Attributes:
        chain (list): List of Block objects representing the blockchain
        difficulty (int): Mining difficulty for Proof of Work
    """

    def __init__(self, difficulty=2):
        """
        Initialize the blockchain with a genesis block.

        Creates an empty chain list and automatically adds the genesis block.

        Args:
            difficulty (int): Mining difficulty (default: 2)
        """
        self.chain = []
        self.difficulty = difficulty
        self.chain.append(self.create_genesis_block())

    def create_genesis_block(self):
        """
        Create the genesis block (first block in the blockchain).

        The genesis block has special properties:
        - Index: 0
        - Previous hash: "0" (no previous block exists)
        - Data: "Genesis Block"
        - Timestamp: Current time when blockchain is created

        The genesis block is mined using Proof of Work.

        Returns:
            Block: The genesis block
        """
        genesis = Block(0, time.time(), "Genesis Block", "0", self.difficulty)
        genesis.mine_block()
        return genesis

    def get_latest_block(self):
        """
        Get the most recent block in the chain.

        Returns:
            Block: The last block in the chain
        """
        return self.chain[-1]

    def add_block(self, data):
        """
        Add a new block to the blockchain.

        Creates a new block with the provided data and appends it to the chain.
        The new block is properly linked to the previous block through its hash
        and is mined using Proof of Work before being added.

        Args:
            data: The data/payload to store in the new block (can be string, dict, list, etc.)

        Returns:
            Block: The newly created and added block
        """
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_previous_hash = previous_block.hash

        new_block = Block(new_index, new_timestamp, data, new_previous_hash, self.difficulty)

        # Mine the block before adding to chain
        new_block.mine_block()

        self.chain.append(new_block)

        return new_block

    def is_chain_valid(self, verbose=False):
        """
        Validate the entire blockchain.

        Checks four key aspects:
        1. Genesis block has previous_hash == "0" and valid hash
        2. Each block's stored hash matches its calculated hash
        3. Each block's previous_hash matches the previous block's hash
        4. Each block meets Proof of Work requirements (hash starts with required zeros)

        Args:
            verbose (bool): If True, print detailed validation info

        Returns:
            bool: True if chain is valid, False otherwise
        """
        for i in range(len(self.chain)):
            current_block = self.chain[i]

            # Check hash integrity
            if current_block.hash != current_block.calculate_hash():
                if verbose:
                    print(f"❌ Block {i} hash mismatch")
                    print(f"   Stored: {current_block.hash}")
                    print(f"   Calculated: {current_block.calculate_hash()}")
                return False

            # Check Proof of Work (hash starts with required zeros)
            target = "0" * current_block.difficulty
            if current_block.hash[:current_block.difficulty] != target:
                if verbose:
                    print(f"❌ Block {i} doesn't meet PoW requirements")
                    print(f"   Expected: {target}...")
                    print(f"   Got: {current_block.hash[:current_block.difficulty]}...")
                return False

            # Check chain continuity
            if i == 0:
                # Genesis block validation
                if current_block.previous_hash != "0":
                    if verbose:
                        print("❌ Genesis block invalid: previous_hash != '0'")
                    return False
            else:
                # Regular block validation
                previous_block = self.chain[i - 1]
                if current_block.previous_hash != previous_block.hash:
                    if verbose:
                        print(f"❌ Block {i} broken chain link")
                        print(f"   previous_hash: {current_block.previous_hash}")
                        print(f"   Previous block hash: {previous_block.hash}")
                    return False

            if verbose:
                print(f"✅ Block {i} valid (Nonce: {current_block.nonce})")

        return True
