"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 8
"Debug the Events" (challenge).

The DEBUG sheet (C3.2 + C3.1): both sprites are supposed to run, but Pixel never
moves. The bug is a MESSAGE MISMATCH — Bit broadcasts 'go' but Pixel's hat waits
for 'jump', so Pixel's receive event never fires. The student finds the mismatch
and fixes it (make the two messages the same). Models the BUGGY run (Pixel stuck
at home) and the FIXED run (messages match, Pixel runs) and asserts both.

Run:  python coding/g2_events_parallel/08_debug_the_events/solution.py
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
    # Bit: green flag -> home 0, forward 2 -> broadcast "go".
    bit = run(0, [(FWD, 2)])
    broadcast = "go"
    assert bit == 2

    # BUGGY: Pixel waits for "jump", but Bit sent "go" -> messages do NOT match.
    pixel_wait_for = "jump"
    pixel_home = 5
    matches_buggy = (broadcast == pixel_wait_for)
    pixel_buggy = run(pixel_home, [(BACK, 2)]) if matches_buggy else pixel_home
    assert matches_buggy is False
    assert pixel_buggy == 5      # Pixel never received its message -> stays home
    print(f"BUGGY -> Bit {bit}; Pixel waits for '{pixel_wait_for}' but Bit sent '{broadcast}' -> Pixel stuck at {pixel_buggy} ✗")

    # FIX: change Pixel's hat to 'when I receive go' so the messages match.
    pixel_wait_fixed = "go"
    matches_fixed = (broadcast == pixel_wait_fixed)
    pixel_fixed = run(pixel_home, [(BACK, 2)]) if matches_fixed else pixel_home
    assert matches_fixed is True
    assert pixel_fixed == 3
    print(f"FIXED -> Pixel now waits for '{pixel_wait_fixed}' -> messages match -> Pixel runs to {pixel_fixed} ✓")

    print("\nALL CHECKS PASSED — the bug was a message mismatch; matching the messages makes Pixel run. Bit 2, Pixel 3.")
