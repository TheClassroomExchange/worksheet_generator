# Language Worksheet Pipeline — Updated Plan / Roadmap

Status: v1 catalogue shipped (112 sheets, Drive-published). This is the plan for
hardening the pipeline and extending the catalogue. Grouped by priority.

## Now self-contained
All language-specific code lives under `language/` (this folder). It **reuses** shared
infra from `pipeline/` (worksheet_pdf render + phonics part-types, coding_build render/
fit/combine, layout_rubric, add_grade_border, drive_publish, slides auth). See
`language/README.md` for the map.

## P1 — correctness & robustness
1. **Retry/backoff on image gen.** Transient "no image"/5xx currently fails a unit
   (e.g. `chalk` returned no image once). Add N retries + exponential backoff in
   `phonics_images._ai`; treat a persistent miss as a unit failure, not a silent skip.
2. **Budget guard.** Read remaining OpenRouter key budget; warn/stop before hitting the
   403 cap mid-run (we lost a run to it). Log $/image and cumulative spend per build.
3. **Fold dryrun into run_build.** Auto dry-run (decodability + image-alignment + target)
   at the start of every `run_build` and refuse to spend image $ on a subject with data
   errors. One command, fail fast.
4. **Visual gate at scale.** We spot-checked 1 page/subject. Add an automated
   near-empty / overflow raster check across ALL pages (extend `layout_rubric`), plus an
   optional montage export per subject for fast human scan.
5. **Image QA gate.** Kawaii images occasionally drift (fruit drawn as an apple). Add a
   lightweight check: is the generated image plausibly the word? (e.g. a small
   vision-model check, or a curated approved-image cache with human thumbs-up per word).

## P2 — content coverage & pedagogy
6. **Reinstate open-syllable / Grade-3 syllable unit** (DEFERRED.md): teach open vs closed
   syllables as multisyllabic decoding (ro-bot, ti-ger) with a build-table, not single-
   grapheme sentence sheets.
7. **Heart-word (tricky-word) worksheets** — the program has irregular/"heart" word cards;
   add a heart-word sheet type (say-it, spell-it, find-the-tricky-part).
8. **Word-mapping / phoneme-box sheets for K-CVC** (say-it → map-it → write-it) as a
   distinct type beyond the letter-sound sheet (the `sound_boxes` part already exists).
9. **Differentiation variants** — auto-generate an "easier" (fewer rows) and "stretch"
   (write-your-own) variant per target from the same data.
10. **Decodable passage sheets** — short connected text (not just 5 sentences) for fluency
    at G1–G3, gated by the same decodability engine.

## P3 — scale, reuse, ops
11. **Promote to a skill** — mirror the coding-worksheet-builder skill: a
    `language-worksheet-builder` skill pointing at `language/AGENTS.md`, so future sessions
    resume/extend deterministically.
12. **Parameterize the image style** — style presets (kawaii / realistic / B&W-classic) via
    a single flag, so a buyer segment can get a different look from the same data.
13. **Bilingual / French** — the generator is language-agnostic in structure; a French
    (FI) phonics scope + curriculum could reuse the same engine.
14. **Marketplace publish module** (deferred) — `language/publish_marketplace.py` mirroring
    `catalogue_upload/coding` (direct-insert, watermark previews, Ontario taxonomy, price/
    description/tags), with the blast-radius protocol (snapshot → item_ids → REVERT file →
    post-verify) and a `--dry-run`.

## P4 — nice-to-have
15. Per-grade bundle PDFs (all of Kindergarten in one file) as a bundle SKU.
16. Answer-key overlay variant (teacher copy with answers filled).
17. Auto-generate marketing previews (carousel PNGs) per grade.

## Immediate next steps (this hand-off)
- Consolidate language code into `language/` (done) + push branch. **No auto-merge to
  main** — user reviews / runs their extra validation pipeline first.
- Marketplace: await user go, then build `publish_marketplace.py` (P3 #14) under the
  blast-radius gate.
