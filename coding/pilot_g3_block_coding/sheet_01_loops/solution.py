"""
solution.py — runnable solution + code-runs gate for
Grade 3 · Block Coding · Sheet 1 "Loops: Code That Repeats".

This is the INTERNAL artifact behind the worksheet's answer key. It models
every loop the student meets as real, executing Python (no display needed) and
asserts the expected outcome. If this script runs clean, the worksheet's loop
logic and answer key are provably correct (rubric C2 hard gate).

Run:  python coding/pilot_g3_block_coding/sheet_01_loops/solution.py
"""


class Bit:
    """A tiny turtle-style model of the Bit sprite on a grid. No GUI — we track
    position + heading so loop outcomes can be asserted deterministically."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0  # degrees, 0 = facing right (east)
        self.path = [(self.x, self.y)]
        self.total_steps = 0

    def move(self, steps):
        import math
        rad = math.radians(self.heading)
        self.x += steps * math.cos(rad)
        self.y += steps * math.sin(rad)
        self.path.append((round(self.x, 3), round(self.y, 3)))
        self.total_steps += steps

    def turn(self, degrees):  # turn right (clockwise)
        self.heading = (self.heading - degrees) % 360

    @property
    def corners(self):
        """Distinct vertices Bit visited (a closed N-gon has N corners)."""
        pts = [(round(x, 1), round(y, 1)) for x, y in self.path]
        seen, out = set(), []
        for p in pts:
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out


# ── Worked example: repeat 4 { move 10, turn 90 } → a square ────────────────
def worked_example_square():
    bit = Bit()
    for _ in range(4):          # repeat 4
        bit.move(10)
        bit.turn(90)
    return bit


# ── Exercise 1 (WRITE): draw a triangle → repeat 3 { move 10, turn 120 } ────
def exercise_1_triangle():
    bit = Bit()
    for _ in range(3):          # repeat 3
        bit.move(10)
        bit.turn(120)
    return bit


# ── Exercise 2 (ALTER + PREDICT): repeat 6 { move 10, turn 60 } → hexagon ───
def exercise_2_hexagon():
    bit = Bit()
    for _ in range(6):          # repeat 6, turn 60
        bit.move(10)
        bit.turn(60)
    return bit


# ── Exercise 3 (PREDICT total steps): repeat 3 { move 20, move 20 } ─────────
def exercise_3_total_steps():
    bit = Bit()
    for _ in range(3):          # repeat 3
        bit.move(20)
        bit.move(20)
    return bit


if __name__ == "__main__":
    sq = worked_example_square()
    assert len(sq.corners) == 4, sq.corners
    assert round(sq.x, 1) == 0.0 and round(sq.y, 1) == 0.0, (sq.x, sq.y)
    print(f"Worked example  : square — {len(sq.corners)} corners, closes back to start ✓")

    tri = exercise_1_triangle()
    assert len(tri.corners) == 3, tri.corners
    print(f"Exercise 1 (write): triangle — repeat 3, turn 120 → {len(tri.corners)} sides ✓")

    hexa = exercise_2_hexagon()
    assert len(hexa.corners) == 6, hexa.corners
    print(f"Exercise 2 (alter): hexagon — repeat 6, turn 60 → {len(hexa.corners)} sides ✓")

    ex3 = exercise_3_total_steps()
    assert ex3.total_steps == 120, ex3.total_steps
    moves = 3 * 2
    print(f"Exercise 3 (predict): repeat 3 × (move 20 + move 20) = {moves} moves = {ex3.total_steps} steps ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
