"""
solution.py — answer-key gate for G2 · Debugging & Reading Code · Sheet 1
"Read Two Scripts Carefully".

Reading foundation for the subject: BOTH parallel scripts are CORRECT (no bug
yet). One green flag starts both; each sprite has two moves on the shared 0..5
number path. The student traces each script move by move and confirms the
combined outcome. Models both scripts and asserts both landings (both meet on 3).

Run:  python coding/g2_debugging_reading/01_read_two_scripts_carefully/solution.py
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
    # One green flag starts both; each has two moves. Both are correct.
    bit = run(0, [(FWD, 2), (FWD, 1)])     # 0 -> 2 -> 3
    pixel = run(5, [(BACK, 1), (BACK, 1)])  # 5 -> 4 -> 3
    assert bit == 3
    assert pixel == 3
    print(f"Read both -> Bit {bit}, Pixel {pixel} ✓")

    # Combined: both land on the same number -> they meet.
    assert bit == pixel
    print(f"Both scripts are correct -> they meet on {bit} ✓")

    print("\nALL CHECKS PASSED — careful reading of two parallel scripts: Bit 3, Pixel 3 (they meet).")
