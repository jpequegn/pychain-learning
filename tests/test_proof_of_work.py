import unittest
import time
from pychain.block import Block
from pychain.blockchain import Blockchain


class TestProofOfWork(unittest.TestCase):
    """Test cases for Proof of Work mining functionality."""

    def test_block_has_difficulty_attribute(self):
        """Test that blocks have difficulty attribute."""
        block = Block(0, time.time(), "test", "0", difficulty=3)

        self.assertEqual(block.difficulty, 3)

    def test_block_has_nonce_attribute(self):
        """Test that blocks have nonce attribute initialized to 0."""
        block = Block(0, time.time(), "test", "0")

        self.assertEqual(block.nonce, 0)

    def test_mining_produces_valid_hash(self):
        """Test that mined blocks meet difficulty requirement."""
        block = Block(1, time.time(), "test", "0", difficulty=3)
        block.mine_block()

        # Hash should start with 3 zeros
        self.assertTrue(block.hash.startswith("000"))

    def test_nonce_increments_during_mining(self):
        """Test that nonce is incremented during mining."""
        block = Block(1, time.time(), "test", "0", difficulty=2)
        initial_nonce = block.nonce

        block.mine_block()

        self.assertGreater(block.nonce, initial_nonce)

    def test_mining_returns_time(self):
        """Test that mine_block returns mining time."""
        block = Block(1, time.time(), "test", "0", difficulty=2)

        mining_time = block.mine_block()

        self.assertIsInstance(mining_time, float)
        self.assertGreater(mining_time, 0)

    def test_different_difficulties(self):
        """Test mining with different difficulty levels."""
        for difficulty in range(1, 4):
            block = Block(0, time.time(), "test", "0", difficulty)
            mining_time = block.mine_block()

            target = "0" * difficulty
            self.assertTrue(block.hash.startswith(target))
            self.assertIsInstance(mining_time, float)

    def test_blockchain_has_difficulty_attribute(self):
        """Test that blockchain has difficulty attribute."""
        blockchain = Blockchain(difficulty=3)

        self.assertEqual(blockchain.difficulty, 3)

    def test_genesis_block_is_mined(self):
        """Test that genesis block is properly mined."""
        blockchain = Blockchain(difficulty=2)
        genesis = blockchain.chain[0]

        # Genesis block should meet PoW requirements
        self.assertTrue(genesis.hash.startswith("00"))
        self.assertGreater(genesis.nonce, 0)

    def test_added_blocks_are_mined(self):
        """Test that blocks added to blockchain are mined."""
        blockchain = Blockchain(difficulty=2)
        blockchain.add_block("Block 1")

        block = blockchain.chain[1]

        # Block should meet PoW requirements
        self.assertTrue(block.hash.startswith("00"))
        self.assertGreater(block.nonce, 0)

    def test_chain_validation_checks_pow(self):
        """Test that chain validation checks PoW requirements."""
        blockchain = Blockchain(difficulty=3)
        blockchain.add_block("Block 1")

        # Valid chain should pass
        self.assertTrue(blockchain.is_chain_valid())

        # Manually set invalid hash (doesn't meet PoW)
        blockchain.chain[1].hash = "invalid_hash_without_zeros"

        # Should fail validation
        self.assertFalse(blockchain.is_chain_valid())

    def test_tampering_breaks_pow(self):
        """Test that tampering with data breaks PoW validation."""
        blockchain = Blockchain(difficulty=2)
        blockchain.add_block("Original data")

        # Initially valid
        self.assertTrue(blockchain.is_chain_valid())

        # Tamper with data
        blockchain.chain[1].data = "Tampered data"

        # Should fail because recalculated hash won't match
        self.assertFalse(blockchain.is_chain_valid())

    def test_multiple_blocks_all_mined(self):
        """Test that multiple blocks are all properly mined."""
        blockchain = Blockchain(difficulty=2)

        for i in range(3):
            blockchain.add_block(f"Block {i}")

        # All blocks should meet PoW
        for block in blockchain.chain:
            self.assertTrue(block.hash.startswith("00"))
            self.assertGreaterEqual(block.nonce, 0)

        # Chain should be valid
        self.assertTrue(blockchain.is_chain_valid())

    def test_different_blockchain_difficulties(self):
        """Test blockchains with different difficulty levels."""
        for difficulty in range(1, 4):
            blockchain = Blockchain(difficulty=difficulty)
            blockchain.add_block("Test block")

            # All blocks should meet their difficulty
            target = "0" * difficulty
            for block in blockchain.chain:
                self.assertTrue(block.hash.startswith(target))

            # Chain should be valid
            self.assertTrue(blockchain.is_chain_valid())

    def test_verbose_validation_with_pow(self):
        """Test verbose validation shows PoW information."""
        blockchain = Blockchain(difficulty=2)
        blockchain.add_block("Block 1")

        # Should pass validation with verbose output
        result = blockchain.is_chain_valid(verbose=True)

        self.assertTrue(result)

    def test_hash_includes_nonce(self):
        """Test that changing nonce changes the hash."""
        block = Block(0, time.time(), "test", "0", difficulty=2)
        hash1 = block.calculate_hash()

        block.nonce = 100
        hash2 = block.calculate_hash()

        self.assertNotEqual(hash1, hash2)

    def test_mining_difficulty_1(self):
        """Test mining with difficulty 1 (should be very fast)."""
        block = Block(0, time.time(), "test", "0", difficulty=1)
        mining_time = block.mine_block()

        self.assertTrue(block.hash.startswith("0"))
        self.assertLess(mining_time, 1.0)  # Should take less than 1 second

    def test_mining_difficulty_4(self):
        """Test mining with difficulty 4 (will take longer)."""
        block = Block(0, time.time(), "test", "0", difficulty=4)
        mining_time = block.mine_block()

        self.assertTrue(block.hash.startswith("0000"))
        self.assertIsInstance(mining_time, float)

    def test_chain_security_demonstration(self):
        """Test that tampering requires re-mining (security demo)."""
        blockchain = Blockchain(difficulty=3)
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        # Original chain is valid
        self.assertTrue(blockchain.is_chain_valid())

        # Tamper with block 1
        original_hash = blockchain.chain[1].hash
        blockchain.chain[1].data = "Tampered"

        # Chain is now invalid (hash doesn't match)
        self.assertFalse(blockchain.is_chain_valid())

        # To make valid again, attacker would need to re-mine
        # (we demonstrate this is required but don't actually do it due to time)
        recalculated_hash = blockchain.chain[1].calculate_hash()
        self.assertNotEqual(original_hash, recalculated_hash)
        self.assertFalse(recalculated_hash.startswith("000"))


if __name__ == '__main__':
    unittest.main()
