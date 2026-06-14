"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 3
"Who Is Ahead?".

Both sprites run their own script on one green flag, on the shared 0..5 number
path. The COMBINED question is a comparison: after both scripts run, which
sprite is on the HIGHER number (ahead), and by how many. Comparing the two
landing numbers is reasoning about the parallel result together — that is what
keeps the concurrency genuine. Models both scripts and asserts both landings,
who is ahead, and the gap.

Run:  python coding/g2_block_concurrent/03_who_is_ahead/solution.py
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
    bit = run(0, [(FWD, 4), (BACK, 1)])     # Bit: start 0, forward 4, back 1
    pixel = run(3, [(FWD, 1), (FWD, 1)])    # Pixel: start 3, forward 1, forward 1
    assert bit == 3
    assert pixel == 5
    print(f"Green flag -> Bit lands on {bit}, Pixel lands on {pixel} ✓")

    # Compare the two combined landings: the higher number is "ahead".
    ahead = "Pixel" if pixel > bit else "Bit"
    gap = abs(pixel - bit)
    assert ahead == "Pixel"
    assert gap == 2
    print(f"{ahead} is ahead by {gap} (on the higher number) ✓")

    print("\nALL CHECKS PASSED — compare both landings; Pixel (5) is ahead of Bit (3) by 2.")
