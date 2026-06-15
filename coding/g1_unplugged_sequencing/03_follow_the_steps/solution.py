"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 3
"Follow the Steps".

The child executes a 6-step algorithm that fills a row of boxes to make an AB
pattern (circle, square, ...). Models the result of running the steps in order
and asserts each box and the pattern.

Run:  python coding/g1_unplugged_sequencing/03_follow_the_steps/solution.py
"""

# Each step says which shape to draw in the next box, in order.
STEPS = [
    ("box 1", "circle"),
    ("box 2", "square"),
    ("box 3", "circle"),
    ("box 4", "square"),
    ("box 5", "circle"),
    ("box 6", "square"),
]


def run_algorithm(steps):
    """Carry out the steps in order; return the list of shapes drawn."""
    return [shape for _, shape in steps]


if __name__ == "__main__":
    result = run_algorithm(STEPS)
    assert result == ["circle", "square"] * 3
    print("Following the steps makes: circle, square, circle, square, circle, square ✓")

    # Ex 2 — box 6 holds a square.
    assert result[5] == "square"
    print("Ex 2: box 6 is a square ✓")

    # Ex 3 — the pattern is circle-square (AB); box 7 would be a circle.
    assert result[0] == "circle" and result[1] == "square"
    next_shape = "circle" if result[-1] == "square" else "square"
    assert next_shape == "circle"
    print("Ex 3: the pattern is circle-square (AB); box 7 would be a circle ✓")

    print("\nALL CHECKS PASSED — running the algorithm makes the AB pattern.")
