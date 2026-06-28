# Layout Revision — Handoff / Checkpoint Log

Additive log for the K & G1 roomy-layout revision. Newest checkpoint at the bottom.

## CP0 — Setup (2026-06-28)
- Branch `roomy-kg1-layout` off `main`.
- Snapshotted all 48 K/G1 originals (PDF + content.json) to
  `scratchpad/backup_originals/` + 48 live Drive PDF IDs (`drive_ids.json`).

## CP1 — Renderer + prototype, human-approved (2026-06-28)
- Implemented roomy mode (v1 fonts/spacing/cards). Prototyped G1 `01_start_and_go` +
  K `01_first_next_last`; content-lock PASS; direction approved by user.
- v2 fixes per feedback: question-with-stimulus grouping (`.qgroup`), large single-answer
  write box (`grid-cell:only-child`), tighter spacing, trimmed header. Re-prototyped +
  before/after shown; **user approved → autonomous for the remaining 46.**

## CP2 — Validator gate (2026-06-28)
- cavecrew-reviewer on renderer diff: 0 critical. Fixed trailing-newline (non-roomy CSS
  now byte-identical). Footer-mask finding N/A (footer_topic has "N." prefix).
- G2/G3 regression: text + page count identical → roomy does not leak.

## CP3 — Batch render + content-lock, all 48 (2026-06-28)
- `coding/layout_revision_batch.py`: render+combine+content-lock for 48 topics.
- 48/48 content-lock PASS (3 initial false-positives — pdftotext dehyphenation +
  symbol-card reflow — resolved by the multiset fallback in `content_unchanged`).

## CP4 — Visual L1–L5 gate, all 48 (2026-06-28)
- Per-subject montages (`coding/layout_montage.py`) + full-res spot checks of every
  wrap/number-path case (put_it_in_order, fix_the_code, plan_and_code).
- 24 K + 24 G1 all PASS (16/16). `layout_grade.json` written per topic.
  Tracker: `LAYOUT_REVISION_PROGRESS.md`.
- Notes: roomy worksheets run +1 page (acceptable — one idea/page); number paths stay
  single-row; multi-glyph "day" cards wrap gracefully with labels; some bottom whitespace
  on block-stack sheets, no orphaned questions.

## CP5 — Commit (pending)
## CP6 — Drive republish (pending)
