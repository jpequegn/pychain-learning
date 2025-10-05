# PyChain - Educational Blockchain Implementation

A simple blockchain implementation in Python for learning blockchain concepts.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Blockchain Concepts](#blockchain-concepts)
- [API Reference](#api-reference)
- [Development](#development)
- [Testing](#testing)
- [CLI Reference](#cli-reference)
- [Contributing](#contributing)
- [Learning Resources](#learning-resources)
- [License](#license)

## Features

- ✅ **Block Creation**: SHA-256 hashing and chain linking
- ✅ **Proof of Work**: Configurable difficulty mining
- ✅ **Dynamic Difficulty**: Auto-adjustment based on mining time
- ✅ **Transactions**: Full transaction system with validation
- ✅ **Balance Tracking**: Account balance management with initial balances
- ✅ **Chain Validation**: Comprehensive integrity verification
- ✅ **CLI Interface**: User-friendly command-line tools
- ✅ **Import/Export**: JSON serialization and deserialization
- ✅ **Pretty-Print**: Human-readable blockchain display

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jpequegn/pychain-learning.git
cd pychain-learning
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. No external dependencies required - uses Python standard library only!

## Quick Start

### Basic Usage (Python API)

```python
from pychain.blockchain import Blockchain

# Create a new blockchain with difficulty 2
blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

# Create transactions
blockchain.create_transaction("Alice", "Bob", 30)
blockchain.create_transaction("Bob", "Charlie", 15)

# Mine pending transactions
blockchain.mine_pending_transactions("Miner1")

# Check balances
print(f"Alice: {blockchain.get_balance('Alice')}")      # 70
print(f"Bob: {blockchain.get_balance('Bob')}")          # 65 (50 + 30 - 15)
print(f"Charlie: {blockchain.get_balance('Charlie')}")  # 15
print(f"Miner1: {blockchain.get_balance('Miner1')}")    # 10 (mining reward)

# Validate blockchain
print(f"Valid: {blockchain.is_chain_valid()}")  # True
```

### CLI Usage

```bash
# Initialize accounts
python cli.py init-balance Alice 100
python cli.py init-balance Bob 50

# Create transactions
python cli.py transaction Alice Bob 30

# Mine blocks
python cli.py mine Miner1

# View blockchain
python cli.py view

# Check balance
python cli.py balance Alice

# Validate chain
python cli.py validate

# Export blockchain
python cli.py export my_blockchain.json

# View summary
python cli.py summary
```

## Usage Examples

### Example 1: Simple Transaction

```python
from pychain.blockchain import Blockchain

# Create blockchain with initial balances
blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

# Create and mine transaction
blockchain.create_transaction("Alice", "Bob", 50)
blockchain.mine_pending_transactions("Miner1")

# View results
blockchain.print_blockchain()
```

### Example 2: Multiple Transactions in One Block

```python
from pychain.blockchain import Blockchain

# Set up accounts
blockchain = Blockchain(difficulty=2, initial_balances={
    "Alice": 200,
    "Bob": 100
})

# Create multiple transactions
blockchain.create_transaction("Alice", "Bob", 50)
blockchain.create_transaction("Alice", "Charlie", 30)
blockchain.create_transaction("Bob", "Charlie", 20)

# Mine all pending transactions in one block
blockchain.mine_pending_transactions("Miner1")

# Check final balances
print(f"Alice: {blockchain.get_balance('Alice')}")      # 120 (200 - 50 - 30)
print(f"Bob: {blockchain.get_balance('Bob')}")          # 130 (100 + 50 - 20)
print(f"Charlie: {blockchain.get_balance('Charlie')}")  # 50 (30 + 20)
print(f"Miner1: {blockchain.get_balance('Miner1')}")    # 10 (reward)
```

### Example 3: Export and Import

```python
from pychain.blockchain import Blockchain

# Create and populate blockchain
blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})
blockchain.create_transaction("Alice", "Bob", 50)
blockchain.mine_pending_transactions("Miner1")

# Export to JSON
blockchain.export_to_file("my_blockchain.json")

# Import later
loaded_blockchain = Blockchain.import_from_file("my_blockchain.json")

# Verify integrity
assert loaded_blockchain.is_chain_valid()
print("Blockchain imported successfully and is valid!")
```

### Example 4: Transaction Validation

```python
from pychain.blockchain import Blockchain

# Create blockchain
blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

# This will succeed
blockchain.create_transaction("Alice", "Bob", 50)

# This will fail - insufficient balance
try:
    blockchain.create_transaction("Alice", "Charlie", 200)
except ValueError as e:
    print(f"Transaction failed: {e}")
    # Output: Transaction failed: Insufficient balance: Alice has 50, but trying to send 200
```

### Example 5: Mining with Different Difficulties

```python
from pychain.blockchain import Blockchain
import time

# Test different difficulties
for difficulty in [1, 2, 3, 4]:
    blockchain = Blockchain(difficulty=difficulty, initial_balances={"Alice": 100})
    blockchain.create_transaction("Alice", "Bob", 50)

    start = time.time()
    blockchain.mine_pending_transactions("Miner1")
    elapsed = time.time() - start

    print(f"Difficulty {difficulty}: {elapsed:.3f}s")
```

## Blockchain Concepts

### What is a Blockchain?

A blockchain is a distributed ledger that stores data in blocks linked together using cryptographic hashes. Each block contains:
- **Index**: Position in the chain (0 for genesis block)
- **Timestamp**: When the block was created (Unix timestamp)
- **Transactions**: List of transactions or data stored in the block
- **Previous Hash**: Link to the previous block (creates the "chain")
- **Hash**: Unique identifier calculated from all block contents
- **Nonce**: Number used in Proof of Work mining
- **Difficulty**: Mining difficulty for this block

### How Hashing Works

Hashing converts data into a fixed-length string using SHA-256:
- **Deterministic**: Same input always produces same output
- **Avalanche Effect**: Changing any input bit completely changes output
- **One-Way**: Cannot reverse hash to get original data
- **Collision-Resistant**: Extremely hard to find two inputs with same hash
- **Fixed Length**: Always 64 hexadecimal characters (256 bits)

Example:
```
Input: "Hello"
SHA-256: 185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969

Input: "Hello!" (just added exclamation mark)
SHA-256: 334d016f755cd6dc58c53a86e183882f8ec14f52fb05345887c8a5edd42c87b7
```

### Proof of Work (PoW)

Mining requires finding a nonce that produces a hash meeting difficulty requirements:
- **Difficulty 1**: Hash starts with 1 zero (e.g., `0abc123...`)
- **Difficulty 2**: Hash starts with 2 zeros (e.g., `00abc123...`)
- **Difficulty 3**: Hash starts with 3 zeros (e.g., `000abc123...`)
- Higher difficulty = exponentially more computation required = more secure

The miner tries different nonce values until finding one that produces a valid hash:
```python
nonce = 0
while True:
    hash = calculate_hash(data + nonce)
    if hash.startswith("0" * difficulty):
        break  # Found valid hash!
    nonce += 1
```

### Chain Validation

The blockchain validates four key aspects:

1. **Hash Integrity**: Each block's stored hash matches its calculated hash
2. **Chain Continuity**: Each block's previous_hash matches the previous block's hash
3. **Proof of Work**: Each block's hash meets the difficulty requirement
4. **Transaction Validity**: All transactions have sufficient balance and valid structure

If any block is tampered with, its hash changes, which breaks the chain link and makes validation fail.

### Transaction System

Transactions represent value transfers between addresses:
- Each transaction has **sender**, **receiver**, **amount**, and **timestamp**
- Transactions are validated before being accepted into the pending pool
- **Balances** are tracked by summing all transactions for each address
- **Miners** receive rewards for successfully mining blocks
- **Initial balances** can be set for starting accounts

### Dynamic Difficulty Adjustment

The blockchain automatically adjusts mining difficulty to maintain target block time:
- **Target Block Time**: Desired time between blocks (default: 10 seconds)
- **Adjustment Interval**: How often to adjust (default: every 5 blocks)
- If blocks are mined too quickly → increase difficulty
- If blocks are mined too slowly → decrease difficulty
- Keeps mining sustainable regardless of computational power

## API Reference

### Block Class

```python
from pychain.block import Block

Block(index, timestamp, transactions, previous_hash, difficulty=2)
```

**Parameters:**
- `index` (int): Position of block in chain
- `timestamp` (float): Unix timestamp
- `transactions` (list): List of Transaction objects or data
- `previous_hash` (str): Hash of previous block
- `difficulty` (int): Mining difficulty (default: 2)

**Methods:**
- `calculate_hash()` → str: Calculate SHA-256 hash of block
- `mine_block()` → float: Perform Proof of Work, returns mining time
- `get_transaction_count()` → int: Number of transactions in block
- `get_total_amount()` → float: Total transaction volume

**Attributes:**
- `hash` (str): Block's SHA-256 hash
- `nonce` (int): Proof of Work nonce value

### Transaction Class

```python
from pychain.transaction import Transaction

Transaction(sender, receiver, amount, timestamp=None)
```

**Parameters:**
- `sender` (str): Sender address
- `receiver` (str): Receiver address
- `amount` (float): Transfer amount
- `timestamp` (float, optional): Unix timestamp (auto-generated if None)

**Methods:**
- `calculate_hash()` → str: Calculate transaction ID
- `is_valid()` → tuple: Returns (bool, str) - validity status and error message
- `to_dict()` → dict: Convert to dictionary

**Attributes:**
- `transaction_id` (str): Unique transaction identifier (SHA-256 hash)

### Blockchain Class

```python
from pychain.blockchain import Blockchain

Blockchain(difficulty=2, target_block_time=10, adjustment_interval=5, initial_balances=None)
```

**Parameters:**
- `difficulty` (int): Initial mining difficulty (default: 2)
- `target_block_time` (float): Target seconds between blocks (default: 10)
- `adjustment_interval` (int): Blocks between difficulty adjustments (default: 5)
- `initial_balances` (dict): Starting balances {address: amount} (default: None)

**Transaction Methods:**
- `create_transaction(sender, receiver, amount)` → Transaction: Create and validate transaction
- `mine_pending_transactions(miner_address)` → Block: Mine pending transactions into block
- `get_balance(address, include_pending=False)` → float: Get account balance
- `get_transaction_history(address)` → list: Get all transactions for address

**Validation Methods:**
- `is_chain_valid(verbose=False)` → bool: Validate entire blockchain
- `validate_block_transactions(block)` → tuple: Validate block's transactions

**Export/Import Methods:**
- `to_dict()` → dict: Convert blockchain to dictionary
- `to_json(indent=2)` → str: Convert to JSON string
- `export_to_file(filename)` → bool: Export to JSON file
- `import_from_file(filename)` → Blockchain: Import from JSON file (class method)

**Display Methods:**
- `print_blockchain()`: Display entire chain
- `print_summary()`: Display blockchain summary with stats
- `print_transaction_details(block_index)` → bool: Display block details
- `print_balances(addresses)`: Display balances for addresses

**Statistics Methods:**
- `get_mining_stats()` → dict: Get mining performance statistics
- `print_mining_stats()`: Display mining statistics

**Block Methods:**
- `add_block(data)` → Block: Add legacy data block (for backward compatibility)
- `get_latest_block()` → Block: Get most recent block
- `adjust_difficulty()` → int: Adjust and return new difficulty

**Attributes:**
- `chain` (list): List of Block objects
- `pending_transactions` (list): Transactions waiting to be mined
- `mining_reward` (float): Reward for mining (default: 10)

## Development

### Project Structure

```
pychain-learning/
├── pychain/              # Main package
│   ├── __init__.py
│   ├── block.py          # Block class implementation
│   ├── transaction.py    # Transaction class implementation
│   └── blockchain.py     # Blockchain class implementation
├── tests/                # Test suite
│   ├── test_block.py
│   ├── test_transaction.py
│   ├── test_blockchain.py
│   ├── test_proof_of_work.py
│   ├── test_difficulty_adjustment.py
│   ├── test_blockchain_transactions.py
│   ├── test_transaction_validation.py
│   ├── test_export_import.py
│   ├── test_pretty_print.py
│   ├── test_cli.py
│   └── test_cli_export.py
├── cli.py                # Command-line interface
├── README.md             # This file
├── CLI_README.md         # CLI documentation
└── CLAUDE.md             # Claude Code instructions
```

### Code Style

This project follows PEP 8 Python style guidelines. All code includes:
- Comprehensive docstrings with examples
- Type hints where beneficial
- Inline comments for complex logic
- Descriptive variable and function names
- Consistent formatting and indentation

### Running the Code

**Python API:**
```python
from pychain.blockchain import Blockchain

blockchain = Blockchain(difficulty=2)
# ... use blockchain ...
```

**CLI:**
```bash
python cli.py <command> [arguments]
```

See [CLI_README.md](CLI_README.md) for complete CLI documentation.

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_blockchain.py -v

# Run with coverage
python -m pytest tests/ --cov=pychain --cov-report=html

# Run specific test
python -m pytest tests/test_blockchain.py::TestBlockchain::test_valid_chain_returns_true -v
```

### Test Coverage

Current test coverage: **241 tests passing**

Test categories:
- Block tests (20 tests)
- Blockchain tests (60 tests)
- Transaction tests (20 tests)
- Proof of Work tests (18 tests)
- Difficulty adjustment tests (18 tests)
- Transaction validation tests (23 tests)
- Blockchain transactions tests (25 tests)
- Export/import tests (19 tests)
- Pretty-print tests (19 tests)
- CLI tests (26 tests)
- CLI export tests (17 tests)

### Test Organization

Tests are organized by functionality:
- `test_block.py` - Block creation and hashing
- `test_blockchain.py` - Basic blockchain operations
- `test_transaction.py` - Transaction creation and validation
- `test_proof_of_work.py` - Mining and PoW validation
- `test_difficulty_adjustment.py` - Dynamic difficulty
- `test_blockchain_transactions.py` - Transaction system integration
- `test_transaction_validation.py` - Transaction validation logic
- `test_export_import.py` - JSON serialization
- `test_pretty_print.py` - Display methods
- `test_cli.py` - CLI commands
- `test_cli_export.py` - CLI export/import/summary commands

## CLI Reference

See [CLI_README.md](CLI_README.md) for complete CLI documentation.

Quick command reference:

| Command | Description | Example |
|---------|-------------|---------|
| `init-balance` | Set initial balance | `python cli.py init-balance Alice 100` |
| `transaction` | Create transaction | `python cli.py transaction Alice Bob 50` |
| `mine` | Mine pending transactions | `python cli.py mine Miner1` |
| `view` | View blockchain | `python cli.py view --detail` |
| `balance` | Check balance | `python cli.py balance Alice --pending` |
| `history` | View transaction history | `python cli.py history Alice` |
| `validate` | Validate chain | `python cli.py validate --verbose` |
| `stats` | Show mining stats | `python cli.py stats` |
| `pending` | View pending transactions | `python cli.py pending` |
| `export` | Export to JSON | `python cli.py export blockchain.json` |
| `import` | Import from JSON | `python cli.py import blockchain.json` |
| `summary` | Show summary | `python cli.py summary` |
| `details` | Show block details | `python cli.py details 1` |
| `reset` | Reset blockchain | `python cli.py reset --confirm` |

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`python -m pytest tests/ -v`)
5. Follow PEP 8 style guidelines
6. Add comprehensive docstrings
7. Submit a pull request

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and add tests
# ...

# Run tests
python -m pytest tests/ -v

# Commit changes
git add .
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/my-feature
```

## Learning Resources

### Blockchain Fundamentals
- [Blockchain Basics - Investopedia](https://www.investopedia.com/terms/b/blockchain.asp)
- [How Bitcoin Works - Original Paper](https://bitcoin.org/bitcoin.pdf)
- [Blockchain Demo - Interactive Visualization](https://andersbrownworth.com/blockchain/)

### Cryptography
- [SHA-256 Hash Function - Wikipedia](https://en.wikipedia.org/wiki/SHA-2)
- [Cryptographic Hash Functions Explained](https://www.khanacademy.org/economics-finance-domain/core-finance/money-and-banking/bitcoin/v/bitcoin-cryptographic-hash-function)

### Consensus Mechanisms
- [Proof of Work - Bitcoin Wiki](https://en.bitcoin.it/wiki/Proof_of_work)
- [Mining Difficulty Explained](https://en.bitcoin.it/wiki/Difficulty)

### Python Resources
- [Python Official Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Testing with pytest](https://docs.pytest.org/)

## License

MIT License - feel free to use this code for learning!

## Acknowledgments

This is an educational project for learning blockchain concepts. It is not intended for production use or real cryptocurrency implementation.

**Key Learning Objectives:**
- Understanding blockchain data structures
- Implementing cryptographic hashing
- Learning Proof of Work consensus
- Transaction validation and balance tracking
- Dynamic difficulty adjustment
- Blockchain security principles

---

**Happy Learning! 🚀**

For questions or issues, please open an issue on GitHub.
