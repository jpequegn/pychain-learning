import time
from pychain.block import Block


class Blockchain:
    """
    A blockchain that manages a chain of blocks.

    The blockchain automatically creates a genesis block upon initialization
    and provides methods to manage the chain.

    Attributes:
        chain (list): List of Block objects representing the blockchain
    """

    def __init__(self):
        """
        Initialize the blockchain with a genesis block.

        Creates an empty chain list and automatically adds the genesis block.
        """
        self.chain = []
        self.chain.append(self.create_genesis_block())

    def create_genesis_block(self):
        """
        Create the genesis block (first block in the blockchain).

        The genesis block has special properties:
        - Index: 0
        - Previous hash: "0" (no previous block exists)
        - Data: "Genesis Block"
        - Timestamp: Current time when blockchain is created

        Returns:
            Block: The genesis block
        """
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        """
        Get the most recent block in the chain.

        Returns:
            Block: The last block in the chain
        """
        return self.chain[-1]
