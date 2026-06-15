"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 6
"Match the Stack".

Matching a program to its outcome, both directions:
  • forward — run a program, find the landing box;
  • reverse — given a wanted box, choose the program that lands there.
Models each program on the 1D stage (Bit on box 1, star on box 4) and asserts
the matches.

Run:  python coding/k_intro_block/06_match_the_stack/solution.py
"""

STAR = 4


def run(start, moves):
    pos = start
    for m in moves:
        pos += 1 if m == "right" else -1
    return pos


# The three programs on the worksheet (move blocks only; GO just starts them).
A = ["right", "right"]            # Program A
P = ["right", "right", "right"]   # Program P
Q = ["right"]                     # Program Q


def program_landing_on(start, box, programs):
    """Reverse match: which named program lands Bit on ``box``?"""
    fits = [name for name, mv in programs if run(start, mv) == box]
    assert len(fits) == 1, f"need exactly one program for box {box}, got {fits}"
    return fits[0]


if __name__ == "__main__":
    # Ex 1 — forward: Program A from box 1 lands on box 3.
    assert run(1, A) == 3
    print("Ex 1: Program A (➡ ➡) -> box 3 ✓")

    named = [("P", P), ("Q", Q)]

    # Ex 2 — reverse: which program lands Bit on the star (box 4)? -> P.
    assert run(1, P) == STAR and run(1, Q) != STAR
    assert program_landing_on(1, STAR, named) == "P"
    print("Ex 2: lands on the star (box 4) -> Program P ✓")

    # Ex 3 — reverse: which program lands Bit on box 2? -> Q.
    assert run(1, Q) == 2 and run(1, P) != 2
    assert program_landing_on(1, 2, named) == "Q"
    print("Ex 3: lands on box 2 -> Program Q ✓")

    print("\nALL CHECKS PASSED — each program matches exactly one landing box.")
