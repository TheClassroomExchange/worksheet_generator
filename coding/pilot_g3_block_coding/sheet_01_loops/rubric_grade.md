# Rubric Grade — G3 · Block Coding · Sheet 1 "Loops: Code That Repeats" (rev. 2)

Graded against `coding/rubrics/rubric_coding_G3.md`. Walk each L1→L4 checklist
top-down, stop at the highest fully-met level. **Pass = total ≥ 15/20 AND C2 ≥ L3.**
Self-assessment (production pipeline runs an independent `rubric_grade` stage).

> **Rev. 2** simplified the sheet to be squarely Grade 3: exercises now focus on the
> REPEAT COUNT (count it / change it / write it) instead of deriving turn angles, and
> the first-time Python bridge was removed (text code belongs in the separate "Intro
> Python Turtle" subject). This deliberately traded two L4 "extras" (the block→text
> bridge in C3, the predict-then-run in C4) for grade-appropriate simplicity.

| # | Criterion | Level | Pts |
|---|---|---|---|
| C1 | Ontario C3 Alignment | **L4** | 4 |
| C2 | Coding-Concept Correctness *(hard gate)* | **L4** | 4 |
| C3 | Grade-Appropriate Pedagogy & Cognitive Load | **L3** | 3 |
| C4 | Clarity, Structure & Mascot/Visual Integration | **L3** | 3 |
| C5 | Teacher Guide Completeness | **L3** | 3 |
| | **Total** | | **17 / 20** |

**Status: PASS** (≥ 15 ✓; C2 ≥ L3 hard gate ✓).

## Justification (evidence)

**C1 — L4.** Ex 3 has the student *write* a repeat loop (C3.1); Ex 2 has them
*alter* the loop's count and *describe the effect* — "more or fewer than before"
(C3.2). Teacher guide cites C3.1 + C3.2 verbatim. L4 needs both write + alter — met.

**C2 — L4 (hard gate cleared).** `solution.py` models every loop and runs clean
with asserts (repeat 4 → 4 moves/4 turns/square; repeat 6 → 6 moves > 4; repeat 5
→ 5 jumps). Answer key + "Big idea" explain what the repeat count controls. L4.

**C3 — L3.** One new idea (the repeat count); single objective; very low cognitive
load (no angle math, no syntax). *Not L4:* the block→text bridge was intentionally
removed for grade fit, and L4 requires it — so L3 is the honest ceiling here.

**C4 — L3.** Worked example → guided (Count it) → independent (Write your own);
blocks legible; mascot **Bit** is the actor in the square diagram; image keywords
(Bit, move 10, turn 90, square) all appear in the text → alignment clean. *Not L4:*
no explicit "predict the drawing, then run" task remains.

**C5 — L3.** Goal, materials, 4-step facilitation, answer key (run-gate checked),
C3 cited, common-error note + support + an extend prompt. *Not L4:* no standalone
"success indicator" line (dropped to keep the guide to one page).

## Notes
- 17/20 is the honest score after simplifying; the lost points are L4 "extras"
  (Python bridge, predict-then-run, success-indicator) traded for Grade-3 clarity.
  If we want to lift them back to ~20 without over-complicating, the cheapest moves
  are: add a one-line "predict, then run on a device" to Ex 2 (C4→L4) and a
  one-line success indicator to the guide (C5→L4). Left out by choice for simplicity.
- Self-graded; warrants an independent re-grade in the production stage before mass publish.
