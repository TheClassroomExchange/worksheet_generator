"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 2
"Which One Is Wrong?".

Diagnosis: both sprites are supposed to MEET on the goal (3), but one script
misses. Bit reaches 3 (correct); Pixel lands on 4 (buggy). Because Bit already
meets the goal, the bug must be in PIXEL's script. The student identifies WHICH
of the two parallel scripts is wrong by comparing each to the goal. Models both
landings and asserts which one misses the goal.

Run:  python coding/g2_debugging_reading/02_which_one_is_wrong/solution.py
"""

LO, HI = 0, 5
GOAL = 3


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Goal: both should meet on 3.
    bit = run(0, [(FWD, 3)])       # 0 -> 3  (correct, reaches goal)
    pixel = run(5, [(BACK, 1)])    # 5 -> 4  (buggy, misses goal)
    assert bit == GOAL
    assert pixel == 4
    print(f"Run -> Bit {bit}, Pixel {pixel} (goal {GOAL}) ✓")

    # Diagnosis: the script that misses the goal is the wrong one.
    wrong = "Bit" if bit != GOAL else ("Pixel" if pixel != GOAL else None)
    assert wrong == "Pixel"
    off_by = abs(pixel - GOAL)
    assert off_by == 1
    print(f"Bit reaches {GOAL}; Pixel misses it (on {pixel}, off by {off_by}) -> {wrong}'s script is wrong ✓")

    print("\nALL CHECKS PASSED — compare each script to the goal; Pixel's script is the buggy one.")
