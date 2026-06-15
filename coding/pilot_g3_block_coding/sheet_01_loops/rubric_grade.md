# Rubric Grade — G3 · Block Coding · Sheet 1 "Loops: Code That Repeats" (rev. 3)

Graded against `coding/rubrics/rubric_coding_G3.md` (recalibrated 2026-06-13) and
enforced by `pipeline/coding_rubric.py`. **Publish gate = total ≥ 19/20 AND C2 ≥ L3
AND C3 = L4 AND C5 = L4.** Self-assessment (the pipeline runs this at the
`content_grade` stage, before any PDF is rendered).

> **Rev. 3** lifts the sheet to the new higher bar: added a real-world hook (song
> chorus / jumping jacks) + an explicit **Challenge** stretch Ex 4 (C3→L4), reframed
> Ex 2 as **predict-then-check** (C4→L4), and added a **Success looks like** indicator
> to the teacher guide (C5→L4). Run-gate extended to model Ex 4 (3 × 2 jumps = 6).

| # | Criterion | Level | Pts |
|---|-----------|-------|-----|
| C1 | Ontario C3 Alignment | **L4** | 4 |
| C2 | Coding-Concept Correctness *(hard gate)* | **L4** | 4 |
| C3 | Grade-Appropriate Pedagogy & Cognitive Load | **L4** | 4 |
| C4 | Clarity, Structure & Mascot/Visual Integration | **L4** | 4 |
| C5 | Teacher Guide Completeness | **L4** | 4 |
| | **Total** | | **20 / 20** |

**Status: PASS** — verified by `coding_rubric.classify()` → `20/20 pass (clean)`;
gate floors C2≥L3, C3=L4, C5=L4 all met.

## Justification (evidence)
- **C1 — L4.** Ex 3 *writes* a loop (C3.1); Ex 2 *alters* the count and *predicts/justifies*
  the effect (C3.2). Teacher guide cites C3.1 + C3.2 verbatim. Both write + alter present.
- **C2 — L4 (hard gate cleared).** `solution.py` models all four loops and runs clean with
  asserts (square 4/4; repeat 6 → 6 > 4; repeat 5 → 5 jumps; **repeat 3 × 2 → 6 jumps**).
  Answer key explains the count/structure and the 3 × 2 reasoning.
- **C3 — L4 (recalibrated).** One idea (the repeat count); explicit low-floor entry
  (Count it); genuine **challenge/stretch** (Ex 4, two inside blocks → multiply); real-world
  hook (chorus / jumping jacks / clap-as-loop). No typed syntax — grade-appropriate.
- **C4 — L4.** Worked example → guided → independent; mascot **Bit** is the actor in the
  square diagram; image keywords (Bit, move 10, turn 90, square) appear in the text →
  alignment clean; Ex 2 is an explicit **predict, then check** prompt.
- **C5 — L4.** Goal, materials, 4-step facilitation, answer key (run-gate verified), C3
  cited, common-error note, differentiation (support + extend), and a success indicator.

## Notes
- Self-graded by the author model; the production `content_grade` stage records the same
  scores as `content_grade.json` before render. An independent re-grade is the eventual
  backstop, per `coding/PILOT_BUILD_PLAN.md`.
- This is the *Block Coding* subject; C2's "Turtle executes clean" clause is satisfied via
  the block-model run-gate (`solution.py`), not a GUI Turtle run.
