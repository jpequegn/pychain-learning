# PyChain CLI - Command-Line Interface

A user-friendly command-line interface for interacting with the PyChain blockchain.

## Installation

No additional dependencies required beyond the base PyChain project.

## Usage

Run commands using:
```bash
python cli.py <command> [arguments]
```

### Available Commands

#### 1. Initialize Account Balance
Set initial balance for an address:
```bash
python cli.py init-balance <address> <amount>
```

Example:
```bash
python cli.py init-balance Alice 100
python cli.py init-balance Bob 50
```

#### 2. Create Transaction
Create a new transaction between addresses:
```bash
python cli.py transaction <sender> <receiver> <amount>
```

Example:
```bash
python cli.py transaction Alice Bob 30
```

#### 3. Mine Blocks
Mine pending transactions and add them to the blockchain:
```bash
python cli.py mine <miner_address>
```

Example:
```bash
python cli.py mine Miner1
```

#### 4. View Blockchain
Display the entire blockchain:
```bash
python cli.py view [--detail]
```

Examples:
```bash
python cli.py view           # Basic view
python cli.py view --detail  # Detailed view with nonces and hashes
```

#### 5. Check Balance
Check the balance of an address:
```bash
python cli.py balance <address> [--pending]
```

Examples:
```bash
python cli.py balance Alice            # Confirmed balance only
python cli.py balance Alice --pending  # Include pending transactions
```

#### 6. View Transaction History
View all transactions for an address:
```bash
python cli.py history <address>
```

Example:
```bash
python cli.py history Alice
```

#### 7. Validate Blockchain
Validate the integrity of the blockchain:
```bash
python cli.py validate [--verbose]
```

Examples:
```bash
python cli.py validate           # Basic validation
python cli.py validate --verbose # Detailed validation output
```

#### 8. Mining Statistics
Display mining performance statistics:
```bash
python cli.py stats
```

#### 9. View Pending Transactions
Display all pending transactions waiting to be mined:
```bash
python cli.py pending
```

#### 10. Reset Blockchain
Reset the blockchain to genesis block (requires confirmation):
```bash
python cli.py reset --confirm
```

## Complete Workflow Example

Here's a complete example workflow:

```bash
# 1. Set up initial balances
python cli.py init-balance Alice 100
python cli.py init-balance Bob 50

# 2. Create some transactions
python cli.py transaction Alice Bob 30
python cli.py transaction Bob Charlie 15

# 3. View pending transactions
python cli.py pending

# 4. Mine the block
python cli.py mine Miner1

# 5. Check balances
python cli.py balance Alice
python cli.py balance Bob
python cli.py balance Charlie
python cli.py balance Miner1

# 6. View the blockchain
python cli.py view

# 7. View transaction history
python cli.py history Alice

# 8. Validate the chain
python cli.py validate

# 9. View mining statistics
python cli.py stats
```

## Features

- **Transaction Validation**: Automatically validates transactions for sufficient balance
- **State Persistence**: Blockchain state is saved to `blockchain_data.json`
- **Error Handling**: Clear error messages for invalid operations
- **Detailed Output**: Optional verbose/detailed views for commands
- **Mining Rewards**: Miners automatically receive rewards for mining blocks
- **Balance Tracking**: Track both confirmed and pending balances

## Output

The CLI provides clear, formatted output with status indicators:
- `[OK]` - Successful operations
- `[ERROR]` - Failed operations
- `[WARNING]` - Warnings and alerts
- `[INFO]` - Informational messages

## Data Persistence

The blockchain state is automatically saved to `blockchain_data.json` after state-modifying operations. This includes:
- Initial balances
- Difficulty settings
- Target block time
- Adjustment interval

## Error Handling

The CLI handles common errors gracefully:
- Insufficient balance for transactions
- Invalid transaction amounts (zero or negative)
- Same sender and receiver
- Validation failures
- Mining with no pending transactions

All errors provide descriptive messages to help users understand what went wrong.
