"""
solution.py — code-runs gate for G3 · Debugging · Sheet 3
"The Wrong Block Inside".

The repeat count is right but a BLOCK inside the loop is wrong. Modelled in both
a block (clap/stomp counts) and turtle (forward+turn vs forward+forward) context.

Run:  python coding/g3_debugging/03_wrong_block/solution.py
"""
import math
from collections import Counter


def pattern_counts(inside, repeats):
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


if __name__ == "__main__":
    # Ex 1: want clap+stomp; buggy clap+clap -> fix 2nd to stomp.
    buggy = pattern_counts(["clap", "clap"], 3)
    fixed = pattern_counts(["clap", "stomp"], 3)
    assert "stomp" not in buggy and fixed["stomp"] == 3 and fixed["clap"] == 3
    print("Ex 1: want (clap, stomp), code (clap, clap) -> FIX 2nd block to stomp ✓")

    # Ex 2/Worked (turtle): square needs forward+right; buggy forward+forward (no turn)
    # -> a straight line, not a square.
    line = Bit()
    for _ in range(4):
        line.forward(50); line.forward(50)     # buggy: two forwards, no turn
    assert not line.closed
    sq = Bit()
    for _ in range(4):
        sq.forward(50); sq.right(90)           # fixed
    assert sq.closed and sq.corners == 4
    print("Ex 2: square code has (forward, forward) -> a line; FIX 2nd block to right(90) ✓")

    # Ex 3 (write): want jump+spin; buggy jump+jump -> fix 2nd to spin.
    b = pattern_counts(["jump", "jump"], 4)
    f = pattern_counts(["jump", "spin"], 4)
    assert "spin" not in b and f["spin"] == 4
    print("Ex 3 (write): want (jump, spin), code (jump, jump) -> FIX 2nd block to spin ✓")

    # Ex 4 (challenge): buggy (forward, forward) repeat 4 -> straight line of 8 forwards,
    # not a square. The wrong block is the 2nd forward; it should be a turn.
    assert not line.closed and len(line.path) - 1 == 8
    print("Ex 4 (challenge): (forward, forward)×4 -> 8 forwards in a line, not a square -> turn is missing ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
