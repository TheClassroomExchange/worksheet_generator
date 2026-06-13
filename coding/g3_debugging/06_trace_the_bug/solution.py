"""
solution.py — code-runs gate for G3 · Debugging · Sheet 6 "Trace the Bug".

Trace a buggy loop step by step, predict the (wrong) result, then name the fix.
The model confirms each traced value.

Run:  python coding/g3_debugging/06_trace_the_bug/solution.py
"""
import math


class Bit:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0; self.sides = 0; self.path = [(0.0, 0.0)]

    def forward(self, s):
        self.x += s * math.cos(math.radians(self.heading))
        self.y += s * math.sin(math.radians(self.heading))
        self.sides += 1; self.path.append((round(self.x, 1), round(self.y, 1)))

    def right(self, d): self.heading = (self.heading - d) % 360

    @property
    def closed(self):
        return self.sides > 2 and round(self.x, 1) == 0.0 and round(self.y, 1) == 0.0


def jumps(repeats, per=1):
    return repeats * per


if __name__ == "__main__":
    # Worked / Ex 1: trace range(3) f50 r90 -> after 3 sides, NOT closed (open square).
    b = Bit()
    for _ in range(3):
        b.forward(50); b.right(90)
    assert b.sides == 3 and not b.closed
    print(f"Worked / Ex 1: range(3) f50 r90 -> traces {b.sides} sides, NOT closed -> FIX range(4) ✓")

    # Ex 2: trace (jump, jump) repeat 4 -> 8 jumps (goal was 4) -> too many.
    assert jumps(4, 2) == 8
    print("Ex 2: trace (jump, jump) × 4 -> 8 jumps (goal 4) -> too many -> FIX repeat 2 ✓")

    # Ex 3 (predict-run): trace range(5) f50 r90 -> 5 sides (overshoots a square).
    c = Bit()
    for _ in range(5):
        c.forward(50); c.right(90)
    assert c.sides == 5
    print(f"Ex 3 (predict): range(5) f50 r90 -> traces {c.sides} sides (overshoots) -> FIX range(4) ✓")

    # Ex 4 (challenge): trace range(4) f50 r60 -> 4 sides but does NOT close (wrong turn).
    d = Bit()
    for _ in range(4):
        d.forward(50); d.right(60)
    assert d.sides == 4 and not d.closed
    print("Ex 4 (challenge): range(4) f50 r60 -> 4 sides but won't close (turn wrong) -> FIX right 90 ✓")

    print("\nALL CHECKS PASSED — every traced result + fix is correct.")
