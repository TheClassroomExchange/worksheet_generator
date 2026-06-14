"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 1 "Meet the Blocks".

Models a block stack as a list of blocks, top block first. The green GO/flag
block starts the program and must sit on TOP; the rest are move blocks. Asserts
which block starts each stack and whether a stack is ready to run.

Run:  python coding/k_intro_block/01_meet_the_blocks/solution.py
"""

GO = "GO"        # green flag / start block (glyph ⚑)
RIGHT = "->"     # a blue move block (glyph ➡)


def starts(stack):
    """The block that runs first is the top block (index 0)."""
    return stack[0]


def is_ready(stack):
    """A stack is ready to run only if its TOP block is the GO block."""
    return len(stack) > 0 and stack[0] == GO


if __name__ == "__main__":
    # Model — Bit's program: GO on top, then two move blocks.
    bit = [GO, RIGHT, RIGHT]
    assert starts(bit) == GO
    assert is_ready(bit)
    print("Bit's program: top block is GO -> it starts the program ✓")

    # Ex 1 — the start block of Bit's program is the green GO block (the top one).
    assert starts(bit) == GO
    print("Ex 1: the start block is the green GO block on top ✓")

    # Ex 2 — Stack A is ready (GO on top); Stack B is NOT (GO is not on top).
    stack_a = [GO, RIGHT]
    stack_b = [RIGHT, GO]
    assert is_ready(stack_a)
    assert not is_ready(stack_b)
    print("Ex 2: Stack A is ready (GO on top); Stack B is not ✓")

    # Ex 3 — adding a GO block on top makes a stack of move blocks ready to run.
    moves = [RIGHT, RIGHT]
    fixed = [GO] + moves
    assert not is_ready(moves) and is_ready(fixed)
    print("Ex 3: add a GO block on top -> the program is ready to run ✓")

    print("\nALL CHECKS PASSED — the start block is always the GO block on top.")
