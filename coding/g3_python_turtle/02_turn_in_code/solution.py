"""
solution.py — code-runs gate for G3 · Intro Python Turtle · Sheet 2
"Turning in Code".

A for-loop with forward + right(given angle) inside. Angles are GIVEN. We model
the path and assert moves, turns, total turning, and whether the figure closes.

Run:  python coding/g3_python_turtle/02_turn_in_code/solution.py
"""
import math


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0
        self.moves = 0; self.turns = 0; self.total_turn = 0
        self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.moves += 1
        self.path.append((round(self.x, 1), round(self.y, 1)))

    def right(self, d):
        self.heading = (self.heading - d) % 360
        self.turns += 1
        self.total_turn += d

    @property
    def closed(self):
        return self.moves >= 3 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0


def move_turn(times, step, angle):
    bit = Bit()
    for _ in range(times):
        bit.forward(step)
        bit.right(angle)
    return bit


if __name__ == "__main__":
    # Worked / Ex 1: range(3): forward(50); right(90) -> 3 moves, 3 turns (open).
    b = move_turn(3, 50, 90)
    assert b.moves == 3 and b.turns == 3 and not b.closed, (b.moves, b.turns, b.closed)
    print(f"Worked / Ex 1 (count): range(3) f50 r90 -> {b.moves} moves, {b.turns} turns (open) ✓")

    # Ex 2 (alter): range(4) -> closes into a square.
    b2 = move_turn(4, 50, 90)
    assert b2.moves == 4 and b2.closed, (b2.moves, b2.closed)
    print(f"Ex 2 (alter):          range(4) f50 r90 -> {b2.moves} moves, closes into a square ✓")

    # Ex 3 (write): range(4): forward(50); right(90).
    b3 = move_turn(4, 50, 90)
    assert b3.moves == 4 and b3.turns == 4, (b3.moves, b3.turns)
    print(f"Ex 3 (write):          range(4) f50 r90 -> {b3.moves} moves, {b3.turns} turns ✓")

    # Ex 4 (challenge): range(4) right(90) -> total turning = 360 degrees.
    assert b3.total_turn == 360, b3.total_turn
    print(f"Ex 4 (challenge):      range(4) right(90) -> total turning = {b3.total_turn}° (a full turn) ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
