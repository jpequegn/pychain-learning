import unittest
import time
from pychain.transaction import Transaction
from pychain.exceptions import ValidationError, InvalidTransactionError


class TestTransaction(unittest.TestCase):
    """Test cases for the Transaction class."""

    def test_transaction_creation(self):
        """Test that a transaction is created correctly."""
        tx = Transaction("Alice", "Bob", 50)

        self.assertEqual(tx.sender, "Alice")
        self.assertEqual(tx.receiver, "Bob")
        self.assertEqual(tx.amount, 50)
        self.assertIsNotNone(tx.transaction_id)
        self.assertIsNotNone(tx.timestamp)

    def test_transaction_with_custom_timestamp(self):
        """Test creating transaction with custom timestamp."""
        custom_time = 1234567890.0
        tx = Transaction("Alice", "Bob", 50, timestamp=custom_time)

        self.assertEqual(tx.timestamp, custom_time)

    def test_transaction_hash_determinism(self):
        """Test that transaction hashes are deterministic."""
        timestamp = 1234567890.0
        tx1 = Transaction("Alice", "Bob", 50, timestamp=timestamp)
        tx2 = Transaction("Alice", "Bob", 50, timestamp=timestamp)

        self.assertEqual(tx1.transaction_id, tx2.transaction_id)

    def test_transaction_hash_uniqueness_different_amount(self):
        """Test that different amounts produce different transaction IDs."""
        tx1 = Transaction("Alice", "Bob", 50)
        tx2 = Transaction("Alice", "Bob", 100)

        self.assertNotEqual(tx1.transaction_id, tx2.transaction_id)

    def test_transaction_hash_uniqueness_different_sender(self):
        """Test that different senders produce different transaction IDs."""
        tx1 = Transaction("Alice", "Bob", 50)
        tx2 = Transaction("Charlie", "Bob", 50)

        self.assertNotEqual(tx1.transaction_id, tx2.transaction_id)

    def test_transaction_hash_uniqueness_different_receiver(self):
        """Test that different receivers produce different transaction IDs."""
        tx1 = Transaction("Alice", "Bob", 50)
        tx2 = Transaction("Alice", "Charlie", 50)

        self.assertNotEqual(tx1.transaction_id, tx2.transaction_id)

    def test_transaction_hash_uniqueness_different_timestamp(self):
        """Test that different timestamps produce different transaction IDs."""
        tx1 = Transaction("Alice", "Bob", 50, timestamp=1000.0)
        tx2 = Transaction("Alice", "Bob", 50, timestamp=2000.0)

        self.assertNotEqual(tx1.transaction_id, tx2.transaction_id)

    def test_transaction_hash_length(self):
        """Test that transaction ID is 64 characters (SHA-256)."""
        tx = Transaction("Alice", "Bob", 50)

        self.assertEqual(len(tx.transaction_id), 64)

    def test_transaction_hash_format(self):
        """Test that transaction ID is hexadecimal."""
        tx = Transaction("Alice", "Bob", 50)

        # Should only contain hex characters
        self.assertTrue(all(c in '0123456789abcdef' for c in tx.transaction_id))

    def test_transaction_to_dict(self):
        """Test converting transaction to dictionary."""
        tx = Transaction("Alice", "Bob", 50, timestamp=1234567890.0)
        tx_dict = tx.to_dict()

        self.assertIsInstance(tx_dict, dict)
        self.assertEqual(tx_dict['sender'], "Alice")
        self.assertEqual(tx_dict['receiver'], "Bob")
        self.assertEqual(tx_dict['amount'], 50)
        self.assertEqual(tx_dict['timestamp'], 1234567890.0)
        self.assertEqual(tx_dict['transaction_id'], tx.transaction_id)

    def test_transaction_str(self):
        """Test string representation of transaction."""
        tx = Transaction("Alice", "Bob", 50)
        tx_str = str(tx)

        self.assertIn("Alice", tx_str)
        self.assertIn("Bob", tx_str)
        self.assertIn("50", tx_str)
        self.assertIn("->", tx_str)  # ASCII arrow for Windows compatibility

    def test_transaction_repr(self):
        """Test debug representation of transaction."""
        tx = Transaction("Alice", "Bob", 50)
        tx_repr = repr(tx)

        self.assertIn("Transaction", tx_repr)
        self.assertIn("Alice", tx_repr)
        self.assertIn("Bob", tx_repr)
        self.assertIn("50", tx_repr)

    def test_transaction_with_float_amount(self):
        """Test transaction with floating point amount."""
        tx = Transaction("Alice", "Bob", 50.5)

        self.assertEqual(tx.amount, 50.5)

    def test_transaction_with_zero_amount(self):
        """Test transaction with zero amount."""
        tx = Transaction("System", "Genesis", 0)

        self.assertEqual(tx.amount, 0)
        self.assertIsNotNone(tx.transaction_id)

    def test_transaction_with_negative_amount(self):
        """Test transaction with negative amount raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Transaction("Alice", "Bob", -50)

        self.assertIn("Amount must be positive", str(context.exception))

    def test_transaction_with_large_amount(self):
        """Test transaction with very large amount."""
        large_amount = 1000000000.0
        tx = Transaction("Alice", "Bob", large_amount)

        self.assertEqual(tx.amount, large_amount)
        self.assertIsNotNone(tx.transaction_id)

    def test_transaction_with_unicode_addresses(self):
        """Test transaction with unicode characters in addresses."""
        tx = Transaction("Алиса", "Bob", 50)

        self.assertEqual(tx.sender, "Алиса")
        self.assertIsNotNone(tx.transaction_id)

    def test_transaction_with_special_characters(self):
        """Test transaction with special characters in addresses."""
        tx = Transaction("Alice@example.com", "Bob#123", 50)

        self.assertEqual(tx.sender, "Alice@example.com")
        self.assertEqual(tx.receiver, "Bob#123")
        self.assertIsNotNone(tx.transaction_id)

    def test_calculate_hash_consistency(self):
        """Test that calculate_hash produces consistent results."""
        tx = Transaction("Alice", "Bob", 50, timestamp=1234567890.0)
        hash1 = tx.calculate_hash()
        hash2 = tx.calculate_hash()

        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, tx.transaction_id)


if __name__ == '__main__':
    unittest.main()
