"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 1
"Two Sprites at Once".

TWO sprites — Bit and Pixel — each run their OWN script at the same time, both
launched by one green flag. Each script moves its sprite on the shared number
path 0..5 (forward adds, back subtracts, the path ends at 0/5). The combined
question is about BOTH landing numbers. Models both scripts and asserts both
results (genuine concurrency: two scripts, one start).

Run:  python coding/g2_block_concurrent/01_two_sprites_at_once/solution.py
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
    # Both scripts launch together on the green flag.
    bit = run(1, [(FWD, 2)])      # Bit: start 1, forward 2
    pixel = run(5, [(BACK, 1)])   # Pixel: start 5, back 1
    assert bit == 3
    assert pixel == 4
    print(f"Green flag -> Bit lands on {bit}, Pixel lands on {pixel} ✓")

    # They do NOT land on the same number (3 vs 4): they do not meet here.
    assert bit != pixel
    print("Bit (3) and Pixel (4) land on different numbers ✓")

    print("\nALL CHECKS PASSED — two scripts run at once; each sprite lands on its own number.")
