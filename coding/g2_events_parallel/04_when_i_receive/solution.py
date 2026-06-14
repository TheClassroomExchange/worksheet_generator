"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 4
"When I Receive".

Focus on the RECEIVE hat and the ORDER of events. Bit runs on the green flag and
broadcasts 'start'; Pixel runs only 'when I receive start'. So the ORDER is: Bit
first, then Pixel. Each sprite moves on the shared 0..5 path. Models the order
the scripts run in (a list, in event order) and asserts the order + both
landings.

Run:  python coding/g2_events_parallel/04_when_i_receive/solution.py
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
    order = []          # the order in which scripts actually run
    landings = {}
    messages = set()

    # Green flag -> Bit runs first, then broadcasts 'start'.
    landings["Bit"] = run(1, [(FWD, 3)])    # home 1, forward 3
    order.append("Bit")
    messages.add("start")
    assert landings["Bit"] == 4

    # Pixel runs only when it receives 'start' -> it runs SECOND.
    if "start" in messages:
        landings["Pixel"] = run(0, [(FWD, 2)])  # home 0, forward 2
        order.append("Pixel")
    assert landings["Pixel"] == 2

    # Order check: Bit (green flag) before Pixel (received message).
    assert order == ["Bit", "Pixel"]
    print(f"Order of events: {order[0]} first (green flag), then {order[1]} (receives 'start') ✓")
    print(f"Landings -> Bit {landings['Bit']}, Pixel {landings['Pixel']} ✓")

    print("\nALL CHECKS PASSED — Bit runs first and sends 'start'; Pixel runs second on the message. Bit 4, Pixel 2.")
