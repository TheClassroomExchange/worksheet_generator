"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 6
"What Must Come First?".

Steps with dependencies: some must come before others, and some can be done in
either order. Models the precedences for a make-a-cup-of-tea algorithm and
asserts the must-come-first step, an illegal early step, the flexible pair, and
a working full order.

Run:  python coding/g1_unplugged_sequencing/06_what_must_come_first/solution.py
"""

from itertools import permutations

# Cards (shown to the child):
#   A = add the milk, B = boil the water, C = put a tea bag in the cup,
#   D = pour the water in the cup
PRE = [("B", "D"), ("C", "D"), ("D", "A")]  # B,C before D; D before A
STEPS = ["A", "B", "C", "D"]


def works(order):
    pos = {s: i for i, s in enumerate(order)}
    return all(pos[a] < pos[b] for a, b in PRE)


def must_precede(x, y):
    """True if x must come before y in EVERY working order."""
    return all(o.index(x) < o.index(y) for o in permutations(STEPS) if works(o))


if __name__ == "__main__":
    # Ex 1 — to pour the water (D) it must be hot: boil the water (B) comes first.
    assert must_precede("B", "D")
    print("Ex 1: 'boil the water' (B) must come before 'pour the water' (D) ✓")

    # Ex 2 — you cannot add the milk (A) before pouring the water (D).
    assert must_precede("D", "A")
    print("Ex 2: 'add the milk' (A) cannot come before 'pour the water' (D) ✓")

    # Ex 3 — B and C can be done in either order (neither must precede the other).
    assert not must_precede("B", "C") and not must_precede("C", "B")
    print("Ex 3: boil the water (B) and tea bag in cup (C) can swap order ✓")

    # A full working order exists, e.g. B, C, D, A.
    assert works(["B", "C", "D", "A"])
    print("A working order: B, C, D, A ✓")

    print("\nALL CHECKS PASSED — dependencies decide what must come first.")
