"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 6
"Predict With Events".

The C4-L4 'predict what happens when both start' sheet, with events: the student
PREDICTS where BOTH sprites land BEFORE running. Bit runs on the green flag and
broadcasts 'go'; Pixel runs 'when I receive go'. Predicting must account for the
event chain (Pixel only runs because Bit's message reaches it). Models both
scripts and asserts both predicted landings.

Run:  python coding/g2_events_parallel/06_predict_with_events/solution.py
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
    # Bit: green flag -> home 1, forward 3 -> broadcast "go".
    bit = run(1, [(FWD, 3)])
    broadcast = "go"
    assert bit == 4

    # Pixel: when I receive "go" -> home 5, back 2. Runs because the message matches.
    pixel = run(5, [(BACK, 2)]) if broadcast == "go" else 5
    assert pixel == 3
    print(f"Predict -> Bit {bit}, Pixel {pixel} ✓")

    # The event chain: green flag starts Bit; Bit's broadcast 'go' starts Pixel.
    assert bit == 4 and pixel == 3
    print("Event chain: green flag -> Bit (broadcasts 'go') -> Pixel runs on the message ✓")

    print("\nALL CHECKS PASSED — predict both with events; Bit 4, Pixel 3 (Pixel runs on Bit's 'go').")
