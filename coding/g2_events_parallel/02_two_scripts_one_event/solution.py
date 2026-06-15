"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 2
"Two Scripts, One Event".

PARALLEL scripts: BOTH Bit and Pixel have the SAME event hat — 'when green flag
clicked'. So one green-flag event starts BOTH scripts at once; they run in
parallel. Each sprite moves on the shared 0..5 number path from its own home.
The combined question is about BOTH landing numbers. Models both event-triggered
scripts and asserts both landings (and that the one event started both).

Run:  python coding/g2_events_parallel/02_two_scripts_one_event/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


def fire(scripts, fired):
    """Run every script whose trigger event has fired (parallel). Returns a dict
    of name -> landing position; scripts whose event did not fire stay home."""
    out = {}
    for name, (trigger, home, moves) in scripts.items():
        out[name] = run(home, moves) if trigger in fired else home
    return out


FWD, BACK = 1, -1

if __name__ == "__main__":
    # BOTH scripts use the same event: when green flag clicked.
    scripts = {
        "Bit": ("green_flag", 0, [(FWD, 2)]),    # home 0, forward 2
        "Pixel": ("green_flag", 5, [(BACK, 1)]),  # home 5, back 1
    }
    # One green-flag event fires -> BOTH run in parallel.
    landings = fire(scripts, {"green_flag"})
    assert landings["Bit"] == 2
    assert landings["Pixel"] == 4
    print(f"One green flag -> BOTH run -> Bit {landings['Bit']}, Pixel {landings['Pixel']} ✓")

    # The same single event started both scripts (parallel).
    assert scripts["Bit"][0] == scripts["Pixel"][0] == "green_flag"
    print("Both scripts share the SAME event hat -> they start together (parallel) ✓")

    print("\nALL CHECKS PASSED — one event starts two parallel scripts; Bit 2, Pixel 4.")
