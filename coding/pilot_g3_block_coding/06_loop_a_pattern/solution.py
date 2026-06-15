"""
solution.py — code-runs gate for G3 · Block Coding · Sheet 6
"Loop a Longer Pattern".

G3 idea: a loop with several blocks inside runs the WHOLE inside each pass, so a
3-action pattern (clap, clap, stomp) repeats as a unit. Students count each
action type across the repeats. Every outcome modelled + asserted, including the
work-backwards challenge.

Run:  python coding/pilot_g3_block_coding/06_loop_a_pattern/solution.py
"""
from collections import Counter


def run_pattern(pattern, repeats):
    """repeat <repeats> { do each action in pattern }. Returns (total, counts)."""
    seq = []
    for _ in range(repeats):
        seq.extend(pattern)
    return len(seq), Counter(seq)


if __name__ == "__main__":
    # Ex 1 (count): repeat 4 { clap, clap, stomp } -> 3 per repeat, 12 total.
    total, counts = run_pattern(["clap", "clap", "stomp"], 4)
    assert total == 12 and counts["clap"] == 8 and counts["stomp"] == 4, (total, counts)
    print(f"Ex 1 (count):      repeat 4 of (clap,clap,stomp) -> 3 per repeat, {total} total ✓")

    # Ex 2 (alter): repeat 5 -> 5 stomps, 10 claps.
    total, counts = run_pattern(["clap", "clap", "stomp"], 5)
    assert counts["stomp"] == 5 and counts["clap"] == 10, counts
    print(f"Ex 2 (alter):      repeat 5 -> {counts['stomp']} stomps, {counts['clap']} claps ✓")

    # Ex 3 (write): pattern (wave, wave, bow) repeat 4 -> 8 waves.
    total, counts = run_pattern(["wave", "wave", "bow"], 4)
    assert counts["wave"] == 8, counts
    print(f"Ex 3 (write):      repeat 4 of (wave,wave,bow) -> {counts['wave']} waves ✓")

    # Ex 4 (challenge, work backwards): 6 stomps, 1 stomp per repeat -> 6 repeats.
    stomps_seen, stomps_per_repeat = 6, 1
    repeats = stomps_seen // stomps_per_repeat
    total, counts = run_pattern(["clap", "clap", "stomp"], repeats)
    assert repeats == 6 and counts["clap"] == 12, (repeats, counts)
    print(f"Ex 4 (challenge):  6 stomps at 1/repeat -> repeated {repeats} times "
          f"(= {counts['clap']} claps) ✓")

    print("\nALL CHECKS PASSED — answer key is provably correct.")
