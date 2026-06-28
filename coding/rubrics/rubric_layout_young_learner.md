# Young-Learner Layout Rubric (K & G1 roomy revision)

Gates the **layout-only** revision of Kindergarten & Grade 1 coding worksheets:
bigger images, more writing room, generous spacing — **content and language
unchanged**. Scored per sheet by `pipeline/layout_rubric.py`. L1–L4 are scored
1–4 by the reviewer reading the rendered pages; L5 is mechanical.

This rubric does NOT re-judge pedagogy or wording — those passed already and are
held invariant by L5. It judges only the physical layout of the revised render.

## Criteria

**L1 — Writing room (HARD: must = 4).**
Every place a child writes is large enough for a young hand:
- single-answer boxes (`grid 1×1`) render as a large full-width write area (~100px);
- ruled answer lines are tall (~34px) with ≥2 lines where a written response is expected;
- multi-cell answer grids (e.g. 1×3) have generous cells (~64px).
4 = all write areas generous · 3 = mostly · ≤2 = any cramped/thin write slot remains.

**L2 — Image / target size.**
Symbol cards, block chips, grids, dot/shape figures, and the mascot are enlarged
and legible; the number path (0–5) reads large and stays on ONE row (no wrap that
reorders cards).
4 = all primitives clearly enlarged & crisp · 3 = mostly · ≤2 = a primitive is small or a row wrapped.

**L3 — Breathing room.**
Generous vertical spacing between items; one idea per cluster; nothing visually
crowded; comfortable margins.
4 = airy throughout · 3 = mostly · ≤2 = cramped clusters.

**L4 — Render integrity & question grouping.**
- nothing clipped, truncated, or running off the page;
- mascot renders (not a broken image), block/symbol colours correct (operators green,
  motion blue, events orange, value slate);
- clean page breaks — no element split mid-box;
- **every question stays on the same page as its stimulus**: an exercise is not
  orphaned at the top of a page away from the blocks/images it refers to (a question
  glued to its primary stimulus by the `.qgroup` wrapper);
- no near-empty leading page (content starts on page 1).
4 = all clean · 3 = one cosmetic nit (e.g. a short trailing summary alone on the last page) ·
≤2 = a question separated from its stimulus, a clip, a wrong colour, or a broken mascot.

**L5 — Content invariance (HARD GATE, pass/fail).**
`pdftotext` of the revised PDF == the snapshot original, normalized (whitespace
collapsed; per-page footer artifacts — "The Classroom Exchange", "page N", the
footer topic — stripped). ANY wording/character change fails. Computed by
`layout_rubric.content_unchanged(old_pdf, new_pdf, footers)`.

## Gate

`classify(scores, content_ok)` → **status = pass** iff:
- `L1 + L2 + L3 + L4 ≥ 14` (of 16), AND
- `L1 == 4`, AND
- `L5 content_ok == True`.

A fail loops back: fix the root cause in the renderer (whole vector, not the one
sheet), re-render, re-verify. Per the snapshot→verify→swap protocol, a sheet that
fails any check is reverted to its snapshot until it passes.

## Note on L1–L3 uniformity

Because all K/G1 sheets share the one approved roomy stylesheet, L1–L3 are a
property of that stylesheet (approved on the 2 prototypes) and are expected to be
4 for every sheet. The per-sheet visual review therefore concentrates on **L4**
(this sheet's specific page-break / overflow / colour / mascot outcome) and on
confirming L1–L3 didn't regress for this sheet's particular content shape.
