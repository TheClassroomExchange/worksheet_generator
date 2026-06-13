"""
solution.py — code-runs gate for G3 · Debugging · Sheet 2 "Off by One".

The repeat/range count is wrong by exactly one. Block (count) + Turtle (a square
needs range(4); off-by-one leaves it open or overshoots). All cases modelled.

Run:  python coding/g3_debugging/02_off_by_one/solution.py
"""
import math


def count(repeats):
    return repeats


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0; self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.path.append((round(self.x, 1), round(self.y, 1)))

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
        return len(self.path) > 1 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0


def square(times, step=50, angle=90):
    b = Bit()
    for _ in range(times):
        b.forward(step); b.right(angle)
    return b


if __name__ == "__main__":
    # Ex 1: want 5; code 6 (one too many) -> fix 5.
    assert count(6) != 5 and count(5) == 5
    print("Ex 1: want 5, code repeat 6 (one too many) -> FIX repeat 5 ✓")

    # Ex 2: want 6; code 5 (one too few) -> fix 6.
    assert count(5) != 6 and count(6) == 6
    print("Ex 2: want 6, code repeat 5 (one too few) -> FIX repeat 6 ✓")

    # Ex 3 (turtle): a square needs range(4); code range(5) overshoots -> fix range(4).
    assert not square(5).closed and square(4).closed and len(square(4).corners) == 4
    print("Ex 3 (turtle): square wants range(4), code range(5) -> FIX range(4) ✓")

    # Ex 4 (challenge): code range(3) draws only 3 sides (open) -> off by one -> range(4).
    assert not square(3).closed and square(4).closed
    print("Ex 4 (challenge): range(3) leaves the square open (off by one) -> FIX range(4) ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
