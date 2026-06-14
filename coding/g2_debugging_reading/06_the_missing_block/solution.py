"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 6
"The Missing Block".

Bug type: a script is MISSING a block, so it lands short of the goal. Both
sprites should meet on the goal (3). Bit is correct; Pixel has only one 'back 1'
(5 -> 4) and is missing a second move. Adding the missing 'back 1' makes Pixel
reach 3. Models the BUGGY run (Pixel short on 4) and the FIXED run (Pixel on 3)
and asserts both.

Run:  python coding/g2_debugging_reading/06_the_missing_block/solution.py
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
    bit = run(0, [(FWD, 3)])             # 0 -> 3  (correct)
    pixel_buggy = run(5, [(BACK, 1)])    # 5 -> 4  (missing a block, lands short)
    assert bit == GOAL
    assert pixel_buggy == 4
    assert pixel_buggy != GOAL
    print(f"BUGGY -> Bit {bit}, Pixel {pixel_buggy} (goal {GOAL}) -> Pixel is missing a block ✗")

    # FIX: add the missing 'back 1' block to Pixel's script.
    pixel_fixed = run(5, [(BACK, 1), (BACK, 1)])   # 5 -> 4 -> 3
    assert pixel_fixed == GOAL
    print(f"FIXED -> Pixel back 1, back 1 -> {pixel_fixed} -> both meet on the goal {GOAL} ✓")

    print("\nALL CHECKS PASSED — the bug was a missing block; adding back 1 lands Pixel on 3.")
