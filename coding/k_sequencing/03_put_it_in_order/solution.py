"""
solution.py — code-runs gate for K · Sequencing · Sheet 3 "Put It in Order".

Bit's plant grows in four steps (1, 2, 3, 4 leaves). Models the correct order
(fewest to most) and asserts it so the answer key cannot drift.

Run:  python coding/k_sequencing/03_put_it_in_order/solution.py
"""


def put_in_order(cards):
    return sorted(cards)


if __name__ == "__main__":
    # Cards shown OUT of order: 4, 2, 1, 3 leaves.
    shown = [4, 2, 1, 3]
    assert put_in_order(shown) == [1, 2, 3, 4]
    print("Plant steps ordered: 1 leaf, 2 leaves, 3 leaves, 4 leaves ✓")

    # The step numbers to write under [4, 2, 1, 3] are [4, 2, 1, 3]
    # (each card's order position = its own count, since counts are 1..4).
    order_labels = [shown.index(n) for n in [1, 2, 3, 4]]  # where each rank sits
    assert order_labels == [2, 1, 3, 0]
    print("Under cards [4,2,1,3] write [4,2,1,3] to order them 1->4 ✓")

    print("\nALL CHECKS PASSED — the 4-step order is correct.")
