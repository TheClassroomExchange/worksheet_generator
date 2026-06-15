"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 3
"The Wrong Number".

Bug type: a move has the WRONG VALUE. Both sprites should reach the goal (4).
Bit is correct; Pixel's 'forward 3' lands it on 3 instead of 4 — the number is
wrong. The fix is to change Pixel's move to 'forward 4'. Models the BUGGY run
(Pixel on 3) and the FIXED run (Pixel on 4) and asserts both.

Run:  python coding/g2_debugging_reading/03_the_wrong_number/solution.py
"""

LO, HI = 0, 5
GOAL = 4


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    bit = run(1, [(FWD, 3)])             # 1 -> 4  (correct, reaches goal)
    pixel_buggy = run(0, [(FWD, 3)])     # 0 -> 3  (wrong number: forward 3)
    assert bit == GOAL
    assert pixel_buggy == 3
    assert pixel_buggy != GOAL
    print(f"BUGGY -> Bit {bit}, Pixel {pixel_buggy} (goal {GOAL}) -> Pixel's number is wrong ✗")

    # FIX: change Pixel's 'forward 3' to 'forward 4'.
    pixel_fixed = run(0, [(FWD, 4)])     # 0 -> 4
    assert pixel_fixed == GOAL
    print(f"FIXED -> Pixel forward 4 -> {pixel_fixed} -> both reach the goal {GOAL} ✓")

    print("\nALL CHECKS PASSED — the bug was a wrong number; forward 3 -> forward 4 lands Pixel on 4.")
