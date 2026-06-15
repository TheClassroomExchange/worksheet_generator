"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 4 "Growing Patterns".

Three-part (ABC) repeating patterns, plus predicting TWO next items. Models
each answer and asserts it so the answer key cannot drift.

Run:  python coding/k_unplugged_ct/04_growing_patterns/solution.py
"""


def next_item(seq, period):
    return seq[-period]


def next_two(seq, period):
    a = next_item(seq, period)
    b = next_item(seq + [a], period)
    return [a, b]


if __name__ == "__main__":
    # Worked model: ▲ ■ ● ▲ ■ ● (period 3) -> next ▲.
    assert next_item(["tri", "sq", "cir", "tri", "sq", "cir"], 3) == "tri"
    print("Model: ▲ ■ ● ▲ ■ ● -> next ▲ ✓")

    # Ex 1: ● ■ ★ ● ■ ★ (period 3) -> next ●.
    assert next_item(["cir", "sq", "star", "cir", "sq", "star"], 3) == "cir"
    print("Ex 1: ● ■ ★ ● ■ ★ -> next ● ✓")

    # Ex 2 (predict TWO): ▲ ● ▲ ● ▲ (period 2) -> next ●, then ▲.
    assert next_two(["tri", "cir", "tri", "cir", "tri"], 2) == ["cir", "tri"]
    print("Ex 2: ▲ ● ▲ ● ▲ -> next two are ● then ▲ ✓")

    # Ex 3 (you try, make your own) — example of a valid ABC pattern continuing.
    assert next_item(["star", "cir", "sq", "star", "cir", "sq"], 3) == "star"
    print("Ex 3: any correct repeating pattern is accepted (example ★ ● ■ … -> ★) ✓")

    print("\nALL CHECKS PASSED — every pattern answer is correct.")
