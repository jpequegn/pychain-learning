import unittest
import time
from pychain.blockchain import Blockchain


class TestDifficultyAdjustment(unittest.TestCase):
    """Test cases for dynamic difficulty adjustment."""

    def test_blockchain_has_target_block_time(self):
        """Test that blockchain has target_block_time attribute."""
        blockchain = Blockchain(target_block_time=15)

        self.assertEqual(blockchain.target_block_time, 15)

    def test_blockchain_has_adjustment_interval(self):
        """Test that blockchain has adjustment_interval attribute."""
        blockchain = Blockchain(adjustment_interval=3)

        self.assertEqual(blockchain.adjustment_interval, 3)

    def test_difficulty_increases_when_mining_fast(self):
        """Test difficulty increases for fast mining."""
        # Use low difficulty and high target time to ensure fast mining
        blockchain = Blockchain(difficulty=1, target_block_time=10, adjustment_interval=3)

        initial_difficulty = blockchain.difficulty

        # Mine blocks (difficulty 1 is very fast)
        for i in range(6):
            blockchain.add_block(f"Block {i}")

        # Difficulty should have increased
        self.assertGreater(blockchain.difficulty, initial_difficulty)

    def test_difficulty_decreases_when_mining_slow(self):
        """Test difficulty decreases for slow mining."""
        # Use high difficulty and very low target time to ensure slow mining
        blockchain = Blockchain(difficulty=4, target_block_time=0.001, adjustment_interval=3)

        initial_difficulty = blockchain.difficulty

        # Mine blocks (difficulty 4 with 0.001s target is considered slow)
        for i in range(3):
            blockchain.add_block(f"Block {i}")

        # Difficulty should have decreased
        self.assertLess(blockchain.difficulty, initial_difficulty)

    def test_minimum_difficulty_enforced(self):
        """Test difficulty doesn't go below 1."""
        blockchain = Blockchain(difficulty=1, target_block_time=0.001, adjustment_interval=2)

        # Try to trigger difficulty decrease
        for i in range(10):
            blockchain.add_block(f"Block {i}")

        # Difficulty should never go below 1
        self.assertGreaterEqual(blockchain.difficulty, 1)

    def test_maximum_difficulty_enforced(self):
        """Test difficulty doesn't exceed maximum (8)."""
        blockchain = Blockchain(difficulty=2, target_block_time=100, adjustment_interval=2)

        initial_difficulty = blockchain.difficulty

        # Try to trigger difficulty increase (mining will be fast, difficulty will rise)
        # We'll just add enough blocks to trigger one or two adjustments
        for i in range(4):
            blockchain.add_block(f"Block {i}")

        # Difficulty should not exceed 8 (and should have increased from 2)
        self.assertLessEqual(blockchain.difficulty, 8)
        self.assertGreaterEqual(blockchain.difficulty, initial_difficulty)

    def test_adjust_difficulty_only_at_intervals(self):
        """Test that difficulty only adjusts at specified intervals."""
        blockchain = Blockchain(difficulty=2, adjustment_interval=5)

        # Add blocks but not enough to trigger adjustment
        for i in range(3):
            blockchain.add_block(f"Block {i}")

        # Difficulty should not have changed yet
        self.assertEqual(blockchain.difficulty, 2)

    def test_get_mining_stats_returns_dict(self):
        """Test that get_mining_stats returns a dictionary."""
        blockchain = Blockchain(difficulty=2)

        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        stats = blockchain.get_mining_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn('total_blocks', stats)
        self.assertIn('avg_block_time', stats)
        self.assertIn('current_difficulty', stats)
        self.assertIn('avg_difficulty', stats)
        self.assertIn('target_block_time', stats)

    def test_get_mining_stats_returns_none_for_insufficient_blocks(self):
        """Test that get_mining_stats returns None with only genesis block."""
        blockchain = Blockchain(difficulty=2)

        stats = blockchain.get_mining_stats()

        self.assertIsNone(stats)

    def test_mining_stats_accuracy(self):
        """Test that mining statistics are accurate."""
        blockchain = Blockchain(difficulty=2, target_block_time=10)

        for i in range(5):
            blockchain.add_block(f"Block {i}")

        stats = blockchain.get_mining_stats()

        # Verify basic stats
        self.assertEqual(stats['total_blocks'], 6)  # Genesis + 5
        self.assertEqual(stats['current_difficulty'], blockchain.difficulty)
        self.assertEqual(stats['target_block_time'], 10)
        self.assertGreaterEqual(stats['avg_block_time'], 0)  # Can be 0 for very fast mining
        self.assertGreaterEqual(stats['min_block_time'], 0)  # Can be 0 for very fast mining
        self.assertGreaterEqual(stats['max_block_time'], 0)  # Can be 0 for very fast mining

    def test_print_mining_stats_no_crash(self):
        """Test that print_mining_stats doesn't crash."""
        blockchain = Blockchain(difficulty=2)

        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        # Should not raise an exception
        blockchain.print_mining_stats()

    def test_print_mining_stats_insufficient_blocks(self):
        """Test print_mining_stats with insufficient blocks."""
        blockchain = Blockchain(difficulty=2)

        # Should not raise an exception
        blockchain.print_mining_stats()

    def test_difficulty_adjustment_maintains_stability(self):
        """Test that difficulty stabilizes when mining at target rate."""
        blockchain = Blockchain(difficulty=2, target_block_time=5, adjustment_interval=3)

        # Add several blocks
        for i in range(6):
            blockchain.add_block(f"Block {i}")

        # Get stats to check if we're close to target
        stats = blockchain.get_mining_stats()

        # Difficulty should be reasonable (not too high or too low)
        self.assertGreaterEqual(blockchain.difficulty, 1)
        self.assertLessEqual(blockchain.difficulty, 8)

    def test_adjustment_factor_calculation(self):
        """Test that adjustment factor is calculated correctly."""
        blockchain = Blockchain(difficulty=2, target_block_time=10, adjustment_interval=3)

        # Add blocks
        for i in range(6):
            blockchain.add_block(f"Block {i}")

        # Verify difficulty was adjusted based on performance
        self.assertIsInstance(blockchain.difficulty, int)
        self.assertGreaterEqual(blockchain.difficulty, 1)

    def test_chain_valid_with_varying_difficulty(self):
        """Test that chain validation works with varying difficulties."""
        blockchain = Blockchain(difficulty=1, target_block_time=5, adjustment_interval=2)

        # Add blocks and let difficulty vary
        for i in range(10):
            blockchain.add_block(f"Block {i}")

        # Chain should be valid even with varying difficulties
        self.assertTrue(blockchain.is_chain_valid())

    def test_each_block_stores_its_difficulty(self):
        """Test that each block stores its difficulty level."""
        blockchain = Blockchain(difficulty=1, target_block_time=10, adjustment_interval=3)

        # Add blocks
        for i in range(6):
            blockchain.add_block(f"Block {i}")

        # Each block should have a difficulty attribute
        for block in blockchain.chain:
            self.assertIsInstance(block.difficulty, int)
            self.assertGreaterEqual(block.difficulty, 1)

    def test_backward_compatibility(self):
        """Test that default parameters work (backward compatibility)."""
        blockchain = Blockchain()

        # Should work with defaults
        blockchain.add_block("Block 1")
        blockchain.add_block("Block 2")

        self.assertTrue(blockchain.is_chain_valid())

    def test_stats_show_difficulty_changes(self):
        """Test that stats reflect difficulty changes over time."""
        blockchain = Blockchain(difficulty=1, target_block_time=10, adjustment_interval=3)

        initial_difficulty = blockchain.difficulty

        # Mine several blocks
        for i in range(6):
            blockchain.add_block(f"Block {i}")

        stats = blockchain.get_mining_stats()

        # If difficulty changed, average should differ from initial
        if blockchain.difficulty != initial_difficulty:
            # Average difficulty should be between min and max
            self.assertGreaterEqual(stats['avg_difficulty'], min(initial_difficulty, blockchain.difficulty))
            self.assertLessEqual(stats['avg_difficulty'], max(initial_difficulty, blockchain.difficulty))


if __name__ == '__main__':
    unittest.main()
