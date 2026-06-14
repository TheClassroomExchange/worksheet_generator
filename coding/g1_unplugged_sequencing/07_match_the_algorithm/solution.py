"""
solution.py — answer-key gate for G1 · Unplugged Sequencing · Sheet 7
"Match the Algorithm".

Each algorithm (an ordered list of steps) does one job. Models the step-lists
and the job each one accomplishes, and asserts the matches. The leftover job is
modelled with a sample algorithm for the write task.

Run:  python coding/g1_unplugged_sequencing/07_match_the_algorithm/solution.py
"""

ALGORITHMS = {
    1: ["wet your hands", "add soap", "rinse", "dry your hands"],
    2: ["get the bowl", "scoop the food", "put it down", "call the dog"],
}

# What job each algorithm does.
JOB = {1: "wash hands", 2: "feed the dog"}

JOBS = ["wash hands", "feed the dog", "get a drink"]  # 'get a drink' is leftover


def job_of(n):
    return JOB[n]


if __name__ == "__main__":
    # Ex 1 — Algorithm 1 washes hands.
    assert job_of(1) == "wash hands"
    print("Ex 1: Algorithm 1 (wet, soap, rinse, dry) -> wash hands ✓")

    # Ex 2 — Algorithm 2 feeds the dog.
    assert job_of(2) == "feed the dog"
    print("Ex 2: Algorithm 2 (bowl, scoop, put down, call) -> feed the dog ✓")

    # The leftover job has no algorithm yet.
    matched = set(JOB.values())
    leftover = [j for j in JOBS if j not in matched]
    assert leftover == ["get a drink"]
    print("Leftover job to write: get a drink ✓")

    # Ex 3 (sample) — a valid 'get a drink' algorithm.
    drink = ["get a cup", "turn on the tap", "fill the cup", "turn off the tap"]
    assert drink[0] == "get a cup" and 3 <= len(drink) <= 5
    print("Sample 'get a drink' algorithm is a valid ordered list ✓")

    print("\nALL CHECKS PASSED — each algorithm matches the job its steps accomplish.")
