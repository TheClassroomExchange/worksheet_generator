"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 8
"Plan Your Algorithm" (challenge / unit finale).

Students plan and write a full algorithm (a pattern, then a real job), then
improve it. The tasks are open; this models a sample for each and asserts the
samples are valid (a runnable pattern + an ordered job + a sensible improvement)
so the answer key is grounded.

Run:  python coding/g1_unplugged_sequencing/08_plan_your_algorithm/solution.py
"""


def run_pattern(steps):
    """steps: list of shapes drawn in order; returns the shape row."""
    return list(steps)


if __name__ == "__main__":
    # Task 1 (sample) — a circle-square-square (ABB) pattern of 6 shapes.
    pattern = ["circle", "square", "square", "circle", "square", "square"]
    row = run_pattern(pattern)
    assert len(row) == 6
    assert row[:3] == row[3:]              # the ABB unit repeats once
    print("Sample pattern (ABB): circle, square, square, circle, square, square ✓")

    # Task 2 (sample) — pack your backpack: an ordered job of 4-5 steps.
    pack = ["open the backpack", "put in your books",
            "put in your lunch", "zip it up", "put it on"]
    assert pack[0] == "open the backpack" and pack[-1] == "put it on"
    assert pack.index("zip it up") < pack.index("put it on")  # zip before wearing
    print("Sample job (pack the backpack) is a valid ordered algorithm ✓")

    # Ex 3 (sample improvement) — add 'check your homework is in' before zipping.
    improved = pack[:3] + ["check your homework is in"] + pack[3:]
    assert improved.index("check your homework is in") < improved.index("zip it up")
    assert len(improved) == len(pack) + 1
    print("Sample improvement: add 'check your homework is in' before zipping ✓")

    print("\nALL CHECKS PASSED — plan, write, and improve a working algorithm.")
