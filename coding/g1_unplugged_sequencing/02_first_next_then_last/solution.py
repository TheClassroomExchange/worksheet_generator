"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 2
"First, Next, Then, Last".

Order each task's lettered step-cards using the sequence words First, Next,
Then, Last. Models the correct order and asserts the letter sequence.

Run:  python coding/g1_unplugged_sequencing/02_first_next_then_last/solution.py
"""

WORDS = ["First", "Next", "Then", "Last"]


def letter_order(cards, correct_actions):
    by_action = {a: l for l, a in cards.items()}
    return [by_action[a] for a in correct_actions]


if __name__ == "__main__":
    # Task 1 — make toast (cards shuffled A-D).
    toast = {"A": "push the lever down", "B": "get the bread",
             "C": "take out the toast", "D": "put it in the toaster"}
    toast_steps = ["get the bread", "put it in the toaster",
                   "push the lever down", "take out the toast"]
    order1 = letter_order(toast, toast_steps)
    assert order1 == ["B", "D", "A", "C"]
    print("Make toast: First B, Next D, Then A, Last C ✓")

    # Task 2 — get ready for recess (cards shuffled A-D).
    recess = {"A": "zip it up", "B": "put on your coat",
              "C": "go outside", "D": "put on your hat"}
    recess_steps = ["put on your coat", "zip it up",
                    "put on your hat", "go outside"]
    order2 = letter_order(recess, recess_steps)
    assert order2 == ["B", "A", "D", "C"]
    print("Get ready for recess: First B, Next A, Then D, Last C ✓")

    # The sequence words line up with the 4 positions.
    assert len(WORDS) == 4
    print("\nALL CHECKS PASSED — First/Next/Then/Last name the four positions in order.")
