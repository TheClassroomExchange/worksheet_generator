"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 6
"Break It Into Parts".

Decomposition: a whole picture is made of smaller shape parts. Models the part
list for each whole and asserts the part counts, so the answer key cannot drift.

Run:  python coding/k_unplugged_ct/06_break_it_into_parts/solution.py
"""
from collections import Counter


def parts_of(whole):
    """Return {shape: count} for the shapes that make up a whole picture."""
    return dict(Counter(whole))


if __name__ == "__main__":
    # Worked model: a rocket = a triangle (top) + a square (body).
    rocket = ["triangle", "square"]
    assert parts_of(rocket) == {"triangle": 1, "square": 1}
    assert len(rocket) == 2
    print("Model: rocket -> 2 parts (1 triangle + 1 square) ✓")

    # Ex 1: a house = a square (walls) + a triangle (roof) -> 2 parts.
    house = ["square", "triangle"]
    assert len(house) == 2 and parts_of(house) == {"square": 1, "triangle": 1}
    print("Ex 1: house -> 2 parts (square + triangle) ✓")

    # Ex 2: a snowman = three circles -> 3 parts.
    snowman = ["circle", "circle", "circle"]
    assert len(snowman) == 3 and parts_of(snowman) == {"circle": 3}
    print("Ex 2: snowman -> 3 parts (3 circles) ✓")

    # Ex 3 (you try): Bit's robot = square body + circle head + 2 square feet -> 4 parts.
    robot = ["square", "circle", "square", "square"]
    assert len(robot) == 4 and parts_of(robot) == {"square": 3, "circle": 1}
    print("Ex 3: robot -> 4 parts (3 squares + 1 circle) ✓")

    print("\nALL CHECKS PASSED — every part list is correct.")
