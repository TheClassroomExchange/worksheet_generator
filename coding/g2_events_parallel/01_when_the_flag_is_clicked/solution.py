"""
solution.py — answer-key gate for G2 · Events & Parallel Scripts · Sheet 1
"When the Flag Is Clicked".

Introduces the EVENT idea: a script does not run on its own — it waits for its
event. The hat block "when green flag clicked" starts the script when the green
flag event happens. Bit's home is 0; when the flag is clicked, Bit runs its
moves on the shared 0..5 number path. Models the event mechanic (a script runs
only if its trigger event has fired) and asserts that Bit runs and lands on 3 on
the flag, and would NOT move with no event.

Run:  python coding/g2_events_parallel/01_when_the_flag_is_clicked/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))
    return pos


def run_if_triggered(script, fired):
    """script = (trigger_event, home, moves). Runs only if its event has fired.
    Returns the landing position, or the home position if the event never fired."""
    trigger, home, moves = script
    if trigger in fired:
        return run(home, moves)
    return home  # event never happened -> script never ran, sprite stays home


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Bit's script: starts on the green-flag event, home 0, forward 3.
    bit_script = ("green_flag", 0, [(FWD, 3)])

    # Click the green flag -> the green-flag event fires.
    fired = {"green_flag"}
    bit = run_if_triggered(bit_script, fired)
    assert bit == 3
    print(f"Green flag clicked -> Bit's script runs -> Bit lands on {bit} ✓")

    # With NO event fired, the script does not run; Bit stays at home (0).
    bit_no_event = run_if_triggered(bit_script, set())
    assert bit_no_event == 0
    print(f"No event -> Bit's script does not run -> Bit stays at {bit_no_event} ✓")

    print("\nALL CHECKS PASSED — a script runs only when its event happens; the green flag starts Bit.")
