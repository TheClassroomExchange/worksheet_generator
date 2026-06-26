# Teacher-Guide Plain-Language Rubric — all grades (K–G3)

**Purpose.** Grade the **Teacher Guide** half of every coding sheet for a teacher
who has **never coded and has never opened Scratch / Python Turtle**. The student
worksheet is graded separately by `rubric_coding_{K,G1,G2,G3}.md`; this rubric
covers ONLY the `teacher_guide` block in each `content.json`.

**What "good" means here:** a substitute teacher with zero coding background can
pick up the printed guide, understand what the page teaches, get the activity
going (or know no computer is needed), run it start-to-finish, mark it correctly,
and adjust for strugglers/fast finishers — without looking anything up.

## Scoring model
5 criteria, each **L1–L4 (1–4 pts)** → **/20**. Grader walks each checklist
top-down, stops at the highest fully-met level.

> **Keep it tight.** Short sentences, no padding — a teacher skims this, not studies it.
> The whole guide must fit **one page**. If content is light, merge sections (e.g. fold
> "You'll know it worked when" into the differentiation note) rather than pad — fewer
> sections beats a cramped page. Wordiness counts against T1.

> **PUBLISH GATE (enforced by `pipeline/teacher_guide_rubric.py`):
> total ≥ 18/20 AND T1 = L4 AND T4 = L4.**
> T1 (plain language) and T4 (answer-key correctness) are the two non-negotiables —
> a guide that still reads technical, or whose answers don't match the verified
> solution, never ships. The droppable points are one each on T2, T3, or T5 → L3.

---

### T1 — Plain language / no-experience accessibility *(HARD GATE — = L4)*
- **L1:** Reads like programmer notes; multiple unexplained code terms (`for-loop`, `range()`, `sprite`, `run-gate`, "computational representation").
- **L2:** Mostly readable but ≥1 technical term used without a plain explanation.
- **L3:** No unexplained jargon; any necessary term is glossed in everyday words on first use.
- **L4:** All of L3 **and** the whole guide could be read aloud by a non-coder cold; instructions phrased as plain actions ("read it top to bottom", "repeat 4 times"), never as code syntax.

### T2 — Step-by-step facilitation a first-timer can follow
- **L1:** No run-it steps, or steps assume the teacher already knows the activity.
- **L2:** Has steps but they skip what to say/do, or jump straight to the answer.
- **L3:** Opens with a 1-line "what this teaches", then ordered run-it steps the teacher can follow in sequence.
- **L4:** All of L3 **and** an explicit show-it → do-it-together → try-alone flow with sample teacher talk, plus a closing "big idea" line.

### T3 — Tool / setup guidance
- **L1:** Doesn't say what (if anything) is needed to run the activity.
- **L2:** Mentions a tool but not how to get it on screen.
- **L3:** States clearly either "no computer needed — paper and pencil" OR names the tool and what to print/hand out.
- **L4:** All of L3 **and** for any on-screen tool, click-level plain steps to display it (open browser → go to playground → type the lines → press Run), framed as optional when the printout suffices.

### T4 — Answer-key correctness & clarity *(HARD GATE — = L4)*
- **L1:** Missing answers, or an answer contradicts the verified solution.
- **L2:** All answers present but no reasoning, or reasoning is in code-speak.
- **L3:** Every exercise answered; answers match `solution_run.json`; reasoning in plain words.
- **L4:** All of L3 **and** a plain "why it works" that a non-coder could re-explain to a student.

### T5 — Curriculum link + differentiation (plain)
- **L1:** No curriculum reference and no differentiation.
- **L2:** Has one of: the curriculum quote OR differentiation — not both.
- **L3:** Verbatim Ontario expectation present (official wording, unchanged) **and** at least one make-it-easier and one make-it-harder.
- **L4:** All of L3 **and** an "In plain terms:" gloss under each verbatim quote, a "watch for" common-slip note, and a 1-line "you'll know it worked when" success indicator.

---

## Drift guard (keep verbatim text exact)
The Ontario C3 (or K-frame) quote MUST stay **word-for-word** as cited in the
source guide / `input_row.json`. The plain-language rewrite adds an
"In plain terms:" line *beneath* the quote — it never edits the quote itself.
`pipeline/teacher_guide_rubric.py::lint_teacher_guide` flags (a) leftover jargon
tokens and (b) a missing "In plain terms:" gloss as advisory warnings before grading;
`pre_grade_drift_check` (in `coding_rubric.py`) still enforces curriculum-verbatim.

## Remediation mapping
- Any criterion below target → re-author the `teacher_guide` block in `content.json`, then re-render.
- T4 fail → also re-check the answers against `solution_run.json` before re-rendering.
