"""
Test that all README examples work correctly.
This ensures documentation stays accurate.
"""

import sys
import os

# Suppress mining output for cleaner test output
import io
from contextlib import redirect_stdout

def test_quick_start_example():
    """Test Quick Start example from README."""
    from pychain.blockchain import Blockchain

    # Create a new blockchain with difficulty 2
    blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100, "Bob": 50})

    # Create transactions
    blockchain.create_transaction("Alice", "Bob", 30)
    blockchain.create_transaction("Bob", "Charlie", 15)

    # Mine pending transactions
    with redirect_stdout(io.StringIO()):
        blockchain.mine_pending_transactions("Miner1")

    # Check balances
    assert blockchain.get_balance('Alice') == 70
    assert blockchain.get_balance('Bob') == 65  # 50 + 30 - 15
    assert blockchain.get_balance('Charlie') == 15
    assert blockchain.get_balance('Miner1') == 10  # mining reward

    # Validate blockchain
    assert blockchain.is_chain_valid() == True

    print("[OK] Quick Start example works")


def test_example_1():
    """Test Example 1: Simple Transaction."""
    from pychain.blockchain import Blockchain

    # Create blockchain with initial balances
    blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

    # Create and mine transaction
    blockchain.create_transaction("Alice", "Bob", 50)
    with redirect_stdout(io.StringIO()):
        blockchain.mine_pending_transactions("Miner1")

    assert blockchain.get_balance("Alice") == 50
    assert blockchain.get_balance("Bob") == 50
    assert blockchain.get_balance("Miner1") == 10

    print("[OK] Example 1 works")


def test_example_2():
    """Test Example 2: Multiple Transactions in One Block."""
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
    with redirect_stdout(io.StringIO()):
        blockchain.mine_pending_transactions("Miner1")

    # Check final balances
    assert blockchain.get_balance('Alice') == 120  # 200 - 50 - 30
    assert blockchain.get_balance('Bob') == 130  # 100 + 50 - 20
    assert blockchain.get_balance('Charlie') == 50  # 30 + 20
    assert blockchain.get_balance('Miner1') == 10  # reward

    print("[OK] Example 2 works")


def test_example_3():
    """Test Example 3: Export and Import."""
    from pychain.blockchain import Blockchain
    import os

    # Create and populate blockchain
    blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})
    blockchain.create_transaction("Alice", "Bob", 50)
    with redirect_stdout(io.StringIO()):
        blockchain.mine_pending_transactions("Miner1")

    # Export to JSON
    test_file = "test_export.json"
    blockchain.export_to_file(test_file)

    # Import later
    loaded_blockchain = Blockchain.import_from_file(test_file)

    # Verify integrity
    assert loaded_blockchain.is_chain_valid()
    assert loaded_blockchain.get_balance("Alice") == blockchain.get_balance("Alice")
    assert loaded_blockchain.get_balance("Bob") == blockchain.get_balance("Bob")

    # Cleanup
    os.remove(test_file)

    print("[OK] Example 3 works")


def test_example_4():
    """Test Example 4: Transaction Validation."""
    from pychain.blockchain import Blockchain

    # Create blockchain
    blockchain = Blockchain(difficulty=2, initial_balances={"Alice": 100})

    # This will succeed
    blockchain.create_transaction("Alice", "Bob", 50)

    # This will fail - insufficient balance
    try:
        blockchain.create_transaction("Alice", "Charlie", 200)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Insufficient balance" in str(e)

    print("[OK] Example 4 works")


def test_example_5():
    """Test Example 5: Mining with Different Difficulties."""
    from pychain.blockchain import Blockchain
    import time

    # Test different difficulties
    for difficulty in [1, 2, 3]:
        blockchain = Blockchain(difficulty=difficulty, initial_balances={"Alice": 100})
        blockchain.create_transaction("Alice", "Bob", 50)

        start = time.time()
        with redirect_stdout(io.StringIO()):
            blockchain.mine_pending_transactions("Miner1")
        elapsed = time.time() - start

        # Just verify it completes (difficulty 3 might take a bit)
        assert elapsed < 10, f"Difficulty {difficulty} took too long: {elapsed}s"

    print("[OK] Example 5 works")


if __name__ == "__main__":
    print("Testing README examples...\n")

    test_quick_start_example()
    test_example_1()
    test_example_2()
    test_example_3()
    test_example_4()
    test_example_5()

    print("\n[SUCCESS] All README examples work correctly!")
