"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 3 "Move Blocks".

Models the move-block vocabulary: each move block makes Bit travel in exactly
one direction. Asserts the block→direction mapping and the answers to each
"circle / draw the block that goes ___" exercise.

Run:  python coding/k_intro_block/03_move_blocks/solution.py
"""

# Each move block maps to the single direction it makes Bit travel.
MOVE = {
    "right": "➡",
    "left": "⬅",
    "up": "⬆",
    "down": "⬇",
}


def block_for(direction):
    """The move block (arrow) that makes Bit go a given way."""
    return MOVE[direction]


if __name__ == "__main__":
    # Model — one block, one direction.
    assert block_for("right") == "➡"
    assert block_for("left") == "⬅"
    assert block_for("up") == "⬆"
    assert block_for("down") == "⬇"
    print("Each move block points the one way Bit goes ✓")

    # Ex 1 — the block that makes Bit go UP is the ⬆ block.
    assert block_for("up") == "⬆"
    print("Ex 1: UP -> ⬆ ✓")

    # Ex 2 — the block that makes Bit go LEFT is the ⬅ block.
    assert block_for("left") == "⬅"
    print("Ex 2: LEFT -> ⬅ ✓")

    # Ex 3 — to go DOWN the child draws the ⬇ arrow in the empty block.
    assert block_for("down") == "⬇"
    print("Ex 3: DOWN -> draw ⬇ ✓")

    # Each block is a different direction (no two the same).
    assert len(set(MOVE.values())) == 4
    print("All four move blocks are different directions ✓")

    print("\nALL CHECKS PASSED — one move block = one direction.")
