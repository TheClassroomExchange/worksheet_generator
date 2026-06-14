"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 7
"Change One Script".

The ALTER sheet (C3.2): one move in Pixel's script is changed, and the student
describes how that change affects the combined outcome (who is ahead / whether
they meet). Both scripts run together on one green flag on the shared 0..5 path.
Models BEFORE and AFTER the change and asserts how the outcome flips from
"do not meet" to "meet".

Run:  python coding/g2_block_concurrent/07_change_one_script/solution.py
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
    # BEFORE the change.
    bit = run(0, [(FWD, 3)])               # Bit: start 0, forward 3
    pixel_before = run(5, [(BACK, 1)])     # Pixel: start 5, back 1
    assert bit == 3
    assert pixel_before == 4
    meet_before = bit == pixel_before
    assert meet_before is False
    print(f"BEFORE -> Bit {bit}, Pixel {pixel_before} -> meet? {meet_before} (Pixel is ahead) ✓")

    # AFTER the change: Pixel's 'back 1' becomes 'back 2'.
    pixel_after = run(5, [(BACK, 2)])      # Pixel: start 5, back 2
    assert pixel_after == 3
    meet_after = bit == pixel_after
    assert meet_after is True
    print(f"AFTER  -> Bit {bit}, Pixel {pixel_after} -> meet? {meet_after} (now they meet) ✓")

    # The single change flipped the combined outcome.
    assert meet_before != meet_after
    print("Changing one move (back 1 -> back 2) changed the outcome: they now MEET on 3 ✓")

    print("\nALL CHECKS PASSED — altering one block changed who's ahead and made the sprites meet.")
