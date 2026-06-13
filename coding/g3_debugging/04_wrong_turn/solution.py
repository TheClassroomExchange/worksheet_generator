"""
solution.py — code-runs gate for G3 · Debugging · Sheet 4 "The Wrong Turn".

Turtle shape loops where the TURN angle is wrong, so the shape does not close.
Correct angles are GIVEN. Each buggy/fixed case modelled.

Run:  python coding/g3_debugging/04_wrong_turn/solution.py
"""
import math


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
        return len(self.path) > 2 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0


def shape(sides, angle, step=50):
    b = Bit()
    for _ in range(sides):
        b.forward(step); b.right(angle)
    return b


if __name__ == "__main__":
    # Ex 1: triangle (3 sides) needs right 120; buggy right 90 -> does not close.
    assert not shape(3, 90).closed and shape(3, 120).closed
    print("Ex 1: triangle code right 90 -> does not close; FIX right 120 ✓")

    # Ex 2: hexagon (6 sides) needs right 60; buggy right 90 -> does not close.
    assert not shape(6, 90).closed and shape(6, 60).closed
    print("Ex 2: hexagon code right 90 -> does not close; FIX right 60 ✓")

    # Ex 3 (write): pentagon (5 sides) needs right 72.
    assert shape(5, 72).closed
    print("Ex 3 (write): pentagon -> right 72 closes it ✓")

    # Ex 4 (challenge): square (4 sides) with right 60 -> does not close; FIX right 90.
    assert not shape(4, 60).closed and shape(4, 90).closed
    print("Ex 4 (challenge): square code right 60 -> open; FIX right 90 ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
