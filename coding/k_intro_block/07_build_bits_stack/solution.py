"""
solution.py — code-runs gate for K · Intro Block Coding · Sheet 7
"Build Bit's Stack".

The child COMPOSES a program: draw an arrow in each empty block so Bit reaches
the star. Models the intended program for each build task, asserts it lands on
the star, and asserts it uses exactly the number of empty blocks provided.

Run:  python coding/k_intro_block/07_build_bits_stack/solution.py
"""


def run(start, moves):
    pos = start
    for m in moves:
        pos += 1 if m == "right" else -1
    return pos


def check_build(start, star, program, n_blocks):
    """A built program is correct if it fills every empty block and lands on
    the star."""
    assert len(program) == n_blocks, f"expected {n_blocks} blocks, got {len(program)}"
    assert run(start, program) == star, f"program does not reach box {star}"
    return True


if __name__ == "__main__":
    # Build 1 — Stage A: box 1 -> star box 4, three empty blocks -> ➡ ➡ ➡.
    assert check_build(1, 4, ["right", "right", "right"], 3)
    print("Build 1: box 1 -> star box 4 = ➡ ➡ ➡ ✓")

    # Build 2 — Stage B: box 4 -> star box 2, two empty blocks -> ⬅ ⬅.
    assert check_build(4, 2, ["left", "left"], 2)
    print("Build 2: box 4 -> star box 2 = ⬅ ⬅ ✓")

    # Build 3 (you try) — Stage C: box 1 -> star box 3, two empty blocks -> ➡ ➡.
    assert check_build(1, 3, ["right", "right"], 2)
    print("Build 3: box 1 -> star box 3 = ➡ ➡ ✓")

    # A wrong fill (too few rights) would miss the star — shows checking matters.
    assert run(1, ["right", "right"]) != 4
    print("Check: ➡ ➡ from box 1 misses box 4 (need three ➡) ✓")

    print("\nALL CHECKS PASSED — each built program reaches its star.")
