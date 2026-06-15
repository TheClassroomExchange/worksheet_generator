"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 8
"Debug Detective" (challenge / unit finale).

A longer program (4 move blocks) has one wrong-way block. The child finds it,
fixes it, explains why, then makes their own buggy program. Models the buggy
run, the fix, and a sample make-your-own bug; asserts them.

Run:  python coding/g1_intro_debugging/08_debug_detective/solution.py
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
    # Mystery program — target 4. start 0, forward 2, back 1, forward 1 -> 2.
    buggy = [(FWD, 2), (BACK, 1), (FWD, 1)]
    assert run(0, buggy) == 2
    # The wrong-way block is 'back 1'; swap it to 'forward 1'.
    fixed = [(FWD, 2), (FWD, 1), (FWD, 1)]
    assert run(0, fixed) == 4
    print("Mystery: swap the wrong-way 'back 1' -> 'forward 1' -> 4 (target) ✓")

    # Ex 3 (sample make-your-own) — a buggy program with one bug + its fix.
    my_target = 3
    my_buggy = [(FWD, 1), (FWD, 1)]            # start 0 -> 2 (one short of 3)
    assert run(0, my_buggy) != my_target
    my_fixed = [(FWD, 1), (FWD, 1), (FWD, 1)]  # add the missing block
    assert run(0, my_fixed) == my_target
    print("Sample make-your-own: missing-block bug, add 'forward 1' -> 3 ✓")

    print("\nALL CHECKS PASSED — find the bug, fix it, explain it, and make your own.")
