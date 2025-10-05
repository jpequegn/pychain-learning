import unittest
import sys
import os
import tempfile
from io import StringIO
from cli import BlockchainCLI


class TestCLIExport(unittest.TestCase):
    """Test cases for CLI export/import/summary commands."""

    def setUp(self):
        """Set up CLI for testing."""
        self.test_data_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_data.json')
        self.test_export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_export.json')
        self.test_data_file.close()
        self.test_export_file.close()

        self.cli = BlockchainCLI(data_file=self.test_data_file.name)

        # Redirect stdout to capture output
        self.held_output = StringIO()
        self.original_stdout = sys.stdout

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout
        sys.stdout = self.original_stdout

        # Remove test files
        for filename in [self.test_data_file.name, self.test_export_file.name]:
            if os.path.exists(filename):
                os.remove(filename)

    def capture_output(self):
        """Start capturing stdout."""
        sys.stdout = self.held_output

    def get_output(self):
        """Get captured output and reset."""
        sys.stdout = self.original_stdout
        output = self.held_output.getvalue()
        self.held_output = StringIO()
        return output

    def test_export_command_basic(self):
        """Test basic export command."""
        self.capture_output()
        self.cli.run(['export', self.test_export_file.name])
        output = self.get_output()

        self.assertIn('[OK]', output)
        self.assertIn('exported', output.lower())
        self.assertIn('Total blocks: 1', output)  # Genesis
        self.assertTrue(os.path.exists(self.test_export_file.name))

    def test_export_command_with_transactions(self):
        """Test exporting blockchain with transactions."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        self.capture_output()
        self.cli.run(['export', self.test_export_file.name])
        output = self.get_output()

        self.assertIn('[OK]', output)
        self.assertIn('Total blocks: 2', output)  # Genesis + 1 mined

    def test_export_command_with_pending(self):
        """Test exporting with pending transactions."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])

        self.capture_output()
        self.cli.run(['export', self.test_export_file.name])
        output = self.get_output()

        self.assertIn('[OK]', output)
        self.assertIn('Pending transactions: 1', output)

    def test_import_command_basic(self):
        """Test basic import command."""
        # Export first
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['export', self.test_export_file.name])

        # Create new CLI and import
        cli2 = BlockchainCLI(data_file=self.test_data_file.name)

        self.capture_output()
        cli2.run(['import', self.test_export_file.name])
        output = self.get_output()

        self.assertIn('[OK]', output)
        self.assertIn('imported', output.lower())
        self.assertIn('Total blocks: 1', output)
        self.assertIn('Difficulty: 2', output)

    def test_import_command_validates_chain(self):
        """Test that import validates the imported chain."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['export', self.test_export_file.name])

        cli2 = BlockchainCLI(data_file=self.test_data_file.name)

        self.capture_output()
        cli2.run(['import', self.test_export_file.name])
        output = self.get_output()

        self.assertIn('Validation: [VALID]', output)

    def test_import_command_file_not_found(self):
        """Test import with non-existent file."""
        self.capture_output()

        with self.assertRaises(SystemExit):
            self.cli.run(['import', 'nonexistent.json'])

        output = self.get_output()
        self.assertIn('[ERROR]', output)
        self.assertIn('File not found', output)

    def test_import_command_invalid_json(self):
        """Test import with invalid JSON file."""
        # Write invalid JSON
        with open(self.test_export_file.name, 'w') as f:
            f.write("not valid json{]")

        self.capture_output()

        with self.assertRaises(SystemExit):
            self.cli.run(['import', self.test_export_file.name])

        output = self.get_output()
        self.assertIn('[ERROR]', output)

    def test_summary_command_basic(self):
        """Test basic summary command."""
        self.capture_output()
        self.cli.run(['summary'])
        output = self.get_output()

        self.assertIn('BLOCKCHAIN SUMMARY', output)
        self.assertIn('Total Blocks: 1', output)
        self.assertIn('Current Difficulty: 2', output)

    def test_summary_command_with_transactions(self):
        """Test summary with transactions."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        self.capture_output()
        self.cli.run(['summary'])
        output = self.get_output()

        self.assertIn('Total Blocks: 2', output)
        self.assertIn('Mining Performance:', output)
        self.assertIn('Chain Validation: [VALID]', output)

    def test_summary_command_shows_initial_balances(self):
        """Test that summary shows initial balances."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['init-balance', 'Bob', '50'])

        self.capture_output()
        self.cli.run(['summary'])
        output = self.get_output()

        self.assertIn('Initial Balances:', output)
        self.assertIn('Alice: 100', output)
        self.assertIn('Bob: 50', output)

    def test_details_command_valid_block(self):
        """Test details command for valid block."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        self.capture_output()
        self.cli.run(['details', '1'])
        output = self.get_output()

        self.assertIn('BLOCK #1 TRANSACTION DETAILS', output)
        self.assertIn('From: Alice', output)
        self.assertIn('To: Bob', output)
        self.assertIn('Amount: 50', output)

    def test_details_command_genesis_block(self):
        """Test details command for genesis block."""
        self.capture_output()
        self.cli.run(['details', '0'])
        output = self.get_output()

        self.assertIn('BLOCK #0 TRANSACTION DETAILS', output)
        self.assertIn('From: System', output)
        self.assertIn('To: Genesis', output)

    def test_details_command_invalid_block(self):
        """Test details command for non-existent block."""
        self.capture_output()

        with self.assertRaises(SystemExit):
            self.cli.run(['details', '999'])

        output = self.get_output()
        self.assertIn('Error: Block 999 does not exist', output)

    def test_export_import_roundtrip(self):
        """Test complete export/import workflow."""
        # Create complex blockchain
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['init-balance', 'Bob', '50'])
        self.cli.run(['transaction', 'Alice', 'Bob', '30'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['transaction', 'Bob', 'Charlie', '15'])

        # Get original balances
        original_alice = self.cli.blockchain.get_balance('Alice')
        original_bob = self.cli.blockchain.get_balance('Bob')
        original_miner = self.cli.blockchain.get_balance('Miner1')

        # Export
        self.cli.run(['export', self.test_export_file.name])

        # Import into new CLI
        cli2 = BlockchainCLI(data_file=self.test_data_file.name)
        cli2.run(['import', self.test_export_file.name])

        # Verify balances match
        self.assertEqual(cli2.blockchain.get_balance('Alice'), original_alice)
        self.assertEqual(cli2.blockchain.get_balance('Bob'), original_bob)
        self.assertEqual(cli2.blockchain.get_balance('Miner1'), original_miner)

        # Verify pending transactions
        self.assertEqual(
            len(cli2.blockchain.pending_transactions),
            len(self.cli.blockchain.pending_transactions)
        )

    def test_workflow_export_modify_import(self):
        """Test workflow where blockchain is exported, modified, then re-imported."""
        # Create initial blockchain
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['export', self.test_export_file.name])

        # Import and continue working
        cli2 = BlockchainCLI(data_file=self.test_data_file.name)
        cli2.run(['import', self.test_export_file.name])
        cli2.run(['transaction', 'Bob', 'Charlie', '25'])
        cli2.run(['mine', 'Miner2'])

        # Verify continuation worked
        self.assertEqual(len(cli2.blockchain.chain), 3)  # Genesis + 2 mined

    def test_summary_after_import(self):
        """Test that summary works correctly after import."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['export', self.test_export_file.name])

        cli2 = BlockchainCLI(data_file=self.test_data_file.name)
        cli2.run(['import', self.test_export_file.name])

        self.capture_output()
        cli2.run(['summary'])
        output = self.get_output()

        self.assertIn('Total Blocks: 2', output)
        self.assertIn('Mining Performance:', output)

    def test_details_after_import(self):
        """Test that details command works after import."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['export', self.test_export_file.name])

        cli2 = BlockchainCLI(data_file=self.test_data_file.name)
        cli2.run(['import', self.test_export_file.name])

        self.capture_output()
        cli2.run(['details', '1'])
        output = self.get_output()

        self.assertIn('BLOCK #1 TRANSACTION DETAILS', output)
        self.assertIn('From: Alice', output)


if __name__ == '__main__':
    unittest.main()
