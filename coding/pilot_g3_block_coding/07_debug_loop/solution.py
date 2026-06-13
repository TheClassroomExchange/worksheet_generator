"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 7
"Find the Loop Bug" (C3.2 — read, find the error, fix it).

G3 idea: read a loop that does the wrong thing, find whether the bug is the
repeat count or a block inside, and fix it. Each buggy case AND its fix are
modelled + asserted, so the answer key (the correct fix) is provably right.

Run:  python coding/pilot_g3_block_coding/07_debug_loop/solution.py
"""


def jumps(repeats, per_repeat=1):
    return repeats * per_repeat


def distance(repeats, step):
    return repeats * step


if __name__ == "__main__":
    # Ex 1: should jump 5; buggy code repeat 3. Fix = repeat 5.
    assert jumps(3) != 5 and jumps(5) == 5
    print("Ex 1 (find bug):   want 5 jumps, code says repeat 3 -> FIX repeat 5 ✓")

    # Ex 2: pattern should be red, blue; buggy inside = red, red. Fix 2nd -> blue.
    buggy = ["red", "red"]; fixed = ["red", "blue"]
    assert buggy != ["red", "blue"] and fixed == ["red", "blue"]
    print("Ex 2 (fix inside): inside is (red, red) -> FIX 2nd block to blue ✓")

    # Ex 3: want 30 steps at 10 each; buggy repeat 2 (=20). Fix = repeat 3 (=30).
    assert distance(2, 10) != 30 and distance(3, 10) == 30
    print("Ex 3 (fix count):  want 30 at 10 each, code repeat 2 -> FIX repeat 3 ✓")

    # Ex 4 (challenge): repeat 4 { move, move } = 8 moves; want 4. Bug = TWO
    # move blocks inside. Fix = one move inside (repeat 4 × 1 = 4).
    assert jumps(4, 2) == 8 and jumps(4, 1) == 4
    print("Ex 4 (challenge):  repeat 4 × 2 moves = 8; want 4 -> FIX to one move inside (=4) ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
