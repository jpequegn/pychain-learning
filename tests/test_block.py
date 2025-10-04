import unittest
import time
from pychain.block import Block


class TestBlock(unittest.TestCase):
    """Test cases for the Block class."""

    def test_block_creation_with_string_data(self):
        """Test creating a block with string data."""
        timestamp = time.time()
        block = Block(0, timestamp, "Genesis Block", "0")

        self.assertEqual(block.index, 0)
        self.assertEqual(block.timestamp, timestamp)
        self.assertEqual(block.data, "Genesis Block")
        self.assertEqual(block.previous_hash, "0")
        self.assertIsNotNone(block.hash)
        self.assertIsInstance(block.hash, str)
        self.assertEqual(len(block.hash), 64)  # SHA-256 produces 64 hex characters

    def test_block_creation_with_dict_data(self):
        """Test creating a block with dictionary data."""
        timestamp = time.time()
        data = {"amount": 100, "sender": "Alice", "receiver": "Bob"}
        block = Block(1, timestamp, data, "previous_hash_123")

        self.assertEqual(block.index, 1)
        self.assertEqual(block.timestamp, timestamp)
        self.assertEqual(block.data, data)
        self.assertEqual(block.previous_hash, "previous_hash_123")
        self.assertIsNotNone(block.hash)

    def test_block_creation_with_list_data(self):
        """Test creating a block with list data."""
        timestamp = time.time()
        data = ["transaction1", "transaction2", "transaction3"]
        block = Block(2, timestamp, data, "previous_hash_456")

        self.assertEqual(block.index, 2)
        self.assertEqual(block.data, data)
        self.assertIsNotNone(block.hash)

    def test_hash_is_deterministic(self):
        """Test that hash is deterministic - same inputs produce same hash."""
        timestamp = 1234567890.123
        block1 = Block(0, timestamp, "Test Data", "0")
        block2 = Block(0, timestamp, "Test Data", "0")

        self.assertEqual(block1.hash, block2.hash)

    def test_different_index_produces_different_hash(self):
        """Test that changing index produces different hash."""
        timestamp = time.time()
        block1 = Block(0, timestamp, "Same Data", "0")
        block2 = Block(1, timestamp, "Same Data", "0")

        self.assertNotEqual(block1.hash, block2.hash)

    def test_different_timestamp_produces_different_hash(self):
        """Test that changing timestamp produces different hash."""
        block1 = Block(0, 1234567890.0, "Same Data", "0")
        block2 = Block(0, 1234567891.0, "Same Data", "0")

        self.assertNotEqual(block1.hash, block2.hash)

    def test_different_data_produces_different_hash(self):
        """Test that changing data produces different hash."""
        timestamp = time.time()
        block1 = Block(0, timestamp, "Data A", "0")
        block2 = Block(0, timestamp, "Data B", "0")

        self.assertNotEqual(block1.hash, block2.hash)

    def test_different_previous_hash_produces_different_hash(self):
        """Test that changing previous_hash produces different hash."""
        timestamp = time.time()
        block1 = Block(0, timestamp, "Same Data", "hash_A")
        block2 = Block(0, timestamp, "Same Data", "hash_B")

        self.assertNotEqual(block1.hash, block2.hash)

    def test_dict_data_ordering_consistency(self):
        """Test that dictionary key ordering doesn't affect hash."""
        timestamp = time.time()
        # These should produce the same hash because dict ordering is normalized
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}

        block1 = Block(0, timestamp, data1, "0")
        block2 = Block(0, timestamp, data2, "0")

        self.assertEqual(block1.hash, block2.hash)

    def test_genesis_block_example(self):
        """Test creating a genesis block as shown in the issue example."""
        block = Block(0, time.time(), "Genesis Block", "0")

        self.assertEqual(block.index, 0)
        self.assertEqual(block.data, "Genesis Block")
        self.assertEqual(block.previous_hash, "0")
        self.assertIsNotNone(block.hash)
        print(f"Genesis block hash: {block.hash}")

    def test_hash_format(self):
        """Test that hash is in correct hexadecimal format."""
        block = Block(0, time.time(), "Test", "0")

        # Hash should be 64 characters long (SHA-256)
        self.assertEqual(len(block.hash), 64)

        # Hash should only contain hexadecimal characters
        self.assertTrue(all(c in '0123456789abcdef' for c in block.hash))

    def test_calculate_hash_can_be_called_independently(self):
        """Test that calculate_hash() can be called independently."""
        block = Block(0, time.time(), "Test", "0")
        original_hash = block.hash

        # Call calculate_hash again
        recalculated_hash = block.calculate_hash()

        # Should produce the same hash
        self.assertEqual(original_hash, recalculated_hash)


if __name__ == '__main__':
    unittest.main()
