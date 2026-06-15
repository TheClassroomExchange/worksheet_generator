"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 8
"Debug Detective" (challenge — the final sheet of the K–G3 catalogue).

The student reads two longer (two-move) parallel scripts, names WHICH is wrong
and WHAT KIND of bug it is, fixes it, and explains. Both should meet on the goal
(3). Bit is correct; Pixel's second move 'back 3' is too big (a WRONG-NUMBER bug)
so Pixel overshoots to 1. The fix is 'back 1'. Models the BUGGY run and the FIXED
run and asserts both.

Run:  python coding/g2_debugging_reading/08_debug_detective/solution.py
"""

LO, HI = 0, 5
GOAL = 3


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    bit = run(0, [(FWD, 1), (FWD, 2)])           # 0 -> 1 -> 3  (correct)
    pixel_buggy = run(5, [(BACK, 1), (BACK, 3)])  # 5 -> 4 -> 1  (overshoots: back 3 too big)
    assert bit == GOAL
    assert pixel_buggy == 1
    assert pixel_buggy != GOAL
    print(f"BUGGY -> Bit {bit}, Pixel {pixel_buggy} (goal {GOAL}) -> Pixel overshoots: a wrong-number bug ✗")

    # FIX: Pixel's 'back 3' is too big; change it to 'back 1' so Pixel reaches 3.
    pixel_fixed = run(5, [(BACK, 1), (BACK, 1)])  # 5 -> 4 -> 3
    assert pixel_fixed == GOAL
    print(f"FIXED -> Pixel back 1, back 1 -> {pixel_fixed} -> both meet on the goal {GOAL} ✓")

    # Detective summary: which script, what kind of bug, the fix.
    assert bit == GOAL and pixel_fixed == GOAL
    print("Detective: Pixel's script was wrong; bug = a number too big (back 3); fix = back 1 ✓")

    print("\nALL CHECKS PASSED — the final catalogue sheet: diagnose, fix and explain a bug in concurrent code.")
