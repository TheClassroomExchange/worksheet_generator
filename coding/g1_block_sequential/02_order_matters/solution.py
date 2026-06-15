"""
solution.py — code-runs gate for G1 · Block Coding (Sequential) · Sheet 2
"Order Matters".

Same interpreter as Sheet 1: Bit on a number path 0..5; the path ENDS at 5, so
a forward move that would pass 5 stops on 5 (and it can't go below 0). Because
of that edge, the SAME blocks in a different order can land Bit on a different
number — this models why order matters. Asserts both orderings.

Run:  python coding/g1_block_sequential/02_order_matters/solution.py
"""

LO, HI = 0, 5


def run(start, moves):
    pos = start
    for sign, n in moves:
        pos += sign * n
        pos = max(LO, min(HI, pos))   # the path ends at 5 and starts at 0
    return pos


FWD, BACK = 1, -1

if __name__ == "__main__":
    # Code 1 — start 3, forward 3, back 1.  3 ->(fwd3, stops at 5) 5 ->(back1) 4.
    assert run(3, [(FWD, 3), (BACK, 1)]) == 4
    print("Code 1: start 3, forward 3 (stops at 5), back 1 -> 4 ✓")

    # Code 2 — SAME blocks, reordered: start 3, back 1, forward 3.
    #          3 ->(back1) 2 ->(fwd3) 5.
    assert run(3, [(BACK, 1), (FWD, 3)]) == 5
    print("Code 2: start 3, back 1, forward 3 -> 5 ✓")

    # Same blocks, different order, DIFFERENT landing (4 vs 5) -> order matters.
    assert run(3, [(FWD, 3), (BACK, 1)]) != run(3, [(BACK, 1), (FWD, 3)])
    print("Same blocks, different order -> different number (order matters) ✓")

    # Challenge — an order of these blocks that lands on 5 = back 1 then forward 3.
    assert run(3, [(BACK, 1), (FWD, 3)]) == 5
    print("Challenge: back 1 then forward 3 lands on 5 ✓")

    print("\nALL CHECKS PASSED — at the edge, the order of the blocks changes the result.")
