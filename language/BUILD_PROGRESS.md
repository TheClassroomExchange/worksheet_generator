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

## ⛔ BLOCKED (2026-06-30): OpenRouter "Key limit exceeded (total limit)" — 76/112 built
Image gen returns HTTP 403; account has credit ($63 left) but the API KEY has a per-key
spend cap that's hit (~$41.84 / ~450 images). **RESUME:** raise/remove the key limit at
openrouter.ai workspace keys (or drop a new key into ~/.claude/.openrouter.env), then:
`cd ~/Desktop/TCE/wg-language && set -a; . ~/.claude/.openrouter.env; set +a`
`PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.run_build all`
(run_build skips already-built; only the 36 remaining generate). Still need G2/G3 data.json
authored (g2_low_freq_vowels, g2_rcontrolled_and_more, g2_silent_letters, g3_*).

## Phase 3 — autonomous build → STOP before publish  ⏳ IN PROGRESS — 76/112 built
Built: K 33/33 ✅ · G1 43/47 (silent_letters 1/5, needs image key) · G2 0/21 (need data) · G3 0/11 (need data)
Catalogue = **112** (open-syllable 5 dropped, see DEFERRED.md).
Loop per subject: author `data.json` → `python -m language.dryrun <sid>` (decode+target+img)
→ `python -m language.run_build <sid>` → spot-check 1 page. Env: source openrouter key.
- [x] k_letter_sounds (24) ✅ 24/24
- [x] k_digraphs (9) ✅ 9/9   → **Kindergarten COMPLETE (33)**
- [x] g1_doubles_blends (9) ✅ 9/9
- [x] g1_long_vowels_vce (5, VCe only) ✅ 5/5   (open-syllable dropped)
- [ ] g1_vowel_teams (15)   — _le, y=/i/, y=/e/, soft c, soft g, ee,ea,ey,ai,ay,oa,oe,ow,ie,igh
- [ ] g1_rcontrolled (7)    — tch,dge,ar,or,er,ir,ur
- [ ] g1_diphthongs (6)     — ou,ow,oo(book),oo(moon),oi,oy
- [ ] g1_silent_letters (5) — kn,wr,mb,ph,gh
- [ ] g2_silent_letters (2) — gn,gh
- [ ] g2_low_freq_vowels (7)— au,aw,al,augh,ew,ui,ue
- [ ] g2_rcontrolled_and_more (12) — air,are,ear,ei,ey,eigh,aigh,ea,ch=/k/,or,ar,schwa
- [ ] g3_suffixes (4)       — -s/-es,-ing,-ed,-er/-est  (-ing sample in _samples/g3_ing)
- [ ] g3_prefixes (3)       — un-/re-, pre-/dis-/mis- ...
- [ ] g3_syllables_morphology (4) — closed, open, compound, contraction
**END at full build. Do NOT publish — user spot-checks random samples first.**
GOTCHAS: pic word MUST appear in its sentence (img-align gate); avoid graphemes past
the target's order (dryrun catches); VCe/pseudo targets use data tab_main+bold+directions.

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
