"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 2
"Loops That Make Patterns".

The G3 idea: a repeat loop runs EVERY block inside it each time around, so a loop
with two stamp blocks builds a repeating pattern. Each loop the student meets is
modelled as executing Python and asserted, so the answer key is provably correct.

Run:  python coding/pilot_g3_block_coding/02_loops_draw/solution.py
"""


class Bit:
    """Models Bit stamping beads/shapes. We record the stamp sequence so the
    pattern AND the total count can be asserted."""

    def __init__(self):
        self.stamps = []

    def stamp(self, symbol):
        self.stamps.append(symbol)

    @property
    def count(self):
        return len(self.stamps)


def repeat_pattern(inside, repeats):
    """repeat <repeats> { stamp each symbol in `inside` }."""
    bit = Bit()
    for _ in range(repeats):
        for sym in inside:
            bit.stamp(sym)
    return bit


if __name__ == "__main__":
    # Worked example / Ex 1: repeat 3 { stamp red, stamp blue } -> 6 beads, R B R B R B
    ex = repeat_pattern(["R", "B"], 3)
    assert ex.count == 6, ex.count
    assert ex.stamps == list("RBRBRB"), ex.stamps
    print(f"Worked / Ex 1 (count): repeat 3 × 2 stamps -> {ex.count} beads, "
          f"pattern {''.join(ex.stamps)} ✓")

    # Ex 2 (alter + predict): change repeat 3 -> repeat 4 -> 8 beads
    e2 = repeat_pattern(["R", "B"], 4)
    assert e2.count == 8, e2.count
    print(f"Ex 2 (alter):          repeat 4 × 2 stamps -> {e2.count} beads ✓")

    # Ex 3 (write): repeat 5 { stamp heart, stamp star } -> 10 stamps
    e3 = repeat_pattern(["♥", "★"], 5)
    assert e3.count == 10, e3.count
    print(f"Ex 3 (write):          repeat 5 × 2 stamps -> {e3.count} stamps ✓")

    # Ex 4 (challenge): THREE stamps inside, repeat 3 -> 9 stamps, ●▲■ ●▲■ ●▲■
    e4 = repeat_pattern(["●", "▲", "■"], 3)
    assert e4.count == 9, e4.count
    assert e4.stamps == list("●▲■●▲■●▲■"), e4.stamps
    print(f"Ex 4 (challenge):      repeat 3 × 3 stamps -> {e4.count} stamps, "
          f"pattern {''.join(e4.stamps)} ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
