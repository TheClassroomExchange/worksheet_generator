"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 4
"Forward and Back".

Sequences that MIX forward and back blocks — forward adds, back subtracts —
a computational representation of adding and subtracting within 10. Models the
landing number for each program and a build task; asserts them.

Run:  python coding/g1_block_sequential/04_forward_and_back/solution.py
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
    # Code A — start 1, forward 3, back 1 -> 3.
    assert run(1, [(FWD, 3), (BACK, 1)]) == 3
    print("Code A: start 1, forward 3, back 1 -> 3 ✓")

    # Code B — start 3, forward 1, back 2 -> 2.
    assert run(3, [(FWD, 1), (BACK, 2)]) == 2
    print("Code B: start 3, forward 1, back 2 -> 2 ✓")

    # Build C — start 2, reach 4 with one forward and one back. Sample: forward 3, back 1.
    assert run(2, [(FWD, 3), (BACK, 1)]) == 4
    print("Build C: start 2 -> 4 = forward 3, back 1 ✓")

    print("\nALL CHECKS PASSED — forward adds, back subtracts; a code can mix them.")
