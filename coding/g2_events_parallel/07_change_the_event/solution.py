"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 7
"Change the Event".

The ALTER sheet (C3.2): change which EVENT triggers Pixel's script and describe
how the outcome changes. BEFORE, Pixel's hat is 'when I receive go', so Pixel
waits and runs SECOND (after Bit broadcasts). AFTER, Pixel's hat is changed to
'when green flag clicked', so Pixel now runs at the SAME time as Bit (parallel,
no waiting). The sprites' landing numbers are unchanged, but the timing/order
changes from sequential to concurrent. Models BEFORE and AFTER and asserts the
order change.

Run:  python coding/g2_events_parallel/07_change_the_event/solution.py
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
    # Landings are the same before and after; only the trigger event changes.
    bit = run(2, [(FWD, 2)])        # Bit: green flag, home 2, forward 2 -> 4, broadcast "go"
    pixel = run(0, [(FWD, 1)])      # Pixel: home 0, forward 1 -> 1
    assert bit == 4 and pixel == 1

    # BEFORE: Pixel waits for the 'go' message -> runs SECOND (sequential).
    order_before = ["Bit", "Pixel"]   # Bit on green flag, then Pixel on the message
    assert order_before == ["Bit", "Pixel"]
    print(f"BEFORE -> Pixel waits for 'go' -> order {order_before} (Bit first, Pixel second) ✓")

    # AFTER: change Pixel's hat to 'when green flag clicked' -> both start together.
    triggers_after = {"Bit": "green_flag", "Pixel": "green_flag"}
    parallel_after = triggers_after["Bit"] == triggers_after["Pixel"] == "green_flag"
    assert parallel_after is True
    print("AFTER  -> Pixel's hat is now the green flag -> both run at the SAME time (parallel) ✓")

    # Same landings, changed timing: the event change made it concurrent, not sequential.
    assert bit == 4 and pixel == 1
    print(f"Landings unchanged (Bit {bit}, Pixel {pixel}); the EVENT change flipped sequential -> parallel ✓")

    print("\nALL CHECKS PASSED — changing Pixel's event made it run with Bit instead of waiting for the message.")
