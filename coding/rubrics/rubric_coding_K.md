# Coding Worksheet Rubric — Kindergarten

**Ontario reference:** Kindergarten Program (2016), **Problem Solving and
Innovating** frame (computational thinking — sequencing, algorithms, directional
language, patterning, debugging-as-fixing-order). *Kindergarten has no Math C3
strand; do not cite C3 codes here.*

**Concept scope (K):** unplugged + symbol/picture-based only (ScratchJr-style
arrows, no reading-dependent instructions). Sequencing daily routines, giving/
following directions (forward/turn), extending patterns, sorting, "fix the mix-up"
debugging. **No text code. No loops/variables.**

## Scoring model
5 criteria, each scored **L1–L4 (1–4 pts)** → **/20**. The grader walks each
criterion's checklist **top-down and stops at the highest level where *every*
item is met**. **Pass = total ≥ 15/20 AND Criterion 2 ≥ L3 (hard gate).**
A worksheet that fails the hard gate cannot ship regardless of total.

> **PUBLISH GATE (this pipeline, all grades — enforced by `pipeline/coding_rubric.py`):
> total ≥ 19/20 AND C2 ≥ L3 AND C3 = L4 AND C5 = L4.** The only droppable point is
> C1 or C4 → L3. The ≥15 line above is the documented minimum-viable score; shipping
> a paid product requires the stricter bar.

### C1 — Curriculum & Computational-Thinking Alignment
- **L1:** Names a CT idea (sequence/pattern/direction) but the activity doesn't actually exercise it.
- **L2:** Activity touches one CT idea; link to the K frame is implied, not stated.
- **L3:** Activity clearly exercises one named CT skill; the teacher guide cites the specific K-frame expectation.
- **L4:** All of L3 **and** the skill is shown in a child-relevant context (routine/play) with a clear "this is how computers think" connection.

### C2 — Coding-Concept Correctness *(HARD GATE — must be ≥ L3)*
- **L1:** The sequence/algorithm shown is wrong or ambiguous (no single correct order).
- **L2:** Mostly correct but one step is out of order or a symbol is misused.
- **L3:** Every modeled sequence/answer is correct and unambiguous; the internal `solution_NN` "trace" matches.
- **L4:** All of L3 **and** the answer key includes the *reasoning* ("the arrow turns Pixel right, so…").

### C3 — Grade-Appropriate Pedagogy & Cognitive Load
- **L1:** Requires reading, counting past 10, or >4 steps — too heavy for K.
- **L2:** Mostly K-appropriate but one element assumes reading or fine-motor precision beyond range.
- **L3:** Picture/symbol-driven; ≤4 steps; large targets; one idea per page; no required reading.
- **L4:** All of L3 **and** built-in scaffold (model → guided → "you try") and an oral/movement option.

### C4 — Clarity, Structure & Mascot/Visual Integration
- **L1:** Cluttered; unclear what the child does; mascot decorative only.
- **L2:** Followable but visual flow (left→right/top→down) is inconsistent.
- **L3:** Clear single task; strong visual flow; **kawaii mascot is the actor** in the activity (e.g. guides the path); every image's `keywords` match the surrounding prompt.
- **L4:** All of L3 **and** the mascot models the worked example then the child repeats — image/text alignment gate clean.

### C5 — Teacher Guide Completeness
- **L1:** Objective only.
- **L2:** Objective + steps, but no answer key or it's an oral activity with no facilitation script.
- **L3:** Objective, materials, step-by-step facilitation script, answer key, K-frame expectation cited.
- **L4:** All of L3 **and** a differentiation note (simplify/extend) + a 1-line "look-for" success indicator.

## Remediation mapping
- C1/C2 fail → regen `worksheet_NN` + `solution_NN`.
- C3/C4 fail → regen `worksheet_NN` (reduce load / fix visual flow).
- C5 fail → regen `teacher_guide_NN` only.
