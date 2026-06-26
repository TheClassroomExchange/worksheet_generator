# Teacher-Guide Plain-Language Rewrite + Combined-PDF — Progress

**Goal:** every K–G3 coding sheet = ONE combined PDF (worksheet pages → teacher guide
at back), with the teacher guide rewritten in plain, non-technical language for a
teacher who has never coded, scored ≥18/20 on `rubric_teacher_guide.md`. Footer brand
corrected to **The Classroom Exchange**.

Branch: `coding-tg-rewrite-wordmark`. **Not merged to main — hand to user at end.**

## Per-sheet gate (every sheet)
rewrite `teacher_guide.parts` → JSON ok → `lint_teacher_guide` clean → self-grade
`record_grade` **pass** (≥18, T1=L4, T4=L4) → `pre_grade_drift_check` passed →
`render_sheet` + `combine_sheet` (one `<Title>.pdf`) → combined page-count = ws+1,
footer correct → `finalize_visual`.

## Infrastructure (done)
- [x] Wordmark fix `worksheet_pdf.py:240` + 6 docs.
- [x] Compact CSS tightened (TG-only) — guides hold 1 page.
- [x] `rubric_teacher_guide.md` + `pipeline/teacher_guide_rubric.py` (gate + linter + record_grade) + concision note.
- [x] `coding_build.combine_sheet()` — pdfunite worksheet→TG, delete components, one PDF/folder.
- [x] `drive_publish.py` — one combined PDF, deletes stale component PDFs on Drive, hygiene = exactly 1 file/topic.

## Subjects (12 batches, 93 sheets) — checkpoint per subject
Legend: ☑ all sheets pass gate + combined · ⬆ republished to Drive · ⎘ committed

| # | Grade | Batch dir | Sheets | Gate | Drive | Commit |
|---|---|---|---|---|---|---|
| 1 | G1 | g1_block_sequential | 8 (1/8) | ▢ | ▢ | ▢ |
| 2 | G3 | g3_python_turtle | 7 (1/7) | ▢ | ▢ | ▢ |
| 3 | K | k_unplugged_ct | 8 | ▢ | ▢ | ▢ |
| 4 | K | k_sequencing | 8 | ▢ | ▢ | ▢ |
| 5 | K | k_intro_block | 8 | ▢ | ▢ | ▢ |
| 6 | G1 | g1_unplugged_sequencing | 8 | ▢ | ▢ | ▢ |
| 7 | G1 | g1_intro_debugging | 8 | ▢ | ▢ | ▢ |
| 8 | G2 | g2_block_concurrent | 8 | ▢ | ▢ | ▢ |
| 9 | G2 | g2_events_parallel | 8 | ▢ | ▢ | ▢ |
| 10 | G2 | g2_debugging_reading | 8 | ▢ | ▢ | ▢ |
| 11 | G3 | pilot_g3_block_coding | 7 | ▢ | ▢ | ▢ |
| 12 | G3 | g3_debugging | 7 | ▢ | ▢ | ▢ |

**Done so far:** 2 sample sheets (g1_block_sequential/01, g3_python_turtle/03) rewritten,
20/20, combined PDF built, finalized. Not yet published (waiting to publish per-subject).

## Per-sheet scores log
(append `batch/NN — total/20 status` as each sheet passes)
- g1_block_sequential/01_start_and_go — 20/20 pass
- g3_python_turtle/03_square_loop — 20/20 pass
