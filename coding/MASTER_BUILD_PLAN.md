# Master Build Plan — Full K–G3 Coding Worksheet Catalogue (~100 worksheets)

**Authorized 2026-06-13.** Build the **entire** K–G3 coding catalogue autonomously —
**no human batch gating** (the calibration batch shipped and proved the pipeline).
This is the authoritative plan; `PILOT_BUILD_PLAN.md` is the proven-process record,
`AUTONOMOUS_BUILD.md` is the process contract, `subjects.json` is the machine queue,
`BUILD_PROGRESS.md` is the live tracker.

## Scope: 12 subjects (4 grades × 3), ~96 worksheets

Each worksheet ships **2 PDFs** (student Worksheet + Teacher Guide). Target ~7–8 topics/subject.

| Grade | Subjects | Rubric | Concept ceiling (grade-correct — do NOT exceed) |
|-------|----------|--------|--------------------------------------------------|
| **K** | Unplugged CT ✅ · Sequencing & Algorithms ✅ · Intro Block Coding ✅ | `rubric_coding_K.md` | unplugged/symbol-only, **no text, no loops**; K-frame (not C3) |
| **G1** | Block Coding (Sequential) ✅ · Unplugged Sequencing ✅ · Intro Debugging ✅ | `rubric_coding_G1.md` | **sequential events only**; ≤6 blocks; no loops/concurrency |
| **G2** | Block Coding (Concurrent) ✅ · Events & Parallel Scripts · Debugging & Reading Code | `rubric_coding_G2.md` | sequential + **concurrent**; ≤8 blocks; **loops still out** |
| **G3** | Block Coding ✅ · Intro Python Turtle ✅ · Debugging ✅ | `rubric_coding_G3.md` | + **repeating events (loops)**; Turtle = first typed code |

**Per-grade arcs differ.** The G3 "loop-centric" lesson is G3-specific (its rubric caps
non-loop sheets at C1-L2). G1 is sequential-centric, G2 concurrent-centric, K unplugged —
each arc is designed against its own rubric + `concept_ceiling`. Never carry one grade's arc down/up.

## Build order (from `subjects.json` `order`) — progress
1. G3 Block Coding ✅ **SHIPPED** → 2. G3 Intro Python Turtle ✅ **SHIPPED** → 3. G3 Debugging ✅ **SHIPPED** →
4. K Unplugged CT ✅ **SHIPPED (8)** → 5. K Sequencing & Algorithms ✅ **SHIPPED (8)** → 6. K Intro Block Coding ✅ **SHIPPED (8)** → 7. G1 Block Coding (Sequential) ✅ **SHIPPED (8)** → 8. G1 Unplugged Sequencing ✅ **SHIPPED (8)** → 9. G1 Intro Debugging ✅ **SHIPPED (8)** → 10. G2 Block Coding (Concurrent) ✅ **SHIPPED (8)** → **11. G2 Events & Parallel Scripts ← NEXT** → 12. G2 Debugging & Reading Code.  *(10/12 subjects, 77 sheets shipped. K + G1 COMPLETE; G2 1/3.)*

**K visual primitives:** `worksheet_pdf.py` carries two additive K helpers — the `symbols` part (large geometric
symbol cards (★ ● ▲ ■ ➡ ↻ …) + a dashed "what comes next" answer card; this is what makes K sheets
genuinely picture/symbol-driven (color emoji render too small/inconsistent — avoid as backbone). The
`blocks` part also takes part-level `size` ("md"/"lg") + per-block `blank:true` dashed slot — the K Intro Block
coloured ScratchJr stack metaphor (green GO ⚑ + blue move ➡⬅⬆⬇). Footer is CSS-escaped (apostrophe-safe).
K solutions MODEL the answer (no executable text code) and assert it for the run-gate. Reuse for K subjects 5 & 6.
(The runner picks the lowest-`order` subject with `status != done`. Reorder `subjects.json` to change priority.)

## Per-subject loop (autonomous, no human gate)
1. **Design the arc** (subject's first step): ~7–8 topics against the grade's rubric +
   `concept_ceiling`; write the batch `<dir>/topics.json` (locked) + `<dir>/STYLE_SPEC.md`.
2. **Per sheet** (one per turn, checkpointed via `manifest.coding_stages_for_sheet`):
   `solution.py` (run-gate; Turtle/forward-left-right paths are MODELLED, not GUI) →
   `content.json` → `coding_build.build_to_render()` (rubric ≥19/20 + floors + drift **before** render) →
   read every rendered page (`visual_grade`) → `finalize_visual()`. Tighten teacher guides to 1 page.
3. **Publish the subject** automatically: `drive_publish.publish_batch(<dir>)` → numbered topic
   folders, only the 2 PDFs each, hygiene-checked. Set the subject `done` in `subjects.json`.
4. **Checkpoint the docs** (see `AUTONOMOUS_BUILD.md` §6): update THIS plan + `HANDOFF.md` +
   `BUILD_PROGRESS.md` + memory; commit + push. Then next subject.

## Gates that REMAIN (only the human gate was removed)
code-runs (solution) → content schema → **content_grade ≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4 + drift** →
render → **visual_grade** (model reads every page). A failed sheet is parked `failed`; the runner
moves on and converges later — never block the catalogue.

## Reused machinery (all proven on G3 Block Coding)
`pipeline/coding_rubric.py` (`select_rubric(grade)`, gate), `pipeline/coding_build.py`
(`run_solution`/`render_sheet`/`build_to_render`/`finalize_visual`), `pipeline/worksheet_pdf.py`
(branded renderer), `pipeline/drive_publish.py` (`publish_batch`), `pipeline/manifest.py`
(checkpoints), `assets/mascots/bit_wave.svg` (Bit; full cast still a fast-follow).

## Known per-grade build notes
- **K**: no C3 codes — cite the **K-frame** (Problem Solving & Innovating). Symbol/picture tasks;
  the run-gate models the intended sequence/answer (no text code to execute).
- **Turtle (G3)**: `solution.py` models the turtle path mathematically and asserts the figure
  ("executes clean" via the model — no Tk/GUI). This is the subject where the block→text bridge L4 path applies.
- **Mascot cast**: Bit is the actor everywhere for now; drawing the 3–5 char cast + INDEX is a
  parallel fast-follow that does not block worksheet production.

## Verification (per subject, before marking done)
All sheets: run-gate PASS, `content_grade` pass (≥19/20), `visual_grade` pass; `drive_publish`
hygiene = exactly 2 PDFs/folder; independent Drive-API audit (0 strays) on the subject's folder.
