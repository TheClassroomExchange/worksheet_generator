"""
solution.py — answer-key gate for G1 · Intro Debugging · Sheet 2
"Spot the Wrong Block".

Bit has a PLAN (what each step should be) and a CODE (what is actually there).
One block in the code has the wrong number. Comparing the plan to the code finds
it. Models each code's run, the differing block, and the fix; asserts them.

Run:  python coding/g1_intro_debugging/02_spot_the_wrong_block/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


def wrong_index(plan, code):
    diffs = [i for i, (p, c) in enumerate(zip(plan, code)) if p != c]
    assert len(diffs) == 1, f"expected exactly one wrong block, got {diffs}"
    return diffs[0]


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Code A — plan: start 1, forward 2, forward 1 (-> 4).  code has forward 3 last.
    plan_a = [(FWD, 2), (FWD, 1)]
    code_a = [(FWD, 2), (FWD, 3)]
    assert run(1, plan_a) == 4
    assert run(1, code_a) == 5            # buggy run lands on 5
    i = wrong_index(plan_a, code_a)
    assert i == 1 and code_a[i] == (FWD, 3) and plan_a[i] == (FWD, 1)
    print("Code A: lands 5; wrong block = forward 3 (should be forward 1) ✓")

    # Code B — plan: start 5, back 2, back 1 (-> 2).  code has back 3 last.
    plan_b = [(BACK, 2), (BACK, 1)]
    code_b = [(BACK, 2), (BACK, 3)]
    assert run(5, plan_b) == 2
    assert run(5, code_b) == 0            # buggy run lands on 0
    j = wrong_index(plan_b, code_b)
    assert j == 1 and code_b[j] == (BACK, 3) and plan_b[j] == (BACK, 1)
    print("Code B: lands 0; wrong block = back 3 (should be back 1) ✓")

    print("\nALL CHECKS PASSED — compare the plan to the code to spot the wrong block.")
