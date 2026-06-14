"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 8
"Debug the Pair" (challenge).

The DEBUG sheet (C3.2 + C3.1): the two scripts are SUPPOSED to make Bit and
Pixel MEET on 3, but one script has a bug so they don't. The student finds the
wrong script (Pixel) and fixes it. Bit already reaches the target, so Pixel's
'back 1' must become 'back 2'. Both scripts launch together on one green flag on
the shared 0..5 path. Models the BUGGY and FIXED versions and asserts the fix
makes them meet on the target.

Run:  python coding/g2_block_concurrent/08_debug_the_pair/solution.py
"""

LO, HI = 0, 5
TARGET = 3


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Goal: both sprites should MEET on the target (3).
    bit = run(0, [(FWD, 3)])               # Bit: start 0, forward 3  (correct)
    pixel_buggy = run(5, [(BACK, 1)])      # Pixel: start 5, back 1   (BUG -> 4)
    assert bit == TARGET
    assert pixel_buggy == 4
    assert bit != pixel_buggy
    print(f"BUGGY -> Bit {bit}, Pixel {pixel_buggy} -> meet on {TARGET}? {bit == pixel_buggy} ✗")

    # Bit already lands on the target, so PIXEL's script is the wrong one.
    # Fix: 'back 1' -> 'back 2' so Pixel reaches 3.
    pixel_fixed = run(5, [(BACK, 2)])      # Pixel (fixed): start 5, back 2
    assert pixel_fixed == TARGET
    assert bit == pixel_fixed
    print(f"FIXED -> Bit {bit}, Pixel {pixel_fixed} -> meet on {TARGET}? {bit == pixel_fixed} ✓")

    print("\nALL CHECKS PASSED — Pixel's script was the bug; back 1 -> back 2 makes the pair meet on 3.")
