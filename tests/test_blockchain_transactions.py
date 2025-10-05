import unittest
from pychain.blockchain import Blockchain
from pychain.transaction import Transaction


class TestBlockchainWithTransactions(unittest.TestCase):
    """Test cases for Blockchain with transaction support."""

    def test_create_transaction(self):
        """Test creating a transaction."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        tx = blockchain.create_transaction("Alice", "Bob", 50)

        self.assertIsInstance(tx, Transaction)
        self.assertEqual(tx.sender, "Alice")
        self.assertEqual(tx.receiver, "Bob")
        self.assertEqual(tx.amount, 50)
        self.assertEqual(len(blockchain.pending_transactions), 1)

    def test_multiple_pending_transactions(self):
        """Test adding multiple pending transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.create_transaction("Bob", "Charlie", 25)
        blockchain.create_transaction("Alice", "Charlie", 15)

        self.assertEqual(len(blockchain.pending_transactions), 3)

    def test_mine_pending_transactions(self):
        """Test mining pending transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.create_transaction("Bob", "Charlie", 25)

        self.assertEqual(len(blockchain.pending_transactions), 2)

        block = blockchain.mine_pending_transactions("Miner1")

        self.assertIsNotNone(block)
        self.assertEqual(len(blockchain.pending_transactions), 0)
        self.assertEqual(len(blockchain.chain), 2)  # Genesis + 1 mined block

    def test_mined_block_contains_reward(self):
        """Test that mined block contains mining reward transaction."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        block = blockchain.mine_pending_transactions("Miner1")

        # Should have original transaction + reward transaction
        self.assertEqual(len(block.transactions), 2)

        # Last transaction should be the reward
        reward_tx = block.transactions[-1]
        self.assertEqual(reward_tx.sender, "System")
        self.assertEqual(reward_tx.receiver, "Miner1")
        self.assertEqual(reward_tx.amount, blockchain.mining_reward)

    def test_mine_with_no_pending_transactions(self):
        """Test mining when there are no pending transactions."""
        blockchain = Blockchain(difficulty=2)

        result = blockchain.mine_pending_transactions("Miner1")

        self.assertIsNone(result)
        self.assertEqual(len(blockchain.chain), 1)  # Only genesis block

    def test_balance_calculation_simple(self):
        """Test simple balance calculation."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        # Alice sends 50 to Bob
        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("Alice"), 50)  # 100 - 50
        self.assertEqual(blockchain.get_balance("Bob"), 50)
        self.assertEqual(blockchain.get_balance("Miner1"), 10)  # Mining reward

    def test_balance_calculation_multiple_transactions(self):
        """Test balance calculation with multiple transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 100})

        # Alice sends 50 to Bob
        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Bob sends 25 to Charlie
        blockchain.create_transaction("Bob", "Charlie", 25)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("Alice"), 50)  # 100 - 50
        self.assertEqual(blockchain.get_balance("Bob"), 125)  # 100 + 50 - 25
        self.assertEqual(blockchain.get_balance("Charlie"), 25)
        self.assertEqual(blockchain.get_balance("Miner1"), 20)  # 2 blocks * 10 reward

    def test_balance_calculation_multiple_miners(self):
        """Test balance calculation with different miners."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        blockchain.create_transaction("Bob", "Charlie", 25)
        blockchain.mine_pending_transactions("Miner2")

        self.assertEqual(blockchain.get_balance("Miner1"), 10)
        self.assertEqual(blockchain.get_balance("Miner2"), 10)

    def test_transaction_history_basic(self):
        """Test basic transaction history retrieval."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        alice_history = blockchain.get_transaction_history("Alice")

        self.assertGreater(len(alice_history), 0)
        self.assertTrue(any(tx['transaction'].sender == "Alice" for tx in alice_history))

    def test_transaction_history_multiple_transactions(self):
        """Test transaction history with multiple transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.create_transaction("Alice", "Charlie", 30)
        blockchain.mine_pending_transactions("Miner1")

        blockchain.create_transaction("Bob", "Alice", 20)
        blockchain.mine_pending_transactions("Miner1")

        alice_history = blockchain.get_transaction_history("Alice")

        # Alice should have 3 transactions (2 sent, 1 received)
        alice_txs = [tx for tx in alice_history if
                     tx['transaction'].sender == "Alice" or tx['transaction'].receiver == "Alice"]
        self.assertEqual(len(alice_txs), 3)

    def test_transaction_history_includes_block_info(self):
        """Test that transaction history includes block information."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        history = blockchain.get_transaction_history("Alice")

        self.assertGreater(len(history), 0)
        for item in history:
            self.assertIn('block', item)
            self.assertIn('transaction', item)
            self.assertIn('timestamp', item)

    def test_genesis_block_has_transaction(self):
        """Test that genesis block contains a genesis transaction."""
        blockchain = Blockchain(difficulty=2)

        genesis = blockchain.chain[0]

        self.assertIsNotNone(genesis.transactions)
        self.assertEqual(len(genesis.transactions), 1)
        self.assertEqual(genesis.transactions[0].sender, "System")
        self.assertEqual(genesis.transactions[0].receiver, "Genesis")

    def test_chain_validation_with_transactions(self):
        """Test that chain validation works with transaction-based blocks."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        blockchain.create_transaction("Bob", "Charlie", 25)
        blockchain.mine_pending_transactions("Miner1")

        self.assertTrue(blockchain.is_chain_valid())

    def test_tampering_detected_with_transactions(self):
        """Test that tampering with transactions is detected."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Tamper with transaction amount
        blockchain.chain[1].transactions[0].amount = 100

        # Should detect tampering
        self.assertFalse(blockchain.is_chain_valid())

    def test_custom_mining_reward(self):
        """Test blockchain with custom mining reward."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})
        blockchain.mining_reward = 25

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("Miner1"), 25)

    def test_block_transaction_count(self):
        """Test getting transaction count from blocks."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.create_transaction("Bob", "Charlie", 25)
        block = blockchain.mine_pending_transactions("Miner1")

        # Should have 2 original transactions + 1 reward
        self.assertEqual(block.get_transaction_count(), 3)

    def test_block_total_amount(self):
        """Test calculating total amount in a block."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.create_transaction("Bob", "Charlie", 25)
        block = blockchain.mine_pending_transactions("Miner1")

        # 50 + 25 + 10 (reward) = 85
        self.assertEqual(block.get_total_amount(), 85)

    def test_zero_balance_for_new_address(self):
        """Test that new addresses have zero balance."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(blockchain.get_balance("NewUser"), 0)

    def test_backward_compatibility_with_data_blocks(self):
        """Test that legacy data blocks still work."""
        blockchain = Blockchain(difficulty=2)

        # Add old-style data block
        blockchain.add_block("Some legacy data")

        self.assertEqual(len(blockchain.chain), 2)
        self.assertEqual(blockchain.chain[1].data, "Some legacy data")
        self.assertIsNone(blockchain.chain[1].transactions)

    def test_mixed_block_types_validation(self):
        """Test validation works with mixed block types."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        # Add transaction block
        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Add legacy data block
        blockchain.add_block("Legacy data")

        # Both should validate
        self.assertTrue(blockchain.is_chain_valid())

    def test_empty_transaction_history(self):
        """Test transaction history for address with no transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        history = blockchain.get_transaction_history("Charlie")

        self.assertEqual(len(history), 0)

    def test_print_blockchain_with_transactions(self):
        """Test that print_blockchain doesn't crash with transactions."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Should not raise an exception
        blockchain.print_blockchain()

    def test_print_balances(self):
        """Test that print_balances doesn't crash."""
        blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

        blockchain.create_transaction("Alice", "Bob", 50)
        blockchain.mine_pending_transactions("Miner1")

        # Should not raise an exception
        blockchain.print_balances(["Alice", "Bob", "Miner1"])


if __name__ == '__main__':
    unittest.main()
