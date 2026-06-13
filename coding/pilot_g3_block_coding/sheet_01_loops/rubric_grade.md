# Rubric Grade — G3 · Block Coding · Sheet 1 "Loops: Code That Repeats"

Graded against `coding/rubrics/rubric_coding_G3.md`. Walk each L1→L4 checklist
top-down, stop at the highest fully-met level. **Pass = total ≥ 15/20 AND C2 ≥ L3.**
This is a self-assessment (the production pipeline runs this as an independent
`rubric_grade` stage; flagged for an independent re-grade before mass publish).

| # | Criterion | Level | Pts |
|---|---|---|---|
| C1 | Ontario C3 Alignment | **L4** | 4 |
| C2 | Coding-Concept Correctness *(hard gate)* | **L4** | 4 |
| C3 | Grade-Appropriate Pedagogy & Cognitive Load | **L4** | 4 |
| C4 | Clarity, Structure & Mascot/Visual Integration | **L4** | 4 |
| C5 | Teacher Guide Completeness | **L4** | 4 |
| | **Total** | | **20 / 20** |

**Status: PASS** (≥ 15 ✓; C2 ≥ L3 hard gate ✓).

## Justification (evidence)

**C1 — L4.** Exercise 1 has the student *write* a repeat loop (C3.1); Exercise 2
has them *alter* an existing loop and *describe/justify* the changed outcome
(C3.2). Teacher guide cites C3.1 and C3.2 verbatim and maps each to its exercise.
L4 requires "both writing a loop AND altering it to predict/justify" — both present.

**C2 — L4 (hard gate cleared).** Every loop on the sheet is modelled by
`solution.py`, which executes clean with asserts (square=4 corners & closes,
triangle=3 sides, hexagon=6 sides, total=120 steps) — the run-gate. The answer
key explains the loop count/structure and what changing the count does
(3×120=360; 6 repeats→6 sides; 3×(20+20)=120). L4 met.

**C3 — L4.** One new idea (the repeat loop); typed Python kept to 3 short lines
with a copy-this model; single objective. Block→text bridge is explicit (the
Scratch stack, then its Python equivalent side-by-side). Low floor (Ex 1 with a
360 hint) + challenge (Ex 3 predict-then-run); differentiation simplifies to
supplying only the count and extends to turn = 360 ÷ sides.

**C4 — L4.** Worked example → guided → independent flow. Code blocks are
monospace with correct indentation. The mascot **Bit** is the actor — drawn
mid-task in the square-path diagram. A "predict the drawing/output, then run"
prompt is present (Ex 3, and the predict in Ex 2). Image keywords (Bit, square,
move 10, turn 90) all appear in the surrounding text → alignment clean.

**C5 — L4.** Teacher guide has objective, materials, step-by-step facilitation,
answer key with runnable code, C3 expectations cited, and a common-error note
(off-by-one / count-vs-angle / non-divisor turn). Plus differentiation
(simplify-to-count / extend-to-parameterized-shape) and an explicit success
indicator. L4 met.

## Notes / honest caveats
- Self-graded by the author model; a perfect score warrants an independent
  re-grade in the production `rubric_grade` stage before mass publishing.
- This is the *Block Coding* subject, so C2's "Turtle executes clean" clause is
  satisfied via the block-model run-gate (`solution.py`), not a GUI Turtle run.
