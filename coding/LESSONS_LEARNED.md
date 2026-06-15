# Coding-Worksheet Catalogue — Lessons Learned

Distilled from building the complete **K–G3 coding-worksheet catalogue**: 12 subjects ·
93 worksheets · 186 PDFs, every sheet 20/20. Companion to `BUILD_PROGRESS.md` (live log +
final summary), `HANDOFF.md`, `MASTER_BUILD_PLAN.md`, `AUTONOMOUS_BUILD.md`, `subjects.json`.
The runnable process also lives as the **`coding-worksheet-builder`** skill (in
`~/.claude/skills/` and the `TheClassroomExchange/skills` repo).

## The per-sheet loop (atomic unit of work)
For each `coding/<subject>/<NN_slug>/`:
1. **`solution.py`** — runnable answer-key gate; MODELS the answer + `assert`s it. Run it; must pass.
2. **`input_row.json`** — grade/subject/topic + `curriculum_codes` + **verbatim** expectations.
3. **`content.json`** — worksheet + teacher_guide renderer specs.
4. **`coding_build.build_to_render(dir, unit_id=, input_row=, scores={C1..C5}, grade_label=, rubric_file=)`**
   — records the content grade (gate **≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4** BEFORE render),
   then renders both PDFs. (Returns the grade dict, not the manifest.)
5. **`pdftoppm -png -r 110`** both PDFs → **read every page** (overflow, mascots, block colours,
   2pp worksheet + 1pp teacher guide).
6. **`coding_build.finalize_visual(dir, status='pass', notes=..., inspected_pages=[...])`**.

Per subject: design the 8-topic arc → `topics.json` → build all sheets → flip `topics.json`
statuses to `"built"` → `drive_publish.publish_batch(<dir>)` → audit the Drive folder
(N topic folders × 2 PDFs, 0 strays) → mark `done` in `subjects.json` → update the 4 tracker
docs + memory → commit/push. Commit WIP ~every 2 sheets to survive context loss.

## What made the quality bar hold
- **Grade BEFORE render** — nothing renders ungraded; the gate is in `build_to_render`.
- **Every answer modelled + asserted** in `solution.py`. For debug sheets, model BOTH the
  buggy run AND the fixed run and assert both.
- **Every page visually inspected** — text pre-flight can't see overflow/placeholder issues.
- **Curriculum cited verbatim** from the Ontario cache (drift-checked).

## Grade-distinct, assertable representations (reuse; don't reinvent)
- **K** = K-frame, symbol-only (`symbols` cards + arrow/flag `blocks`), no text/loops; solution.py
  MODELS the answer. Lanes: classify/pattern · arrow-path board · ScratchJr colour BLOCK-STACK.
- **G1 / G2 / debug** = **number-path 0–5 clamped interpreter** `run(start, moves)` with
  `pos = max(0, min(5, pos))`; Scratch text-label blocks.
- **G2 two-sprite concurrency** = Bit (green `assets/mascots/bit_wave.svg`) + Pixel (purple
  `assets/mascots/pixel_wave.svg`), each its own script on a shared 0–5 path; one green flag
  starts BOTH; every question = COMBINED outcome (the C2 hard gate for genuine concurrency).
- **G2 events** = **event-aware interpreter** `scripts = (trigger_event, home, moves)`; track fired
  events (green flag + broadcasts) + sent messages; run only triggered scripts; `broadcast 'm'` +
  `when I receive 'm'` fires only on a matching message.
- **Debug sheets** = state the goal, give two parallel scripts where exactly ONE is buggy (the
  correct sprite already meets the goal). Bug types: wrong value · wrong direction · mismatched
  message · missing block · predict-then-find · mixed challenge.

**Per-grade concept ceilings are grade-specific** (`subjects.json`): loop-centric = **G3 only**;
G1 sequential (no loops/concurrency); G2 + concurrent (loops OUT); K K-frame (no C3). Carrying one
grade's arc into another scores out-of-grade and fails the rubric. **Each subject gets its own arc.**

## Renderer primitives (`pipeline/worksheet_pdf.py`, additive / zero-regression)
- `blocks`: per-block `cat` colour (operators=green, motion=blue, **events=orange ⚑ hats**,
  value=slate); part-level `size` "md"/"lg"; per-block **`blank:true`** = dashed write-slot.
- `symbols`: large geometric cards (★ ● ▲ ■ ➡ ↻) + per-item `label` (★ = path goal-marker on
  debug sheets). **Color emoji render too small — never the backbone; ⚑ renders mono.**
- Images embed via `Path(...).resolve().as_uri()` (file:// URI; PNG + SVG both work).
- Footer = CSS Paged-Media margin boxes in `_css()` (`@bottom-left` topic · `@bottom-center` brand
  · `@bottom-right` page N). Teacher guides use `compact` body typography.

## Gotchas (learned the hard way)
- **Teacher-guide overflow:** long before/after TGs (alter sheets) spill to a 2nd near-empty page.
  Fix: trim a differentiate bullet or two, re-render via `coding_build.render_sheet` (no re-grade).
- **Publish needs `"built"`:** `publish_batch` only pushes topics whose `topics.json` status is
  `"built"` — flip them first; it's idempotent (updates the 2 PDFs/topic in place).
- **Number path stays 0–5 (6 cards)** — 7 cards (0–6) wrap and break the number-line metaphor.
- **WeasyPrint env:** run python with `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`.
- **Disk/temp:** if the machine disk fills mid-run, clear `/tmp/*.png` render artifacts to continue;
  `finalize_visual` writes tiny JSON. Avoid `/tmp/*.png` globs in compound zsh commands
  ("no matches found") — run `pdftoppm` separately or use distinct output prefixes.
- `input_row.json` may be re-written by a linter after creation — harmless, intentional.

## Extending the catalogue
Add a subject = new row in `subjects.json` (status != done, grade-specific `concept_ceiling`) +
its own `topics.json` + run the per-sheet loop. The runner picks the lowest-`order` subject with
`status != done`.

## Open items
- **Branding** (pending): add the chalkboard mascot + "The Classroom Exchange" wordmark to every
  footer — see `BRANDING_PLAN.md`.
- **Branch → main:** the catalogue is on `coding-worksheet-pilot`; `main` is 66 commits behind. A
  PR-merge (preserve history) was chosen but is a deliberate, separate step.
