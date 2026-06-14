"""
solution.py — code-runs gate for K · Sequencing · Sheet 7 "Give Bit the Steps".

The child writes the arrow program that gets Bit from its box to the star.
Models the needed program (and verifies it actually lands on the star) and
asserts it.

Run:  python coding/k_sequencing/07_give_bit_the_steps/solution.py
"""


def steps_to(bit, star):
    """The arrow program from bit to star: ➡ for each box right, ⬅ for left."""
    n = abs(star - bit)
    return ["right"] * n if star > bit else ["left"] * n


def land(start, program):
    pos = start
    for m in program:
        pos += 1 if m == "right" else -1
    return pos


if __name__ == "__main__":
    # Model: Bit on box 1, star on box 3 -> ➡ ➡ (and it lands on the star).
    prog = steps_to(1, 3)
    assert prog == ["right", "right"] and land(1, prog) == 3
    print("Model: box 1 -> star box 3 needs ➡ ➡ ✓")

    # Ex 1: Bit on box 1, star on box 4 -> ➡ ➡ ➡.
    prog = steps_to(1, 4)
    assert prog == ["right"] * 3 and land(1, prog) == 4
    print("Ex 1: box 1 -> star box 4 needs ➡ ➡ ➡ ✓")

    # Ex 2: Bit on box 2, star on box 3 -> ➡.
    prog = steps_to(2, 3)
    assert prog == ["right"] and land(2, prog) == 3
    print("Ex 2: box 2 -> star box 3 needs ➡ ✓")

    # Ex 3 (you try): Bit on box 4, star on box 2 -> ⬅ ⬅.
    prog = steps_to(4, 2)
    assert prog == ["left", "left"] and land(4, prog) == 2
    print("Ex 3: box 4 -> star box 2 needs ⬅ ⬅ ✓")

    print("\nALL CHECKS PASSED — every program reaches the star.")
