"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 1
"Start and Go".

A tiny sequential interpreter for Bit on a NUMBER PATH 0..6. The green start
block sets Bit's starting number; each blue move block adds (forward) or
subtracts (back) steps. Bit cannot step off the path — it stops at 0 or at 6
(this boundary is why ORDER can matter on later sheets; here every program
stays in range so it never triggers). The RESULT is the number Bit lands on.

Run:  python coding/g1_block_sequential/01_start_and_go/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    """moves: list of (sign, n) where sign is +1 (forward) or -1 (back)."""
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))   # stay on the path
    return pos


FWD = 1
BACK = -1

if __name__ == "__main__":
    # Code A — start 0, forward 2, forward 1 -> 3.
    assert run(0, [(FWD, 2), (FWD, 1)]) == 3
    print("Code A: start 0, forward 2, forward 1 -> 3 ✓")

    # Code B — start 1, forward 3 -> 4.
    assert run(1, [(FWD, 3)]) == 4
    print("Code B: start 1, forward 3 -> 4 ✓")

    # Ex 3 (alter) — change Code B's 'forward 3' to 'forward 2' -> lands on 3.
    assert run(1, [(FWD, 2)]) == 3
    print("Ex 3: change to forward 2 -> 3 ✓")

    print("\nALL CHECKS PASSED — run the blocks in order to find the landing number.")
