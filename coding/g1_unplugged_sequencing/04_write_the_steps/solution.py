"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 4
"Write the Steps".

The child writes an algorithm in order. Task 1 uses a step bank (one correct
order, modelled and asserted). Task 2 is open; a sample bedtime algorithm is
modelled to show a valid ordered answer for the key.

Run:  python coding/g1_unplugged_sequencing/04_write_the_steps/solution.py
"""


def letter_order(cards, correct_actions):
    by_action = {a: l for l, a in cards.items()}
    return [by_action[a] for a in correct_actions]


if __name__ == "__main__":
    # Task 1 — brush your teeth (step bank shuffled A-D).
    brush = {"A": "brush your teeth", "B": "wet the brush",
             "C": "rinse your mouth", "D": "put on toothpaste"}
    brush_steps = ["wet the brush", "put on toothpaste",
                   "brush your teeth", "rinse your mouth"]
    assert letter_order(brush, brush_steps) == ["B", "D", "A", "C"]
    print("Brush your teeth: order = B, D, A, C ✓")

    # The first step must be 'wet the brush'; you cannot brush before toothpaste.
    assert brush_steps[0] == "wet the brush"
    assert brush_steps.index("put on toothpaste") < brush_steps.index("brush your teeth")
    print("First step is 'wet the brush'; toothpaste comes before brushing ✓")

    # Task 2 (open) — a sample bedtime algorithm: a valid ordered list of 3-4 steps.
    bedtime = ["put on pyjamas", "brush your teeth", "read a book", "turn off the light"]
    assert 3 <= len(bedtime) <= 4
    assert bedtime[-1] == "turn off the light"
    print("Sample bedtime algorithm has 3-4 ordered steps, lights off last ✓")

    print("\nALL CHECKS PASSED — an algorithm is the steps written in the right order.")
