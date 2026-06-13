"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 7
"Fix the Turtle Code" (C3.2 — debug).

Each buggy loop AND its fix are modelled, so the answer key (the correct fix) is
provably right. 'Executes clean' via the model.

Run:  python coding/g3_python_turtle/07_fix_turtle/solution.py
"""
import math


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0
        self.dist = 0.0; self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.dist += s; self.path.append((round(self.x, 1), round(self.y, 1)))

    def right(self, d): self.heading = (self.heading - d) % 360

    @property
    def corners(self):
        seen, out = set(), []
        for p in self.path:
            if p not in seen:
                seen.add(p); out.append(p)
        return out

    @property
    def closed(self):
        return self.dist > 0 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0

    @property
    def span(self):
        """Bounding size of the figure (max extent in x or y)."""
        return max(max(abs(px), abs(py)) for px, py in self.path)


def shape(sides, step, angle):
    bit = Bit()
    for _ in range(sides):
        bit.forward(step); bit.right(angle)
    return bit


if __name__ == "__main__":
    # Ex 1: want a SQUARE; buggy range(3); fix range(4).
    assert not shape(3, 50, 90).closed
    assert len(shape(4, 50, 90).corners) == 4 and shape(4, 50, 90).closed
    print("Ex 1 (fix count): want square, code range(3) -> FIX range(4) ✓")

    # Ex 2: want a TRIANGLE; buggy right(90); fix right(120).
    assert len(shape(3, 50, 90).corners) != 3 or not shape(3, 50, 90).closed
    assert len(shape(3, 50, 120).corners) == 3 and shape(3, 50, 120).closed
    print("Ex 2 (fix angle): want triangle, code right(90) -> FIX right(120) ✓")

    # Ex 3: want a line 100 long at 20 each; buggy range(3) (=60); fix range(5).
    assert shape(3, 20, 0).dist != 100 and shape(5, 20, 0).dist == 100
    print("Ex 3 (fix count): want 100-long line at 20 each, code range(3) -> FIX range(5) ✓")

    # Ex 4 (challenge): want a BIGGER square. Buggy 'fix' = range(8) just RETRACES
    # the same square (no bigger). Correct fix = change forward, keep range(4).
    assert shape(8, 50, 90).span == shape(4, 50, 90).span    # range(8) is NOT bigger
    assert shape(4, 100, 90).span > shape(4, 50, 90).span    # forward(100) IS bigger
    assert len(shape(4, 100, 90).corners) == 4 and shape(4, 100, 90).closed
    print("Ex 4 (challenge): bigger square -> change forward (keep range(4)); range(8) just retraces ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
