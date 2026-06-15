"""
solution.py — code-runs gate for K · Sequencing · Sheet 8 "Fix the Order".

A buggy arrow program does not reach the star. Models WHERE the program goes
wrong and HOW to fix it (the corrected program lands on the star) and asserts it.

Run:  python coding/k_sequencing/08_fix_the_order/solution.py
"""


def land(start, program):
    pos = start
    for m in program:
        pos += 1 if m == "right" else -1
    return pos


if __name__ == "__main__":
    # Model: start box 1, star box 3. Buggy ➡ ⬅ ➡ -> box 2 (the ⬅ is wrong).
    buggy = ["right", "left", "right"]
    assert land(1, buggy) == 2          # does not reach the star (box 3)
    fixed = ["right", "right"]           # remove the ⬅
    assert land(1, fixed) == 3
    print("Model: ➡ ⬅ ➡ lands box 2; the ⬅ is the bug -> fix to ➡ ➡ (box 3) ✓")

    # Ex 1: start box 1, star box 4. Buggy ➡ ➡ -> box 3 (one step missing).
    assert land(1, ["right", "right"]) == 3
    assert land(1, ["right", "right", "right"]) == 4   # add one ➡
    print("Ex 1: ➡ ➡ lands box 3; missing a step -> add ➡ to reach box 4 ✓")

    # Ex 2: start box 1, star box 2. Buggy ➡ ➡ -> box 3 (one step too many).
    assert land(1, ["right", "right"]) == 3
    assert land(1, ["right"]) == 2                      # remove one ➡
    print("Ex 2: ➡ ➡ lands box 3; one too many -> remove a ➡ to reach box 2 ✓")

    # Ex 3 (you try): start box 1, star box 3. Buggy ⬅ ➡ ➡ -> box 2 (first ⬅ wrong).
    assert land(1, ["left", "right", "right"]) == 2
    assert land(1, ["right", "right"]) == 3            # the ⬅ should be ➡ (or removed)
    print("Ex 3: ⬅ ➡ ➡ lands box 2; first ⬅ is wrong -> ➡ ➡ reaches box 3 ✓")

    print("\nALL CHECKS PASSED — every fix makes the program reach the star.")
