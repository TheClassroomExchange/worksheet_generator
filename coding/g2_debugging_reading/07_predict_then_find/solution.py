"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 7
"Predict, Then Find".

Combines prediction with debugging: the student first PREDICTS where both sprites
SHOULD land for the goal (4), then RUNS the code and finds the one script that is
off. Bit is correct (reaches 4); Pixel's 'forward 2' lands it on 3 — the bug.
The fix is 'forward 3'. Models the predicted/correct landing, the BUGGY run, and
the FIXED run, and asserts them.

Run:  python coding/g2_debugging_reading/07_predict_then_find/solution.py
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
    # PREDICT: for the goal, BOTH should land on 4.
    predicted = GOAL
    assert predicted == 4
    print(f"Predict -> for the goal, both sprites SHOULD land on {predicted} ✓")

    # RUN: Bit is correct; Pixel is off.
    bit = run(2, [(FWD, 2)])             # 2 -> 4  (matches the goal)
    pixel_buggy = run(1, [(FWD, 2)])     # 1 -> 3  (off by 1)
    assert bit == GOAL
    assert pixel_buggy == 3
    print(f"Run -> Bit {bit} (matches), Pixel {pixel_buggy} (off) -> Pixel's script is the bug ✗")

    # FIND & FIX: Pixel starts at 1 and needs 4, so its move should be forward 3.
    pixel_fixed = run(1, [(FWD, 3)])     # 1 -> 4
    assert pixel_fixed == GOAL
    print(f"Fix -> Pixel forward 3 -> {pixel_fixed} -> both match the prediction {GOAL} ✓")

    print("\nALL CHECKS PASSED — predict the goal (4), run to find the off script (Pixel), fix it (forward 3).")
