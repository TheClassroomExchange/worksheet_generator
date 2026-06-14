"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 4
"The Wrong Direction".

Bug type: a move goes the WRONG WAY (forward instead of back). Both sprites
should reach the goal (2). Bit is correct; Pixel's 'forward 2' sends it the wrong
direction (4 -> clamped to 5) instead of toward 2. The fix is to change the
direction to 'back 2'. Models the BUGGY run (Pixel overshoots) and the FIXED run
(Pixel on 2) and asserts both.

Run:  python coding/g2_debugging_reading/04_the_wrong_direction/solution.py
"""

LO, HI = 0, 5
GOAL = 2


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    bit = run(0, [(FWD, 2)])             # 0 -> 2  (correct)
    pixel_buggy = run(4, [(FWD, 2)])     # 4 -> 6 clamped to 5  (wrong direction)
    assert bit == GOAL
    assert pixel_buggy == 5
    assert pixel_buggy != GOAL
    print(f"BUGGY -> Bit {bit}, Pixel {pixel_buggy} (goal {GOAL}) -> Pixel went the WRONG WAY ✗")

    # FIX: change Pixel's 'forward 2' to 'back 2'.
    pixel_fixed = run(4, [(BACK, 2)])    # 4 -> 2
    assert pixel_fixed == GOAL
    print(f"FIXED -> Pixel back 2 -> {pixel_fixed} -> both reach the goal {GOAL} ✓")

    print("\nALL CHECKS PASSED — the bug was the wrong direction; forward 2 -> back 2 lands Pixel on 2.")
