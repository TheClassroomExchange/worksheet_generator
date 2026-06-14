"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 1
"Put It in Order".

An algorithm is steps carried out in order. Each task is a set of lettered
step-cards shown SHUFFLED; the correct order is modelled here and the letter
sequence is asserted so the answer key cannot drift from the worksheet.

Run:  python coding/g1_unplugged_sequencing/01_put_it_in_order/solution.py
"""


def letter_order(cards, correct_actions):
    """cards: {letter: action}; correct_actions: actions in the right order.
    Returns the letters in the order the child should write."""
    by_action = {a: l for l, a in cards.items()}
    return [by_action[a] for a in correct_actions]


if __name__ == "__main__":
    # Task 1 — plant a seed (cards shown shuffled A-D).
    plant_cards = {"A": "drop the seed", "B": "water it",
                   "C": "dig a hole", "D": "cover the seed"}
    plant_steps = ["dig a hole", "drop the seed", "cover the seed", "water it"]
    assert letter_order(plant_cards, plant_steps) == ["C", "A", "D", "B"]
    print("Plant a seed: order = C, A, D, B (dig, drop, cover, water) ✓")

    # Task 2 — wash your hands (cards shown shuffled A-D).
    wash_cards = {"A": "dry hands", "B": "wet hands",
                  "C": "rub on soap", "D": "rinse hands"}
    wash_steps = ["wet hands", "rub on soap", "rinse hands", "dry hands"]
    assert letter_order(wash_cards, wash_steps) == ["B", "C", "D", "A"]
    print("Wash hands: order = B, C, D, A (wet, soap, rinse, dry) ✓")

    print("\nALL CHECKS PASSED — each task has one correct step order.")
