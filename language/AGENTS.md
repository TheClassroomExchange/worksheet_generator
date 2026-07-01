# Language (Phonics) Worksheet Pipeline — Agent Guide

Builds **K-3 Ontario structured-phonics worksheets** by reusing the coding pipeline.
Distinct from the Math units (tce-unit-builder) and the Coding worksheets (coding/AGENTS.md).
This is the **language/phonics** catalogue.

## What it makes
Per phonics target: ONE combined PDF = **student worksheet + plain-language teacher guide**,
graded **20/20**, K/G1 in **roomy** layout, wrapped in the per-grade colour border, organized
**Language Worksheets → Grade → Unit → one PDF**. Design follows the Drive references
(TCDSB "Foundations of Language" + "I Can Read Sentences").

## Worksheet types by stage
- early-K single letters → **formation** + **picture_row** (beginning sound) + **sound_boxes** (CVC build)
- late-K / CVC → **sound_boxes** (word mapping) + simple **reading_rows**
- G1-G2 digraphs/blends/vowels → **reading_rows** ("I Can Read Sentences", 5 sentences + pictures) + **read_tracker** + word-work
- G3 morphology → word-building (**sound_boxes**/exercise) + **reading_rows**

## Single source of truth
- `language/phonics_scope.json` — ordered grapheme-unlock list (orders 1-117) + cumulative heart words.
- `curriculum/language.json` — verbatim Ontario K (A2.x) + G1-3 (B2.x) expectations.
- `coding/rubrics/rubric_language_{K,G1,G2,G3}.md` — the 20/20 rubric per grade.
- `language/subjects.json` + `language/<subject>/topics.json` — the build queue.
- `language/DESIGN_STANDARD.md` — the LOCKED design (big template · kawaii faces-on-animals · decorative border).

## All language code is under `language/` (reuses ../pipeline shared infra)
`decodability.py` · `language_rubric.py` · `phonics_images.py` · `language_build.py` ·
`gen_content.py` · `run_build.py` · `dryrun.py` · `publish_drive.py`. Reused from `../pipeline/`:
`worksheet_pdf` (render + phonics part-types), `coding_build` (render/fit/combine), `layout_rubric`,
`add_grade_border`, `drive_publish`, `slides` (Drive auth).

## Build loop — DATA-DRIVEN (the real workflow)
Env: `cd <repo>; set -a; . ~/.claude/.openrouter.env; set +a; export PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`;
`PY=~/Desktop/TCE/worksheet_generator/venv/bin/python`.
1. **Author** `language/<subject>/data.json` — compact per-target entries (keyed by topic dir/nn/target).
   Sentences: `{sub, sound, order?, sentences:[{text, pic, bold?}]}` (5 rows; every `pic` word must appear
   in its sentence; `bold`=target word). VCe/pseudo: add `tab_main`, `label`, `directions`, `order`.
   letter_sound: `{keyword_pic, sort_yes:[], sort_no:[], cvc:[]}`. word_building: `{title, intro,
   build:[[base,word]] | build_lines:[...], extra_words:[], note, sentences:[...]}`.
   `gen_content.py` turns each entry → full content.json (per DESIGN_STANDARD + verbatim curriculum).
2. **Dry-run (NO key):** `$PY -m language.dryrun <subject>` — decodability + target-present + image-in-text.
   Fix the DATA until ALL OK before spending image $.
3. **Build (gated, resumable):** `$PY -m language.run_build <subject|all>` — per unit: gen_content →
   `language_build.build_unit` (decodability run-gate → resolve kawaii images → fit_render roomy →
   grade border) → `language_rubric.record_grade` 20/20 + drift → checkpoint `topics.json` (skips built;
   background caps ~14 → re-run). Spot-check 1 page/subject (Read the PNG).
4. **Publish Drive:** `$PY -m language.publish_drive [dry]` (idempotent; Grade/Subject/Unit; 1 PDF/folder).
5. **Marketplace:** SEPARATE, explicit-go only, under the blast-radius protocol (not built yet — P3 in PIPELINE_PLAN).

## Images
`phonics_images.resolve(word, backend)`:
- `ai` (DEFAULT for the catalogue) — kawaii line-art via OpenRouter (`OPENROUTER_API_KEY`,
  `google/gemini-2.5-flash-image`); animals/people get a face, objects don't; auto-trimmed; cached `assets/ai_line_art/`.
- `openmoji` — OpenMoji *black* B&W SVGs (CC BY-SA), free fallback, cached `assets/openmoji_black/`.
Every image word MUST appear in the decodable text (drift gate).

## Gotchas
- WeasyPrint needs `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`.
- macOS Python lacks root certs → image fetch uses curl (handled in `phonics_images`).
- `drive_publish` only publishes topics with `status:"built"` — flip before publishing.
- Directions text in a `prose` part is HTML-escaped — do NOT put raw `<b>`; row-level bolding is automatic via `reading_rows.bold`.
- Mascot is optional in the header (language sheets may use an OpenMoji book/owl).
- Publish is a SEPARATE phase — never publish without explicit user approval.
