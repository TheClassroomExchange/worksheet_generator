"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 4
"Put It Back in Order".

Two re-ordering bugs:
  • Program 1 — the start block is not first (a program must BEGIN with start);
    fix by moving the start block to the top.
  • Program 2 — two move blocks are in the wrong order, and because the path
    ends at 5 the order changes the result; fix by swapping them.
Models the buggy and fixed runs and asserts them.

Run:  python coding/g1_intro_debugging/04_put_it_back_in_order/solution.py
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
    # Program 1 — target 4. Blocks (top to bottom): forward 2, start at 1, forward 1.
    # The start block is in the middle. A program must begin with start; reorder:
    # start at 1, forward 2, forward 1 -> 4.
    fixed1 = [(FWD, 2), (FWD, 1)]
    assert run(1, fixed1) == 4
    print("Program 1: move 'start at 1' to the top -> start 1, forward 2, forward 1 -> 4 ✓")

    # Program 2 — target 4, start 3. Buggy order: forward 3, back 2.
    #   3 -> forward 3 stops at 5 -> back 2 -> 3  (misses 4).
    assert run(3, [(FWD, 3), (BACK, 2)]) == 3
    # Fix: swap the two move blocks -> back 2, forward 3.
    #   3 -> back 2 -> 1 -> forward 3 -> 4.
    assert run(3, [(BACK, 2), (FWD, 3)]) == 4
    print("Program 2: swap the moves -> back 2, forward 3 -> 4 ✓")

    print("\nALL CHECKS PASSED — fix the bug by putting the blocks back in order.")
