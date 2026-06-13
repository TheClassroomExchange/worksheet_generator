"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 4
"Change the Shape" (C3.2 — read & alter code).

Change the range() count and the GIVEN turn angle to draw different regular
shapes. We model each polygon and assert its corner count + that it closes.

Run:  python coding/g3_python_turtle/04_change_shape/solution.py
"""
import math


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0; self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.path.append((round(self.x, 1), round(self.y, 1)))

    def right(self, d):
        self.heading = (self.heading - d) % 360

    @property
    def corners(self):
        seen, out = set(), []
        for p in self.path:
            if p not in seen:
                seen.add(p); out.append(p)
        return out

    @property
    def closed(self):
        return round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0


def shape(sides, angle, side_len=50):
    bit = Bit()
    for _ in range(sides):
        bit.forward(side_len); bit.right(angle)
    return bit


if __name__ == "__main__":
    # Square (start), triangle, hexagon, pentagon — angles GIVEN.
    sq = shape(4, 90)
    assert len(sq.corners) == 4 and sq.closed
    print(f"Square:    range(4) right 90  -> {len(sq.corners)} sides, closes ✓")

    tri = shape(3, 120)
    assert len(tri.corners) == 3 and tri.closed
    print(f"Ex 1/3 (triangle): range(3) right 120 -> {len(tri.corners)} sides, closes ✓")

    hexa = shape(6, 60)
    assert len(hexa.corners) == 6 and hexa.closed
    print(f"Ex 2 (hexagon): range(6) right 60  -> {len(hexa.corners)} sides, closes ✓")

    pent = shape(5, 72)
    assert len(pent.corners) == 5 and pent.closed
    print(f"Ex 4 (pentagon): range(5) right 72 -> {len(pent.corners)} sides, closes ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
