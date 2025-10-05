import hashlib
import time


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
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transaction_id = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate unique transaction ID using SHA-256.

        The hash is based on sender, receiver, amount, and timestamp,
        ensuring each transaction has a unique identifier.

        Returns:
            str: Transaction hash/ID (64 character hexadecimal string)
        """
        transaction_string = (
            str(self.sender) +
            str(self.receiver) +
            str(self.amount) +
            str(self.timestamp)
        )
        transaction_bytes = transaction_string.encode()
        hash_object = hashlib.sha256(transaction_bytes)
        return hash_object.hexdigest()

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
        return f"{self.sender} → {self.receiver}: {self.amount}"

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

        Returns:
            tuple: (is_valid, error_message)
                - is_valid (bool): True if transaction is valid
                - error_message (str): Error description if invalid, None if valid
        """
        # Check for positive amount (System can send zero for genesis/special transactions)
        if self.amount <= 0 and self.sender != "System":
            return False, "Transaction amount must be positive"

        # Check sender and receiver are different
        if self.sender == self.receiver:
            return False, "Sender and receiver cannot be the same"

        return True, None
