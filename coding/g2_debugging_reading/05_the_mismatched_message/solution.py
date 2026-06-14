"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 5
"The Mismatched Message".

Bug type: a broadcast and a receive use DIFFERENT words, so the receiving script
never starts. Bit broadcasts 'go'; Pixel waits for 'stop'. Because the messages
do not match, Pixel's event never fires and it stays home (misses the goal 3).
The fix is to make the two messages the same word. Models the BUGGY run (Pixel
stuck) and the FIXED run (Pixel reaches 3) and asserts both.

Run:  python coding/g2_debugging_reading/05_the_mismatched_message/solution.py
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
    bit = run(0, [(FWD, 1)])     # 0 -> 1, then broadcast "go"
    broadcast = "go"
    assert bit == 1

    # BUGGY: Pixel waits for "stop", but Bit sent "go" -> no match -> Pixel never runs.
    pixel_wait_buggy = "stop"
    pixel_home = 5
    matches_buggy = (broadcast == pixel_wait_buggy)
    pixel_buggy = run(pixel_home, [(BACK, 2)]) if matches_buggy else pixel_home
    assert matches_buggy is False
    assert pixel_buggy == 5            # stuck at home, misses the goal 3
    assert pixel_buggy != GOAL
    print(f"BUGGY -> Bit broadcasts '{broadcast}' but Pixel waits for '{pixel_wait_buggy}' -> Pixel stuck at {pixel_buggy} ✗")

    # FIX: change Pixel's hat to 'when I receive go' so the messages match.
    pixel_wait_fixed = "go"
    matches_fixed = (broadcast == pixel_wait_fixed)
    pixel_fixed = run(pixel_home, [(BACK, 2)]) if matches_fixed else pixel_home
    assert matches_fixed is True
    assert pixel_fixed == GOAL
    print(f"FIXED -> Pixel now waits for '{pixel_wait_fixed}' -> messages match -> Pixel reaches {pixel_fixed} ✓")

    print("\nALL CHECKS PASSED — the bug was a mismatched message; matching the words lets Pixel run to 3.")
