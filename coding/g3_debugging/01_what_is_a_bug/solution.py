"""
solution.py — code-runs gate for G3 · Debugging · Sheet 1 "What Is a Bug?".

Debugging method: say what the code SHOULD do, compare to what it DOES, fix the
wrong repeat count. Each buggy case + its fix are modelled and asserted.

Run:  python coding/g3_debugging/01_what_is_a_bug/solution.py
"""


def total(repeats, per_repeat=1):
    return repeats * per_repeat


if __name__ == "__main__":
    # Worked: should jump 5; buggy repeat 3; fix repeat 5.
    assert total(3) != 5 and total(5) == 5
    print("Worked: want 5 jumps, code repeat 3 -> FIX repeat 5 ✓")

    # Ex 1: should clap 6; buggy repeat 4; fix repeat 6.
    assert total(4) != 6 and total(6) == 6
    print("Ex 1: want 6 claps, code repeat 4 -> FIX repeat 6 ✓")

    # Ex 2: should move 4; buggy repeat 7 (too many); fix repeat 4.
    assert total(7) != 4 and total(4) == 4
    print("Ex 2: want 4 moves, code repeat 7 (too many) -> FIX repeat 4 ✓")

    # Ex 3: should hop 8; buggy repeat 2; fix repeat 8.
    assert total(8) == 8 and total(2) != 8
    print("Ex 3: want 8 hops, code repeat 2 -> FIX repeat 8 ✓")

    # Ex 4 (challenge): 2 claps inside, want 6 claps total -> repeat 3; buggy repeat 6 (=12).
    assert total(6, 2) == 12 and total(3, 2) == 6
    print("Ex 4 (challenge): 2 claps/repeat, want 6 total, code repeat 6 (=12) -> FIX repeat 3 ✓")

    print("\nALL CHECKS PASSED — every fix produces the correct result.")
