"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 3 "What Comes Next?".

Models the answer to each repeating pattern (the item that comes next) and
asserts it, so the worksheet's answer key cannot drift.

Run:  python coding/k_unplugged_ct/03_what_comes_next/solution.py
"""


def next_item(seq, period):
    """The next item continuing a repeating pattern of the given period."""
    return seq[-period]


if __name__ == "__main__":
    # Worked model: ▲ ■ ▲ ■ (period 2) -> next ▲.
    assert next_item(["tri", "sq", "tri", "sq"], 2) == "tri"
    print("Model: ▲ ■ ▲ ■ -> next ▲ ✓")

    # Ex 1: ● ★ ● ★ ● (period 2) -> next ★.
    assert next_item(["cir", "star", "cir", "star", "cir"], 2) == "star"
    print("Ex 1: ● ★ ● ★ ● -> next ★ ✓")

    # Ex 2: ■ ▲ ■ ▲ (period 2) -> next ■.
    assert next_item(["sq", "tri", "sq", "tri"], 2) == "sq"
    print("Ex 2: ■ ▲ ■ ▲ -> next ■ ✓")

    # Ex 3 (you try, AAB): ★ ★ ● ★ ★ ● (period 3) -> next ★.
    assert next_item(["star", "star", "cir", "star", "star", "cir"], 3) == "star"
    print("Ex 3: ★ ★ ● ★ ★ ● -> next ★ ✓")

    print("\nALL CHECKS PASSED — every 'next' answer is correct.")
