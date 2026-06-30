# Language Worksheet Build — Progress

Plan: `~/.claude/plans/using-the-examples-peaceful-rossum.md`
Worktree: `~/Desktop/TCE/wg-language` (branch `language-worksheets`).
Venv: `~/Desktop/TCE/worksheet_generator/venv`. Run with
`PYTHONPATH=<worktree> DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib` and
`set -a; . ~/.claude/.openrouter.env; set +a` (image key).

## Phase 0 — Curriculum + scaffolding ✅ DONE
## Phase 1 — samples (×2 image variants) ✅ APPROVED
Design LOCKED 2026-06-30: big "A Teachable Teacher" template (corner tab, huge
sentences, big bordered picture column, big tracker), **kawaii AI images (faces on
animals/people only, none on objects)**, **decorative rounded double border**.
See `language/DESIGN_STANDARD.md` (gated by rubric C4 + pipeline defaults).

## Phase 2 — scope-lock ✅ DONE
`language/subjects.json` + per-subject `topics.json` = **14 subjects / 117 worksheets**
(K 33 · G1 52 · G2 21 · G3 11), one sheet per phonics target.

## Autonomous engine ✅ BUILT + PROVEN
- `language/gen_content.py` — data-entry → content.json (3 templates: sentences,
  word_building, letter_sound) per DESIGN_STANDARD, verbatim curriculum. `order`
  override supported (early digraph fluency uses full cumulative inventory).
- `language/run_build.py` — `python -m language.run_build <subject_id|all>`;
  per-subject: gen → `language_build.build_unit` (decodability→images→render→border)
  → `language_rubric.record_grade` (20/20, drift-gated) → checkpoint topics.json
  per unit (RESUMABLE; re-run skips `built`).
- Per-subject **data.json** = the authored IP (sentences/words). Build a subject:
  author `language/<sid>/data.json` (keyed by target/dir/nn) → `run_build <sid>`.

## Phase 3 — autonomous build → STOP before publish  ⏳ IN PROGRESS
Per-subject status (author data.json → run_build → spot-check 1 page → mark done):
- [⏳] k_letter_sounds (24) — data.json authored; BUILDING in background (img-gen slow)
- [ ] k_digraphs (9)            — needs data.json (qu,z,ng,sh,ch,ck,th,th,wh; use order:33; sh sentences in _samples/g1_sh)
- [ ] g1_doubles_blends (9)
- [ ] g1_long_vowels_vce (10)
- [ ] g1_vowel_teams (15)
- [ ] g1_rcontrolled (7)
- [ ] g1_diphthongs (6)
- [ ] g1_silent_letters (5)
- [ ] g2_silent_letters (2)
- [ ] g2_low_freq_vowels (7)
- [ ] g2_rcontrolled_and_more (12)
- [ ] g3_suffixes (4)            — -ing sample in _samples/g3_ing
- [ ] g3_prefixes (3)
- [ ] g3_syllables_morphology (4)
Approved reference samples (build once data is in): _samples/{g1_sh,k_short_m,g2_aw,g3_ing}.
**END at full build. Do NOT publish — user spot-checks random samples first.**

## Phase 4 — publish (Drive + marketplace) — DEFERRED until user approval
Drive: `Language Worksheets / Grade N / <NN. Title> / Title.pdf` (drive_publish, flip
topics status→built first). Marketplace: catalogue_upload direct-insert + watermark;
blast-radius protocol; REVERT_ITEM_IDS.json.

## Authoring notes / gotchas
- Decodable sentences must pass the gate at the target's order (+heart words). Early
  digraphs (qu@25) are inventory-tight → set data `"order"` to the band end (K=33).
- Every pic word must appear in its sentence (image_alignment drift gate).
- Give all rows in a reading_rows pictures OR none (empty pic cells look odd).
- Image gen ~5-10s each; run subjects in background; cache in assets/ai_line_art.
- Spot-check 1 page/subject (design approved); rely on automated gates for the rest.
