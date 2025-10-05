import unittest
from pychain.transaction import Transaction
from pychain.blockchain import Blockchain


class TestTransactionValidation(unittest.TestCase):
    """Test cases for transaction validation functionality."""

    def test_transaction_is_valid_returns_tuple(self):
        """Test that is_valid() returns a tuple."""
        tx = Transaction("Alice", "Bob", 50)
        result = tx.is_valid()

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_valid_transaction(self):
        """Test that a valid transaction passes validation."""
        tx = Transaction("Alice", "Bob", 50)
        is_valid, error = tx.is_valid()

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_negative_amount_invalid(self):
        """Test that negative amount makes transaction invalid."""
        tx = Transaction("Alice", "Bob", -50)
        is_valid, error = tx.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("positive", error.lower())

    def test_zero_amount_invalid(self):
        """Test that zero amount makes transaction invalid (except for System)."""
        # Regular user cannot send zero
        tx = Transaction("Alice", "Bob", 0)
        is_valid, error = tx.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("positive", error.lower())

        # But System can send zero (for genesis blocks)
        tx_system = Transaction("System", "Genesis", 0)
        is_valid, error = tx_system.is_valid()

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_same_sender_receiver_invalid(self):
        """Test that sender == receiver makes transaction invalid."""
        tx = Transaction("Alice", "Alice", 50)
        is_valid, error = tx.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("same", error.lower())

    def test_initial_balances_in_blockchain(self):
        """Test that blockchain supports initial balances."""
        initial_balances = {"Alice": 100, "Bob": 50}
        blockchain = Blockchain(difficulty=2, initial_balances=initial_balances)

        self.assertEqual(blockchain.get_balance("Alice"), 100)
        self.assertEqual(blockchain.get_balance("Bob"), 50)
        self.assertEqual(blockchain.get_balance("Charlie"), 0)

    def test_create_transaction_with_insufficient_balance(self):
        """Test that creating transaction with insufficient balance raises error."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 50})

        with self.assertRaises(ValueError) as context:
            blockchain.create_transaction("Alice", "Bob", 100)

        self.assertIn("Insufficient balance", str(context.exception))
        self.assertIn("Alice", str(context.exception))
        self.assertIn("50", str(context.exception))
        self.assertIn("100", str(context.exception))

    def test_create_transaction_with_sufficient_balance(self):
        """Test that creating transaction with sufficient balance succeeds."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        tx = blockchain.create_transaction("Alice", "Bob", 50)

        self.assertEqual(tx.sender, "Alice")
        self.assertEqual(tx.receiver, "Bob")
        self.assertEqual(tx.amount, 50)

    def test_create_transaction_invalid_structure(self):
        """Test that creating invalid transaction raises error."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        # Zero amount
        with self.assertRaises(ValueError) as context:
            blockchain.create_transaction("Alice", "Bob", 0)
        self.assertIn("Invalid transaction", str(context.exception))

        # Same sender and receiver
        with self.assertRaises(ValueError) as context:
            blockchain.create_transaction("Alice", "Alice", 50)
        self.assertIn("Invalid transaction", str(context.exception))

    def test_pending_transactions_reduce_balance(self):
        """Test that pending transactions are included in balance calculation."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 30)
        blockchain.create_transaction("Alice", "Charlie", 20)

        # Balance with pending should be 100 - 30 - 20 = 50
        self.assertEqual(blockchain.get_balance("Alice", include_pending=True), 50)

        # Balance without pending should still be 100
        self.assertEqual(blockchain.get_balance("Alice", include_pending=False), 100)

    def test_cannot_overspend_with_pending(self):
        """Test that pending transactions prevent overspending."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 60)

        # Alice has 100 - 60 = 40 available
        # Should not be able to send 50
        with self.assertRaises(ValueError) as context:
            blockchain.create_transaction("Alice", "Charlie", 50)

        self.assertIn("Insufficient balance", str(context.exception))

    def test_system_can_send_without_balance(self):
        """Test that System can create transactions without balance check."""
        blockchain = Blockchain(difficulty=2)

        # System should be able to send even with no balance
        tx = blockchain.create_transaction("System", "Alice", 100)

        self.assertEqual(tx.sender, "System")
        self.assertEqual(tx.amount, 100)

    def test_validate_block_transactions_valid_block(self):
        """Test that validate_block_transactions passes for valid block."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        block = blockchain.mine_pending_transactions("Miner1")

        is_valid, error = blockchain.validate_block_transactions(block)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_block_transactions_legacy_block(self):
        """Test that validate_block_transactions handles legacy data blocks."""
        blockchain = Blockchain(difficulty=2)
        block = blockchain.add_block("Legacy data")

        is_valid, error = blockchain.validate_block_transactions(block)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_block_transactions_insufficient_balance(self):
        """Test that validate_block_transactions detects insufficient balance."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 50})

        blockchain.create_transaction("Alice", "Bob", 30)
        block = blockchain.mine_pending_transactions("Miner1")

        # Manually create invalid transaction and add to block
        block.transactions.insert(0, Transaction("Alice", "Charlie", 100))

        is_valid, error = blockchain.validate_block_transactions(block)

        self.assertFalse(is_valid)
        self.assertIn("Insufficient balance", error)

    def test_validate_block_transactions_invalid_structure(self):
        """Test that validate_block_transactions detects invalid transaction structure."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        block = blockchain.mine_pending_transactions("Miner1")

        # Manually create invalid transaction (zero amount)
        invalid_tx = Transaction.__new__(Transaction)
        invalid_tx.sender = "Alice"
        invalid_tx.receiver = "Bob"
        invalid_tx.amount = 0
        invalid_tx.timestamp = 123456
        invalid_tx.transaction_id = "fake_hash"

        block.transactions.insert(0, invalid_tx)

        is_valid, error = blockchain.validate_block_transactions(block)

        self.assertFalse(is_valid)
        self.assertIn("Invalid transaction structure", error)

    def test_is_chain_valid_with_transaction_validation(self):
        """Test that is_chain_valid validates transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        self.assertTrue(blockchain.is_chain_valid())

    def test_is_chain_valid_detects_tampered_transaction(self):
        """Test that is_chain_valid detects tampered transaction amounts."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Tamper with transaction amount
        blockchain.chain[1].transactions[0].amount = 1000

        # Should fail validation
        self.assertFalse(blockchain.is_chain_valid())

    def test_balance_after_mining(self):
        """Test that balances update correctly after mining."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("Alice"), 50)
        self.assertEqual(blockchain.get_balance("Bob"), 50)
        self.assertEqual(blockchain.get_balance("Miner1"), 10)  # Mining reward

    def test_multiple_transactions_in_block(self):
        """Test validation with multiple transactions in one block."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 30)
        blockchain.create_transaction("Bob", "Charlie", 20)
        blockchain.create_transaction("Alice", "Charlie", 10)

        block = blockchain.mine_pending_transactions("Miner1")

        is_valid, error = blockchain.validate_block_transactions(block)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_chain_validation_with_multiple_blocks(self):
        """Test full chain validation with multiple transaction blocks."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 30)
        blockchain.mine_pending_transactions("Miner1")

        blockchain.create_transaction("Bob", "Charlie", 20)
        blockchain.mine_pending_transactions("Miner2")

        self.assertTrue(blockchain.is_chain_valid())

    def test_get_balance_with_initial_balances_and_transactions(self):
        """Test that get_balance correctly combines initial balances and transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 30)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("Alice"), 70)  # 100 - 30
        self.assertEqual(blockchain.get_balance("Bob"), 80)  # 50 + 30


if __name__ == '__main__':
    unittest.main()
