# Pilot Build Plan — Coding-Worksheet Pipeline: quality-first, checkpointed autonomous build

**Approved 2026-06-13.** This is the authoritative execution plan for the K–G3
coding-worksheet build. Live status lives in `BUILD_PROGRESS.md`; the durable
*process* (checkpoints/handoffs/quality/drift/context) lives in `AUTONOMOUS_BUILD.md`.

## Context

Sheet 1 proved the per-sheet *content* loop works, but three things were missing:

1. **Grade quality BEFORE building the final product.** Author content → grade →
   *then* render. Alignment + pedagogy + teacher-guide completeness are evaluated at
   the **content stage**; nothing renders until content passes. Final **visual
   inspection** runs only on content that already cleared the bar.
2. **A higher bar: 19/20**, with **C3 (pedagogy & cognitive load)** and **C5
   (teacher-guide completeness)** held at L4. (Sheet 1 scored 17/20, so the bar bites.)
3. **A written, robust process for autonomous building** — clean checkpoints, handoff
   updates, quality validation, drift + context management — so sheets 2–N (and the
   rest of K–3) are produced reliably across sessions/compaction.

Locked decisions: **recalibrate the rubric** so grade-appropriate excellence doesn't
require an un-grade Python "block→text bridge"; **reuse `pipeline/manifest.py`** as the
per-sheet checkpoint backbone; **grading applies to ALL grades / every product**;
**autonomy is supervised by batch** — a human verification gate ends each subject-batch.

Outcome: every published coding sheet — every grade, every subject — clears a code-runs
gate, a content-stage rubric ≥19/20 (C2≥L3 hard, C3=L4, C5=L4), and a final visual
inspection — all checkpointed and resumable, with drift + context controlled by design,
and each batch human-verified before the next.

---

## Part 1 — Revised per-sheet pipeline (grade-before-render)

Each sheet = one manifest "unit" dir. Stages run **one per turn**, each gated;
`complete_stage()` marks `done` only when its schema/gate passes (atomic write +
`run.log.jsonl`). `next_pending()` resumes after any stop/compaction.

| # | Stage | Gate to mark `done` | Output |
|---|-------|---------------------|--------|
| 0 | `solution` | **Code-runs gate** — `solution.py` executes clean; asserts pass | `solution.py`, `solution_run.json` |
| 1 | `content` | Schema-valid `CodingWorksheet` + `TeacherGuide` JSON; answer key copied from `solution_run` | `content.json` |
| 2 | `content_grade` | **Quality gate (NEW, before render):** rubric ≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4; drift pre-checks clean | `content_grade.json` |
| 3 | `render` | Worksheet + Teacher-Guide PDFs from the *validated* `content.json` | `*.pdf` |
| 4 | `visual_grade` | **Final visual inspection:** render→PNG, check C4 layout (no overflow/truncation, boxes intact, images render, footer/pages) | `visual_grade.json` |
| 5 | `publish` | (Deferred to batch approval) push ONLY the 2 PDFs to Drive + folder hygiene check | Drive folder |

Rubric is applied **twice, split by what's knowable when**: `content_grade` evaluates
C1/C2/C3/C5 fully + C4's text side; `visual_grade` confirms C4's *visual* side on the
real PDF. Render never runs on ungraded content.

**Remediation:** a failed gate resets the upstream stage per the coding remediation map
(C1/C2→`solution`+`content`; C3/C4→`content`; C5→`content` teacher-guide block) and the
runner re-walks from there.

### Batch gate (supervised autonomy)
Sheets auto-build through stages 0–4 within a **batch = one subject (~7 sheets)**. A batch
does not publish or advance until a human **`batch_verification`** gate: every sheet
(both PDFs + grades) is presented for sign-off. Only then do `publish` stages run and the
next batch begin. The first batch (G3·Block Coding) is the **calibration batch**, reviewed
in full before widening autonomy. This is the "one more batch verification before fully
autonomous" gate.

---

## Part 2 — Rubric recalibration + the 19/20 gate (ALL grades)

Gate + grading apply to **every product in every grade**. Recalibrate **all four** rubrics
(`rubrics/rubric_coding_{K,G1,G2,G3}.md`) consistently:

- **C3-L4 rewrite (each grade):** remove any requirement forcing un-grade content. New
  C3-L4 = *"All of L3 AND grade-appropriate excellence: a low-floor entry every student
  can start, a genuine challenge/stretch, and the new idea hooked to a concrete real-world
  or cross-strand context — within the grade's concept scope; no typed syntax unless it's
  the Turtle subject."* Text-bridge stays an L4 path only in Intro-Python-Turtle (G3).
- **C4-L4 (each grade):** keep "predict, then check/run" + alignment-clean.
- **Gate line (all four):** publish gate = **total ≥ 19/20 AND C2 ≥ L3 (hard) AND C3 = L4
  AND C5 = L4**. Only droppable point is C1 or C4 → L3. (Intrinsic ≥15 floor stays as the
  documented minimum; pipeline enforces the stricter publish bar.)

**New module `pipeline/coding_rubric.py`** (analogue of `rubric.py`): `select_rubric(grade)`,
`THRESHOLD=19`, floors `{C2:3, C3:4, C5:4}`, `classify()`, `required_lifts()`,
`REMEDIATION_MAP`, `pre_grade_drift_check()` (curriculum-verbatim + answer↔solution +
image-keyword, reusing `curriculum.py`/`image_alignment.py`). Every `content_grade`, any
grade, runs through this — no product unmarked.

**Lift Sheet 1:** add a real-world hook + explicit stretch (C3→L4), a "predict, then check"
(C4→L4), a success indicator in the teacher guide (C5→L4) → re-grade ≥19/20; re-run gate +
re-render + visual-inspect.

---

## Part 3 — Checkpoint backbone (reuse `manifest.py`)

- **`pipeline/stages.py`** — add `coding_stages_for_sheet()` (the 6 stages above).
- **`pipeline/schemas.py`** — add coding schemas (extend, don't break math): `CodingWorksheet`
  (reuse `WorksheetPage/Part/ImagePlaceholder/Header`; add `code_block`/`blocks`/`exercise`
  parts), `TeacherGuide`, `SolutionRun`, `ContentGrade`, `VisualGrade`, `CourseBlueprint`.
  Content authored as **schema-validated JSON via Write** (replacing the bootstrap
  `content.py`); `worksheet_pdf.py` gets a render-from-validated-JSON adapter.
- **Sheet/unit layout:** `pilot_g3_block_coding/<NN_topic>/` holds `manifest.json`,
  `input_row.json` (topic + verbatim C3 text), `solution.py`, `solution_run.json`,
  `content.json`, `content_grade.json`, the 2 PDFs, `visual_grade.json`. Sheet 1 migrates in.

---

## Part 4 — Autonomous-build process (see `AUTONOMOUS_BUILD.md`)

- **Clean checkpoints** — per-sheet `manifest.json`; one stage per turn; `complete_stage`
  atomic + validated + `run.log.jsonl`; never end on `in_progress`; cold resume via
  `next_pending()`.
- **Updating handoffs** — `BUILD_PROGRESS.md` live (per terminal gate); `HANDOFF.md` stable
  (process/scope changes); memory at session end + per subject completed. Cadence written down.
- **Quality validation** — ordered gate chain: code-runs → content schema → content_grade
  (≥19/20 + floors + drift) → render → visual_grade.
- **Drift management** — curriculum verbatim; answer key generated *from* executed solution;
  image keywords-in-text; cross-sheet `STYLE_SPEC.md`; locked `topics.json` scope.
- **Context management** — all state on disk; one sheet authored fresh per turn from disk;
  target ~50% context; `/clear`-safe.
- **Supervised autonomy** — bounded to one batch; human `batch_verification` ends each batch
  before publish + next batch; no cross-batch unattended runs until the user widens the leash.

Also create `pilot_g3_block_coding/topics.json` (locked 7-topic arc) + `STYLE_SPEC.md`.

---

## Files to create / modify

**Create:** `pipeline/coding_rubric.py`, `coding/AUTONOMOUS_BUILD.md`,
`coding/pilot_g3_block_coding/topics.json`, `coding/pilot_g3_block_coding/STYLE_SPEC.md`,
`pipeline/drive_publish.py` (deferred).
**Modify:** `coding/rubrics/rubric_coding_{K,G1,G2,G3}.md`, `pipeline/stages.py`,
`pipeline/schemas.py`, `pipeline/worksheet_pdf.py`, Sheet 1 content (lift + migrate),
`coding/BUILD_PROGRESS.md` + memory.

## Execution order
- **0. Land plan + handoffs + memory, push branch** (this step).
- **A. Quality + process:** recalibrate 4 rubrics → `coding_rubric.py` → lift+re-grade Sheet 1
  → `AUTONOMOUS_BUILD.md`, `topics.json`, `STYLE_SPEC.md`.
- **B. Checkpoint backbone:** coding stages + schemas + adapter → migrate Sheet 1 → prove
  `next_pending`/resume + `status_table`.
- **C. Proof:** generate Sheet 2 end-to-end through the checkpointed, grade-before-render pipeline.
- **D. Calibration batch:** sheets 3–7 → stop at `batch_verification` for sign-off.
- **E. Publish + widen:** on sign-off, `drive_publish.py` + publish; then next batch (Intro
  Python Turtle), repeating the batch gate.

## Verification
- Sheet 1 re-grades ≥19/20 with C3=L4, C5=L4; run-gate passes; re-rendered PDFs pass visual
  inspection (150dpi, Read each page).
- `manifest.status_table()` shows Sheet 1's 6 stages; stop mid-pipeline → `next_pending()`
  resumes the right stage.
- Sheet 2 completes the full chain; a forced rubric fail resets the correct upstream stage.
- `coding_rubric.classify()` rejects 18/20 and any C3<L4 or C5<L4; accepts a clean 19–20.
