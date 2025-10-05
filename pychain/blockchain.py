import time
from pychain.block import Block


class Blockchain:
    """
    A blockchain that manages a chain of blocks.

    The blockchain automatically creates a genesis block upon initialization
    and provides methods to manage the chain with dynamic difficulty adjustment.

    Attributes:
        chain (list): List of Block objects representing the blockchain
        difficulty (int): Current mining difficulty for Proof of Work
        target_block_time (float): Target time between blocks in seconds
        adjustment_interval (int): Adjust difficulty every N blocks
    """

    def __init__(self, difficulty=2, target_block_time=10, adjustment_interval=5):
        """
        Initialize the blockchain with a genesis block and dynamic difficulty.

        Creates an empty chain list and automatically adds the genesis block.

        Args:
            difficulty (int): Initial mining difficulty (default: 2)
            target_block_time (float): Target time between blocks in seconds (default: 10)
            adjustment_interval (int): Adjust difficulty every N blocks (default: 5)
        """
        self.chain = []
        self.difficulty = difficulty
        self.target_block_time = target_block_time
        self.adjustment_interval = adjustment_interval
        self.chain.append(self.create_genesis_block())

    def create_genesis_block(self):
        """
        Create the genesis block (first block in the blockchain).

        The genesis block has special properties:
        - Index: 0
        - Previous hash: "0" (no previous block exists)
        - Data: "Genesis Block"
        - Timestamp: Current time when blockchain is created

        The genesis block is mined using Proof of Work.

        Returns:
            Block: The genesis block
        """
        genesis = Block(0, time.time(), "Genesis Block", "0", self.difficulty)
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

    def is_chain_valid(self, verbose=False):
        """
        Validate the entire blockchain.

        Checks four key aspects:
        1. Genesis block has previous_hash == "0" and valid hash
        2. Each block's stored hash matches its calculated hash
        3. Each block's previous_hash matches the previous block's hash
        4. Each block meets Proof of Work requirements (hash starts with required zeros)

        Args:
            verbose (bool): If True, print detailed validation info

        Returns:
            bool: True if chain is valid, False otherwise
        """
        for i in range(len(self.chain)):
            current_block = self.chain[i]

            # Check hash integrity
            if current_block.hash != current_block.calculate_hash():
                if verbose:
                    print(f"❌ Block {i} hash mismatch")
                    print(f"   Stored: {current_block.hash}")
                    print(f"   Calculated: {current_block.calculate_hash()}")
                return False

            # Check Proof of Work (hash starts with required zeros)
            target = "0" * current_block.difficulty
            if current_block.hash[:current_block.difficulty] != target:
                if verbose:
                    print(f"❌ Block {i} doesn't meet PoW requirements")
                    print(f"   Expected: {target}...")
                    print(f"   Got: {current_block.hash[:current_block.difficulty]}...")
                return False

            # Check chain continuity
            if i == 0:
                # Genesis block validation
                if current_block.previous_hash != "0":
                    if verbose:
                        print("❌ Genesis block invalid: previous_hash != '0'")
                    return False
            else:
                # Regular block validation
                previous_block = self.chain[i - 1]
                if current_block.previous_hash != previous_block.hash:
                    if verbose:
                        print(f"❌ Block {i} broken chain link")
                        print(f"   previous_hash: {current_block.previous_hash}")
                        print(f"   Previous block hash: {previous_block.hash}")
                    return False

            if verbose:
                print(f"✅ Block {i} valid (Nonce: {current_block.nonce})")

        return True

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
