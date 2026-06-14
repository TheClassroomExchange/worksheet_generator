"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 8
"Fix the Stack".

Debugging: a program has ONE block pointing the wrong way, so Bit misses the
star. Models the buggy program (it misses), finds the wrong block, and models
the fixed program (it reaches the star). Asserts each result.

Run:  python coding/k_intro_block/08_fix_the_stack/solution.py
"""

STAR = 4


def run(start, moves):
    pos = start
    for m in moves:
        pos += 1 if m == "right" else -1
    return pos


def find_bug(start, moves, star):
    """Return the index of the one block that, if flipped, makes the program
    reach the star (the wrong-way block)."""
    bugs = []
    for i, m in enumerate(moves):
        flipped = list(moves)
        flipped[i] = "left" if m == "right" else "right"
        if run(start, flipped) == star:
            bugs.append(i)
    assert len(bugs) == 1, f"expected exactly one fixable block, got {bugs}"
    return bugs[0]


if __name__ == "__main__":
    # Bit on box 1, star on box 4. Buggy program: ➡ ⬅ ➡ (the middle block is ⬅).
    buggy = ["right", "left", "right"]
    assert run(1, buggy) == 2          # lands on box 2, NOT the star
    print("Buggy program ➡ ⬅ ➡ from box 1 -> box 2 (misses the star) ✓")

    # Ex 1 — Bit lands on box 2, which is not the star.
    assert run(1, buggy) != STAR
    print("Ex 1: Bit lands on box 2 — not the star ✓")

    # Ex 2 — the wrong-way block is the middle one (index 1, the ⬅).
    bug_i = find_bug(1, buggy, STAR)
    assert bug_i == 1 and buggy[bug_i] == "left"
    print("Ex 2: the wrong block is the middle ⬅ ✓")

    # Ex 3 — fix it: the middle block should be ➡. Fixed program reaches box 4.
    fixed = ["right", "right", "right"]
    assert run(1, fixed) == STAR
    print("Ex 3: fixed program ➡ ➡ ➡ -> box 4 (the star) ✓")

    print("\nALL CHECKS PASSED — find the wrong block, flip it, Bit reaches the star.")
