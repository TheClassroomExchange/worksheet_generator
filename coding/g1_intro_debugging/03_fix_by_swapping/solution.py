"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 3 "Fix by Swapping".

One block points the WRONG WAY (forward where it should be back, or back where it
should be forward). Swapping its direction fixes the program. Models the buggy
run, the wrong block, and the fixed run; asserts them.

Run:  python coding/g1_intro_debugging/03_fix_by_swapping/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


def swap_dir(move):
    sign, n = move
    return (-sign, n)


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Program 1 — target 4. Buggy: start 1, forward 2, back 1 -> 2.
    p1 = [(FWD, 2), (BACK, 1)]
    assert run(1, p1) == 2
    fixed1 = [p1[0], swap_dir(p1[1])]          # back 1 -> forward 1
    assert fixed1 == [(FWD, 2), (FWD, 1)] and run(1, fixed1) == 4
    print("Program 1: swap 'back 1' -> 'forward 1' -> 4 (target) ✓")

    # Program 2 — target 1. Buggy: start 3, forward 1, back 1 -> 3.
    p2 = [(FWD, 1), (BACK, 1)]
    assert run(3, p2) == 3
    fixed2 = [swap_dir(p2[0]), p2[1]]          # forward 1 -> back 1
    assert fixed2 == [(BACK, 1), (BACK, 1)] and run(3, fixed2) == 1
    print("Program 2: swap 'forward 1' -> 'back 1' -> 1 (target) ✓")

    print("\nALL CHECKS PASSED — swap the wrong-way block to fix the program.")
