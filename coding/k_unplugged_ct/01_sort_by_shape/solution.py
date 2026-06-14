"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 1 "Sort by Shape".

Kindergarten has no executable text code; the run-gate instead MODELS the
intended answer (the correct sort) and asserts it, so the worksheet's answer
key cannot drift from a wrong grouping.

Run:  python coding/k_unplugged_ct/01_sort_by_shape/solution.py
"""


def sort_by_shape(items):
    """Group items by their shape name; return {shape: count}."""
    groups = {}
    for it in items:
        groups.setdefault(it, []).append(it)
    return {k: len(v) for k, v in groups.items()}


if __name__ == "__main__":
    # Bit's pile (worksheet shows: ● ▲ ■ ● ▲ ■).
    pile = ["circle", "triangle", "square", "circle", "triangle", "square"]
    result = sort_by_shape(pile)
    assert result == {"circle": 2, "triangle": 2, "square": 2}, result
    print("Pile ● ▲ ■ ● ▲ ■ -> circle group = 2, triangle group = 2, square group = 2 ✓")

    # 'You try' pile for Ex 3 (find the squares): ■ ● ■ -> 2 squares.
    you_try = ["square", "circle", "square"]
    assert sort_by_shape(you_try)["square"] == 2
    print("You-try pile ■ ● ■ -> 2 squares ✓")

    print("\nALL CHECKS PASSED — every group count is correct.")
