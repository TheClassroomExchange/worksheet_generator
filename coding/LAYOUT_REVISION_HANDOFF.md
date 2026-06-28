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

## CP5 — Commit (2026-06-28)
- Commit `e92056d` on branch `roomy-kg1-layout` (pushed to origin): 106 files — 48 K/G1
  PDFs + 48 layout_grade.json + renderer/rubric + trackers/tooling. No content.json edits;
  no non-K/G1 PDFs touched.

## CP6 — Drive republish (2026-06-28) — COMPLETE
- `drive_publish.publish_batch` for all 6 K/G1 batches (statuses already "built").
  Hygiene 1 file/topic for all 48.
- Blast-radius verified: pre vs post Drive listing — 48==48, keys identical, **0 IDs
  changed** (in-place update, no dupes/orphans); all 48 modifiedTime = 2026-06-28.
- Byte-check: 2 live PDFs (G1 Start and Go, K First, Next, Last) md5-identical to local
  roomy versions → roomy layout confirmed LIVE.
- Revert path remains: `scratchpad/backup_originals/` PDFs + `drive_ids.json` (re-upload
  by exact id).

## DONE (Round 1) — all 48 K/G1 worksheets revised (roomy), gated, committed, live on Drive.

---

# ROUND 2 — kill near-empty pages (2026-06-28)

## R2 CP0 — Bug + sweep
- User found near-empty pages (page with only the title), e.g. spot_the_wrong_block p1.
- Ink-coverage sweep of all 48: **11/48 (23%)** had a near-empty worksheet page (page-1 blank
  ×6, trailing near-empty ×5); 3/48 mild underfill; reflow flags cosmetic only.
- Root cause: `.qgroup { break-inside: avoid }` force-pushes an over-tall group to the next page,
  blanking the page it left.
- Baseline snapshot of all 48 round-1 PDFs → `scratchpad/backup_round2/`.

## R2 CP1 — Fix + 2-item review gate (user-approved)
- Adaptive `roomy_level` ladder (L0 full → L3 plain-flow) in `worksheet_pdf.py`; `page_fill_ok()`
  ink-oracle in `layout_rubric.py`; `coding_build.fit_render()` accepts the roomiest level passing
  content-lock AND page_fill_ok. L0 == round-1 output (byte-identical CSS).
- Proved on 2 items (spot_the_wrong_block = page-1 blank; build_the_code = trailing blank) → both
  fixed at L1; **user approved → autonomous.**

## R2 CP2 — Validator
- cavecrew-reviewer: 1 finding (page_fill_ok assumed 1-page TG). Verified all 48 TGs are 1 page;
  hardened `page_fill_ok` to detect TG pages by footer. No other issues.

## R2 CP3 — Batch auto-fit (all 48)
- `fit_render` all 48: **48/48 pass**, 11 changed (8×L1, 3×L2), 37 stay L0.
- Authoritative re-sweep: **page_fill_ok 48/48, content_lock 48/48**.
- Visual: all 11 changed sheets reviewed full-size — full pages, no blanks/clipping, colours/mascot
  intact, compaction barely perceptible. 11 re-graded (layout_grade.json), all pass.
- The 37 L0 sheets restored to round-1 bytes (re-render only re-stamps PDF timestamp) → only the
  11 changed PDFs differ.

## R2 CP4 — Commit (pending)
## R2 CP5 — Republish 11 changed topics (pending)
