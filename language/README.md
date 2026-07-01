# `language/` — K–3 Ontario Phonics Worksheet Pipeline

Self-contained language-worksheet generator. Reuses shared render/publish infra from
`../pipeline/`. Built the full 112-sheet K–3 catalogue (Drive-published 2026-07-01).

## Docs (read these)
- `DESIGN_STANDARD.md` — LOCKED design (big template · kawaii images, faces on animals only · decorative border)
- `AGENTS.md` — how to operate the pipeline (per-unit build loop)
- `LEARNINGS.md` — everything learned building v1
- `PIPELINE_PLAN.md` — roadmap / proposed updates
- `DEFERRED.md` — dropped/backlog items (open-syllables, x-wording)
- `BUILD_PROGRESS.md` — status tracker (112/112 built + Drive-published)

## Code (all language-specific logic)
- `phonics_scope.json` — 117-grapheme ordered scope + cumulative heart words (source of truth)
- `decodability.py` — decodability run-gate (grapheme segmenter + vowel-team guard)
- `language_rubric.py` — 20/20 rubric + drift check (decodability + verbatim curriculum + image-align)
- `phonics_images.py` — word→image resolver: kawaii AI (OpenRouter) + OpenMoji fallback
- `gen_content.py` — data-entry → content.json (3 templates: sentences · word_building · letter_sound)
- `language_build.py` — `build_unit`: decodability → images → render → border (reuses pipeline.coding_build)
- `run_build.py` — resumable per-subject runner (gen → build → grade → checkpoint)
- `dryrun.py` — pre-build validation (no image key needed) — ALWAYS run first
- `publish_drive.py` — Drive publish (reuses pipeline.drive_publish; Grade/Subject/Unit)
- `subjects.json` + `<subject>/topics.json` — the build queue (14 subjects / 112 units)
- `<subject>/data.json` — authored IP (decodable sentences/words per target)
- `<subject>/<NN_slug>/` — per-unit: content.json, state json, combined PDF

## Reused from ../pipeline/ (shared, not language-specific)
`worksheet_pdf.py` (render + phonics part-types), `coding_build.py` (render/fit/combine),
`layout_rubric.py`, `add_grade_border.py`, `drive_publish.py`, `slides.py` (Drive auth).

## Quickstart
```bash
cd <repo> && set -a; . ~/.claude/.openrouter.env; set +a
export PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib
PY=~/Desktop/TCE/worksheet_generator/venv/bin/python
$PY -m language.dryrun <subject_id>      # validate data (no key)
$PY -m language.run_build <subject_id|all> # build (resumable)
$PY -m language.publish_drive [dry]        # publish to Drive
```

## Status
112/112 built (20/20) + Drive-published + verified. Marketplace: held for validation.
