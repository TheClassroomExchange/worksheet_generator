"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 2
"Read Both Scripts".

Each sprite now has a TWO-move script, so there is more code to READ on each
side. Bit and Pixel still launch together on one green flag and each moves on
the shared 0..5 number path (forward adds, back subtracts, clamp to the ends).
The combined question is about BOTH landing numbers. Models both scripts and
asserts both results (genuine concurrency: two scripts, one start).

Run:  python coding/g2_block_concurrent/02_read_both_scripts/solution.py
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
    # Both scripts launch together on the green flag; each has two moves.
    bit = run(0, [(FWD, 3), (BACK, 1)])     # Bit: start 0, forward 3, back 1
    pixel = run(5, [(BACK, 2), (FWD, 1)])   # Pixel: start 5, back 2, forward 1
    assert bit == 2
    assert pixel == 4
    print(f"Green flag -> Bit lands on {bit}, Pixel lands on {pixel} ✓")

    # They do NOT land on the same number (2 vs 4): they do not meet here.
    assert bit != pixel
    print("Bit (2) and Pixel (4) land on different numbers ✓")

    print("\nALL CHECKS PASSED — read both two-move scripts; each sprite lands on its own number.")
