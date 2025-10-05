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

    # Tests for add_block() method

    def test_add_single_block(self):
        """Test adding a single block to the blockchain."""
        blockchain = Blockchain()

        # Add a block
        new_block = blockchain.add_block("Test data")

        # Verify chain length increased
        self.assertEqual(len(blockchain.chain), 2)

        # Verify new block properties
        self.assertEqual(new_block.index, 1)
        self.assertEqual(new_block.data, "Test data")
        self.assertEqual(new_block.previous_hash, blockchain.chain[0].hash)

        # Verify new block is in chain
        self.assertIs(blockchain.chain[1], new_block)

    def test_add_block_with_string_data(self):
        """Test adding a block with string data."""
        blockchain = Blockchain()
        blockchain.add_block("First transaction")

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(blockchain.chain[1].data, "First transaction")

    def test_add_block_with_dict_data(self):
        """Test adding a block with dictionary data."""
        blockchain = Blockchain()
        data = {"from": "Alice", "to": "Bob", "amount": 50}
        blockchain.add_block(data)

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(blockchain.chain[1].data, data)

    def test_add_block_with_list_data(self):
        """Test adding a block with list data."""
        blockchain = Blockchain()
        data = ["item1", "item2", "item3"]
        blockchain.add_block(data)

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(blockchain.chain[1].data, data)

    def test_add_multiple_blocks_sequentially(self):
        """Test adding multiple blocks and verify sequential indices."""
        blockchain = Blockchain()

        blockchain.add_block("First")
        blockchain.add_block("Second")
        blockchain.add_block("Third")

        # Verify chain length
        self.assertEqual(len(blockchain.chain), 4)  # genesis + 3

        # Verify sequential indices
        self.assertEqual(blockchain.chain[0].index, 0)
        self.assertEqual(blockchain.chain[1].index, 1)
        self.assertEqual(blockchain.chain[2].index, 2)
        self.assertEqual(blockchain.chain[3].index, 3)

    def test_hash_linking_between_blocks(self):
        """Test that blocks are properly linked via hashes."""
        blockchain = Blockchain()

        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")
        blockchain.add_block("Block 3")

        # Verify hash linking for each block
        self.assertEqual(blockchain.chain[1].previous_hash, blockchain.chain[0].hash)
        self.assertEqual(blockchain.chain[2].previous_hash, blockchain.chain[1].hash)
        self.assertEqual(blockchain.chain[3].previous_hash, blockchain.chain[2].hash)

    def test_get_latest_block_after_adding_blocks(self):
        """Test that get_latest_block() returns the most recent block."""
        blockchain = Blockchain()

        block1 = blockchain.add_block("First")
        self.assertIs(blockchain.get_latest_block(), block1)

        block2 = blockchain.add_block("Second")
        self.assertIs(blockchain.get_latest_block(), block2)

        block3 = blockchain.add_block("Third")
        self.assertIs(blockchain.get_latest_block(), block3)

    def test_add_block_returns_new_block(self):
        """Test that add_block() returns the newly created block."""
        blockchain = Blockchain()

        returned_block = blockchain.add_block("Test")

        # Verify returned block is the one added to chain
        self.assertIs(returned_block, blockchain.chain[-1])
        self.assertEqual(returned_block.data, "Test")

    def test_add_block_creates_valid_hash(self):
        """Test that added blocks have valid SHA-256 hashes."""
        blockchain = Blockchain()

        new_block = blockchain.add_block("Test data")

        # Verify hash format
        self.assertIsNotNone(new_block.hash)
        self.assertEqual(len(new_block.hash), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in new_block.hash))

    def test_add_block_with_different_data_types(self):
        """Test adding blocks with various data types."""
        blockchain = Blockchain()

        blockchain.add_block("String")
        blockchain.add_block({"key": "value"})
        blockchain.add_block(["list", "of", "items"])
        blockchain.add_block(42)

        self.assertEqual(len(blockchain.chain), 5)  # genesis + 4

    def test_usage_example_from_issue_4(self):
        """Test the usage example from issue #4."""
        # Create blockchain
        blockchain = Blockchain()

        # Add some blocks
        blockchain.add_block("First transaction")
        blockchain.add_block("Second transaction")
        blockchain.add_block({"from": "Alice", "to": "Bob", "amount": 50})

        # Verify chain
        self.assertEqual(len(blockchain.chain), 4)  # genesis + 3

        # Verify blocks
        self.assertEqual(blockchain.chain[1].data, "First transaction")
        self.assertEqual(blockchain.chain[2].data, "Second transaction")
        self.assertEqual(blockchain.chain[3].data, {"from": "Alice", "to": "Bob", "amount": 50})

        # Print chain (optional)
        print("\nBlockchain:")
        for block in blockchain.chain:
            print(f"Block {block.index}: {block.data}")
            print(f"  Hash: {block.hash}")
            print(f"  Previous: {block.previous_hash}")

    # Tests for is_chain_valid() method

    def test_valid_chain_returns_true(self):
        """Test that a valid blockchain returns True."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        self.assertTrue(blockchain.is_chain_valid())

    def test_valid_genesis_only_chain(self):
        """Test that a blockchain with only genesis block is valid."""
        blockchain = Blockchain()

        self.assertTrue(blockchain.is_chain_valid())

    def test_invalid_genesis_previous_hash(self):
        """Test that invalid genesis previous_hash is detected."""
        blockchain = Blockchain()

        # Tamper with genesis block's previous_hash
        blockchain.chain[0].previous_hash = "invalid"

        self.assertFalse(blockchain.is_chain_valid())

    def test_invalid_genesis_hash(self):
        """Test that invalid genesis hash is detected."""
        blockchain = Blockchain()

        # Tamper with genesis block's hash
        blockchain.chain[0].hash = "invalid_hash"

        self.assertFalse(blockchain.is_chain_valid())

    def test_tampered_block_data_detected(self):
        """Test that tampering with block data is detected."""
        blockchain = Blockchain()
        blockchain.add_block("Original data")
        blockchain.add_block("Block 2")

        # Tamper with block data
        blockchain.chain[1].data = "Tampered data"

        self.assertFalse(blockchain.is_chain_valid())

    def test_tampered_block_hash_detected(self):
        """Test that tampering with block hash is detected."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")

        # Tamper with block hash
        blockchain.chain[1].hash = "fake_hash_12345"

        self.assertFalse(blockchain.is_chain_valid())

    def test_broken_chain_link_detected(self):
        """Test that broken chain links are detected."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        # Break the chain by modifying previous_hash
        blockchain.chain[2].previous_hash = "wrong_hash"

        self.assertFalse(blockchain.is_chain_valid())

    def test_multiple_blocks_valid_chain(self):
        """Test validation with multiple blocks in chain."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")
        blockchain.add_block("Block 3")
        blockchain.add_block("Block 4")
        blockchain.add_block("Block 5")

        self.assertTrue(blockchain.is_chain_valid())

    def test_validation_after_tampering_middle_block(self):
        """Test that tampering with middle block is detected."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")
        blockchain.add_block("Block 3")

        # Tamper with middle block
        blockchain.chain[2].data = "Tampered"

        self.assertFalse(blockchain.is_chain_valid())

    def test_verbose_mode_genesis_only(self):
        """Test verbose mode with genesis-only blockchain."""
        blockchain = Blockchain()

        # Capture printed output (optional - just ensure it doesn't crash)
        result = blockchain.is_chain_valid(verbose=True)

        self.assertTrue(result)

    def test_verbose_mode_with_tampering(self):
        """Test verbose mode when tampering is detected."""
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.chain[1].data = "Tampered"

        # Should return False even in verbose mode
        result = blockchain.is_chain_valid(verbose=True)

        self.assertFalse(result)

    def test_usage_example_from_issue_5(self):
        """Test the usage examples from issue #5."""
        # Test 1: Valid chain
        blockchain = Blockchain()
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")
        self.assertTrue(blockchain.is_chain_valid())

        # Test 2: Tampered data
        blockchain.chain[1].data = "Tampered"
        self.assertFalse(blockchain.is_chain_valid())

        # Test 3: Invalid genesis
        blockchain2 = Blockchain()
        blockchain2.chain[0].previous_hash = "invalid"
        self.assertFalse(blockchain2.is_chain_valid())

        # Test 4: Broken chain
        blockchain3 = Blockchain()
        blockchain3.add_block("Block 1")
        blockchain3.chain[1].previous_hash = "wrong_hash"
        self.assertFalse(blockchain3.is_chain_valid())

    # Edge Case Tests

    def test_add_block_with_empty_string_data(self):
        """Test adding block with empty string data."""
        blockchain = Blockchain()
        blockchain.add_block("")

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(blockchain.chain[1].data, "")
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_large_data(self):
        """Test adding block with large data (10KB)."""
        blockchain = Blockchain()
        large_data = "x" * 10000

        blockchain.add_block(large_data)

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(len(blockchain.chain[1].data), 10000)
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_special_characters(self):
        """Test adding block with special characters."""
        blockchain = Blockchain()
        special_data = "Test!@#$%^&*()_+-=[]{}|;':\",./<>?\\`~"

        blockchain.add_block(special_data)

        self.assertEqual(blockchain.chain[1].data, special_data)
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_unicode_data(self):
        """Test adding block with unicode characters."""
        blockchain = Blockchain()
        unicode_data = "Hello 世界 🌍 Привет"

        blockchain.add_block(unicode_data)

        self.assertEqual(blockchain.chain[1].data, unicode_data)
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_numeric_data(self):
        """Test adding block with numeric data."""
        blockchain = Blockchain()
        blockchain.add_block(42)
        blockchain.add_block(3.14159)

        self.assertEqual(blockchain.chain[1].data, 42)
        self.assertEqual(blockchain.chain[2].data, 3.14159)
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_boolean_data(self):
        """Test adding block with boolean data."""
        blockchain = Blockchain()
        blockchain.add_block(True)
        blockchain.add_block(False)

        self.assertEqual(blockchain.chain[1].data, True)
        self.assertEqual(blockchain.chain[2].data, False)
        self.assertTrue(blockchain.is_chain_valid())

    def test_add_block_with_none_data(self):
        """Test adding block with None data."""
        blockchain = Blockchain()
        blockchain.add_block(None)

        self.assertEqual(blockchain.chain[1].data, None)
        self.assertTrue(blockchain.is_chain_valid())

    def test_multiple_edge_case_blocks(self):
        """Test adding multiple blocks with various edge case data."""
        blockchain = Blockchain()

        blockchain.add_block("")  # Empty
        blockchain.add_block("x" * 10000)  # Large
        blockchain.add_block("!@#$%^&*()")  # Special chars
        blockchain.add_block(12345)  # Numeric
        blockchain.add_block({"nested": {"data": "value"}})  # Nested dict
        blockchain.add_block([1, "two", {"three": 3}])  # Mixed list

        self.assertEqual(len(blockchain.chain), 7)  # Genesis + 6
        self.assertTrue(blockchain.is_chain_valid())


if __name__ == '__main__':
    unittest.main()
