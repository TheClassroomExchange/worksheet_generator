"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 6
"Change One Block".

Start from one base program and change exactly ONE block each time; model the
new landing number and assert it. This shows how a single edit changes the
outcome (C3.2: alter code and describe the effect).

Run:  python coding/g1_block_sequential/06_change_one_block/solution.py
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
    # Base code — start 1, forward 2, forward 1 -> 4.
    assert run(1, [(FWD, 2), (FWD, 1)]) == 4
    print("Base: start 1, forward 2, forward 1 -> 4 ✓")

    # Ex 1 — change 'forward 2' to 'forward 3': start 1, forward 3, forward 1 -> 5.
    assert run(1, [(FWD, 3), (FWD, 1)]) == 5
    print("Ex 1: forward 2 -> forward 3 gives 5 (one higher) ✓")

    # Ex 2 — change the last 'forward 1' to 'back 1': start 1, forward 2, back 1 -> 2.
    assert run(1, [(FWD, 2), (BACK, 1)]) == 2
    print("Ex 2: last forward 1 -> back 1 gives 2 (lower) ✓")

    # Ex 3 — change the start block to 'start at 0': start 0, forward 2, forward 1 -> 3.
    assert run(0, [(FWD, 2), (FWD, 1)]) == 3
    print("Ex 3: start 1 -> start 0 gives 3 (everything shifts down by 1) ✓")

    print("\nALL CHECKS PASSED — one changed block changes the result in a predictable way.")
