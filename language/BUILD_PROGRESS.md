# Language Worksheet Build — Progress

Plan: `~/.claude/plans/using-the-examples-peaceful-rossum.md`
Worktree: `~/Desktop/TCE/wg-language` (branch `language-worksheets`, off origin/main + roomy merge).
Venv: `~/Desktop/TCE/worksheet_generator/venv` (run with `PYTHONPATH=<worktree> DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`).

## Phase 0 — Curriculum + scaffolding  ✅ DONE
- [x] worktree off origin/main + merged roomy-kg1-layout (layout_rubric, fit_render, finalize_visual) + border tool
- [x] `curriculum/language.json` — verbatim K (A2.1-6) + G1 (B2.1-8) + G2/G3 (B2.1-5). 28 expectations, validated.
- [x] `language/phonics_scope.json` — 117 ordered grapheme unlocks + cumulative heart words.
- [x] `pipeline/decodability.py` — run-gate; BACKTESTED 12/12 controls (pos + neg: boat/rain/cake/oo/early-K).
- [x] `pipeline/language_rubric.py` + `rubric_language_{K,G1,G2,G3}.md` — 20/20 gate, drift-check (decodability+curriculum+image). validated.
- [x] `pipeline/phonics_images.py` — OpenMoji black resolver (20/20 backtested) + AI backend (OpenRouter/OpenAI/Stability).
- [x] `pipeline/worksheet_pdf.py` — added phonics parts: reading_rows, read_tracker, sound_boxes, formation, picture_row + CSS; mascot optional. Rendered OK (sh smoke test).
- [x] `language/AGENTS.md` ops guide.

## Phase 1 — 2 samples × 2 image variants → STOP for approval  ⏳ IN PROGRESS
- [ ] Sample 1 — G1 "I Can Read Sentences" (sh): OpenMoji variant
- [ ] Sample 1 — sh: AI variant (BLOCKED on OPENROUTER_API_KEY → ~/.claude/.openrouter.env)
- [ ] Sample 2 — K Letter & Sound (short a / m): OpenMoji variant
- [ ] Sample 2 — K: AI variant (blocked on key)
- Each: combined ws+TG, 20/20, grade border (G1 blue / K pink), read every page. NO publishing.

## Phase 2 — scope lock (full K-3 queue)  ⬜ PENDING
## Phase 3 — autonomous full build → STOP (no publish)  ⬜ PENDING
## Phase 4 — publish (Drive + marketplace) — DEFERRED until user approves random samples  ⬜

## Open items
- AI image backend: awaiting OPENROUTER_API_KEY in ~/.claude/.openrouter.env (OpenRouter support wired;
  model google/gemini-2.5-flash-image-preview). OpenMoji variants proceed without it.
- prose parts HTML-escape: directions use plain text; row-level bold via reading_rows.bold.
