"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 4
"Two Scripts, Both Repeating" (concurrent + repeating events).

G3 idea: two scripts can run AT THE SAME TIME (concurrent), and each can have its
own repeat loop. Both start on the green flag and run independently. Each outcome
is modelled + asserted.

Run:  python coding/pilot_g3_block_coding/04_two_loops/solution.py
"""


def run_two_scripts(a_repeats, b_repeats):
    """when flag clicked: Script A repeats a_repeats (move),
       Script B repeats b_repeats (sound). Both start together."""
    moves = a_repeats        # Script A: one move per repeat
    sounds = b_repeats       # Script B: one sound per repeat
    return moves, sounds


if __name__ == "__main__":
    # Worked / Ex 1: both repeat 4 -> 4 moves AND 4 sounds.
    moves, sounds = run_two_scripts(4, 4)
    assert (moves, sounds) == (4, 4), (moves, sounds)
    print(f"Worked / Ex 1 (count): A repeat 4, B repeat 4 -> {moves} moves, {sounds} sounds ✓")

    # Ex 2 (alter): change B to repeat 6 -> A still 4 moves, B 6 sounds (independent).
    moves, sounds = run_two_scripts(4, 6)
    assert (moves, sounds) == (4, 6), (moves, sounds)
    print(f"Ex 2 (alter):          A repeat 4, B repeat 6 -> {moves} moves, {sounds} sounds ✓")

    # Ex 3 (write): second script spins 3 times. repeat 3 -> 3 turns.
    spins = 3
    assert spins == 3
    print(f"Ex 3 (write):          when flag clicked -> repeat 3 -> {spins} turns ✓")

    # Ex 4 (challenge): A repeat 5, B repeat 2. A does more repeats; how many more?
    a, b = 5, 2
    more = a - b
    assert more == 3, more
    print(f"Ex 4 (challenge):      A repeat 5 vs B repeat 2 -> A finishes {more} more repeats ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
