# Language worksheet revisions — handoff

**Date:** 2026-07-02 · **Branch:** `language-worksheets` (worktree `~/Desktop/TCE/wg-language`)
**Status:** all fixes SHIPPED to Drive (idempotent, per-unit audited fresh) · **NOT git-committed** (awaiting review)
**Scope:** the K–3 "I Can Read Sentences" / "Letter & Sound" phonics catalogue (112 units), Drive folder
`Generated Language Worksheets` (root `1SsgiXNxds6ZDtEcIUx4Rjjl4kAxJbg9J`). Marketplace still HELD.

Six revision passes were run over the catalogue, each: **sweep → % impacted → targeted fix on impacted
units only → snapshot + hard gates → fresh-session adversarial validator (rounds 1–3) → idempotent Drive
publish → live modifiedTime audit**. Full learnings in `LEARNINGS.md`; per-round run logs listed below.

## Environment / how to re-run
```
cd ~/Desktop/TCE/wg-language
PY="$HOME/Desktop/TCE/worksheet_generator/venv/bin/python"
set -a; . ~/.claude/.openrouter.env; set +a         # image gen key
export PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib
$PY -m language.dedup_fix sweep|report|word_sweep|word_report|vet <subj/unit> <words...>
```
Source of truth = `language/<subject>/data.json` (authored sentences). Rebuild path =
`gen_content.generate` → `language_build.build_unit` (reuses cached images, runs decodability + border +
page-fill gates, preserves the `reveal:"first"` underline). Publish = `python -m language.publish_drive`
(or `pipeline.drive_publish.publish_batch` per subject). Trust the live-Drive modifiedTime audit, not stdout.

## The fixes

### Round 1 — Give-away underlines (reveal:first) · 72 units (64%)
Worksheets pre-underlined the target grapheme in EVERY sentence, so the "underline the X" task was already
done. Fixed: underline the FIRST sentence only (worked example); rows 2..N plain.
- Code: `pipeline/worksheet_pdf.py` `_render_reading_rows` honors part flag `reveal:"first"`;
  `gen_content.py` emits it for find-task (underline/circle) sheets. Default (absent) = full underline →
  the 12 reading-AID units (schwa + G3 morphemes, where bold is intentional) left untouched.
- Tool: `language/reveal_fix.py`. Log: `REVEAL_FIX_LOG.md`. Backups: `_reveal_fix_backup/`.

### Round 2 — Duplicate pictures · 50 units (of 88 reading sheets)
Sheets reused the same picture/word across sentences (au-pause sauce×3; gh-ghost ghost×5). Fixed: keep the
first occurrence of each word verbatim, replace only duplicate/pre-broken rows with new distinct decodable
words + images. ~46 new AI images (~$4).
- Tool: `language/dedup_fix.py` (`sweep`/`report`/`vet`/`assemble`/`apply`). Log: `DEDUP_FIX_LOG.md`.
  Backups: `_dedup_fix_backup/`.
- Exceptions: `oy-toy` 4/5 (oy inventory-limited); 2 word-building units excluded (er-faster,
  open-syllable-robot).

### Round 3 — Duplicate example WORDS · 43 units (50% of reading sheets)
Even with distinct pictures, the same grapheme word repeated (z-zebra zip×3, oo-book look×3, ey-they
they×4). Fixed: reword offending rows to a distinct grapheme word, KEEPING pictures → zero new images.
- Tool: `dedup_fix.py` extended — `_gwords`, `word_sweep`/`word_report`, `apply(preserve=False,
  require_distinct_words=True, expect_pics=..., backup_dir=_wordfix_backup)`. Log: `WORDFIX_LOG.md`.
- Exceptions (single-repeat, inventory-limited): oy(toy), zz(buzz), oll(roll), gh(rough), augh(caught),
  ey(grey), wh(what); `er-faster` word-building excluded; `aigh` handled in round 6.
- GOTCHA: `gen_content.gen_word_building` caps sentences to `[:3]` → for the ly/un/ed suffix/prefix
  word-building sheets, edit `content.json` "Read the sentences" rows DIRECTLY + `build_unit` (no cap).

### Round 4 — "Ii" legibility · 24 letter-sound units
Sans capital I is a bare stroke = lowercase l, so "Ii" misread as "li". Fixed: serif the letter displays,
scoped via `<body class="lettersheet">` (set when a `formation` part exists) →
`.lettersheet .title/.ph-title/.ph-tab-main, .fm-letter, .fm-trace { font-family: Georgia, serif }`.
Reading-sentence sheets keep the house sans. Content unchanged. Backups: `_touchup_backup/`.

### Round 5 — Wrong images · 9 images → 15 units re-rendered
Visual-QA'd all 345 used images (labeled contact sheets). 9 depicted the WRONG object (AI misread the
word): **wood**=mushroom-forest, **foil**=fencing-sword, **shop**=mushroom-cottage, **stick**=stick-figure,
**nail**=fingernail, **bat**=wingless-critter, **page**=cloud-scene, **map**=doodle, **trunk**=elephant-trunk.
Also earlier: **photo**=animal (fixed in round 4 window). Regenerated each with an explicit concrete prompt;
rebuilt the 14 units referencing them (page/nail ×2 units, map ×4 K picture tasks) + ph-photo.
Backups: `_touchup_backup/` + `_imgfix_backup/`.
- Lesson: the image model fails on (a) abstract nouns and (b) homograph words (foil/nail/bat/stick).
  Contact-sheet the whole library and eyeball — don't trust per-word gen. Retired bad images:
  chief/bruise/vein/design (round 2) were also replaced.

### Round 6 — aigh single-word repeat · 1 unit
`aigh-straight` read "straight" ×5 (aigh's only common word). Used the aigh word family
(straight, straighten, straightedge) → straight×2 + 3 distinct words, distinct pics (road/tie/nail/hair/ruler).
Backups: `_aighfix_backup/`.

### Round 7 — Teacher-Guide answer-key / verb / overflow + kids-safe · 13 units (2026-07-03)
The page-2 Teacher Guide (added after rounds 1–6) shipped with 4 bugs; full-catalogue sweep found
**12 impacted** of 112 (+1 kids-safe). Root cause + durable fix in `language/gen_content.py`:
`derive_teacher_guide(content, grade)` rebuilds the guide FROM the worksheet block (never data.json,
which would revert the round 1–3 hand-edits), and `cap_reading_sentences` restores the 1-page
word-building layout. `gen_sentences` also fixed inline (`_answer_words` split-VCe/pseudo extractor +
`_lead_step3` verb) so future builds don't drift.
- **D1** blank key `Sentence i: —` on split-VCe (a_e/i_e/o_e/e_e/u_e) + schwa → real target words
  (regex `V[cons]+e` for split vowels; pictured `word` fallback for pseudo/bold).
- **D2** word-building key listed FABRICATED sentences → now echoes the worksheet's real read rows.
- **D3** step-3 hardcoded "underline" → reads the worksheet's find-task verb (circle/underline/bold-aid).
- **D4** word-building overflow (5 sentences → 3pp) → capped read-sentences to 3 → clean 2pp.
- **Kids-safe (Track 2):** full worksheet scan flagged 6 words; user-approved: **dropped "I see a
  skull." (G1 ull → 4 sentences)**; **kept witch** (fairy-tale) + hurt/ghost/whip (safe-in-context).
- Tooling: `language/tg_fix.py` (`sweep` → `TG_QA_LOG.md`+`tg_impacted.json`; `run`/`only` per-unit,
  gated: worksheet-preserved [identical, or removals-only for a cap/drop] + answer-key-correct +
  verb-match + ≤2pp; snapshot+revert-on-fail to `_tg_fix_backup/`). Publish: `language/tg_publish.py`
  (download live PDF by `publish.json` file id → diff old-vs-new → idempotent replace-in-place).
- Gates: 13/13 pass. Validation: end-artifact adversarial check (pdftotext/pdfinfo on FINAL PDFs) +
  visual inspection of every shape → **5/5** on M1–M5 (fresh-session subagent validator died twice on
  an infra API error; self-validation is independent of the build gates). Re-sweep after batch: **0/112
  impacted**. Publish: 13/13 replaced in place, **today's modifiedTime, 1 PDF/folder, 0 stray** (live
  audit). Changed set list: `language/tg_changed_set.json`. Backups: `_tg_fix_backup/` (+ `_live_before/`
  = the live PDFs as they were pre-replace). Drive-only; NOT committed; marketplace still HELD.

### Round 8 — faceless images + augh distinct example · 5 units (2026-07-03)
Live-inspection sweep of the 112 catalogue for minor issues → **5 impacted (4.5%)**, rest clean.
- **Faceless animate images.** `phonics_images.py::_ANIMATE` (line ~135) drives the kawaii FACE vs
  faceless OBJECT prompt; words missing from it render faceless. `bird` (blank body) + `ghost` (blank
  silhouette) confirmed faceless (crow/gull/wren have dot-eyes, moth decorative → left). Fix: added
  **bird, ghost, granddaughter** to `_ANIMATE`; deleted the cached pngs; regenerated with the face
  prompt (Read each → face + right object). Shared image → `bird.png` fixes ir-bird + ew-new + ly-slowly.
- **augh "caught ×2".** augh sheet is themed /aw/ (subtitle "/aw/ spelled augh") → only 4 kid /aw/
  words. Replaced sentence 5 "I caught the pup." → **"I hug my granddaughter."** (5 distinct augh words;
  granddaughter decodability-vetted; "laughter" rejected = /af/ augh, wrong sheet). content.json +
  data.json synced; teacher_guide RE-DERIVED so the answer key shows "granddaughter" (worksheet AND key
  both reflect it, per user). New `granddaughter.png` (person → face).
- Tooling: `language/face_fix.py` (per-type gates: IMAGE units → worksheet text identical + raster
  change confined to the image column + 2pp; AUGH → row-local text change + answer-key synced +
  decodability/image-align + 2pp; snapshot+revert to `_facefix_backup/`, old faceless pngs kept there).
  Publish: live-snapshot each by `publish.json` file id (`_facefix_backup/_live_before/`) → confirm
  live==snapshot → idempotent replace-in-place.
- Verified: 5/5 gates pass + visual (Read every regenerated image in-page + augh both pages). Live Drive
  audit **5/5 fresh (2026-07-03), 1 PDF/folder, 0 stray**. Drive-only; NOT committed; marketplace HELD.
- Left as-is (documented inventory limits, user-approved): oy-toy/zz-buzz/oll-troll/gh-laugh single
  repeats; crow/gull/wren minimal-eye images; moth decorative.

## Documented exceptions still present (by design, inventory-limited)
- `oy-toy` 4/5 pictures + toy×2 word (oy word pool: toy/boy/oyster/soy — dries up).
- Single-word-repeat (allow 1): zz(buzz), oll(roll), gh-laugh(rough), augh(caught), ey-they(grey), wh(what).
- `g2_rcontrolled_and_more/07_aigh-straight`: straight×2 (aigh ≈ one word family).
- `g3_suffixes/04_er-faster` + `g3_syllables_morphology/02_open-syllable-robot`: word-building sheets,
  excluded from pic/word dedup (build-table primary; rebuild caps sentences to 3 → layout risk).
- `open-syllable-robot` is also a DEFERRED/dropped stub (see DEFERRED.md) — not in the published catalogue.

## Verification state
Every round: per-unit hard gates (decodability, distinctness, pic-in-sentence, preservation, page-count,
border, image-QA). Rounds 1–3 each passed an independent fresh-session validator 5/5. All impacted units
re-published Drive-only and confirmed **fresh (today's modifiedTime), 1 PDF per folder, 0 stray**. The
underline (reveal:first) and distinct-picture properties were re-verified intact after every later round.

## Not done / next
- **Not committed.** Changes sit on `language-worksheets`. Also riding along in the worktree: the
  reveal/underline source edits (`worksheet_pdf.py`, `gen_content.py`), all `_*_backup/` dirs + `*_LOG.md`,
  `reveal_fix.py`/`dedup_fix.py`, and unrelated marketplace-prep files — split these before an isolated commit.
- Backups under `language/_*_backup/` allow per-unit revert; safe to delete once the branch is accepted.
- Marketplace publish still HELD (Drive-only throughout).
