"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 3
"Draw a Square with a Loop".

for i in range(4): forward(s); right(90)  →  a square. Angle GIVEN. We model the
path and assert it closes (4 corners) and the perimeter (4 × side). Cross-strand
link: the path length is the square's perimeter.

Run:  python coding/g3_python_turtle/03_square_loop/solution.py
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


def square(side, times=4, angle=90):
    bit = Bit()
    for _ in range(times):
        bit.forward(side); bit.right(angle)
    return bit


if __name__ == "__main__":
    # Worked / Ex 1: range(4) f50 r90 -> square, closes, perimeter 200.
    b = square(50)
    assert len(b.corners) == 4 and b.closed and b.dist == 200, (b.corners, b.dist)
    print(f"Worked / Ex 1: range(4) f50 r90 -> square, {len(b.corners)} corners, perimeter {int(b.dist)} ✓")

    # Ex 2 (alter): forward 100 -> still a square, perimeter 400 (size changes, shape same).
    b2 = square(100)
    assert b2.closed and b2.dist == 400, b2.dist
    print(f"Ex 2 (alter): forward 100 -> still a square, perimeter {int(b2.dist)} (bigger, same shape) ✓")

    # Ex 3 (write): right 90 closes the square.
    assert square(60, angle=90).closed
    print("Ex 3 (write): range(4) f60 right 90 -> closes the square ✓")

    # Ex 4 (challenge): perimeter of the range(4) f50 square = 4 × 50 = 200.
    assert square(50).dist == 4 * 50
    print(f"Ex 4 (challenge): whole path = 4 × 50 = {4*50} (the perimeter) ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
