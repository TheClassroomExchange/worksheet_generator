"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 5
"Build Pixel's Script".

This is the WRITE sheet (C3.1): Bit's script is GIVEN; the student writes
Pixel's script so the two sprites MEET (land on the same number) when one green
flag starts both. Bit lands on 3. Pixel starts at 5, so the intended answer is
"back 2" -> 3. Models Bit's given script and the intended Pixel answer, and
asserts they meet. (Any Pixel script that lands on 3 is correct; this models
the simplest one.)

Run:  python coding/g2_block_concurrent/05_build_pixels_script/solution.py
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
    # Bit's script is GIVEN.
    bit = run(0, [(FWD, 3)])              # Bit: start 0, forward 3
    assert bit == 3
    print(f"Given -> Bit lands on {bit} ✓")

    # The student WRITES Pixel's script so Pixel meets Bit on 3.
    # Pixel starts at 5; the simplest answer is back 2.
    pixel = run(5, [(BACK, 2)])           # Pixel (student answer): start 5, back 2
    assert pixel == 3
    print(f"Student writes Pixel -> Pixel lands on {pixel} ✓")

    # Green flag starts both: same number means they MEET.
    assert bit == pixel
    print(f"Green flag -> both land on {bit} -> they MEET ✓")

    print("\nALL CHECKS PASSED — Pixel's script (back 2) makes the two sprites meet on 3.")
