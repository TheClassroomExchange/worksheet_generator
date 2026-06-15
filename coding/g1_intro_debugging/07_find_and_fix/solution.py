"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 7 "Find and Fix".

Mixed bugs: each program has a DIFFERENT kind of bug. The child diagnoses the
kind and fixes it. Models the buggy runs and the fixed runs and asserts them.

Run:  python coding/g1_intro_debugging/07_find_and_fix/solution.py
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
    # Program A — target 4. Bug = WRONG VALUE: start 1, forward 1 -> 2.
    a = [(FWD, 1)]
    assert run(1, a) == 2
    a_fixed = [(FWD, 3)]                       # forward 1 should be forward 3
    assert run(1, a_fixed) == 4
    print("Program A: wrong value — forward 1 -> forward 3 -> 4 ✓")

    # Program B — target 3. Bug = EXTRA BLOCK: start 0, forward 2, forward 1, forward 1 -> 4.
    b = [(FWD, 2), (FWD, 1), (FWD, 1)]
    assert run(0, b) == 4
    b_fixed = [(FWD, 2), (FWD, 1)]             # remove one extra 'forward 1'
    assert run(0, b_fixed) == 3
    print("Program B: extra block — remove one 'forward 1' -> 3 ✓")

    # The two bugs are different kinds.
    assert a != a_fixed and len(b) != len(b_fixed)
    print("\nALL CHECKS PASSED — diagnose the kind of bug, then fix it.")
