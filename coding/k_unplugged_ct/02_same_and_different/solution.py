"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 2 "Same and Different".

Models the matching answers (which option is the SAME as the target, and which
item is the one that is DIFFERENT) and asserts them, so the worksheet's answer
key cannot drift.

Run:  python coding/k_unplugged_ct/02_same_and_different/solution.py
"""
from collections import Counter


def find_same(target, options):
    """Return the indices of options equal to the target."""
    return [i for i, o in enumerate(options) if o == target]


def find_different(items):
    """Return the index of the one item that differs from all the rest."""
    counts = Counter(items)
    odd = min(counts, key=counts.get)
    return [i for i, x in enumerate(items) if x == odd]


if __name__ == "__main__":
    # Worked model: target ● among ▲ ● ■  -> the circle (index 1).
    assert find_same("circle", ["triangle", "circle", "square"]) == [1]
    print("Model: same as ● in [▲ ● ■] -> the circle ✓")

    # Ex 1: target ★ among ● ★ ▲ -> index 1.
    assert find_same("star", ["circle", "star", "triangle"]) == [1]
    print("Ex 1: same as ★ in [● ★ ▲] -> the star ✓")

    # Ex 2: target ■ among ● ▲ ■ -> index 2.
    assert find_same("square", ["circle", "triangle", "square"]) == [2]
    print("Ex 2: same as ■ in [● ▲ ■] -> the square ✓")

    # Ex 3 (you try): which is DIFFERENT in ● ● ▲ ● -> the triangle (index 2).
    assert find_different(["circle", "circle", "triangle", "circle"]) == [2]
    print("Ex 3: different in [● ● ▲ ●] -> the triangle ✓")

    print("\nALL CHECKS PASSED — every same/different answer is correct.")
