# Layout Revision — Plan (K & G1 roomy layout)

## Why
Kindergarten & Grade 1 learners need **bigger images and large spaces to write**.
The existing K/G1 coding worksheets were pedagogically fine but cramped. This pass
revises ONLY size & spacing — **content and language are byte-identical** (enforced
by a hard `pdftotext` content-lock). G2/G3 and all teacher guides are untouched.

Reference exemplars for the target feel: Drive page-6 "Map My Way" and Image #5
"Code with Symbols / Match the Code" (large images, large write areas, generous rows).

## What changed (renderer only — no content.json edits)
- **`pipeline/worksheet_pdf.py`** — new grade-scoped "roomy" mode (`spec["roomy"]`):
  - `_roomy_css()` scales body font (11→13pt), line-height, item spacing, part titles,
    the goal/name bars, the mascot, symbol cards & glyphs, block chips, ruled answer
    lines (22→34px), and grid cells (40→64px).
  - **Large single-answer box:** `.ex-grid .grid-cell:only-child { height:100px }` turns
    a `grid 1×1` answer ("Run Code A", "You try") into a big full-width write area;
    multi-cell grids (write-the-order, maps) keep 64px.
  - **Question stays with its stimulus:** `render_worksheet_html` (roomy only) wraps each
    exercise + its preceding stimulus parts into `<div class="qgroup">`
    (`break-inside: avoid`). Grouping = [stimulus + FIRST following exercise]; each
    extra consecutive exercise is its own group — keeps the key pairing intact without
    dumping a whole long activity onto a fresh page.
- **`pipeline/coding_build.py`** — `render_sheet` sets `roomy=True` when the topic's grade
  ∈ {Kindergarten, Grade 1} (`_grade_of`, `ROOMY_GRADES`). TG stays `compact`.

## Gates (all passed)
1. **Content-lock (hard):** `pipeline/layout_rubric.content_unchanged` — `pdftotext` of new
   == snapshot original (footers stripped; tier-2 fallback = identical word multiset,
   hyphen/reflow-tolerant, still catches any real word change). 48/48 PASS.
2. **Layout rubric L1–L5** (`pipeline/layout_rubric.py` + `rubrics/rubric_layout_young_learner.md`):
   L1 writing room (hard=4) · L2 image size · L3 breathing room · L4 integrity & question
   grouping · L5 content invariance. 48/48 PASS (16/16 each). `layout_grade.json` per topic.
3. **Adversarial validator** (cavecrew-reviewer) on the renderer diff: 0 critical; 2 minor
   (trailing-newline fixed; footer-mask not applicable — footer_topic carries "N." prefix,
   never equals a content line).
4. **Visual** (per-subject montages + full-res spot checks of every wrap/number-path case):
   all roomy, grouped, no clipping / blank pages / orphaned questions / wrong colours /
   broken mascots. Number paths stay single-row; multi-glyph "day" cards wrap gracefully.
5. **Regression:** one G2 + one G3 re-rendered → text + page count identical (roomy doesn't leak).

## Revert safety
Per-sheet snapshot in `scratchpad/backup_originals/<batch>/<topic>/` (PDF + content.json),
plus `backup_originals/drive_ids.json` (48 live Drive PDF IDs). Any sheet that failed a
gate was auto-restored from its snapshot (driver `coding/layout_revision_batch.py`).

## Scope
24 K (k_unplugged_ct, k_sequencing, k_intro_block) + 24 G1 (g1_block_sequential,
g1_unplugged_sequencing, g1_intro_debugging) = 48 sheets.
