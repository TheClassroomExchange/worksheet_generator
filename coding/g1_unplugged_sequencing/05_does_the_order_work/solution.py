"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 5
"Does the Order Work?".

Each algorithm is a list of steps with some required precedences (step X must
come before step Y). An order WORKS only if every precedence is satisfied.
Models each algorithm, asserts works/broken, and gives the fixed order for the
broken one.

Run:  python coding/g1_unplugged_sequencing/05_does_the_order_work/solution.py
"""


def works(order, precedences):
    """True if every (before, after) precedence holds in this order."""
    pos = {s: i for i, s in enumerate(order)}
    return all(pos[a] < pos[b] for a, b in precedences)


if __name__ == "__main__":
    # Algorithm A — draw a sun. Need the circle before the rays/colour.
    a_order = ["draw a circle", "add rays", "colour it yellow"]
    a_pre = [("draw a circle", "add rays"), ("draw a circle", "colour it yellow")]
    assert works(a_order, a_pre) is True
    print("Algorithm A (draw a sun): order WORKS ✓")

    # Algorithm B — have cereal. Must pour cereal then milk, both before eating.
    b_order = ["eat it", "pour the milk", "pour the cereal in the bowl"]
    b_pre = [("pour the cereal in the bowl", "pour the milk"),
             ("pour the milk", "eat it"),
             ("pour the cereal in the bowl", "eat it")]
    assert works(b_order, b_pre) is False
    print("Algorithm B (have cereal): order does NOT work — you can't eat first ✓")

    # Algorithm C — go down the slide. Climb, then sit at the top, then slide.
    c_order = ["climb the ladder", "slide down", "sit at the top"]
    c_pre = [("climb the ladder", "sit at the top"), ("sit at the top", "slide down")]
    assert works(c_order, c_pre) is False
    print("Algorithm C (go down the slide): order does NOT work ✓")

    # Fixed order for C (Ex 3 rewrite).
    c_fixed = ["climb the ladder", "sit at the top", "slide down"]
    assert works(c_fixed, c_pre) is True
    print("Fixed C: climb the ladder, sit at the top, slide down ✓")

    print("\nALL CHECKS PASSED — an order works only when each step's needs come first.")
