"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 5
"Finish the Stack".

A program is missing ONE move block (a gap). The child chooses the move block
that makes Bit reach the star. Models each partial program, tries the candidate
move blocks, and asserts which one lands Bit on the star.

Run:  python coding/k_intro_block/05_finish_the_stack/solution.py
"""

CANDIDATES = {"right": "➡", "left": "⬅"}


def run(start, moves):
    pos = start
    for m in moves:
        pos += 1 if m == "right" else -1
    return pos


def missing_block(start, program_with_gap, star):
    """``program_with_gap`` is the move list with None at the empty block.
    Return the candidate move that lands Bit on the star (exactly one fits)."""
    fits = [c for c in CANDIDATES
            if run(start, [c if m is None else m for m in program_with_gap]) == star]
    assert len(fits) == 1, f"need exactly one solution, got {fits}"
    return fits[0]


if __name__ == "__main__":
    # Stage 1: Bit on box 1, star on box 4.
    # Ex 1 — GO, ➡, ➡, [ ]  -> missing block is ➡ (box 1->2->3->4).
    assert missing_block(1, ["right", "right", None], 4) == "right"
    print("Ex 1: GO ➡ ➡ [ ] -> ➡  (lands on box 4, the star) ✓")

    # Ex 2 — GO, ➡, [ ], ➡  -> missing block is ➡ (the gap in the middle).
    assert missing_block(1, ["right", None, "right"], 4) == "right"
    print("Ex 2: GO ➡ [ ] ➡ -> ➡  (lands on box 4, the star) ✓")

    # Stage 2: Bit on box 4, star on box 2.
    # Ex 3 — GO, ⬅, [ ]  -> missing block is ⬅ (box 4->3->2).
    assert missing_block(4, ["left", None], 2) == "left"
    print("Ex 3: GO ⬅ [ ] -> ⬅  (lands on box 2, the star) ✓")

    print("\nALL CHECKS PASSED — each gap has exactly one block that reaches the star.")
