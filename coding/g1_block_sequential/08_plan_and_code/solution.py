"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 8
"Plan and Code" (challenge / unit finale).

Students PLAN and write a full program to a goal, meet a harder goal (mix
forward + back), then ALTER their program to a new goal. Models sample programs
for each task and asserts they reach the goal (more than one program can work).

Run:  python coding/g1_block_sequential/08_plan_and_code/solution.py
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
    # Goal 1 — start 1, reach 5 with two move blocks. Sample: forward 2, forward 2.
    assert run(1, [(FWD, 2), (FWD, 2)]) == 5
    print("Goal 1: start 1 -> 5 = forward 2, forward 2 ✓")

    # Goal 2 (challenge) — start 2, reach 3 using ONE forward and ONE back block.
    g2 = [(FWD, 2), (BACK, 1)]
    assert run(2, g2) == 3
    assert any(s == FWD for s, _ in g2) and any(s == BACK for s, _ in g2)
    print("Goal 2: start 2 -> 3 = forward 2, back 1 (one forward + one back) ✓")

    # Ex 3 (alter Goal 1) — change one block so it reaches 4 instead of 5.
    assert run(1, [(FWD, 2), (FWD, 1)]) == 4
    print("Ex 3: change last forward 2 to forward 1 -> 4 ✓")

    print("\nALL CHECKS PASSED — plan a program, meet the goal, then alter it for a new goal.")
