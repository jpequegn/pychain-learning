import unittest
import os
import json
import tempfile
from pychain.blockchain import Blockchain
from pychain.transaction import Transaction


class TestExportImport(unittest.TestCase):
    """Test cases for blockchain export and import functionality."""

    def setUp(self):
        """Set up test blockchain."""
        self.blockchain = Blockchain(
            difficulty=2,
            target_block_time=10,
            adjustment_interval=5,
            initial_balances={"Alice": 100, "Bob": 50}
        )
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_filename = self.test_file.name
        self.test_file.close()

    def tearDown(self):
        """Clean up test file."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_to_dict_basic(self):
        """Test converting blockchain to dictionary."""
        data = self.blockchain.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['difficulty'], 2)
        self.assertEqual(data['target_block_time'], 10)
        self.assertEqual(data['adjustment_interval'], 5)
        self.assertEqual(data['mining_reward'], 10)
        self.assertEqual(data['initial_balances'], {"Alice": 100, "Bob": 50})
        self.assertIn('blocks', data)
        self.assertIn('pending_transactions', data)

    def test_to_dict_with_transactions(self):
        """Test to_dict with transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        data = self.blockchain.to_dict()

        # Check blocks
        self.assertEqual(len(data['blocks']), 2)  # Genesis + 1 mined

        # Check first mined block has transactions
        block_data = data['blocks'][1]
        self.assertIsNotNone(block_data['transactions'])
        self.assertEqual(len(block_data['transactions']), 2)  # Original tx + reward

    def test_to_dict_with_pending(self):
        """Test to_dict with pending transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)

        data = self.blockchain.to_dict()

        # Check pending transactions
        self.assertEqual(len(data['pending_transactions']), 1)
        pending_tx = data['pending_transactions'][0]
        self.assertEqual(pending_tx['sender'], "Alice")
        self.assertEqual(pending_tx['receiver'], "Bob")
        self.assertEqual(pending_tx['amount'], 30)

    def test_to_json_format(self):
        """Test JSON string generation."""
        json_str = self.blockchain.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['difficulty'], 2)

    def test_to_json_indent(self):
        """Test JSON with different indentation."""
        json_str_2 = self.blockchain.to_json(indent=2)
        json_str_4 = self.blockchain.to_json(indent=4)

        # Both should be valid
        self.assertIsInstance(json.loads(json_str_2), dict)
        self.assertIsInstance(json.loads(json_str_4), dict)

        # 4-space should be longer due to more whitespace
        self.assertGreater(len(json_str_4), len(json_str_2))

    def test_export_to_file_success(self):
        """Test successful file export."""
        success = self.blockchain.export_to_file(self.test_filename)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_filename))

        # Verify file content
        with open(self.test_filename, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['difficulty'], 2)
        self.assertEqual(len(data['blocks']), 1)  # Genesis block

    def test_export_to_file_with_transactions(self):
        """Test exporting blockchain with transactions."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        success = self.blockchain.export_to_file(self.test_filename)
        self.assertTrue(success)

        # Verify content
        with open(self.test_filename, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['blocks']), 2)
        self.assertEqual(len(data['blocks'][1]['transactions']), 2)

    def test_import_from_file_basic(self):
        """Test importing blockchain from file."""
        # Export first
        self.blockchain.export_to_file(self.test_filename)

        # Import
        imported = Blockchain.import_from_file(self.test_filename)

        self.assertIsNotNone(imported)
        self.assertEqual(imported.difficulty, 2)
        self.assertEqual(imported.target_block_time, 10)
        self.assertEqual(imported.adjustment_interval, 5)
        self.assertEqual(imported.mining_reward, 10)
        self.assertEqual(imported.initial_balances, {"Alice": 100, "Bob": 50})
        self.assertEqual(len(imported.chain), 1)  # Genesis

    def test_import_from_file_with_transactions(self):
        """Test importing blockchain with transactions."""
        # Create transactions and mine
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")
        self.blockchain.create_transaction("Bob", "Charlie", 15)

        # Export
        self.blockchain.export_to_file(self.test_filename)

        # Import
        imported = Blockchain.import_from_file(self.test_filename)

        # Verify structure
        self.assertEqual(len(imported.chain), 2)  # Genesis + 1 mined
        self.assertEqual(len(imported.pending_transactions), 1)

        # Verify transaction data
        block = imported.chain[1]
        self.assertEqual(len(block.transactions), 2)  # Original + reward
        self.assertEqual(block.transactions[0].sender, "Alice")
        self.assertEqual(block.transactions[0].receiver, "Bob")
        self.assertEqual(block.transactions[0].amount, 30)

    def test_import_validates_chain(self):
        """Test that imported blockchain is valid."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        self.blockchain.export_to_file(self.test_filename)
        imported = Blockchain.import_from_file(self.test_filename)

        # Chain should be valid
        self.assertTrue(imported.is_chain_valid())

    def test_import_preserves_balances(self):
        """Test that import preserves balance calculations."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        original_alice = self.blockchain.get_balance("Alice")
        original_bob = self.blockchain.get_balance("Bob")
        original_miner = self.blockchain.get_balance("Miner1")

        # Export and import
        self.blockchain.export_to_file(self.test_filename)
        imported = Blockchain.import_from_file(self.test_filename)

        # Balances should match
        self.assertEqual(imported.get_balance("Alice"), original_alice)
        self.assertEqual(imported.get_balance("Bob"), original_bob)
        self.assertEqual(imported.get_balance("Miner1"), original_miner)

    def test_import_file_not_found(self):
        """Test import with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            Blockchain.import_from_file("nonexistent.json")

    def test_import_invalid_json(self):
        """Test import with invalid JSON."""
        with open(self.test_filename, 'w') as f:
            f.write("not valid json{]")

        with self.assertRaises(ValueError):
            Blockchain.import_from_file(self.test_filename)

    def test_import_missing_fields(self):
        """Test import with missing required fields."""
        with open(self.test_filename, 'w') as f:
            json.dump({"some": "data"}, f)

        # Should use defaults for missing fields
        imported = Blockchain.import_from_file(self.test_filename)
        self.assertEqual(imported.difficulty, 2)
        self.assertEqual(len(imported.chain), 0)  # No blocks in file

    def test_export_import_roundtrip(self):
        """Test that export->import produces identical blockchain."""
        # Create complex blockchain
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")
        self.blockchain.create_transaction("Bob", "Charlie", 15)
        self.blockchain.mine_pending_transactions("Miner2")
        self.blockchain.create_transaction("Charlie", "Alice", 10)

        # Export
        self.blockchain.export_to_file(self.test_filename)

        # Import
        imported = Blockchain.import_from_file(self.test_filename)

        # Compare key attributes
        self.assertEqual(len(imported.chain), len(self.blockchain.chain))
        self.assertEqual(len(imported.pending_transactions), len(self.blockchain.pending_transactions))

        # Compare block hashes
        for i in range(len(self.blockchain.chain)):
            self.assertEqual(
                imported.chain[i].hash,
                self.blockchain.chain[i].hash
            )

    def test_export_empty_blockchain(self):
        """Test exporting blockchain with only genesis."""
        blockchain = Blockchain(difficulty=1)
        success = blockchain.export_to_file(self.test_filename)

        self.assertTrue(success)

        imported = Blockchain.import_from_file(self.test_filename)
        self.assertEqual(len(imported.chain), 1)

    def test_export_large_blockchain(self):
        """Test exporting larger blockchain."""
        # Create multiple blocks
        for i in range(5):
            self.blockchain.create_transaction("Alice", "Bob", 10)
            self.blockchain.mine_pending_transactions(f"Miner{i}")

        success = self.blockchain.export_to_file(self.test_filename)
        self.assertTrue(success)

        imported = Blockchain.import_from_file(self.test_filename)
        self.assertEqual(len(imported.chain), 6)  # Genesis + 5 mined

    def test_import_preserves_transaction_ids(self):
        """Test that transaction IDs are preserved on import."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        original_tx_id = self.blockchain.chain[1].transactions[0].transaction_id

        self.blockchain.export_to_file(self.test_filename)
        imported = Blockchain.import_from_file(self.test_filename)

        imported_tx_id = imported.chain[1].transactions[0].transaction_id
        self.assertEqual(imported_tx_id, original_tx_id)

    def test_import_preserves_timestamps(self):
        """Test that timestamps are preserved on import."""
        self.blockchain.create_transaction("Alice", "Bob", 30)
        self.blockchain.mine_pending_transactions("Miner1")

        original_block_time = self.blockchain.chain[1].timestamp
        original_tx_time = self.blockchain.chain[1].transactions[0].timestamp

        self.blockchain.export_to_file(self.test_filename)
        imported = Blockchain.import_from_file(self.test_filename)

        self.assertEqual(imported.chain[1].timestamp, original_block_time)
        self.assertEqual(imported.chain[1].transactions[0].timestamp, original_tx_time)


if __name__ == '__main__':
    unittest.main()
