"""
solution.py — code-runs gate for K · Sequencing · Sheet 5 "Follow the Arrows".

The 1D board has boxes 1..5 with a star on box 4. Models Bit's landing box for
each arrow program and asserts it.

Run:  python coding/k_sequencing/05_follow_the_arrows/solution.py
"""


def land(start, program):
    pos = start
    for move in program:
        pos += 1 if move == "right" else -1
    return pos


if __name__ == "__main__":
    STAR = 4

    # Model: start 1, ➡ ➡ ➡ -> box 4 (the star).
    assert land(1, ["right"] * 3) == STAR
    print("Start 1, ➡ ➡ ➡ -> box 4 (the star) ✓")

    # Ex 1: start 1, ➡ ➡ -> box 3.
    assert land(1, ["right"] * 2) == 3
    print("Ex 1: start 1, ➡ ➡ -> box 3 ✓")

    # Ex 2: start 1, ➡ ➡ ➡ ➡ -> box 5.
    assert land(1, ["right"] * 4) == 5
    print("Ex 2: start 1, ➡ ➡ ➡ ➡ -> box 5 ✓")

    # Ex 3: start 2, ➡ ➡ -> box 4 (the star).
    assert land(2, ["right"] * 2) == STAR
    print("Ex 3: start 2, ➡ ➡ -> box 4 (the star) ✓")

    print("\nALL CHECKS PASSED — every landing box is correct.")
