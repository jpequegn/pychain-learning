import time
import json
from pychain.block import Block
from pychain.transaction import Transaction
from pychain.logger_config import get_logger
from pychain.exceptions import (
    BlockchainError,
    InvalidTransactionError,
    InsufficientBalanceError,
    InvalidBlockError,
    ChainValidationError,
    MiningError,
    ImportExportError,
    ValidationError
)

# Set up logger for this module
logger = get_logger('pychain.blockchain')


class Blockchain:
    """
    A blockchain that manages a chain of blocks.

    The blockchain automatically creates a genesis block upon initialization
    and provides methods to manage the chain with dynamic difficulty adjustment.
    Supports both legacy data blocks and transaction-based blocks.

    Attributes:
        chain (list): List of Block objects representing the blockchain
        difficulty (int): Current mining difficulty for Proof of Work
        target_block_time (float): Target time between blocks in seconds
        adjustment_interval (int): Adjust difficulty every N blocks
        pending_transactions (list): Pool of transactions waiting to be mined
        mining_reward (float): Reward given to miners for mining a block
    """

    def __init__(self, difficulty=2, target_block_time=10, adjustment_interval=5, initial_balances=None):
        """
        Initialize the blockchain with a genesis block and dynamic difficulty.

        Creates an empty chain list and automatically adds the genesis block.

        Args:
            difficulty (int): Initial mining difficulty (default: 2)
            target_block_time (float): Target time between blocks in seconds (default: 10)
            adjustment_interval (int): Adjust difficulty every N blocks (default: 5)
            initial_balances (dict): Initial balances for addresses (default: None)
                Example: {"Alice": 100, "Bob": 50}

        Raises:
            BlockchainError: If blockchain initialization fails
        """
        logger.info(f"Initializing blockchain (difficulty: {difficulty}, target_block_time: {target_block_time}s)")

        try:
            self.chain = []
            self.difficulty = difficulty
            self.target_block_time = target_block_time
            self.adjustment_interval = adjustment_interval
            self.pending_transactions = []
            self.mining_reward = 10
            self.initial_balances = initial_balances if initial_balances is not None else {}

            if self.initial_balances:
                logger.debug(f"Initial balances set for {len(self.initial_balances)} addresses")

            genesis = self.create_genesis_block()
            self.chain.append(genesis)

            logger.info("Blockchain initialized successfully with genesis block")

        except Exception as e:
            logger.critical(f"Blockchain initialization failed: {e}")
            raise BlockchainError(f"Blockchain initialization failed: {e}") from e

    def create_genesis_block(self):
        """
        Create the genesis block (first block in the blockchain).

        The genesis block has special properties:
        - Index: 0
        - Previous hash: "0" (no previous block exists)
        - Contains a single genesis transaction from System
        - Timestamp: Current time when blockchain is created

        The genesis block is mined using Proof of Work.

        Returns:
            Block: The genesis block
        """
        genesis_tx = Transaction("System", "Genesis", 0)
        genesis = Block(0, time.time(), [genesis_tx], "0", self.difficulty)
        genesis.mine_block()
        return genesis

    def get_latest_block(self):
        """
        Get the most recent block in the chain.

        Returns:
            Block: The last block in the chain
        """
        return self.chain[-1]

    def adjust_difficulty(self):
        """
        Adjust difficulty based on recent mining times.

        Only adjusts at specified intervals. Increases difficulty if blocks
        are mined too quickly, decreases if too slowly.

        Returns:
            int: New difficulty level
        """
        # Only adjust at intervals
        if len(self.chain) % self.adjustment_interval != 0:
            return self.difficulty

        # Need enough blocks to calculate average
        if len(self.chain) < self.adjustment_interval:
            return self.difficulty

        # Get recent blocks
        recent_blocks = self.chain[-self.adjustment_interval:]

        # Calculate individual block times
        block_times = []
        for i in range(1, len(recent_blocks)):
            time_diff = recent_blocks[i].timestamp - recent_blocks[i - 1].timestamp
            block_times.append(time_diff)

        # Calculate average block time
        avg_block_time = sum(block_times) / len(block_times)

        # Calculate adjustment factor
        adjustment_factor = avg_block_time / self.target_block_time

        print(f"\n--- Difficulty Adjustment ---")
        print(f"Target block time: {self.target_block_time}s")
        print(f"Actual avg time: {avg_block_time:.2f}s")
        print(f"Adjustment factor: {adjustment_factor:.2f}")

        # Gradual adjustment with bounds
        MIN_DIFFICULTY = 1
        MAX_DIFFICULTY = 8

        if adjustment_factor < 0.75:
            # Too fast, increase difficulty
            new_difficulty = min(MAX_DIFFICULTY, self.difficulty + 1)
            print(f"⬆️ Increasing: {self.difficulty} → {new_difficulty}")
        elif adjustment_factor > 1.5:
            # Too slow, decrease difficulty
            new_difficulty = max(MIN_DIFFICULTY, self.difficulty - 1)
            print(f"⬇️ Decreasing: {self.difficulty} → {new_difficulty}")
        else:
            # Acceptable range
            new_difficulty = self.difficulty
            print(f"✓ Maintaining: {self.difficulty}")

        print(f"----------------------------\n")

        return new_difficulty

    def add_block(self, data):
        """
        Add a new block to the blockchain with dynamic difficulty adjustment.

        Creates a new block with the provided data and appends it to the chain.
        The new block is properly linked to the previous block through its hash
        and is mined using Proof of Work before being added.

        Difficulty is automatically adjusted based on recent mining performance.

        Args:
            data: The data/payload to store in the new block (can be string, dict, list, etc.)

        Returns:
            Block: The newly created and added block
        """
        # Adjust difficulty if needed
        self.difficulty = self.adjust_difficulty()

        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_previous_hash = previous_block.hash

        new_block = Block(new_index, new_timestamp, data, new_previous_hash, self.difficulty)

        # Mine the block before adding to chain
        new_block.mine_block()

        self.chain.append(new_block)

        return new_block

    def create_transaction(self, sender, receiver, amount):
        """
        Create and add a transaction to the pending transaction pool with validation.

        Validates the transaction before adding it to the pool:
        1. Checks transaction is valid (positive amount, different sender/receiver)
        2. Verifies sender has sufficient balance (including pending transactions)

        Args:
            sender (str): Sender address
            receiver (str): Receiver address
            amount (float): Transfer amount

        Returns:
            Transaction: The created transaction

        Raises:
            InvalidTransactionError: If transaction is invalid
            InsufficientBalanceError: If sender has insufficient balance
        """
        logger.debug(f"Creating transaction: {sender} -> {receiver}: {amount}")

        try:
            # Create transaction (will validate inputs)
            transaction = Transaction(sender, receiver, amount)

            # Validate transaction structure
            is_valid, error_msg = transaction.is_valid()
            if not is_valid:
                logger.warning(f"Transaction rejected: {error_msg}")
                raise InvalidTransactionError(f"Invalid transaction: {error_msg}")

            # Check sender balance (including pending transactions)
            current_balance = self.get_balance(sender, include_pending=True)

            # System can create transactions without balance check
            if sender != "System" and current_balance < amount:
                error_msg = (
                    f"Insufficient balance for {sender}. "
                    f"Available: {current_balance}, Required: {amount}"
                )
                logger.warning(f"Transaction rejected: {error_msg}")
                raise InsufficientBalanceError(error_msg)

            self.pending_transactions.append(transaction)
            logger.info(f"Transaction accepted and added to pool: {transaction}")
            print(f"Transaction added: {transaction}")
            return transaction

        except (InvalidTransactionError, InsufficientBalanceError):
            raise
        except Exception as e:
            logger.error(f"Transaction creation failed: {e}")
            raise BlockchainError(f"Transaction creation failed: {e}") from e

    def mine_pending_transactions(self, miner_address):
        """
        Mine a new block with all pending transactions.

        Creates a block containing all pending transactions plus a mining
        reward transaction. After mining, clears the pending transaction pool.

        Args:
            miner_address (str): Address to receive the mining reward

        Returns:
            Block: The newly mined block, or None if no transactions to mine

        Raises:
            MiningError: If mining fails
            ValidationError: If miner address is invalid
        """
        logger.info(f"Mining requested by {miner_address}")

        if not self.pending_transactions:
            logger.warning("No transactions to mine")
            print("No transactions to mine")
            return None

        if not miner_address:
            logger.error("Miner address cannot be empty")
            raise ValidationError("Miner address cannot be empty")

        try:
            # Adjust difficulty if needed
            old_difficulty = self.difficulty
            self.difficulty = self.adjust_difficulty()

            if old_difficulty != self.difficulty:
                logger.info(f"Difficulty adjusted: {old_difficulty} -> {self.difficulty}")

            # Create mining reward transaction
            reward_tx = Transaction("System", miner_address, self.mining_reward)

            # Create block with pending transactions + reward
            block_transactions = self.pending_transactions + [reward_tx]
            logger.debug(f"Creating block with {len(block_transactions)} transactions ({len(self.pending_transactions)} pending + 1 reward)")

            previous_block = self.get_latest_block()
            new_block = Block(
                previous_block.index + 1,
                time.time(),
                block_transactions,
                previous_block.hash,
                self.difficulty
            )

            # Mine the block
            mining_time = new_block.mine_block()
            self.chain.append(new_block)

            # Clear pending transactions
            self.pending_transactions = []

            logger.info(
                f"Block {new_block.index} mined successfully in {mining_time:.2f}s. "
                f"Reward ({self.mining_reward}) sent to {miner_address}"
            )

            print(f"Block mined! Reward sent to {miner_address}")
            return new_block

        except ValidationError:
            raise
        except Exception as e:
            logger.critical(f"Mining failed: {e}")
            raise MiningError(f"Mining failed: {e}") from e

    def get_balance(self, address, include_pending=False):
        """
        Calculate the balance for a given address.

        Iterates through all blocks and transactions to calculate
        the current balance by summing all incoming and outgoing amounts.
        Optionally includes pending transactions.

        Args:
            address (str): Address to check balance for
            include_pending (bool): If True, include pending transactions (default: False)

        Returns:
            float: Current balance of the address
        """
        # Start with initial balance if one exists
        balance = self.initial_balances.get(address, 0)

        # Go through all blocks
        for block in self.chain:
            # Only process transaction-based blocks
            if block.transactions is not None:
                for transaction in block.transactions:
                    if transaction.sender == address:
                        balance -= transaction.amount
                    if transaction.receiver == address:
                        balance += transaction.amount

        # Include pending transactions if requested
        if include_pending:
            for transaction in self.pending_transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.receiver == address:
                    balance += transaction.amount

        return balance

    def validate_block_transactions(self, block):
        """
        Validate all transactions in a block.

        Checks each transaction for:
        1. Transaction structure validity (positive amount, different sender/receiver)
        2. Transaction hash integrity
        3. Sender balance sufficiency (reconstructed at block position)

        Args:
            block (Block): Block to validate

        Returns:
            tuple: (is_valid, error_message)
                - is_valid (bool): True if all transactions are valid
                - error_message (str): Error description if invalid, None if valid
        """
        if block.transactions is None:
            # Legacy data block, no transaction validation needed
            return True, None

        # Build balance state up to this block
        balances = dict(self.initial_balances)

        # Get block index in chain
        try:
            block_index = self.chain.index(block)
        except ValueError:
            return False, "Block not in chain"

        # Reconstruct balances from genesis to block before this one
        for i in range(block_index):
            current_block = self.chain[i]
            if current_block.transactions is not None:
                for tx in current_block.transactions:
                    balances[tx.sender] = balances.get(tx.sender, 0) - tx.amount
                    balances[tx.receiver] = balances.get(tx.receiver, 0) + tx.amount

        # Validate each transaction in the block
        for tx in block.transactions:
            # Check transaction structure
            is_valid, error_msg = tx.is_valid()
            if not is_valid:
                return False, f"Invalid transaction structure: {error_msg}"

            # Check transaction hash
            if tx.transaction_id != tx.calculate_hash():
                return False, f"Transaction hash mismatch for {tx.transaction_id}"

            # Check balance (System can send without balance)
            if tx.sender != "System":
                sender_balance = balances.get(tx.sender, 0)
                if sender_balance < tx.amount:
                    return False, f"Insufficient balance: {tx.sender} has {sender_balance}, trying to send {tx.amount}"

            # Update balances for next transaction
            balances[tx.sender] = balances.get(tx.sender, 0) - tx.amount
            balances[tx.receiver] = balances.get(tx.receiver, 0) + tx.amount

        return True, None

    def get_transaction_history(self, address):
        """
        Get all transactions involving a specific address.

        Args:
            address (str): Address to get transaction history for

        Returns:
            list: List of dictionaries containing transaction details
        """
        history = []

        for block in self.chain:
            # Only process transaction-based blocks
            if block.transactions is not None:
                for transaction in block.transactions:
                    if transaction.sender == address or transaction.receiver == address:
                        history.append({
                            'block': block.index,
                            'transaction': transaction,
                            'timestamp': transaction.timestamp
                        })

        return history

    def is_chain_valid(self, verbose=False):
        """
        Validate the entire blockchain.

        Checks five key aspects:
        1. Genesis block has previous_hash == "0" and valid hash
        2. Each block's stored hash matches its calculated hash
        3. Each block's previous_hash matches the previous block's hash
        4. Each block meets Proof of Work requirements (hash starts with required zeros)
        5. All transactions in each block are valid (structure, balance, hash integrity)

        Args:
            verbose (bool): If True, print detailed validation info

        Returns:
            bool: True if chain is valid, False otherwise
        """
        logger.info(f"Starting blockchain validation ({len(self.chain)} blocks)")

        try:
            for i in range(len(self.chain)):
                current_block = self.chain[i]

                # Check hash integrity
                calculated_hash = current_block.calculate_hash()
                if current_block.hash != calculated_hash:
                    error_msg = f"Block {i}: Hash mismatch"
                    logger.error(error_msg)
                    logger.debug(f"Stored: {current_block.hash}")
                    logger.debug(f"Calculated: {calculated_hash}")
                    if verbose:
                        print(f"[X] {error_msg}")
                        print(f"   Stored: {current_block.hash}")
                        print(f"   Calculated: {calculated_hash}")
                    return False

                # Check Proof of Work (hash starts with required zeros)
                target = "0" * current_block.difficulty
                if current_block.hash[:current_block.difficulty] != target:
                    error_msg = f"Block {i}: Invalid PoW (difficulty {current_block.difficulty})"
                    logger.error(error_msg)
                    if verbose:
                        print(f"[X] {error_msg}")
                        print(f"   Expected: {target}...")
                        print(f"   Got: {current_block.hash[:current_block.difficulty]}...")
                    return False

                # Check chain continuity
                if i == 0:
                    # Genesis block validation
                    if current_block.previous_hash != "0":
                        error_msg = "Genesis block invalid: previous_hash != '0'"
                        logger.error(error_msg)
                        if verbose:
                            print(f"[X] {error_msg}")
                        return False
                else:
                    # Regular block validation
                    previous_block = self.chain[i - 1]
                    if current_block.previous_hash != previous_block.hash:
                        error_msg = f"Block {i}: Broken chain link"
                        logger.error(error_msg)
                        logger.debug(f"Expected: {previous_block.hash}")
                        logger.debug(f"Got: {current_block.previous_hash}")
                        if verbose:
                            print(f"[X] {error_msg}")
                            print(f"   previous_hash: {current_block.previous_hash}")
                            print(f"   Previous block hash: {previous_block.hash}")
                        return False

                # Validate transactions in block
                tx_valid, tx_error = self.validate_block_transactions(current_block)
                if not tx_valid:
                    logger.error(f"Block {i}: {tx_error}")
                    if verbose:
                        print(f"[X] Block {i} transaction validation failed")
                        print(f"   Error: {tx_error}")
                    return False

                logger.debug(f"Block {i} validated successfully")
                if verbose:
                    print(f"[OK] Block {i} valid (Nonce: {current_block.nonce})")

            logger.info("Blockchain validation completed successfully")
            return True

        except Exception as e:
            logger.critical(f"Blockchain validation failed with error: {e}")
            return False

    def get_mining_stats(self):
        """
        Get statistics about mining performance.

        Returns:
            dict: Mining statistics including block times, difficulties, and performance
            None: If not enough blocks for statistics
        """
        if len(self.chain) < 2:
            return None

        block_times = []
        difficulties = []

        for i in range(1, len(self.chain)):
            time_diff = self.chain[i].timestamp - self.chain[i - 1].timestamp
            block_times.append(time_diff)
            difficulties.append(self.chain[i].difficulty)

        return {
            'total_blocks': len(self.chain),
            'avg_block_time': sum(block_times) / len(block_times),
            'min_block_time': min(block_times),
            'max_block_time': max(block_times),
            'current_difficulty': self.difficulty,
            'avg_difficulty': sum(difficulties) / len(difficulties),
            'target_block_time': self.target_block_time
        }

    def print_mining_stats(self):
        """Print formatted mining statistics."""
        stats = self.get_mining_stats()

        if not stats:
            print("Not enough blocks for statistics")
            return

        print("\n=== Mining Statistics ===")
        print(f"Total blocks: {stats['total_blocks']}")
        print(f"Current difficulty: {stats['current_difficulty']}")
        print(f"Average difficulty: {stats['avg_difficulty']:.2f}")
        print(f"Target block time: {stats['target_block_time']}s")
        print(f"Average block time: {stats['avg_block_time']:.2f}s")
        print(f"Min block time: {stats['min_block_time']:.2f}s")
        print(f"Max block time: {stats['max_block_time']:.2f}s")

        # Performance indicator
        ratio = stats['avg_block_time'] / stats['target_block_time']
        if 0.8 <= ratio <= 1.2:
            print("✅ Performance: On target")
        elif ratio < 0.8:
            print("⚡ Performance: Mining too fast")
        else:
            print("🐌 Performance: Mining too slow")

        print("========================\n")

    def print_blockchain(self):
        """Print a formatted view of the entire blockchain."""
        print("\n" + "=" * 60)
        print("BLOCKCHAIN")
        print("=" * 60)

        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print(f"Hash: {block.hash[:32]}...")
            print(f"Previous: {block.previous_hash[:32]}...")
            print(f"Nonce: {block.nonce}")
            print(f"Difficulty: {block.difficulty}")

            # Display transactions or legacy data
            if block.transactions is not None:
                print(f"Transactions ({len(block.transactions)}):")
                for tx in block.transactions:
                    print(f"  • {tx.sender} → {tx.receiver}: {tx.amount}")
            else:
                print(f"Data: {block.data}")

        print("\n" + "=" * 60)

    def print_balances(self, addresses):
        """
        Print balances for multiple addresses.

        Args:
            addresses (list): List of addresses to display balances for
        """
        print("\n" + "=" * 40)
        print("ACCOUNT BALANCES")
        print("=" * 40)

        for address in addresses:
            balance = self.get_balance(address)
            print(f"{address:20s}: {balance:10.2f}")

        print("=" * 40 + "\n")

    def to_dict(self):
        """
        Convert blockchain to dictionary format.

        Returns:
            dict: Dictionary representation of blockchain with all data
        """
        return {
            'difficulty': self.difficulty,
            'target_block_time': self.target_block_time,
            'adjustment_interval': self.adjustment_interval,
            'mining_reward': self.mining_reward,
            'initial_balances': self.initial_balances,
            'blocks': [
                {
                    'index': block.index,
                    'timestamp': block.timestamp,
                    'previous_hash': block.previous_hash,
                    'hash': block.hash,
                    'nonce': block.nonce,
                    'difficulty': block.difficulty,
                    'transactions': [
                        {
                            'sender': tx.sender,
                            'receiver': tx.receiver,
                            'amount': tx.amount,
                            'timestamp': tx.timestamp,
                            'transaction_id': tx.transaction_id
                        } for tx in block.transactions
                    ] if block.transactions is not None else None,
                    'data': block.data
                } for block in self.chain
            ],
            'pending_transactions': [
                {
                    'sender': tx.sender,
                    'receiver': tx.receiver,
                    'amount': tx.amount,
                    'timestamp': tx.timestamp,
                    'transaction_id': tx.transaction_id
                } for tx in self.pending_transactions
            ]
        }

    def to_json(self, indent=2):
        """
        Convert blockchain to JSON string.

        Args:
            indent (int): Number of spaces for indentation (default: 2)

        Returns:
            str: JSON string representation of blockchain
        """
        return json.dumps(self.to_dict(), indent=indent)

    def export_to_file(self, filename):
        """
        Export blockchain to JSON file.

        Args:
            filename (str): Path to file to write

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ImportExportError: If export fails
        """
        logger.info(f"Exporting blockchain to {filename}")

        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)

            logger.info(f"Blockchain exported successfully to {filename} ({len(self.chain)} blocks)")
            return True

        except IOError as e:
            logger.error(f"File I/O error during export: {e}")
            print(f"Error exporting to file: {e}")
            return False
        except Exception as e:
            logger.error(f"Export failed: {e}")
            print(f"Error exporting to file: {e}")
            return False

    @classmethod
    def import_from_file(cls, filename):
        """
        Import blockchain from JSON file.

        Args:
            filename (str): Path to file to read

        Returns:
            Blockchain: Reconstructed blockchain instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ImportExportError: If file format is invalid or import fails
        """
        logger.info(f"Importing blockchain from {filename}")

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            logger.debug(f"JSON loaded, creating blockchain instance")

            # Create blockchain with saved parameters
            blockchain = cls(
                difficulty=data.get('difficulty', 2),
                target_block_time=data.get('target_block_time', 10),
                adjustment_interval=data.get('adjustment_interval', 5),
                initial_balances=data.get('initial_balances', {})
            )

            # Clear genesis block (will be replaced with imported blocks)
            blockchain.chain = []

            # Reconstruct blocks
            logger.debug(f"Reconstructing {len(data.get('blocks', []))} blocks")
            for block_data in data.get('blocks', []):
                # Reconstruct transactions
                transactions = None
                if block_data.get('transactions') is not None:
                    transactions = []
                    for tx_data in block_data['transactions']:
                        tx = Transaction(
                            tx_data['sender'],
                            tx_data['receiver'],
                            tx_data['amount']
                        )
                        tx.timestamp = tx_data['timestamp']
                        tx.transaction_id = tx_data['transaction_id']
                        transactions.append(tx)

                # Reconstruct block
                block = Block(
                    block_data['index'],
                    block_data['timestamp'],
                    transactions if transactions is not None else block_data.get('data'),
                    block_data['previous_hash'],
                    block_data['difficulty']
                )
                block.hash = block_data['hash']
                block.nonce = block_data['nonce']

                blockchain.chain.append(block)

            # Reconstruct pending transactions
            blockchain.pending_transactions = []
            pending_count = len(data.get('pending_transactions', []))
            logger.debug(f"Reconstructing {pending_count} pending transactions")

            for tx_data in data.get('pending_transactions', []):
                tx = Transaction(
                    tx_data['sender'],
                    tx_data['receiver'],
                    tx_data['amount']
                )
                tx.timestamp = tx_data['timestamp']
                tx.transaction_id = tx_data['transaction_id']
                blockchain.pending_transactions.append(tx)

            # Set mining reward
            blockchain.mining_reward = data.get('mining_reward', 10)

            logger.info(
                f"Blockchain imported successfully from {filename} "
                f"({len(blockchain.chain)} blocks, {pending_count} pending transactions)"
            )

            return blockchain

        except FileNotFoundError as e:
            logger.error(f"File not found: {filename}")
            raise FileNotFoundError(f"File not found: {filename}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            raise ImportExportError(f"Invalid JSON format: {e}") from e
        except KeyError as e:
            logger.error(f"Missing required field in blockchain data: {e}")
            raise ImportExportError(f"Invalid blockchain file format - missing field: {e}") from e
        except Exception as e:
            logger.critical(f"Import failed: {e}")
            raise ImportExportError(f"Error importing blockchain: {e}") from e

    def print_summary(self):
        """
        Print a summary of the blockchain state.

        Displays:
        - Total blocks, difficulty, pending transactions
        - Mining statistics if available
        - Chain validation status
        """
        print("\n" + "=" * 60)
        print("BLOCKCHAIN SUMMARY")
        print("=" * 60)

        print(f"\nChain Information:")
        print(f"  Total Blocks: {len(self.chain)}")
        print(f"  Current Difficulty: {self.difficulty}")
        print(f"  Target Block Time: {self.target_block_time}s")
        print(f"  Adjustment Interval: Every {self.adjustment_interval} blocks")
        print(f"  Mining Reward: {self.mining_reward}")
        print(f"  Pending Transactions: {len(self.pending_transactions)}")

        # Mining stats
        stats = self.get_mining_stats()
        if stats:
            print(f"\nMining Performance:")
            print(f"  Average Block Time: {stats['avg_block_time']:.2f}s")
            print(f"  Average Difficulty: {stats['avg_difficulty']:.2f}")

            ratio = stats['avg_block_time'] / stats['target_block_time']
            if 0.8 <= ratio <= 1.2:
                status = "On Target"
            elif ratio < 0.8:
                status = "Too Fast"
            else:
                status = "Too Slow"
            print(f"  Status: {status}")

        # Validation
        is_valid = self.is_chain_valid()
        print(f"\nChain Validation: {'[VALID]' if is_valid else '[INVALID]'}")

        # Initial balances
        if self.initial_balances:
            print(f"\nInitial Balances:")
            for address, balance in self.initial_balances.items():
                print(f"  {address}: {balance}")

        print("=" * 60 + "\n")

    def print_transaction_details(self, block_index):
        """
        Print detailed transaction information for a specific block.

        Args:
            block_index (int): Index of the block to display

        Returns:
            bool: True if successful, False if block doesn't exist
        """
        if block_index < 0 or block_index >= len(self.chain):
            print(f"Error: Block {block_index} does not exist")
            return False

        block = self.chain[block_index]

        print("\n" + "=" * 60)
        print(f"BLOCK #{block.index} TRANSACTION DETAILS")
        print("=" * 60)

        print(f"\nBlock Information:")
        print(f"  Timestamp: {time.ctime(block.timestamp)}")
        print(f"  Hash: {block.hash}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Nonce: {block.nonce}")
        print(f"  Difficulty: {block.difficulty}")

        if block.transactions is not None:
            print(f"\nTransactions ({len(block.transactions)}):")
            print("-" * 60)

            total_amount = 0
            for i, tx in enumerate(block.transactions, 1):
                print(f"\n  Transaction {i}:")
                print(f"    ID: {tx.transaction_id}")
                print(f"    From: {tx.sender}")
                print(f"    To: {tx.receiver}")
                print(f"    Amount: {tx.amount}")
                print(f"    Timestamp: {time.ctime(tx.timestamp)}")

                # Validate transaction
                is_valid, error_msg = tx.is_valid()
                print(f"    Status: {'[VALID]' if is_valid else f'[INVALID: {error_msg}]'}")

                total_amount += tx.amount

            print("\n" + "-" * 60)
            print(f"Total Transaction Volume: {total_amount}")

        elif block.data is not None:
            print(f"\nLegacy Data Block:")
            print(f"  Data: {block.data}")

        print("\n" + "=" * 60 + "\n")
        return True
