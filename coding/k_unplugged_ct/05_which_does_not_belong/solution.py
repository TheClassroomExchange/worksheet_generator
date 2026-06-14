"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 5
"Which One Does Not Belong?".

Models the odd-one-out for each group and asserts it, so the answer key cannot
drift.

Run:  python coding/k_unplugged_ct/05_which_does_not_belong/solution.py
"""
from collections import Counter


def odd_one_out(items):
    """Return the index of the single item that differs from all the rest."""
    counts = Counter(items)
    odd = min(counts, key=counts.get)
    idx = [i for i, x in enumerate(items) if x == odd]
    assert len(idx) == 1, "there must be exactly one odd item"
    return idx[0]


if __name__ == "__main__":
    # Worked model: ● ● ● ▲ -> the triangle (index 3).
    assert odd_one_out(["cir", "cir", "cir", "tri"]) == 3
    print("Model: ● ● ● ▲ -> odd is the triangle ✓")

    # Ex 1: ★ ★ ● ★ -> the circle (index 2).
    assert odd_one_out(["star", "star", "cir", "star"]) == 2
    print("Ex 1: ★ ★ ● ★ -> odd is the circle ✓")

    # Ex 2: ■ ▲ ■ ■ -> the triangle (index 1).
    assert odd_one_out(["sq", "tri", "sq", "sq"]) == 1
    print("Ex 2: ■ ▲ ■ ■ -> odd is the triangle ✓")

    # Ex 3 (you try): ● ● ★ ● ● -> the star (index 2).
    assert odd_one_out(["cir", "cir", "star", "cir", "cir"]) == 2
    print("Ex 3: ● ● ★ ● ● -> odd is the star ✓")

    print("\nALL CHECKS PASSED — every odd-one-out is correct.")
