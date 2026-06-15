"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 4
"Do They Meet?".

Both sprites run their own script on one green flag, on the shared 0..5 number
path. The COMBINED question: do the two sprites land on the SAME number (they
MEET) or not? Deciding "meet / don't meet" depends on BOTH parallel results at
once — genuine concurrency reasoning. Here the two scripts were written so the
sprites DO meet (both land on 2). Models both scripts and asserts both landings
and the meet result.

Run:  python coding/g2_block_concurrent/04_do_they_meet/solution.py
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
    bit = run(1, [(FWD, 2), (BACK, 1)])     # Bit: start 1, forward 2, back 1
    pixel = run(4, [(BACK, 1), (BACK, 1)])  # Pixel: start 4, back 1, back 1
    assert bit == 2
    assert pixel == 2
    print(f"Green flag -> Bit lands on {bit}, Pixel lands on {pixel} ✓")

    # Combined result: same number means they MEET.
    meet = bit == pixel
    assert meet is True
    print(f"They land on the SAME number ({bit}) -> they MEET ✓")

    print("\nALL CHECKS PASSED — both scripts run at once; Bit and Pixel meet on 2.")
