"""
solution.py — answer-key gate for G2 · Block Coding (Concurrent) · Sheet 6
"Predict Both".

The C4-L4 "predict what happens when both start" sheet: the student PREDICTS
where BOTH sprites land BEFORE running, then runs to check. Both scripts launch
together on one green flag on the shared 0..5 path. Models both scripts and
asserts both predicted landings (and that they do not meet).

Run:  python coding/g2_block_concurrent/06_predict_both/solution.py
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
    # Both scripts launch together on the green flag.
    bit = run(0, [(FWD, 2), (FWD, 1)])      # Bit: start 0, forward 2, forward 1
    pixel = run(5, [(BACK, 2), (BACK, 1)])  # Pixel: start 5, back 2, back 1
    assert bit == 3
    assert pixel == 2
    print(f"Green flag -> Bit lands on {bit}, Pixel lands on {pixel} ✓")

    # Combined prediction: different numbers -> they do NOT meet.
    assert bit != pixel
    print("Predicted: Bit 3, Pixel 2 -> they do NOT meet (adjacent) ✓")

    print("\nALL CHECKS PASSED — predict both landings; Bit 3 and Pixel 2 when the green flag starts both.")
