"""
solution.py — code-runs gate for K · Sequencing · Sheet 6 "Which Way?".

Bit and a star sit on a 1D board. Models which single arrow (➡ right / ⬅ left)
moves Bit toward the star and asserts it.

Run:  python coding/k_sequencing/06_which_way/solution.py
"""


def which_way(bit, star):
    """Return 'right' (➡) if the star is to the right of Bit, else 'left' (⬅)."""
    return "right" if star > bit else "left"


if __name__ == "__main__":
    # Model: Bit on box 3, star on box 5 -> go right ➡.
    assert which_way(3, 5) == "right"
    print("Bit 3, star 5 -> ➡ right ✓")

    # Ex 1: Bit on box 2, star on box 5 -> ➡ right.
    assert which_way(2, 5) == "right"
    print("Ex 1: Bit 2, star 5 -> ➡ right ✓")

    # Ex 2: Bit on box 4, star on box 2 -> ⬅ left.
    assert which_way(4, 2) == "left"
    print("Ex 2: Bit 4, star 2 -> ⬅ left ✓")

    # Ex 3 (you try): Bit on box 5, star on box 1 -> ⬅ left.
    assert which_way(5, 1) == "left"
    print("Ex 3: Bit 5, star 1 -> ⬅ left ✓")

    print("\nALL CHECKS PASSED — every direction choice is correct.")
