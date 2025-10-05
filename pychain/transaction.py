import hashlib
import time
from .logger_config import get_logger
from .exceptions import InvalidTransactionError, ValidationError

# Set up logger for this module
logger = get_logger('pychain.transaction')


class Transaction:
    """
    A transaction representing a transfer of value between parties.

    Attributes:
        sender (str): Address/name of the sender
        receiver (str): Address/name of the receiver
        amount (float): Amount to transfer
        timestamp (float): Unix timestamp of when transaction was created
        transaction_id (str): Unique transaction hash/ID
    """

    def __init__(self, sender, receiver, amount, timestamp=None):
        """
        Create a transaction.

        Args:
            sender (str): Address/name of sender
            receiver (str): Address/name of receiver
            amount (float): Amount to transfer
            timestamp (float): Transaction timestamp (defaults to current time)

        Raises:
            InvalidTransactionError: If transaction validation fails
            ValidationError: If input data is invalid
        """
        logger.debug(f"Creating transaction: {sender} -> {receiver}: {amount}")

        try:
            # Validate inputs
            if sender is None or receiver is None:
                raise ValidationError("Sender and receiver cannot be None")

            if amount is None:
                raise ValidationError("Amount cannot be None")

            if not isinstance(amount, (int, float)):
                raise ValidationError(f"Amount must be numeric, got {type(amount).__name__}")

            if amount <= 0 and sender != "System":
                raise ValidationError(f"Amount must be positive, got {amount}")

            if sender == receiver:
                raise InvalidTransactionError("Sender and receiver cannot be the same")

            self.sender = sender
            self.receiver = receiver
            self.amount = amount
            self.timestamp = timestamp if timestamp is not None else time.time()
            self.transaction_id = self.calculate_hash()

            logger.info(f"Transaction created: {self} (ID: {self.transaction_id[:16]}...)")

        except (InvalidTransactionError, ValidationError) as e:
            logger.error(f"Transaction creation failed: {e}")
            raise

    def calculate_hash(self):
        """
        Calculate unique transaction ID using SHA-256.

        The hash is based on sender, receiver, amount, and timestamp,
        ensuring each transaction has a unique identifier.

        Returns:
            str: Transaction hash/ID (64 character hexadecimal string)

        Raises:
            ValidationError: If hash calculation fails
        """
        try:
            transaction_string = (
                str(self.sender) +
                str(self.receiver) +
                str(self.amount) +
                str(self.timestamp)
            )
            transaction_bytes = transaction_string.encode()
            hash_object = hashlib.sha256(transaction_bytes)
            hash_value = hash_object.hexdigest()

            logger.debug(f"Transaction hash calculated: {hash_value[:16]}...")
            return hash_value

        except Exception as e:
            logger.error(f"Transaction hash calculation failed: {e}")
            raise ValidationError(f"Hash calculation failed: {e}") from e

    def to_dict(self):
        """
        Convert transaction to dictionary for JSON serialization.

        Returns:
            dict: Transaction data with all attributes
        """
        return {
            'transaction_id': self.transaction_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

    def __str__(self):
        """
        String representation of transaction.

        Returns:
            str: Human-readable transaction string
        """
        return f"{self.sender} -> {self.receiver}: {self.amount}"

    def __repr__(self):
        """
        Debug representation of transaction.

        Returns:
            str: Python code-like representation
        """
        return f"Transaction({self.sender!r}, {self.receiver!r}, {self.amount})"

    def is_valid(self):
        """
        Validate the transaction.

        Checks:
        1. Amount is positive (greater than 0), except for System transactions which can be zero
        2. Sender and receiver are different
        3. No None values for required fields

        Returns:
            tuple: (is_valid, error_message)
                - is_valid (bool): True if transaction is valid
                - error_message (str): Error description if invalid, None if valid
        """
        try:
            # Check for None values
            if self.sender is None or self.receiver is None or self.amount is None:
                error_msg = "Transaction has missing data (sender, receiver, or amount is None)"
                logger.warning(f"Invalid transaction: {error_msg}")
                return False, error_msg

            # Check for same sender and receiver
            if self.sender == self.receiver:
                error_msg = "Sender and receiver cannot be the same"
                logger.warning(f"Invalid transaction: {error_msg}")
                return False, error_msg

            # Check for positive amount (System can send zero for genesis/special transactions)
            if self.amount <= 0 and self.sender != "System":
                error_msg = f"Transaction amount must be positive, got {self.amount}"
                logger.warning(f"Invalid transaction: {error_msg}")
                return False, error_msg

            # System transactions are special and always valid
            if self.sender == "System":
                logger.debug(f"Valid system transaction: {self.transaction_id[:16]}...")
                return True, None

            logger.debug(f"Transaction validation passed: {self.transaction_id[:16]}...")
            return True, None

        except Exception as e:
            error_msg = f"Validation error: {e}"
            logger.error(f"Transaction validation failed: {error_msg}")
            return False, error_msg
