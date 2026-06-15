"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 5
"Match the Event".

Reading sheet: each script is started by a different event. Bit's hat is the
green flag; Pixel's hat is 'when I receive jump'. Bit's script broadcasts 'jump',
which MATCHES Pixel's receive hat, so Pixel runs. Models the event matching (a
receive hat runs only if the broadcast message matches it) and asserts which
event starts each script + both landings.

Run:  python coding/g2_events_parallel/05_match_the_event/solution.py
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
    # Each script's trigger event.
    bit_event = "green_flag"
    pixel_event = "receive:jump"      # Pixel runs when it receives the message "jump"
    assert bit_event == "green_flag"
    assert pixel_event == "receive:jump"
    print(f"Bit's event = {bit_event}; Pixel's event = {pixel_event} ✓")

    # Run: green flag starts Bit; Bit broadcasts "jump".
    bit = run(0, [(FWD, 1)])          # home 0, forward 1
    broadcast = "jump"
    assert bit == 1

    # Pixel's receive hat matches the broadcast "jump" -> Pixel runs.
    matches = pixel_event == f"receive:{broadcast}"
    assert matches is True
    pixel = run(4, [(BACK, 1)]) if matches else 4   # home 4, back 1
    assert pixel == 3
    print(f"Broadcast 'jump' matches Pixel's hat -> Pixel runs -> Bit {bit}, Pixel {pixel} ✓")

    print("\nALL CHECKS PASSED — Bit starts on the green flag, Pixel on the matching 'jump' message. Bit 1, Pixel 3.")
