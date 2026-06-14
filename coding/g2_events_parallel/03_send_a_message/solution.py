"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 3
"Send a Message".

BROADCAST -> RECEIVE: Bit's script (started by the green flag) ends with a
'broadcast go' block. Pixel's script has the hat 'when I receive go', so Pixel
only starts AFTER Bit sends the message. Each sprite moves on the shared 0..5
number path. Models the message passing — Bit runs and broadcasts, which fires
the 'receive go' event, which runs Pixel — and asserts both landings + that
Pixel ran only because it received the message.

Run:  python coding/g2_events_parallel/03_send_a_message/solution.py
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
    fired = {"green_flag"}        # clicking the flag fires the green-flag event
    messages = set()              # broadcast messages that have been sent

    # Bit: when green flag clicked -> home 0, forward 2 -> then broadcast "go".
    bit = None
    if "green_flag" in fired:
        bit = run(0, [(FWD, 2)])
        messages.add("go")        # Bit's last block broadcasts the message "go"
    assert bit == 2
    print(f"Green flag -> Bit runs -> Bit lands on {bit}, then broadcasts 'go' ✓")

    # Pixel: when I receive "go" -> home 5, back 2. Runs ONLY if "go" was sent.
    pixel = None
    if "go" in messages:
        pixel = run(5, [(BACK, 2)])
    assert pixel == 3
    print(f"Pixel receives 'go' -> Pixel runs -> Pixel lands on {pixel} ✓")

    # Without Bit's broadcast, Pixel would never start.
    pixel_no_msg = run(5, [(BACK, 2)]) if "nope" in messages else 5
    assert pixel_no_msg == 5
    print("No matching message -> Pixel stays home at 5 ✓")

    print("\nALL CHECKS PASSED — Bit broadcasts 'go'; Pixel runs only because it received it. Bit 2, Pixel 3.")
