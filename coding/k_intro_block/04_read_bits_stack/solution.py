"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 4
"Read Bit's Stack".

Bit's stage is a 1D row of boxes 1..5 with a star on box 4. Bit starts on
box 1. A block stack is run from the top down: each ➡ block moves Bit one box
right, each ⬅ block moves one box left. Models Bit's landing box for each
stack on the worksheet and asserts it.

Run:  python coding/k_intro_block/04_read_bits_stack/solution.py
"""

STAR = 4


def run_stack(start, moves):
    """Run the move blocks top to bottom; return Bit's landing box."""
    pos = start
    for m in moves:
        pos += 1 if m == "right" else -1
    return pos


if __name__ == "__main__":
    # Stack 1 — GO, ➡, ➡ from box 1 -> box 3.
    assert run_stack(1, ["right", "right"]) == 3
    print("Stack 1: box 1, ➡ ➡ -> box 3 ✓")

    # Stack 2 — GO, ➡, ➡, ➡ from box 1 -> box 4 (the star).
    assert run_stack(1, ["right", "right", "right"]) == STAR
    print("Stack 2: box 1, ➡ ➡ ➡ -> box 4 (the star) ✓")

    # Stack 3 (you try) — GO, ➡, ➡, ⬅ from box 1 -> box 2.
    assert run_stack(1, ["right", "right", "left"]) == 2
    print("Stack 3: box 1, ➡ ➡ ⬅ -> box 2 ✓")

    print("\nALL CHECKS PASSED — run each block in order to find the landing box.")
