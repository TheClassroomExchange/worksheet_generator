"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 6
"Read the Turtle Code" (C3.2 — read & predict).

Trace each loop; the model confirms the prediction (shape, side count, total
length, end position). 'Executes clean' via the model.

Run:  python coding/g3_python_turtle/06_read_turtle/solution.py
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
    def left(self, d): self.heading = (self.heading + d) % 360

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


def shape(sides, step, angle, turn="right"):
    bit = Bit()
    for _ in range(sides):
        bit.forward(step)
        (bit.right if turn == "right" else bit.left)(angle)
    return bit


def line(times, step):
    bit = Bit()
    for _ in range(times):
        bit.forward(step)
    return bit


if __name__ == "__main__":
    sq = shape(4, 30, 90)                     # Ex 1
    assert len(sq.corners) == 4 and sq.closed
    print(f"Ex 1 (read): range(4) f30 r90 -> square ({len(sq.corners)} sides) ✓")

    tri = shape(3, 40, 120, turn="left")      # Ex 2
    assert len(tri.corners) == 3 and tri.closed
    print(f"Ex 2 (read): range(3) f40 left120 -> triangle ({len(tri.corners)} sides) ✓")

    ln = line(5, 20)                          # Ex 3
    assert ln.dist == 100 and len(ln.corners) == 6
    print(f"Ex 3 (predict): range(5) f20 -> straight line, length {int(ln.dist)} ✓")

    end = shape(4, 50, 90)                     # Ex 4
    assert end.closed
    print("Ex 4 (challenge): range(4) f50 r90 -> Bit ends back at the start ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
