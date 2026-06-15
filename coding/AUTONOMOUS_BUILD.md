# Autonomous Build Process — Coding-Worksheet Pipeline

How sheets get built reliably across sessions, compaction, and `/clear`. This is the
durable *process* contract referenced by `PILOT_BUILD_PLAN.md`. Read it before generating.

The four pillars the user asked for — **clean checkpoints, handoff updates, quality
validation, drift + context management** — plus the **supervised-autonomy** batch model.

---

## 0. Unit of work

- **Sheet** = one topic = one manifest "unit" dir under
  `coding/<batch>/<NN_topic>/` (e.g. `pilot_g3_block_coding/02_events/`).
- **Batch** = one subject (~7 sheets), e.g. *G3 · Block Coding*.
- Each sheet runs the 6-stage pipeline; each batch ends at a human gate.

Per-sheet files: `manifest.json`, `input_row.json` (topic + verbatim curriculum),
`solution.py` + `solution_run.json`, `content.json`, `content_grade.json`, the 2 PDFs,
`visual_grade.json`.

---

## 1. Clean checkpoints (reuse `pipeline/manifest.py`)

Stages, in order — **one stage per turn, never batch them**:

| Stage | Done when |
|-------|-----------|
| `solution` | `solution.py` executes clean; `solution_run.json.passed == true` |
| `content` | `content.json` is schema-valid (`CodingWorksheet` + `TeacherGuide`); answers copied from the run |
| `content_grade` | `coding_rubric.classify()` → pass (≥19/20, C2≥L3, C3=L4, C5=L4) **and** `pre_grade_drift_check().passed` |
| `render` | both PDFs produced from the *validated* `content.json` |
| `visual_grade` | every page inspected (render→PNG→Read); C4 layout checklist clean |
| `publish` | (batch-gated) only the 2 PDFs pushed to Drive + folder hygiene check |

Rules:
- `complete_stage()` is the only way to finish a stage — atomic write, schema/gate
  validation, `run.log.jsonl` transition. On failure it parks the bad output as
  `<stage>.attempt_N.failed.json` and marks `failed`; it never half-writes the manifest.
- **Never end a session on an `in_progress` stage.** Finish it cleanly or revert to `pending`.
- Cold resume = `next_pending()` swept across all sheet dirs → the exact stage to do next.
- A sheet is **done** at `visual_grade` pass. `publish` waits for the batch gate.

---

## 2. Quality validation (the gate chain)

Independent gates, in series — nothing skips ahead:

```
code-runs (solution_run) → content schema → content_grade (≥19/20 + floors + drift) → render → visual_grade
```

- **Grade BEFORE render.** `content_grade` sits before `render`; a PDF is never built from
  ungraded content. (This is the core change from the Sheet-1 bootstrap.)
- **Rubric split by what's knowable when.** `content_grade` scores C1/C2/C3/C5 fully + C4's
  text side; `visual_grade` confirms C4's *visual* side on the real PDF.
- **The bar is the same for every product, every grade** — `coding_rubric.select_rubric(grade)`
  routes to the band rubric; the gate (≥19/20, C2≥L3, C3=L4, C5=L4) is uniform.
- On a failed gate, `coding_rubric.stages_needing_regen(scores)` + `manifest.mark_for_remediation`
  reset the right upstream stage; the runner re-walks from there.

---

## 3. Drift management

- **Curriculum drift** — every cited C3 code is validated for the grade and its text matched
  verbatim against the Ontario cache (`coding_rubric.pre_grade_drift_check` → `curriculum.py`).
- **Answer-key drift** — the answer key is generated *from* the executed `solution.py`, so it
  cannot drift from the code. A failed/missing `solution_run.json` blocks `content_grade`.
- **Image-text drift** — every `ImagePlaceholder` keyword must appear in the surrounding
  student text (`image_alignment`); enforced at `content_grade` and re-checked at `visual_grade`.
- **Cross-sheet drift** — every sheet conforms to `<batch>/STYLE_SPEC.md` (voice, format,
  mascot rotation, difficulty band). A consistency skim at batch end catches divergence.
- **Scope drift** — the topic arc is locked in `<batch>/topics.json` up front; sheets do not
  wander or self-invent topics.

---

## 4. Context management

- **All state on disk.** The manifest + JSON specs + `STYLE_SPEC.md` are the source of truth —
  not the conversation. The plan, prior findings, and current stage survive compaction.
- **One sheet authored fresh per turn**, by reading disk (the topic row, the style spec, the
  prior stage's output) — prior sheets are **not** carried in context.
- Target **~50% context** (standing user preference); lean on files over in-conversation memory.
- `/clear`-safe: resume via `next_pending()`. Nothing is lost by clearing between sheets.

---

## 5. Continuous autonomous build (NO human batch gate — updated 2026-06-13)

The calibration batch (G3 · Block Coding) shipped and the user **removed batch gating**:
build the full ~100-worksheet K–G3 catalogue autonomously, subject after subject, no human
sign-off between batches.

- **Drive the queue from `coding/subjects.json`.** The runner picks the lowest-`order` subject
  whose `status != "done"`, designs its topic arc (its first step — against that grade's rubric
  **and** `concept_ceiling`), locks it into the batch's `topics.json`, then builds every sheet.
- **Within a subject**, sheets auto-advance through ALL six stages — including `publish`. When a
  subject's sheets all pass their gates, **publish the batch to Drive automatically**
  (`drive_publish.publish_batch`) and mark the subject `done` in `subjects.json`. Then start the
  next subject. No stopping in between.
- **The quality gates REMAIN — only the *human* gate is gone.** Every sheet still must clear the
  code-runs gate, `content_grade` ≥19/20 (C2≥L3, C3=L4, C5=L4), and the model-driven
  `visual_grade` (read every rendered page). Nothing publishes that fails a gate; a failed sheet
  is parked (`failed`) and the runner moves on, converging later — never block the catalogue.
- **Grade-correct arcs.** Each grade has its own `concept_ceiling` in `subjects.json` — do NOT
  carry G3's loop-centric arc into G1/G2 (their rubrics score loops as out-of-grade). K = K-frame
  (no C3 codes). Turtle solutions are MODELLED (no GUI) and asserted.
- A `/loop` or Workflow may drive the whole catalogue unattended.

---

## 6. Handoff & memory cadence — UPDATE THE PLAN + HANDOFF AT EVERY CHECKPOINT

A **checkpoint** = a completed sheet (minor) or a completed subject (major). The user's
standing instruction: keep the plan and handoff current at each checkpoint, not just at session end.

**At each completed SHEET (minor checkpoint):**
- Finalize the manifest (visual_grade pass); append a one-line entry to `BUILD_PROGRESS.md`;
  `git commit` the sheet.

**At each completed SUBJECT (major checkpoint):**
- Publish the batch to Drive; set the subject `done` (+ `built`/`published`) in `subjects.json`.
- **Update `MASTER_BUILD_PLAN.md`** (catalogue progress table + what's next) **and `HANDOFF.md`**
  (status line + next subject) — every subject, no exceptions.
- Update `BUILD_PROGRESS.md` and **memory** (`project_coding_worksheet_pipeline.md` + the
  `MEMORY.md` hook), then `git commit` + `git push`.

Docs map: `MASTER_BUILD_PLAN.md` = authoritative full-build plan; `PILOT_BUILD_PLAN.md` = the
proven-process record (G3 Block Coding); `HANDOFF.md` = stable context; `BUILD_PROGRESS.md` = live
tracker; `subjects.json` = the machine queue. **All of plan + handoff stay current at every checkpoint.**
