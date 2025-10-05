import unittest
import sys
from io import StringIO
from pychain.blockchain import Blockchain


class TestPrettyPrint(unittest.TestCase):
    """Test cases for blockchain pretty-print functionality."""

    def setUp(self):
        """Set up test blockchain and output capture."""
        self.blockchain = Blockchain(
            difficulty=2,
            initial_balances={"Alice": 100, "Bob": 50}
        )
        self.held_output = StringIO()
        self.original_stdout = sys.stdout

    def tearDown(self):
        """Restore stdout."""
        sys.stdout = self.original_stdout

    def capture_output(self):
        """Start capturing stdout."""
        sys.stdout = self.held_output

    def get_output(self):
        """Get captured output and reset."""
        sys.stdout = self.original_stdout
        output = self.held_output.getvalue()
        self.held_output = StringIO()
        return output

    def test_print_summary_basic(self):
        """Test basic summary output."""
        self.capture_output()
        self.blockchain.print_summary()
        output = self.get_output()

        # Check for key information
        self.assertIn("BLOCKCHAIN SUMMARY", output)
        self.assertIn("Total Blocks: 1", output)
        self.assertIn("Current Difficulty: 2", output)
        self.assertIn("Mining Reward: 10", output)
        self.assertIn("Pending Transactions: 0", output)

    def test_print_summary_with_initial_balances(self):
        """Test summary shows initial balances."""
        self.capture_output()
        self.blockchain.print_summary()
        output = self.get_output()

        self.assertIn("Initial Balances:", output)
        self.assertIn("Alice: 100", output)
        self.assertIn("Bob: 50", output)

    def test_print_summary_with_transactions(self):
        """Test summary with transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_summary()
        output = self.get_output()

        self.assertIn("Total Blocks: 2", output)
        self.assertIn("Pending Transactions: 0", output)

    def test_print_summary_validation_status(self):
        """Test summary shows validation status."""
        self.capture_output()
        self.blockchain.print_summary()
        output = self.get_output()

        self.assertIn("Chain Validation:", output)
        self.assertIn("[VALID]", output)

    def test_print_summary_mining_stats(self):
        """Test summary shows mining stats when available."""
        # Need at least 2 blocks for stats
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_summary()
        output = self.get_output()

        self.assertIn("Mining Performance:", output)
        self.assertIn("Average Block Time:", output)
        self.assertIn("Average Difficulty:", output)
        self.assertIn("Status:", output)

    def test_print_transaction_details_valid_block(self):
        """Test printing transaction details for valid block."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        result = self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertTrue(result)
        self.assertIn("BLOCK #1 TRANSACTION DETAILS", output)
        self.assertIn("Block Information:", output)
        self.assertIn("Hash:", output)
        self.assertIn("Previous Hash:", output)
        self.assertIn("Nonce:", output)
        self.assertIn("Difficulty:", output)

    def test_print_transaction_details_shows_transactions(self):
        """Test that transaction details show individual transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("Transactions (2):", output)  # Original + reward
        self.assertIn("Transaction 1:", output)
        self.assertIn("From: Alice", output)
        self.assertIn("To: Bob", output)
        self.assertIn("Amount: 30", output)
        self.assertIn("Transaction 2:", output)  # Reward
        self.assertIn("From: System", output)

    def test_print_transaction_details_shows_ids(self):
        """Test that transaction IDs are displayed."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("ID:", output)

    def test_print_transaction_details_shows_timestamps(self):
        """Test that timestamps are displayed."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("Timestamp:", output)

    def test_print_transaction_details_shows_status(self):
        """Test that transaction validation status is shown."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("Status: [VALID]", output)

    def test_print_transaction_details_shows_total(self):
        """Test that total transaction volume is shown."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("Total Transaction Volume: 40", output)  # 30 + 10 reward

    def test_print_transaction_details_invalid_block_index(self):
        """Test printing details for non-existent block."""
        self.capture_output()
        result = self.blockchain.print_transaction_details(999)
        output = self.get_output()

        self.assertFalse(result)
        self.assertIn("Error: Block 999 does not exist", output)

    def test_print_transaction_details_negative_index(self):
        """Test printing details with negative index."""
        self.capture_output()
        result = self.blockchain.print_transaction_details(-1)
        output = self.get_output()

        self.assertFalse(result)
        self.assertIn("Error:", output)

    def test_print_transaction_details_genesis_block(self):
        """Test printing details for genesis block."""
        self.capture_output()
        result = self.blockchain.print_transaction_details(0)
        output = self.get_output()

        self.assertTrue(result)
        self.assertIn("BLOCK #0 TRANSACTION DETAILS", output)
        self.assertIn("From: System", output)
        self.assertIn("To: Genesis", output)

    def test_print_transaction_details_legacy_data_block(self):
        """Test printing details for legacy data block."""
        self.blockchain.add_block("Some legacy data")

        self.capture_output()
        result = self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertTrue(result)
        self.assertIn("Legacy Data Block:", output)
        self.assertIn("Data: Some legacy data", output)

    def test_print_transaction_details_multiple_transactions(self):
        """Test printing block with multiple transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.create_transaction("Bob", "Charlie", 15)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_transaction_details(1)
        output = self.get_output()

        self.assertIn("Transactions (3):", output)  # 2 original + reward
        self.assertIn("Transaction 1:", output)
        self.assertIn("Transaction 2:", output)
        self.assertIn("Transaction 3:", output)

    def test_print_blockchain_still_works(self):
        """Test that existing print_blockchain method still works."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_blockchain()
        output = self.get_output()

        self.assertIn("BLOCKCHAIN", output)
        self.assertIn("Block #0", output)
        self.assertIn("Block #1", output)

    def test_print_balances_still_works(self):
        """Test that existing print_balances method still works."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.capture_output()
        self.blockchain.print_balances(["Alice", "Bob", "Miner1"])
        output = self.get_output()

        self.assertIn("ACCOUNT BALANCES", output)
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)
        self.assertIn("Miner1", output)

    def test_print_summary_no_stats_for_genesis_only(self):
        """Test summary doesn't show stats with only genesis block."""
        blockchain = Blockchain(difficulty=2)

        self.capture_output()
        blockchain.print_summary()
        output = self.get_output()

        # Should not have mining stats section
        self.assertNotIn("Mining Performance:", output)


if __name__ == '__main__':
    unittest.main()
