"""
solution.py — code-runs gate for G3 · Debugging · Sheet 5
"Extra or Missing Block".

A loop has an EXTRA block (one too many actions) or is MISSING a needed block.
Modelled in block (counts) and turtle (square needs forward+turn) contexts.

Run:  python coding/g3_debugging/05_extra_or_missing/solution.py
"""
import math
from collections import Counter


def counts(inside, repeats):
    seq = []
    for _ in range(repeats):
        seq.extend(inside)
    return Counter(seq)


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0; self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.path.append((round(self.x, 1), round(self.y, 1)))

    def right(self, d): self.heading = (self.heading - d) % 360

    @property
    def closed(self):
        return len(self.path) > 3 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0

    @property
    def corners(self):
        return len(set(self.path))

    @property
    def is_square(self):
        return self.corners == 4 and self.closed


def square_missing_turn(times=4, step=50):
    """Buggy: only forward inside (turn is MISSING) -> a straight line."""
    b = Bit()
    for _ in range(times):
        b.forward(step)
    return b


def square_ok(times=4, step=50):
    b = Bit()
    for _ in range(times):
        b.forward(step); b.right(90)
    return b


def square_extra_turn(times=4, step=50):
    """Buggy: an EXTRA right(90) inside -> Bit turns 180 each side, no square."""
    b = Bit()
    for _ in range(times):
        b.forward(step); b.right(90); b.right(90)
    return b


if __name__ == "__main__":
    # Ex 1 (extra): want (clap, stomp); buggy (clap, stomp, stomp) -> remove extra stomp.
    bug = counts(["clap", "stomp", "stomp"], 3)
    ok = counts(["clap", "stomp"], 3)
    assert bug["stomp"] == 6 and ok["stomp"] == 3
    print("Ex 1 (extra): (clap, stomp, stomp) -> 6 stomps; REMOVE the extra stomp -> 3 ✓")

    # Ex 2 (missing): square missing the turn -> a straight line (not a square).
    assert not square_missing_turn().is_square and square_ok().is_square
    print("Ex 2 (missing): forward-only square -> a line; ADD bit.right(90) ✓")

    # Ex 3 (write): adding right(90) makes a proper square.
    assert square_ok().is_square
    print("Ex 3 (write): add right(90) -> square (4 corners) ✓")

    # Ex 4 (challenge): EXTRA turn -> Bit turns 180 per side and just goes back and
    # forth on a line (only 2 distinct points), NOT a square.
    assert not square_extra_turn().is_square and square_extra_turn().corners == 2
    print("Ex 4 (challenge): extra right(90) -> back-and-forth line (2 points), no square; REMOVE the extra turn ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
