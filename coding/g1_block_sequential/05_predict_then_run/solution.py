"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 5
"Predict, Then Run".

Read a program, PREDICT the landing number, then run to check. Models each
program's landing and one altered version; asserts them.

Run:  python coding/g1_block_sequential/05_predict_then_run/solution.py
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
    # Code A — start 0, forward 2, forward 2 -> 4.
    assert run(0, [(FWD, 2), (FWD, 2)]) == 4
    print("Code A: start 0, forward 2, forward 2 -> predict 4 ✓")

    # Code B — start 5, back 1, back 2 -> 2.
    assert run(5, [(BACK, 1), (BACK, 2)]) == 2
    print("Code B: start 5, back 1, back 2 -> predict 2 ✓")

    # Ex 3 (alter) — change Code B's 'back 2' to 'back 1' -> 5, back 1, back 1 -> 3.
    assert run(5, [(BACK, 1), (BACK, 1)]) == 3
    print("Ex 3: change back 2 to back 1 -> predict 3 ✓")

    print("\nALL CHECKS PASSED — predict by reading the blocks, then run to confirm.")
