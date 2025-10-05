"""
PyChain Command-Line Interface

A user-friendly CLI for interacting with the blockchain.
Supports creating transactions, mining blocks, viewing the chain, and validating integrity.
"""

import argparse
import sys
import time
import json
import os
from pychain.blockchain import Blockchain
from pychain.transaction import Transaction


class BlockchainCLI:
    """Command-line interface for PyChain blockchain."""

    def __init__(self, data_file='blockchain_data.json'):
        """
        Initialize the CLI with a blockchain instance.

        Args:
            data_file (str): Path to file for persisting blockchain state
        """
        self.data_file = data_file
        self.blockchain = self.load_blockchain()
        self.setup_parser()

    def load_blockchain(self):
        """
        Load blockchain from file or create new one.

        Returns:
            Blockchain: Loaded or new blockchain instance
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    blockchain = Blockchain(
                        difficulty=data.get('difficulty', 2),
                        target_block_time=data.get('target_block_time', 10),
                        adjustment_interval=data.get('adjustment_interval', 5),
                        initial_balances=data.get('initial_balances', {})
                    )
                    # Note: Full blockchain restoration would require more complex serialization
                    # For now, we just preserve initial balances
                    return blockchain
            except Exception as e:
                print(f"Warning: Could not load blockchain data: {e}")
                print("Starting with fresh blockchain...")

        return Blockchain(difficulty=2)

    def save_blockchain(self):
        """Save blockchain state to file."""
        try:
            data = {
                'difficulty': self.blockchain.difficulty,
                'target_block_time': self.blockchain.target_block_time,
                'adjustment_interval': self.blockchain.adjustment_interval,
                'initial_balances': self.blockchain.initial_balances,
                'blocks': len(self.blockchain.chain),
                'pending': len(self.blockchain.pending_transactions)
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save blockchain data: {e}")

    def setup_parser(self):
        """Set up command-line argument parser."""
        self.parser = argparse.ArgumentParser(
            prog='pychain',
            description='PyChain - A simple blockchain implementation',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Initialize accounts
  python cli.py init-balance Alice 100

  # Create a transaction
  python cli.py transaction Alice Bob 50

  # Mine pending transactions
  python cli.py mine Miner1

  # View the blockchain
  python cli.py view

  # Check balance
  python cli.py balance Alice

  # Validate chain
  python cli.py validate
            '''
        )

        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')

        # Init balance command
        init_parser = subparsers.add_parser('init-balance', help='Set initial balance for an address')
        init_parser.add_argument('address', help='Address to fund')
        init_parser.add_argument('amount', type=float, help='Initial amount')

        # Transaction command
        tx_parser = subparsers.add_parser('transaction', help='Create a new transaction')
        tx_parser.add_argument('sender', help='Sender address')
        tx_parser.add_argument('receiver', help='Receiver address')
        tx_parser.add_argument('amount', type=float, help='Amount to send')

        # Mine command
        mine_parser = subparsers.add_parser('mine', help='Mine pending transactions')
        mine_parser.add_argument('miner', help='Miner address to receive reward')

        # View command
        view_parser = subparsers.add_parser('view', help='View blockchain')
        view_parser.add_argument('--detail', action='store_true', help='Show detailed view')

        # Balance command
        balance_parser = subparsers.add_parser('balance', help='Check address balance')
        balance_parser.add_argument('address', help='Address to check')
        balance_parser.add_argument('--pending', action='store_true', help='Include pending transactions')

        # History command
        history_parser = subparsers.add_parser('history', help='View transaction history')
        history_parser.add_argument('address', help='Address to check')

        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate blockchain integrity')
        validate_parser.add_argument('--verbose', action='store_true', help='Show detailed validation')

        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show mining statistics')

        # Pending command
        pending_parser = subparsers.add_parser('pending', help='View pending transactions')

        # Reset command
        reset_parser = subparsers.add_parser('reset', help='Reset blockchain to genesis')
        reset_parser.add_argument('--confirm', action='store_true', help='Confirm reset')

        # Export command
        export_parser = subparsers.add_parser('export', help='Export blockchain to JSON file')
        export_parser.add_argument('filename', help='Output filename')

        # Import command
        import_parser = subparsers.add_parser('import', help='Import blockchain from JSON file')
        import_parser.add_argument('filename', help='Input filename')

        # Summary command
        summary_parser = subparsers.add_parser('summary', help='Show blockchain summary')

        # Block details command
        details_parser = subparsers.add_parser('details', help='Show detailed transaction info for a block')
        details_parser.add_argument('block_index', type=int, help='Block index to display')

    def run(self, args=None):
        """
        Run CLI with provided arguments.

        Args:
            args (list): Command-line arguments (default: sys.argv)
        """
        args = self.parser.parse_args(args)

        if not args.command:
            self.parser.print_help()
            return

        # Route to appropriate handler
        handler_name = f'handle_{args.command.replace("-", "_")}'
        handler = getattr(self, handler_name, None)

        if handler:
            try:
                handler(args)
                # Save state after successful command execution
                if args.command not in ['view', 'balance', 'history', 'validate', 'stats', 'pending', 'export', 'summary', 'details']:
                    self.save_blockchain()
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    def handle_init_balance(self, args):
        """Handle init-balance command."""
        if args.address in self.blockchain.initial_balances:
            print(f"Warning: {args.address} already has initial balance of {self.blockchain.initial_balances[args.address]}")
            print(f"Updating to {args.amount}...")

        self.blockchain.initial_balances[args.address] = args.amount
        print(f"[OK] Set initial balance: {args.address} = {args.amount}")

    def handle_transaction(self, args):
        """Handle transaction command."""
        try:
            tx = self.blockchain.create_transaction(
                args.sender,
                args.receiver,
                args.amount
            )

            print(f"[OK] Transaction created:")
            print(f"   {args.sender} -> {args.receiver}: {args.amount}")
            print(f"   Transaction ID: {tx.transaction_id[:16]}...")
            print(f"   Pending transactions: {len(self.blockchain.pending_transactions)}")

        except ValueError as e:
            print(f"[ERROR] Transaction failed: {e}")
            sys.exit(1)

    def handle_mine(self, args):
        """Handle mine command."""
        pending_count = len(self.blockchain.pending_transactions)

        if pending_count == 0:
            print("[WARNING] No pending transactions to mine")
            return

        print(f"[MINING] Mining {pending_count} transaction(s)...")
        start_time = time.time()

        block = self.blockchain.mine_pending_transactions(args.miner)

        mining_duration = time.time() - start_time

        if block:
            print(f"[OK] Block #{block.index} mined successfully!")
            print(f"   Hash: {block.hash[:32]}...")
            print(f"   Nonce: {block.nonce}")
            print(f"   Transactions: {len(block.transactions)}")
            print(f"   Mining time: {mining_duration:.2f}s")
            print(f"   Reward sent to: {args.miner}")

    def handle_view(self, args):
        """Handle view command."""
        print("\n" + "=" * 70)
        print(f"{'BLOCKCHAIN':^70}")
        print("=" * 70)
        print(f"Total blocks: {len(self.blockchain.chain)}")
        print(f"Difficulty: {self.blockchain.difficulty}")
        print(f"Pending transactions: {len(self.blockchain.pending_transactions)}")
        print("=" * 70)

        for block in self.blockchain.chain:
            print(f"\n[Block #{block.index}]")
            print(f"   Timestamp: {time.ctime(block.timestamp)}")
            print(f"   Hash: {block.hash}")

            if args.detail:
                print(f"   Previous Hash: {block.previous_hash}")
                print(f"   Nonce: {block.nonce}")
                print(f"   Difficulty: {block.difficulty}")

            if block.transactions:
                print(f"   Transactions ({len(block.transactions)}):")
                for i, tx in enumerate(block.transactions, 1):
                    if args.detail:
                        print(f"      {i}. {tx.sender} -> {tx.receiver}: {tx.amount}")
                        print(f"         ID: {tx.transaction_id[:16]}...")
                    else:
                        print(f"      {i}. {tx.sender} -> {tx.receiver}: {tx.amount}")
            elif block.data is not None:
                print(f"   Data: {block.data}")

        print("\n" + "=" * 70 + "\n")

    def handle_balance(self, args):
        """Handle balance command."""
        balance = self.blockchain.get_balance(args.address, include_pending=args.pending)

        print(f"\nBalance for {args.address}")
        print(f"   {balance:.2f}")

        if args.pending:
            confirmed_balance = self.blockchain.get_balance(args.address, include_pending=False)
            if confirmed_balance != balance:
                print(f"   Confirmed: {confirmed_balance:.2f}")
                print(f"   Pending: {balance - confirmed_balance:+.2f}")

        if balance < 0:
            print(f"   [WARNING] Negative balance (debt)")
        elif balance == 0:
            print(f"   [INFO] Zero balance")

        print()

    def handle_history(self, args):
        """Handle history command."""
        history = self.blockchain.get_transaction_history(args.address)

        if not history:
            print(f"No transaction history for {args.address}")
            return

        print(f"\nTransaction History for {args.address}")
        print("=" * 70)

        for item in history:
            tx = item['transaction']
            block_num = item['block']

            direction = "->" if tx.sender == args.address else "<-"
            other_party = tx.receiver if tx.sender == args.address else tx.sender
            amount = tx.amount

            if tx.sender == args.address:
                amount_str = f"-{amount:.2f}"
            else:
                amount_str = f"+{amount:.2f}"

            print(f"Block #{block_num:3d} | {direction} {other_party:15s} | {amount_str:>10s}")

        print("=" * 70 + "\n")

    def handle_validate(self, args):
        """Handle validate command."""
        print("Validating blockchain...")

        is_valid = self.blockchain.is_chain_valid(verbose=args.verbose)

        if is_valid:
            print("[OK] Blockchain is valid!")
            print(f"   Total blocks: {len(self.blockchain.chain)}")
            print(f"   Current difficulty: {self.blockchain.difficulty}")
        else:
            print("[ERROR] Blockchain validation failed!")
            print("   Chain integrity compromised")
            sys.exit(1)

    def handle_stats(self, args):
        """Handle stats command."""
        stats = self.blockchain.get_mining_stats()

        if not stats:
            print("[WARNING] Not enough data for statistics")
            return

        print("\nMining Statistics")
        print("=" * 50)
        print(f"Total blocks:       {stats['total_blocks']}")
        print(f"Current difficulty: {stats['current_difficulty']}")
        print(f"Average difficulty: {stats['avg_difficulty']:.2f}")
        print(f"Target block time:  {stats['target_block_time']}s")
        print(f"Average block time: {stats['avg_block_time']:.2f}s")
        print(f"Min block time:     {stats['min_block_time']:.2f}s")
        print(f"Max block time:     {stats['max_block_time']:.2f}s")

        ratio = stats['avg_block_time'] / stats['target_block_time']
        if 0.8 <= ratio <= 1.2:
            print("\n[OK] Mining on target")
        elif ratio < 0.8:
            print("\n[FAST] Mining too fast")
        else:
            print("\n[SLOW] Mining too slow")

        print("=" * 50 + "\n")

    def handle_pending(self, args):
        """Handle pending command."""
        pending = self.blockchain.pending_transactions

        if not pending:
            print("No pending transactions")
            return

        print(f"\nPending Transactions ({len(pending)})")
        print("=" * 70)

        total_amount = 0
        for i, tx in enumerate(pending, 1):
            print(f"{i}. {tx.sender} -> {tx.receiver}: {tx.amount}")
            total_amount += tx.amount

        print("=" * 70)
        print(f"Total volume: {total_amount:.2f}")
        print()

    def handle_reset(self, args):
        """Handle reset command."""
        if not args.confirm:
            print("[WARNING] This will reset the blockchain to genesis block!")
            print("   Use --confirm flag to proceed")
            return

        self.blockchain = Blockchain(difficulty=2)
        self.save_blockchain()
        print("[OK] Blockchain reset to genesis block")

    def handle_export(self, args):
        """Handle export command."""
        success = self.blockchain.export_to_file(args.filename)

        if success:
            print(f"[OK] Blockchain exported to {args.filename}")
            print(f"   Total blocks: {len(self.blockchain.chain)}")
            print(f"   Pending transactions: {len(self.blockchain.pending_transactions)}")
        else:
            print(f"[ERROR] Failed to export blockchain")
            sys.exit(1)

    def handle_import(self, args):
        """Handle import command."""
        try:
            self.blockchain = Blockchain.import_from_file(args.filename)

            print(f"[OK] Blockchain imported from {args.filename}")
            print(f"   Total blocks: {len(self.blockchain.chain)}")
            print(f"   Pending transactions: {len(self.blockchain.pending_transactions)}")
            print(f"   Difficulty: {self.blockchain.difficulty}")

            # Validate imported chain
            is_valid = self.blockchain.is_chain_valid()
            if is_valid:
                print(f"   Validation: [VALID]")
            else:
                print(f"   Validation: [INVALID - chain may be corrupted]")

        except FileNotFoundError:
            print(f"[ERROR] File not found: {args.filename}")
            sys.exit(1)
        except ValueError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)

    def handle_summary(self, args):
        """Handle summary command."""
        self.blockchain.print_summary()

    def handle_details(self, args):
        """Handle details command."""
        success = self.blockchain.print_transaction_details(args.block_index)
        if not success:
            sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli = BlockchainCLI()
    cli.run()


if __name__ == '__main__':
    main()
