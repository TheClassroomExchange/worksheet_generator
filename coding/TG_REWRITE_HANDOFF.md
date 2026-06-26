# TG Rewrite + Combined-PDF — Handoff / Resume State

**Resume:** read `coding/TG_REWRITE_PROGRESS.md` for the subject checklist, then pick the
lowest-row batch whose Gate is ▢ and run the per-subject loop below.

## What this job is
1. Rewrite each sheet's `teacher_guide` block (plain language for a non-coder; rubric
   `coding/rubrics/rubric_teacher_guide.md`).
2. Merge worksheet + teacher guide into ONE `<Title>.pdf` per folder (`combine_sheet`).
3. Re-publish per subject (idempotent; deletes old component PDFs → one Drive copy).
4. Footer brand fixed to "The Classroom Exchange" (rides along on every re-render).

## Per-subject loop (do all sheets, then checkpoint)
```
export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib
BATCH=coding/<batch_dir>
# for each NN_* in BATCH:
#  1. edit content.json teacher_guide.parts → plain-language template (see below)
#  2. python: lint_teacher_guide(dir).clean == True
#  3. python: record_grade(dir, grade, scores) → status 'pass'  (≥18, T1=L4, T4=L4)
#  4. python: coding_rubric.pre_grade_drift_check(dir)['passed'] == True
#  5. python: coding_build.render_sheet(dir); coding_build.combine_sheet(dir)
#  6. pdfinfo combined == worksheet_pages + 1 ; spot-Read a PNG for footer/voice
#  7. python: coding_build.finalize_visual(dir, status='pass', notes=..., inspected_pages=[...])
# then per subject:
#  - back-test: lint+classify+drift across batch all pass
#  - each topic dir has exactly ONE <Title>.pdf, no strays
#  - drive_publish.publish_batch(Path(BATCH))  → hygiene 1 file/topic
#  - update PROGRESS.md row + scores; refresh this handoff
#  - git commit (one per subject) on coding-tg-rewrite-wordmark ; DO NOT merge main
```

## TG section template (grade-adapted)
What this worksheet teaches · Before you start (tool/no-computer) · How to lead it
(show→together→try-alone + big idea) · Answer key (verified correct) · If students get
stuck (watch-for + easier + harder) · Ontario curriculum link (verbatim quote + "In
plain terms:" gloss) · You'll know it worked when. **Keep it tight — one page.**

## Grade-specific notes (preserve named concepts, gloss once)
- **K**: unplugged/MODEL, symbols only, NO loops/code; curriculum = K-frame statement (not C3). Most K = "no computer needed".
- **G1**: sequential only, no loops. Debugging subject = "find the bug / fix it".
- **G2**: concurrency = two sprites Bit (green) + Pixel (purple) running AT THE SAME TIME; events = broadcast / receive message. Keep these terms, gloss them.
- **G3**: loops (repeat N) + Python Turtle; debugging method = SHOULD → DOES → FIX.

## Gotchas
- WeasyPrint needs `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`.
- `text` field is a string OR list[str] — handle both when rewriting.
- Keep the verbatim Ontario quote EXACT (drift gate) — add gloss beneath, never edit the quote.
- Linter excludes lines starting C1./C2./C3./k-frame from jargon scan (the verbatim quotes).
- Compact CSS already tightened; if a guide still spills to 2 pages, trim wording (don't loosen CSS).
- topics.json statuses are already "built" — no flip needed before publish.
- Publish is outbound to Drive (token.json) — authorized by the approved plan.

## State as of last update (2026-06-26)
Infrastructure done + committed. 2 sample sheets done (g1_block_sequential/01,
g3_python_turtle/03) — combined PDF built + finalized, NOT yet published.
Next: finish g1_block_sequential (sheets 02–08), then g3_python_turtle (01,02,04–07), then the K/G1/G2/G3 batches.
