"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 5 "The Extra Block".

The program OVERSHOOTS the target because it has one extra block. Removing the
extra block fixes it. Models the buggy run and the fixed run (with the extra
block removed) and asserts them.

Run:  python coding/g1_intro_debugging/05_the_extra_block/solution.py
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
    # Program 1 — target 4. Buggy: start 1, forward 2, forward 1, forward 1 -> 5.
    p1 = [(FWD, 2), (FWD, 1), (FWD, 1)]
    assert run(1, p1) == 5
    fixed1 = [(FWD, 2), (FWD, 1)]            # remove ONE extra 'forward 1'
    assert run(1, fixed1) == 4
    print("Program 1: remove one extra 'forward 1' -> 4 (target) ✓")

    # Program 2 — target 1. Buggy: start 0, forward 2, back 1, back 1 -> 0.
    p2 = [(FWD, 2), (BACK, 1), (BACK, 1)]
    assert run(0, p2) == 0
    fixed2 = [(FWD, 2), (BACK, 1)]           # remove ONE extra 'back 1'
    assert run(0, fixed2) == 1
    print("Program 2: remove one extra 'back 1' -> 1 (target) ✓")

    print("\nALL CHECKS PASSED — remove the extra block to stop overshooting.")
