"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 2
"Run It Top to Bottom".

Models that Bit runs a block stack from the TOP block down, one block at a
time. The run order is purely positional: the top block (index 0) runs at
step 1, the next at step 2, and so on. Asserts the run order, the first
block, and the last block for each stack on the worksheet.

Run:  python coding/k_intro_block/02_run_it_top_to_bottom/solution.py
"""

GO = "GO"  # green ⚑ start block


def run_order(stack):
    """Bit runs the stack top to bottom: block at index i runs at step i+1."""
    return list(range(1, len(stack) + 1))


def runs_first(stack):
    return stack[0]


def runs_last(stack):
    return stack[-1]


if __name__ == "__main__":
    # Bit's stack (top to bottom): GO, ➡, ⬆, ⬅
    stack = [GO, "right", "up", "left"]
    assert run_order(stack) == [1, 2, 3, 4]
    print("Bit's stack runs in order 1-2-3-4, top to bottom ✓")

    # Ex 1 — the block Bit runs FIRST is the top block (the GO block).
    assert runs_first(stack) == GO
    print("Ex 1: the first block Bit runs is the GO block on top ✓")

    # Ex 2 — number the blocks in run order: GO=1, ➡=2, ⬆=3, ⬅=4.
    assert run_order(stack) == [1, 2, 3, 4]
    print("Ex 2: order GO=1, ➡=2, ⬆=3, ⬅=4 ✓")

    # Ex 3 — the second stack: GO, ⬅, ➡. Last block Bit runs is the bottom ➡.
    stack2 = [GO, "left", "right"]
    assert runs_last(stack2) == "right"
    assert run_order(stack2) == [1, 2, 3]
    print("Ex 3: second stack — last block is the bottom ➡; order 1-2-3 ✓")

    print("\nALL CHECKS PASSED — a stack always runs top to bottom, in order.")
