"""
solution.py — runnable solution + code-runs gate for
Grade 3 · Block Coding · Sheet 1 "Loops: Code That Repeats".

INTERNAL artifact behind the worksheet's answer key. The Grade-3 idea on this
sheet is the REPEAT COUNT — "how many times do the inside blocks run." Every
loop the student meets is modelled as real, executing Python and asserted, so
the answer key is provably correct (rubric C2 hard gate). No angle geometry is
required of the student; the square is only the teacher's worked example.

Run:  python coding/pilot_g3_block_coding/sheet_01_loops/solution.py
"""


class Bit:
    """A tiny model of the Bit sprite. No GUI — we just count what the loop
    does so outcomes can be asserted deterministically."""

    def __init__(self):
        import math
        self._math = math
        self.x = 0.0
        self.y = 0.0
        self.heading = 0          # 0 = facing right
        self.path = [(0.0, 0.0)]
        self.moves = 0
        self.turns = 0
        self.jumps = 0

    def move(self, steps):
        rad = self._math.radians(self.heading)
        self.x += steps * self._math.cos(rad)
        self.y += steps * self._math.sin(rad)
        self.path.append((round(self.x, 1), round(self.y, 1)))
        self.moves += 1

    def turn(self, degrees):
        self.heading = (self.heading - degrees) % 360
        self.turns += 1

    def jump(self):
        self.jumps += 1

    @property
    def corners(self):
        seen, out = set(), []
        for p in self.path:
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out


# ── Worked example: repeat 4 { move 10, turn 90 } → a square ────────────────
def worked_example(repeats=4):
    bit = Bit()
    for _ in range(repeats):
        bit.move(10)
        bit.turn(90)
    return bit


# ── Exercise 3 (WRITE): Bit jumps 5 times → repeat 5 { jump } ───────────────
def exercise_3_jump(repeats=5):
    bit = Bit()
    for _ in range(repeats):
        bit.jump()
    return bit


# ── Exercise 4 (CHALLENGE): repeat 3 { jump, jump } → 6 jumps total ─────────
# Stretch: two actions inside the loop, so total = repeats × 2 (a genuine
# step up from the single-action loops above — requires multiplying, not just
# reading the repeat number).
def exercise_4_challenge(repeats=3):
    bit = Bit()
    for _ in range(repeats):
        bit.jump()
        bit.jump()
    return bit


if __name__ == "__main__":
    # Worked example + Exercise 1 (count): repeat 4 → 4 moves, 4 turns, square.
    sq = worked_example(4)
    assert sq.moves == 4 and sq.turns == 4, (sq.moves, sq.turns)
    assert len(sq.corners) == 4, sq.corners
    print(f"Worked example / Ex 1 (count): repeat 4 -> Bit moves {sq.moves} times, "
          f"turns {sq.turns} times; draws a square ({len(sq.corners)} corners) ✓")

    # Exercise 2 (alter): change repeat 4 -> repeat 6. More moves than before.
    six = worked_example(6)
    assert six.moves == 6, six.moves
    assert six.moves > sq.moves, (six.moves, sq.moves)
    print(f"Exercise 2 (alter):            repeat 6 -> Bit moves {six.moves} times "
          f"(more than {sq.moves}) ✓")

    # Exercise 3 (write): repeat 5 { jump } -> 5 jumps.
    j = exercise_3_jump(5)
    assert j.jumps == 5, j.jumps
    print(f"Exercise 3 (write):            repeat 5 -> Bit jumps {j.jumps} times ✓")

    # Exercise 4 (challenge): repeat 3 { jump, jump } -> 6 jumps (3 × 2).
    ch = exercise_4_challenge(3)
    assert ch.jumps == 6, ch.jumps
    print(f"Exercise 4 (challenge):        repeat 3 × 2 jumps -> {ch.jumps} jumps total ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
