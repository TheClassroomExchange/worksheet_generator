"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 7 "Sort Two Ways".

The SAME pile is sorted by two different rules (by exact shape, and by
round-vs-pointy). Models both groupings and asserts the counts so the answer
key cannot drift.

Run:  python coding/k_unplugged_ct/07_sort_two_ways/solution.py
"""
from collections import Counter

POINTY = {"triangle", "star"}   # have corners/points
ROUND = {"circle"}              # no corners


def sort_by_shape(pile):
    return dict(Counter(pile))


def sort_round_pointy(pile):
    out = {"round": 0, "pointy": 0}
    for x in pile:
        out["round" if x in ROUND else "pointy"] += 1
    return out


if __name__ == "__main__":
    # Pile (worksheet shows: ● ▲ ● ★ ▲).
    pile = ["circle", "triangle", "circle", "star", "triangle"]

    # Way 1 — by exact shape.
    assert sort_by_shape(pile) == {"circle": 2, "triangle": 2, "star": 1}
    print("Way 1 (by shape): circle = 2, triangle = 2, star = 1 ✓")

    # Way 2 — by round vs pointy.
    assert sort_round_pointy(pile) == {"round": 2, "pointy": 3}
    print("Way 2 (round vs pointy): round = 2, pointy = 3 ✓")

    # Ex 3 (you try) pile: ★ ● ▲ ● (star, circle, triangle, circle).
    # By shape: star 1, circle 2, triangle 1. Round/pointy: round 2 (circles),
    # pointy 2 (star + triangle).
    you_try = ["star", "circle", "triangle", "circle"]
    assert sort_by_shape(you_try) == {"star": 1, "circle": 2, "triangle": 1}
    assert sort_round_pointy(you_try) == {"round": 2, "pointy": 2}
    print("Ex 3 (you try): by shape star1/circle2/triangle1; round 2 / pointy 2 ✓")

    print("\nALL CHECKS PASSED — both sorts of every pile are correct.")
