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

## 5. Supervised autonomy (the batch gate)

- Autonomy is **bounded to one batch** at a time. Within a batch, sheets auto-advance through
  stages 0–4.
- A batch **stops** at a human **`batch_verification`** gate: every sheet (both PDFs + its
  `content_grade`/`visual_grade`) is presented for the user's sign-off.
- Only on sign-off do the batch's `publish` stages run and the **next** batch begin.
- The **first** batch (G3 · Block Coding) is the **calibration batch**, reviewed in full before
  autonomy widens to later subjects/grades.
- **Non-negotiable:** no cross-batch unattended runs until the user explicitly widens the leash.
  A `/loop` or Workflow may drive sheet-after-sheet *within* a batch, but always halts at the gate.

---

## 6. Handoff & memory cadence

- **`BUILD_PROGRESS.md`** (live tracker) — updated whenever a sheet hits a terminal gate
  (pass, or parked-failed) and at every session end.
- **`HANDOFF.md`** (stable) — updated only when the process or scope changes.
- **`PILOT_BUILD_PLAN.md`** (authoritative plan) — updated if the plan itself changes.
- **Memory** (`project_coding_worksheet_pipeline.md` + the `MEMORY.md` hook) — updated at session
  end and on each subject completed; always points at `BUILD_PROGRESS.md` as live truth.
- Commit at every terminal gate; push at session end.
