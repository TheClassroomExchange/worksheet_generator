"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 1
"Meet Python Turtle".

First typed code, shown as a for-loop (the same repeat the student knows from
blocks, now in Python). We MODEL the turtle path (no GUI): forward() advances Bit
along its heading. Every outcome is asserted, so the answer key is provably
correct and "executes clean" via the model.

Run:  python coding/g3_python_turtle/01_meet_turtle/solution.py
"""
import math


class Bit:
    """A modelled turtle. Tracks position + heading so figures/positions can be
    asserted without a GUI."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0      # degrees; 0 = east
        self.moves = 0
        self.distance = 0.0

    def forward(self, steps):
        self.x += steps * math.cos(math.radians(self.heading))
        self.y += steps * math.sin(math.radians(self.heading))
        self.moves += 1
        self.distance += steps

    def right(self, deg):
        self.heading = (self.heading - deg) % 360

    def left(self, deg):
        self.heading = (self.heading + deg) % 360


def forward_loop(times, step):
    """for s in range(times): bit.forward(step)."""
    bit = Bit()
    for _ in range(times):
        bit.forward(step)
    return bit


if __name__ == "__main__":
    # Worked / Ex 1: for step in range(3): bit.forward(20) -> 3 moves, 60 steps.
    b = forward_loop(3, 20)
    assert b.moves == 3 and b.distance == 60, (b.moves, b.distance)
    print(f"Worked / Ex 1 (count): range(3), forward(20) -> {b.moves} moves, {int(b.distance)} steps ✓")

    # Ex 2 (alter): range(5) -> 5 moves, 100 steps.
    b2 = forward_loop(5, 20)
    assert b2.moves == 5 and b2.distance == 100, (b2.moves, b2.distance)
    print(f"Ex 2 (alter):          range(5), forward(20) -> {b2.moves} moves, {int(b2.distance)} steps ✓")

    # Ex 3 (write): range(4), forward(10) -> 4 moves, 40 steps.
    b3 = forward_loop(4, 10)
    assert b3.moves == 4 and b3.distance == 40, (b3.moves, b3.distance)
    print(f"Ex 3 (write):          range(4), forward(10) -> {b3.moves} moves, {int(b3.distance)} steps ✓")

    # Ex 4 (challenge): range(4), forward(25) -> total 100 steps.
    b4 = forward_loop(4, 25)
    assert b4.distance == 100, b4.distance
    print(f"Ex 4 (challenge):      range(4), forward(25) -> {int(b4.distance)} steps total ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
