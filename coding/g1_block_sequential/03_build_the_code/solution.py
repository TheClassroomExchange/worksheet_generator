"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 3
"Build the Code".

The student WRITES a program (fills the empty move blocks) to land Bit on a
target number. Models a correct program for each build task and asserts it
reaches the target. (More than one program can work; the answer key gives a
sample, and check_build verifies any candidate.)

Run:  python coding/g1_block_sequential/03_build_the_code/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


def check_build(start, target, moves, n_blocks):
    assert len(moves) == n_blocks, f"expected {n_blocks} move blocks"
    assert run(start, moves) == target, f"program does not reach {target}"
    return True


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Build 1 — start 0, target 3, two move blocks. Sample: forward 2, forward 1.
    assert check_build(0, 3, [(FWD, 2), (FWD, 1)], 2)
    print("Build 1: start 0 -> 3 = forward 2, forward 1 ✓")

    # Build 2 — start 5, target 2, two move blocks. Sample: back 2, back 1.
    assert check_build(5, 2, [(BACK, 2), (BACK, 1)], 2)
    print("Build 2: start 5 -> 2 = back 2, back 1 ✓")

    # Build 3 (challenge) — start 1, target 5, two move blocks. Sample: forward 2, forward 2.
    assert check_build(1, 5, [(FWD, 2), (FWD, 2)], 2)
    print("Build 3: start 1 -> 5 = forward 2, forward 2 ✓")

    # A second valid Build-3 program (shows there can be more than one).
    assert run(1, [(FWD, 1), (FWD, 3)]) == 5
    print("Build 3 alt: forward 1, forward 3 also reaches 5 ✓")

    print("\nALL CHECKS PASSED — each built program lands Bit on its target.")
