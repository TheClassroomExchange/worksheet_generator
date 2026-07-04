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

## ✅ PHASE 3 COMPLETE (2026-07-01): 112/112 BUILT, all 20/20 — autonomous build DONE
K 33 · G1 47 · G2 21 · G3 11. Every sheet: decodability + verbatim-curriculum + image-align
+ page-fill + border gates PASS; kawaii design (faces on animals only) + decorative border.
One combined PDF (worksheet + teacher guide) per unit; 112 PDFs on disk; 1 pdf/dir hygiene clean.
**STOPPED before publish** — awaiting user random-sample review, then Phase 4 (Drive + marketplace).
(Earlier blocker resolved: user raised the OpenRouter key limit.)

## (history) BLOCKED 2026-06-30: OpenRouter key limit — resolved
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

## Phase 4a — Drive publish ✅ DONE (2026-07-01)
112/112 live in Product/Resources/Generated Language Worksheets/<Grade>/<Subject>/<N. Title>/ (1 PDF each, verified live: K33/G1-47/G2-21/G3-11). Root folder 1SsgiXNxds6ZDtEcIUx4Rjjl4kAxJbg9J.
**Marketplace: NOT published** — held for user validation pipeline + explicit go + blast-radius protocol.

## Phase 4b — post-publish QA remediation ✅ DONE (2026-07-01)
User spot-checked live PDFs, found a page-break rendering bug + 2 unsafe/unclear words. Full scan → 3-sample gate → 5/5 adversarial validation → full-batch remediation → republish:
- **Root cause (systemic, 88/112 files at risk):** `pipeline/worksheet_pdf.py`'s `.rr-table` (the reading_rows sentence+picture table) had no `break-inside:avoid`, so WeasyPrint could split a row across a page boundary. Fixed with `.rr-table tr { break-inside: avoid; page-break-inside: avoid; }` (worksheet_pdf.py:642) — CSS-only, zero content touched.
- **Word swap:** `k_letter_sounds/data.json` letter-F CVC list `"fat"` → `"for"` (K heart word, keeps the target-letter theme, decodes clean at lesson order 7).
- **Sentence swap:** `g1_silent_letters/01_kn-knee` "I see a knife." → "I know my dog." (kn + long-o "ow" both already unlocked at order 81; dog.png reused from cache, no new image gen).
- **Image sweep:** all 290 images actually referenced by the catalogue (openmoji_black fallback = 0 references, unused) reviewed via 7 contact sheets — zero offensive content, nothing changed.
- **Full rebuild:** all 112 units re-run through `language_build.build_unit` + `language_rubric.record_grade` — 112/112 ok, 0 failures, all still 20/20.
- **Republish:** `language.publish_drive` — all 112 PDFs updated in place (idempotent), hygiene OK on every topic, 0 stray files. Post-publish Drive audit: 112 topic folders / 112 PDFs / 0 non-pdf / 0 duplicates, all with today's modifiedTime.
- Snapshots of every before/after sample kept in session scratchpad for the record; nothing auto-merged to marketplace — Drive-only, per the standing hold above.

## 2026-07-02 — Give-away underline fix (Drive-only, published + verified)

- 72/112 units fixed to underline the target on the FIRST sentence only (worked example); rows 2..N
  plain so the child finds the pattern. 12 reading-aid units left untouched. See LEARNINGS.md.
- Code: `pipeline/worksheet_pdf.py` (reveal:first support) + `language/gen_content.py` (durability).
  Orchestrator + gates: `language/reveal_fix.py`. Run log: `language/REVEAL_FIX_LOG.md` (72/72 pass).
  Original PDFs + content.json snapshotted in `language/_reveal_fix_backup/` (revertible).
- Published Drive-only (marketplace still HELD). Final live audit: **72/72 topic PDFs updated today,
  exactly 1 PDF per folder, 0 stray, 0 stale.**

## 2026-07-02 — Repeated-example fix (Drive-only, published + verified)

- 50 sentence-type reading worksheets fixed so each shows DISTINCT target words + images (no more
  sauce×3 / ghost×5). First-occurrence sentences kept verbatim; only duplicate/broken rows swapped.
- Exceptions: `oy-toy` 4/5 (oy inventory-limited); 2 word-building units excluded. See LEARNINGS.md.
- Tooling: `language/dedup_fix.py`; log `language/DEDUP_FIX_LOG.md`; backups `_dedup_fix_backup/`.
- Gates: distinctness + decodability + image-word-in-sentence + preservation (originals verbatim) +
  page-count + border + mandatory image QA. Fresh adversarial validator 5/5.
- Published Drive-only. Live audit: **50/50 fixed units fresh, 1 PDF/folder, 0 stray.** Underline
  (reveal:first) fix confirmed still intact on every sheet.

## 2026-07-02 — Round 3: distinct example word per sentence (Drive-only)

- 43 reading sheets reworded so each sentence demonstrates a DISTINCT grapheme word (z-zebra zip×3 →
  zebra/zip/zigzag/zap/buzz, etc.). Pictures unchanged → zero new images.
- Documented single-repeat exceptions (inventory-limited): oy,zz,oll,gh,augh,ey,wh; aigh unavoidable;
  er-faster (word-building) excluded. Tooling: dedup_fix.py word_sweep/word_report; log WORDFIX_LOG.md.
- Validator 5/5. reveal:first + distinct-pictures (rounds 1-2) confirmed intact.

## 2026-07-03 — Round 7: Teacher-Guide fix + kids-safe (Drive-only, published + verified)
Page-2 Teacher Guide had 4 bugs; catalogue sweep → 12 impacted + 1 kids-safe = 13 fixed.
- Durable fix in `gen_content.py`: `derive_teacher_guide()` projects the guide FROM the worksheet
  (D1 blank key on split-VCe/schwa · D2 fabricated word-building sentences · D3 hardcoded "underline"
  verb) + `cap_reading_sentences()` (D4 word-building overflow 3pp→2pp). Inline `_answer_words`/
  `_lead_step3` fix future builds too.
- Kids-safe: dropped "I see a skull." (G1 ull→4 sentences); kept witch; hurt/ghost/whip safe-in-context.
- Tooling: `language/tg_fix.py` (sweep+gated per-unit) · `language/tg_publish.py` (live-snapshot→diff→
  idempotent replace). Logs: `TG_QA_LOG.md`, `TG_FIX_LOG.md`, `TG_PUBLISH_LOG.md`. Backups: `_tg_fix_backup/`.
- Verified: 13/13 gates pass · end-artifact adversarial 5/5 · re-sweep 0/112 impacted · live Drive audit
  13/13 fresh (2026-07-03), 1 PDF/folder, 0 stray. Drive-only, NOT committed, marketplace HELD.

## 2026-07-03 — Round 8: faceless images + augh distinct example (Drive-only, published + verified)
Live-inspection minor-fix sweep of 112 → 5 impacted (4.5%).
- Faces: `_ANIMATE` (phonics_images.py) drives face vs faceless prompt; bird+ghost were faceless (missing
  from set). Added bird/ghost/granddaughter → deleted cached pngs → regenerated with face prompt (verified).
  bird.png shared → fixes ir-bird/ew-new/ly-slowly; ghost.png → gh-ghost.
- augh: /aw/ sheet had caught×2 (only 4 kid /aw/ words). s5 "I caught the pup."→"I hug my granddaughter."
  (5 distinct; granddaughter vetted; laughter rejected=/af/). content+data synced, TG answer key re-derived.
- Tool `language/face_fix.py` (per-type gates + snapshot/revert `_facefix_backup/`). Publish = live-snapshot→
  replace-in-place. Verified 5/5 gates + visual; live audit 5/5 fresh, 1 PDF/folder, 0 stray. Log FACE_FIX_LOG.md.
- Left as-is: oy/zz/oll/gh single repeats + crow/gull/wren (dot-eyes) + moth (decorative) — inventory/design.
