"""
solution.py — code-runs gate for K · Sequencing · Sheet 1 "First, Next, Last".

Bit builds a tower one block at a time: 1 block, then 2, then 3. Ordering the
steps from fewest to most models 'first → next → last'. Models the order and
asserts it so the answer key cannot drift.

Run:  python coding/k_sequencing/01_first_next_last/solution.py
"""


def order_by_count(cards):
    """Return the card counts in sequence order (fewest = first)."""
    return sorted(cards)


if __name__ == "__main__":
    # Cards shown OUT of order: 3 blocks, 1 block, 2 blocks.
    shown = [3, 1, 2]
    assert order_by_count(shown) == [1, 2, 3]
    print("Tower steps ordered: first 1 block, next 2 blocks, last 3 blocks ✓")

    # Ex: first = the card with the fewest (1), last = the most (3).
    assert min(shown) == 1 and max(shown) == 3
    print("First = 1 block (fewest), Last = 3 blocks (most) ✓")

    print("\nALL CHECKS PASSED — the first/next/last order is correct.")
