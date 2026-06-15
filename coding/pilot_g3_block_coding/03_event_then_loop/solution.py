"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 3
"Start It, Then Repeat".

G3 idea: an EVENT (when flag clicked / when sprite clicked / when key pressed)
starts a script, and a repeat loop inside it then runs. Fire the event again and
the loop runs again. Every outcome is modelled + asserted.

Run:  python coding/pilot_g3_block_coding/03_event_then_loop/solution.py
"""


class Bit:
    def __init__(self):
        self.moves = 0
        self.inside_runs = 0

    def run_loop(self, repeats, blocks_inside=1):
        """One firing of the event runs the loop once (repeats × inside)."""
        for _ in range(repeats):
            self.inside_runs += 1
            self.moves += blocks_inside


if __name__ == "__main__":
    # Worked / Ex 1: when clicked -> repeat 3 { 2 blocks }. Inside runs 3 times.
    b = Bit(); b.run_loop(3, blocks_inside=2)
    assert b.inside_runs == 3, b.inside_runs
    print(f"Worked / Ex 1 (count): event -> repeat 3 -> inside runs {b.inside_runs} times ✓")

    # Ex 3 (write): when SPACE pressed -> repeat 4 { turn }. 4 turns per firing.
    b3 = Bit(); b3.run_loop(4)
    assert b3.moves == 4, b3.moves
    print(f"Ex 3 (write):          when space pressed -> repeat 4 -> {b3.moves} turns ✓")

    # Ex 4 (challenge): when flag clicked -> repeat 5 { move }. Click ONCE = 5,
    # click TWICE = the event fires twice = 10.
    once = Bit(); once.run_loop(5)
    twice = Bit(); twice.run_loop(5); twice.run_loop(5)
    assert once.moves == 5 and twice.moves == 10, (once.moves, twice.moves)
    print(f"Ex 4 (challenge):      flag once -> {once.moves} moves; flag twice -> {twice.moves} moves ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
