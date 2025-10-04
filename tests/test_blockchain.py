import unittest
import time
from pychain.blockchain import Blockchain
from pychain.block import Block


class TestBlockchain(unittest.TestCase):
    """Test cases for the Blockchain class."""

    def test_blockchain_initialization(self):
        """Test that blockchain initializes with a genesis block."""
        blockchain = Blockchain()

        # Verify chain is created
        self.assertIsNotNone(blockchain.chain)
        self.assertIsInstance(blockchain.chain, list)

        # Verify chain has exactly one block (genesis)
        self.assertEqual(len(blockchain.chain), 1)

    def test_genesis_block_properties(self):
        """Test that genesis block has correct properties."""
        blockchain = Blockchain()
        genesis = blockchain.chain[0]

        # Verify it's a Block instance
        self.assertIsInstance(genesis, Block)

        # Verify genesis block properties
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(genesis.data, "Genesis Block")

        # Verify timestamp is recent (within last second)
        current_time = time.time()
        self.assertAlmostEqual(genesis.timestamp, current_time, delta=1.0)

    def test_genesis_block_hash(self):
        """Test that genesis block has a valid hash."""
        blockchain = Blockchain()
        genesis = blockchain.chain[0]

        # Verify hash exists and is correct format
        self.assertIsNotNone(genesis.hash)
        self.assertIsInstance(genesis.hash, str)
        self.assertEqual(len(genesis.hash), 64)  # SHA-256 produces 64 hex chars
        self.assertTrue(all(c in '0123456789abcdef' for c in genesis.hash))

    def test_create_genesis_block_method(self):
        """Test that create_genesis_block() creates a valid genesis block."""
        blockchain = Blockchain()
        genesis = blockchain.create_genesis_block()

        # Verify it's a Block instance with correct properties
        self.assertIsInstance(genesis, Block)
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(genesis.data, "Genesis Block")

    def test_get_latest_block_returns_genesis_initially(self):
        """Test that get_latest_block() returns genesis block initially."""
        blockchain = Blockchain()
        latest = blockchain.get_latest_block()

        # Verify it returns the genesis block
        self.assertIsInstance(latest, Block)
        self.assertEqual(latest.index, 0)
        self.assertEqual(latest.previous_hash, "0")
        self.assertEqual(latest.data, "Genesis Block")

        # Verify it's the same object as chain[0]
        self.assertIs(latest, blockchain.chain[0])

    def test_multiple_blockchains_have_different_genesis_blocks(self):
        """Test that each blockchain instance has its own genesis block."""
        blockchain1 = Blockchain()
        time.sleep(0.01)  # Small delay to ensure different timestamps
        blockchain2 = Blockchain()

        genesis1 = blockchain1.get_latest_block()
        genesis2 = blockchain2.get_latest_block()

        # Both should be genesis blocks
        self.assertEqual(genesis1.index, 0)
        self.assertEqual(genesis2.index, 0)

        # But they should have different timestamps and hashes
        self.assertNotEqual(genesis1.timestamp, genesis2.timestamp)
        self.assertNotEqual(genesis1.hash, genesis2.hash)

        # They should be different objects
        self.assertIsNot(genesis1, genesis2)

    def test_genesis_block_is_deterministic_within_instance(self):
        """Test that calling create_genesis_block doesn't modify existing chain."""
        blockchain = Blockchain()
        original_genesis = blockchain.chain[0]
        original_hash = original_genesis.hash

        # Call create_genesis_block again (shouldn't affect chain)
        new_genesis = blockchain.create_genesis_block()

        # Original genesis should still be in chain
        self.assertIs(blockchain.chain[0], original_genesis)
        self.assertEqual(blockchain.chain[0].hash, original_hash)

        # Chain length should still be 1
        self.assertEqual(len(blockchain.chain), 1)

    def test_chain_length_after_initialization(self):
        """Test that chain length is 1 after initialization."""
        blockchain = Blockchain()
        self.assertEqual(len(blockchain.chain), 1)

    def test_usage_example_from_issue(self):
        """Test the usage example provided in the issue."""
        # Create a new blockchain
        blockchain = Blockchain()

        # Access genesis block
        genesis = blockchain.get_latest_block()

        # Verify expected behavior
        self.assertIsNotNone(genesis.hash)
        self.assertEqual(genesis.index, 0)
        self.assertEqual(len(blockchain.chain), 1)

        # Print for manual verification (optional)
        print(f"\nGenesis block hash: {genesis.hash}")
        print(f"Genesis block index: {genesis.index}")
        print(f"Chain length: {len(blockchain.chain)}")


if __name__ == '__main__':
    unittest.main()
