"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 5
"Read and Change a Loop" (C3.2 — read, alter, predict).

G3 idea: read an existing loop to say what it does, then change its count or its
inside block and describe how the outcome changes. Every outcome is modelled +
asserted, including the work-backwards challenge.

Run:  python coding/pilot_g3_block_coding/05_read_alter_loop/solution.py
"""


def total_distance(repeats, step):
    """repeat <repeats> { move <step> } -> total steps travelled."""
    dist = 0
    for _ in range(repeats):
        dist += step
    return dist, repeats


if __name__ == "__main__":
    # Ex 1 (read): repeat 5 { move 10 } -> 5 moves, 50 steps.
    dist, moves = total_distance(5, 10)
    assert (moves, dist) == (5, 50), (moves, dist)
    print(f"Ex 1 (read):       repeat 5, move 10 -> {moves} moves, {dist} steps ✓")

    # Ex 2 (alter count): repeat 3 { move 10 } -> 3 moves, 30 steps.
    dist, moves = total_distance(3, 10)
    assert (moves, dist) == (3, 30), (moves, dist)
    print(f"Ex 2 (change count): repeat 3, move 10 -> {moves} moves, {dist} steps ✓")

    # Ex 3 (alter inside): repeat 5 { move 2 } -> 10 steps.
    dist, moves = total_distance(5, 2)
    assert dist == 10, dist
    print(f"Ex 3 (change inside): repeat 5, move 2 -> {dist} steps ✓")

    # Ex 4 (challenge, work backwards): want 40 steps total, 10 each move.
    # repeat = 40 // 10 = 4. Verify it lands on 40.
    need = 40 // 10
    dist, moves = total_distance(need, 10)
    assert need == 4 and dist == 40, (need, dist)
    print(f"Ex 4 (challenge):  need 40 steps at 10 each -> repeat {need} (= {dist} steps) ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
