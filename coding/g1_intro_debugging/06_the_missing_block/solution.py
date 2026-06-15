"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 6 "The Missing Block".

The program FALLS SHORT of the target because a block is missing. Adding the
missing block fixes it. Models the short run and the fixed run (with the missing
block added) and asserts them.

Run:  python coding/g1_intro_debugging/06_the_missing_block/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Program 1 — target 4. Short: start 1, forward 2 -> 3. Add 'forward 1'.
    p1 = [(FWD, 2)]
    assert run(1, p1) == 3
    fixed1 = p1 + [(FWD, 1)]
    assert run(1, fixed1) == 4
    print("Program 1: add 'forward 1' -> 4 (target) ✓")

    # Program 2 — target 1. Short: start 4, back 1 -> 3. Add 'back 2'.
    p2 = [(BACK, 1)]
    assert run(4, p2) == 3
    fixed2 = p2 + [(BACK, 2)]
    assert run(4, fixed2) == 1
    print("Program 2: add 'back 2' -> 1 (target) ✓")

    print("\nALL CHECKS PASSED — add the missing block to reach the target.")
