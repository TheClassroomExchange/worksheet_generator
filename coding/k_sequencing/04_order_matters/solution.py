"""
solution.py — code-runs gate for K · Sequencing · Sheet 4 "Order Matters".

Introduces the 1D board: numbered boxes left to right; ➡ moves Bit one box to
the right. Models Bit's landing box for each program and asserts it, showing
the NUMBER of steps changes where Bit ends up.

Run:  python coding/k_sequencing/04_order_matters/solution.py
"""


def land(start, program):
    """Landing box: start + one box right for each ➡, one left for each ⬅."""
    pos = start
    for move in program:
        pos += 1 if move == "right" else -1
    return pos


if __name__ == "__main__":
    # Board boxes 1,2,3; star at box 3; Bit starts at box 1.
    # One ➡ -> box 2 (not the star).
    assert land(1, ["right"]) == 2
    print("Start box 1, program ➡ -> lands box 2 (not the star) ✓")

    # Two ➡ -> box 3 (the star!).
    assert land(1, ["right", "right"]) == 3
    print("Start box 1, program ➡ ➡ -> lands box 3 (the star) ✓")

    # So you need exactly two ➡ in order to reach the star from box 1.
    steps_needed = 3 - 1
    assert steps_needed == 2
    print("Steps needed from box 1 to box 3 = 2 ✓")

    print("\nALL CHECKS PASSED — the number of steps decides the landing box.")
