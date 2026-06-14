"""
solution.py — code-runs gate for G3 · Debugging · Sheet 7 "More Than One Fix".

Some loop bugs have TWO valid fixes (change the repeat count OR change the inside
blocks). The model confirms both fixes reach the goal.

Run:  python coding/g3_debugging/07_two_fixes/solution.py
"""


def total(repeats, per_repeat):
    return repeats * per_repeat


if __name__ == "__main__":
    # Worked: want 4 claps. Buggy (clap, clap) × 4 = 8.
    # Fix A: repeat 2 (2 × 2 = 4).  Fix B: one clap inside (1 × 4 = 4).
    assert total(4, 2) == 8
    assert total(2, 2) == 4 and total(4, 1) == 4
    print("Worked: want 4, code (clap,clap)×4 = 8 -> Fix A repeat 2, Fix B one clap inside (both = 4) ✓")

    # Ex 1: want 6 claps. Buggy (clap, clap) × 6 = 12.
    # Fix A: repeat 3.  Fix B: one clap inside (× 6).
    assert total(6, 2) == 12 and total(3, 2) == 6 and total(6, 1) == 6
    print("Ex 1: want 6, code (clap,clap)×6 = 12 -> Fix A repeat 3, Fix B one clap (both = 6) ✓")

    # Ex 2: want 10 hops. Buggy (hop, hop) × 10 = 20.
    # Fix A: repeat 5.  Fix B: one hop inside.
    assert total(10, 2) == 20 and total(5, 2) == 10 and total(10, 1) == 10
    print("Ex 2: want 10, code (hop,hop)×10 = 20 -> Fix A repeat 5, Fix B one hop (both = 10) ✓")

    # Ex 3 (write): want 8 stomps. Buggy (stomp, stomp) × 8 = 16. Fix A repeat 4, Fix B one stomp ×8.
    assert total(8, 2) == 16 and total(4, 2) == 8 and total(8, 1) == 8
    print("Ex 3 (write): want 8, two valid fixes -> repeat 4 (2 each) OR repeat 8 (1 each) ✓")

    # Ex 4 (challenge): want 12 claps from (clap, clap, clap) — 3 inside.
    # Fix A: repeat 4 (3 × 4 = 12).  Fix B: keep repeat 6 but 2 claps inside (2 × 6 = 12).
    assert total(4, 3) == 12 and total(6, 2) == 12
    print("Ex 4 (challenge): want 12 -> repeat 4 with 3 inside, OR repeat 6 with 2 inside (both = 12) ✓")

    print("\nALL CHECKS PASSED — both fixes reach the goal in every case.")
