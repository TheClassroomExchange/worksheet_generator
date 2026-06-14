"""
solution.py — code-runs gate for K · Sequencing · Sheet 2 "What Comes First?".

Some steps must happen before others. Models which step comes FIRST in each
little two-step action and asserts it.

Run:  python coding/k_sequencing/02_what_comes_first/solution.py
"""


def comes_first(ordered_steps):
    """Given the steps already in correct order, return the first one."""
    return ordered_steps[0]


if __name__ == "__main__":
    # Slide: you must climb UP before you slide DOWN. First = up (⬆).
    assert comes_first(["up", "down"]) == "up"
    print("Slide: first ⬆ climb up, then ⬇ slide down -> first is ⬆ ✓")

    # Door: open the door, then walk through. First = open.
    assert comes_first(["open", "through"]) == "open"
    print("Door: first open, then go through -> first is 'open' ✓")

    # Shoes: sock first, then shoe. First = sock.
    assert comes_first(["sock", "shoe"]) == "sock"
    print("Shoes: first sock, then shoe -> first is 'sock' ✓")

    print("\nALL CHECKS PASSED — the first step is correct each time.")
