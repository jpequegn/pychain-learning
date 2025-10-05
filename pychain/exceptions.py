"""
Custom exception classes for PyChain.

This module defines specific exceptions for different blockchain error scenarios,
making error handling more precise and providing better error messages to users.
"""


class BlockchainError(Exception):
    """
    Base exception for all blockchain-related errors.

    All custom PyChain exceptions inherit from this base class,
    making it easy to catch all blockchain-specific errors.

    Example:
        >>> try:
        ...     blockchain.create_transaction("Alice", "Bob", 1000)
        ... except BlockchainError as e:
        ...     print(f"Blockchain error occurred: {e}")
    """
    pass


class InvalidTransactionError(BlockchainError):
    """
    Raised when a transaction is invalid.

    This includes validation failures such as:
    - Invalid sender or receiver
    - Same sender and receiver
    - Invalid amount (zero, negative, or non-numeric)
    - Missing required data

    Example:
        >>> transaction = Transaction("Alice", "Alice", 50)  # Same sender/receiver
        Traceback (most recent call last):
        InvalidTransactionError: Sender and receiver cannot be the same
    """
    pass


class InsufficientBalanceError(BlockchainError):
    """
    Raised when an account has insufficient balance for a transaction.

    This error includes details about:
    - Current balance
    - Required amount
    - Pending transactions affecting available balance

    Example:
        >>> blockchain.create_transaction("Alice", "Bob", 1000)
        Traceback (most recent call last):
        InsufficientBalanceError: Insufficient balance for Alice. Available: 100, Required: 1000
    """
    pass


class InvalidBlockError(BlockchainError):
    """
    Raised when a block is invalid.

    This includes:
    - Invalid hash calculation
    - Failed Proof of Work validation
    - Invalid timestamp
    - Invalid transactions within block

    Example:
        >>> block.hash = "tampered_hash"
        >>> blockchain.is_chain_valid()
        Traceback (most recent call last):
        InvalidBlockError: Block 5: Hash mismatch detected
    """
    pass


class ChainValidationError(BlockchainError):
    """
    Raised when blockchain chain validation fails.

    This includes:
    - Broken chain links (previous_hash mismatch)
    - Invalid genesis block
    - Transaction validation failures
    - Balance inconsistencies

    Example:
        >>> blockchain.chain[5].previous_hash = "wrong_hash"
        >>> blockchain.is_chain_valid()
        Traceback (most recent call last):
        ChainValidationError: Block 5: Broken chain link
    """
    pass


class MiningError(BlockchainError):
    """
    Raised when mining operation fails.

    This includes:
    - No transactions to mine
    - Invalid miner address
    - Mining timeout
    - Difficulty adjustment failures

    Example:
        >>> blockchain.mine_pending_transactions("")
        Traceback (most recent call last):
        MiningError: Miner address cannot be empty
    """
    pass


class ImportExportError(BlockchainError):
    """
    Raised when import or export operations fail.

    This includes:
    - File not found
    - Invalid JSON format
    - Missing required fields
    - Data corruption

    Example:
        >>> blockchain = Blockchain.import_from_file("invalid.json")
        Traceback (most recent call last):
        ImportExportError: Invalid blockchain file format
    """
    pass


class ValidationError(BlockchainError):
    """
    Raised when data validation fails.

    This is a general validation error for cases that don't fit
    more specific exception categories.

    Example:
        >>> blockchain.set_initial_balance("Alice", -100)
        Traceback (most recent call last):
        ValidationError: Balance cannot be negative
    """
    pass
