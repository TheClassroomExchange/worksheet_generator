"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 7
"Fix the Code".

Debugging: a program is supposed to reach a TARGET but one block is wrong, so
Bit misses it. Models the buggy program (it misses), finds the wrong block, and
models the fixed program (it reaches the target). Asserts each.

Run:  python coding/g1_block_sequential/07_fix_the_code/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1


def find_bug(start, moves, target):
    """Return the index of the one block whose direction flip makes the program
    reach the target (the wrong block)."""
    fixes = []
    for i, (sign, n) in enumerate(moves):
        flipped = list(moves)
        flipped[i] = (-sign, n)
        if run(start, flipped) == target:
            fixes.append(i)
    assert len(fixes) == 1, f"expected one fixable block, got {fixes}"
    return fixes[0]


if __name__ == "__main__":
    TARGET = 4
    # Buggy code — start 1, forward 2, back 1 -> 2 (should reach 4).
    buggy = [(FWD, 2), (BACK, 1)]
    assert run(1, buggy) == 2 and run(1, buggy) != TARGET
    print("Buggy: start 1, forward 2, back 1 -> 2 (misses target 4) ✓")

    # Ex 2 — the wrong block is the last one (back 1); flipping it reaches 4.
    i = find_bug(1, buggy, TARGET)
    assert i == 1 and buggy[i] == (BACK, 1)
    print("Ex 2: the wrong block is 'back 1' (moves Bit away from 4) ✓")

    # Ex 3 — fix: change 'back 1' to 'forward 1' -> start 1, forward 2, forward 1 -> 4.
    fixed = [(FWD, 2), (FWD, 1)]
    assert run(1, fixed) == TARGET
    print("Ex 3: fixed code (back 1 -> forward 1) -> 4 (the target) ✓")

    print("\nALL CHECKS PASSED — find the wrong block, fix it, Bit reaches the target.")
