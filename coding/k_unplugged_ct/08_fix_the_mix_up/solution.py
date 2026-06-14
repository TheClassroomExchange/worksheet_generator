"""
solution.py — code-runs gate for K · Unplugged CT · Sheet 8 "Fix the Mix-Up".

Debugging for K: one card breaks a pattern or group. Models WHERE the mistake
is and WHAT it should be, then asserts it, so the answer key cannot drift.

Run:  python coding/k_unplugged_ct/08_fix_the_mix_up/solution.py
"""


def find_pattern_bug(seq, period):
    """Find the first position that breaks a repeating pattern of `period`.
    Returns (index, should_be). The first `period` items define the unit."""
    unit = seq[:period]
    for i, x in enumerate(seq):
        expected = unit[i % period]
        if x != expected:
            return i, expected
    return None, None


def find_group_bug(items, correct):
    """In a group that should be all `correct`, find the odd item.
    Returns (index, should_be)."""
    for i, x in enumerate(items):
        if x != correct:
            return i, correct
    return None, None


if __name__ == "__main__":
    # Worked model: ● ▲ ● ▲ ■ ▲  (should be ● ▲ repeating). Bug at index 4 (■ -> ●).
    idx, fix = find_pattern_bug(["cir", "tri", "cir", "tri", "sq", "tri"], 2)
    assert (idx, fix) == (4, "cir")
    print("Model: ● ▲ ● ▲ ■ ▲ -> bug at spot 5 (■), should be ● ✓")

    # Ex 1: circle group with a triangle: ● ● ▲ ● -> bug at index 2 (▲ -> ●).
    idx, fix = find_group_bug(["cir", "cir", "tri", "cir"], "cir")
    assert (idx, fix) == (2, "cir")
    print("Ex 1: ● ● ▲ ● -> the ▲ does not belong, should be ● ✓")

    # Ex 2: pattern ★ ■ ★ ■ ★ ★ (should be ★ ■). Bug at index 5 (★ -> ■).
    idx, fix = find_pattern_bug(["star", "sq", "star", "sq", "star", "star"], 2)
    assert (idx, fix) == (5, "sq")
    print("Ex 2: ★ ■ ★ ■ ★ ★ -> bug at spot 6 (★), should be ■ ✓")

    # Ex 3 (you try): ▲ ● ▲ ● ▲ ▲ (should be ▲ ●). Bug at index 5 (▲ -> ●).
    idx, fix = find_pattern_bug(["tri", "cir", "tri", "cir", "tri", "tri"], 2)
    assert (idx, fix) == (5, "cir")
    print("Ex 3: ▲ ● ▲ ● ▲ ▲ -> bug at spot 6 (▲), should be ● ✓")

    print("\nALL CHECKS PASSED — every mix-up is found and fixed correctly.")
