"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 1 "What Is a Bug?".

Bit runs a number-path program (start 0..5; forward adds, back subtracts; the
path ends at 0/5 so a move past the end stops there). A bug is code that makes
Bit land on the WRONG number. Models a correct program and a buggy one and
asserts which one has the bug.

Run:  python coding/g1_intro_debugging/01_what_is_a_bug/solution.py
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
    TARGET = 4

    # Program A — start 1, forward 3 -> 4. Reaches the target: NO bug.
    assert run(1, [(FWD, 3)]) == TARGET
    print("Program A: start 1, forward 3 -> 4 (reaches target, no bug) ✓")

    # Program B — start 1, forward 1 -> 2. Misses the target: HAS a bug.
    assert run(1, [(FWD, 1)]) != TARGET
    assert run(1, [(FWD, 1)]) == 2
    print("Program B: start 1, forward 1 -> 2 (misses target 4, has a bug) ✓")

    print("\nALL CHECKS PASSED — a bug is code that lands Bit on the wrong number.")
