import unittest
import sys
import os
import json
from io import StringIO
from cli import BlockchainCLI


class TestCLI(unittest.TestCase):
    """Test cases for the command-line interface."""

    def setUp(self):
        """Set up CLI for testing."""
        self.test_data_file = 'test_blockchain_data.json'
        self.cli = BlockchainCLI(data_file=self.test_data_file)
        # Redirect stdout to capture output
        self.held_output = StringIO()
        self.original_stdout = sys.stdout

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout
        sys.stdout = self.original_stdout
        # Remove test data file
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def capture_output(self):
        """Start capturing stdout."""
        sys.stdout = self.held_output

    def get_output(self):
        """Get captured output and reset."""
        sys.stdout = self.original_stdout
        output = self.held_output.getvalue()
        self.held_output = StringIO()
        return output

    def test_init_balance_command(self):
        """Test init-balance command."""
        self.cli.run(['init-balance', 'Alice', '100'])

        balance = self.cli.blockchain.get_balance('Alice')
        self.assertEqual(balance, 100)

    def test_init_balance_updates_existing(self):
        """Test that init-balance updates existing balance."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['init-balance', 'Alice', '200'])

        balance = self.cli.blockchain.get_balance('Alice')
        self.assertEqual(balance, 200)

    def test_transaction_command_success(self):
        """Test successful transaction command."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])

        self.assertEqual(len(self.cli.blockchain.pending_transactions), 1)
        tx = self.cli.blockchain.pending_transactions[0]
        self.assertEqual(tx.sender, 'Alice')
        self.assertEqual(tx.receiver, 'Bob')
        self.assertEqual(tx.amount, 50)

    def test_transaction_command_insufficient_balance(self):
        """Test transaction with insufficient balance."""
        self.cli.run(['init-balance', 'Alice', '50'])

        with self.assertRaises(SystemExit):
            self.cli.run(['transaction', 'Alice', 'Bob', '100'])

    def test_transaction_command_invalid_amount(self):
        """Test transaction with invalid amount."""
        self.cli.run(['init-balance', 'Alice', '100'])

        with self.assertRaises(SystemExit):
            self.cli.run(['transaction', 'Alice', 'Bob', '0'])

    def test_mine_command_success(self):
        """Test successful mine command."""
        initial_blocks = len(self.cli.blockchain.chain)

        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        self.assertEqual(len(self.cli.blockchain.chain), initial_blocks + 1)
        self.assertEqual(len(self.cli.blockchain.pending_transactions), 0)

    def test_mine_command_no_pending(self):
        """Test mine command with no pending transactions."""
        self.capture_output()
        self.cli.run(['mine', 'Miner1'])
        output = self.get_output()

        self.assertIn('No pending', output)

    def test_view_command(self):
        """Test view command."""
        self.capture_output()
        self.cli.run(['view'])
        output = self.get_output()

        self.assertIn('BLOCKCHAIN', output)
        self.assertIn('Block #0', output)

    def test_view_command_detail(self):
        """Test view command with detail flag."""
        self.capture_output()
        self.cli.run(['view', '--detail'])
        output = self.get_output()

        self.assertIn('BLOCKCHAIN', output)
        self.assertIn('Nonce', output)
        self.assertIn('Difficulty', output)

    def test_balance_command(self):
        """Test balance command."""
        self.cli.run(['init-balance', 'Alice', '100'])

        self.capture_output()
        self.cli.run(['balance', 'Alice'])
        output = self.get_output()

        self.assertIn('Alice', output)
        self.assertIn('100', output)

    def test_balance_command_with_pending(self):
        """Test balance command with pending flag."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '30'])

        self.capture_output()
        self.cli.run(['balance', 'Alice', '--pending'])
        output = self.get_output()

        self.assertIn('70', output)  # 100 - 30

    def test_balance_command_negative(self):
        """Test balance command with negative balance."""
        # Create transaction without initial balance (will create negative balance after mining)
        self.cli.blockchain.initial_balances['Alice'] = 0

        self.capture_output()
        self.cli.run(['balance', 'Alice'])
        output = self.get_output()

        self.assertIn('0', output)

    def test_history_command_empty(self):
        """Test history command with no transactions."""
        self.capture_output()
        self.cli.run(['history', 'Alice'])
        output = self.get_output()

        self.assertIn('No transaction history', output)

    def test_history_command_with_transactions(self):
        """Test history command with transactions."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        self.capture_output()
        self.cli.run(['history', 'Alice'])
        output = self.get_output()

        self.assertIn('Transaction History', output)
        self.assertIn('Bob', output)
        self.assertIn('-50', output)

    def test_validate_command_valid(self):
        """Test validate command with valid chain."""
        self.capture_output()
        self.cli.run(['validate'])
        output = self.get_output()

        self.assertIn('valid', output.lower())

    def test_validate_command_verbose(self):
        """Test validate command with verbose flag."""
        self.capture_output()
        self.cli.run(['validate', '--verbose'])
        output = self.get_output()

        self.assertIn('valid', output.lower())

    def test_stats_command_insufficient_blocks(self):
        """Test stats command with only genesis block."""
        self.capture_output()
        self.cli.run(['stats'])
        output = self.get_output()

        self.assertIn('Not enough data', output)

    def test_stats_command_with_blocks(self):
        """Test stats command with multiple blocks."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])
        self.cli.run(['transaction', 'Bob', 'Charlie', '25'])
        self.cli.run(['mine', 'Miner2'])

        self.capture_output()
        self.cli.run(['stats'])
        output = self.get_output()

        self.assertIn('Mining Statistics', output)
        self.assertIn('Total blocks', output)

    def test_pending_command_empty(self):
        """Test pending command with no pending transactions."""
        self.capture_output()
        self.cli.run(['pending'])
        output = self.get_output()

        self.assertIn('No pending', output)

    def test_pending_command_with_transactions(self):
        """Test pending command with pending transactions."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['transaction', 'Alice', 'Charlie', '30'])

        self.capture_output()
        self.cli.run(['pending'])
        output = self.get_output()

        self.assertIn('Pending Transactions (2)', output)
        self.assertIn('Bob', output)
        self.assertIn('Charlie', output)

    def test_reset_command_without_confirm(self):
        """Test reset command without confirmation."""
        initial_blocks = len(self.cli.blockchain.chain)

        self.cli.run(['init-balance', 'Alice', '100'])

        self.capture_output()
        self.cli.run(['reset'])
        output = self.get_output()

        self.assertIn('confirm', output.lower())
        # Blockchain should not be reset
        self.assertIn('Alice', self.cli.blockchain.initial_balances)

    def test_reset_command_with_confirm(self):
        """Test reset command with confirmation."""
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])

        self.cli.run(['reset', '--confirm'])

        # Blockchain should be reset
        self.assertEqual(len(self.cli.blockchain.chain), 1)  # Only genesis
        self.assertEqual(len(self.cli.blockchain.pending_transactions), 0)
        self.assertEqual(len(self.cli.blockchain.initial_balances), 0)

    def test_persistence_save_and_load(self):
        """Test blockchain state persistence."""
        # Create and save state
        cli1 = BlockchainCLI(data_file=self.test_data_file)
        cli1.blockchain.initial_balances['Alice'] = 100
        cli1.save_blockchain()

        # Load in new instance
        cli2 = BlockchainCLI(data_file=self.test_data_file)

        # Verify state was restored
        self.assertEqual(cli2.blockchain.initial_balances.get('Alice'), 100)

    def test_no_command_shows_help(self):
        """Test that no command shows help message."""
        self.capture_output()
        self.cli.run([])
        output = self.get_output()

        self.assertIn('usage', output.lower())

    def test_workflow_complete_transaction_cycle(self):
        """Test complete transaction workflow."""
        # Set up initial balances
        self.cli.run(['init-balance', 'Alice', '100'])
        self.cli.run(['init-balance', 'Bob', '50'])

        # Create transactions
        self.cli.run(['transaction', 'Alice', 'Bob', '30'])
        self.cli.run(['transaction', 'Bob', 'Charlie', '20'])

        # Verify pending
        self.assertEqual(len(self.cli.blockchain.pending_transactions), 2)

        # Mine block
        self.cli.run(['mine', 'Miner1'])

        # Verify balances
        self.assertEqual(self.cli.blockchain.get_balance('Alice'), 70)  # 100 - 30
        self.assertEqual(self.cli.blockchain.get_balance('Bob'), 60)  # 50 + 30 - 20
        self.assertEqual(self.cli.blockchain.get_balance('Charlie'), 20)
        self.assertEqual(self.cli.blockchain.get_balance('Miner1'), 10)  # Mining reward

        # Validate chain
        self.assertTrue(self.cli.blockchain.is_chain_valid())

    def test_workflow_multiple_mining_rounds(self):
        """Test workflow with multiple mining rounds."""
        self.cli.run(['init-balance', 'Alice', '200'])

        # First round
        self.cli.run(['transaction', 'Alice', 'Bob', '50'])
        self.cli.run(['mine', 'Miner1'])

        # Second round
        self.cli.run(['transaction', 'Bob', 'Charlie', '25'])
        self.cli.run(['mine', 'Miner2'])

        # Third round
        self.cli.run(['transaction', 'Alice', 'Charlie', '30'])
        self.cli.run(['mine', 'Miner1'])

        # Verify final state
        self.assertEqual(len(self.cli.blockchain.chain), 4)  # Genesis + 3 mined
        self.assertEqual(self.cli.blockchain.get_balance('Alice'), 120)  # 200 - 50 - 30
        self.assertEqual(self.cli.blockchain.get_balance('Miner1'), 20)  # 2 blocks * 10


if __name__ == '__main__':
    unittest.main()
