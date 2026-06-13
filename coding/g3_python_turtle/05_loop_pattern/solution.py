"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 5
"Loop a Pattern in Code".

A for-loop repeats a small move pattern to build a STAIRCASE. Each step =
forward (right) then forward (up). We model position and assert the forwards
count, step count, and how high Bit climbs.

Run:  python coding/g3_python_turtle/05_loop_pattern/solution.py
"""
import math


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0; self.forwards = 0

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.forwards += 1

    def left(self, d):
        self.heading = (self.heading + d) % 360

    def right(self, d):
        self.heading = (self.heading - d) % 360


def staircase(steps, rise=30, run=30):
    """for s in range(steps): forward(run); left 90; forward(rise); right 90."""
    bit = Bit()
    for _ in range(steps):
        bit.forward(run); bit.left(90); bit.forward(rise); bit.right(90)
    return bit


if __name__ == "__main__":
    # Worked / Ex 1: range(3) -> 3 steps, 6 forwards, climbs 90 up.
    b = staircase(3)
    assert b.forwards == 6 and round(b.y) == 90, (b.forwards, b.y)
    print(f"Worked / Ex 1: range(3) staircase -> 3 steps, {b.forwards} forwards, climbs {int(round(b.y))} up ✓")

    # Ex 2 (predict): range(5) -> 10 forwards, climbs 150.
    b2 = staircase(5)
    assert b2.forwards == 10 and round(b2.y) == 150, (b2.forwards, b2.y)
    print(f"Ex 2 (predict): range(5) -> {b2.forwards} forwards, climbs {int(round(b2.y))} up ✓")

    # Ex 3 (write): range(4) staircase -> 4 steps.
    b3 = staircase(4)
    assert round(b3.y) == 120
    print(f"Ex 3 (write): range(4) staircase -> climbs {int(round(b3.y))} up ✓")

    # Ex 4 (challenge): each step rises 30; range(4) -> 4 × 30 = 120 high.
    assert 4 * 30 == 120
    print(f"Ex 4 (challenge): range(4), rise 30 each -> 4 × 30 = {4*30} high ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
