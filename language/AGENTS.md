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

## Per-unit build loop (mirror coding/AGENTS.md §6a)
Run with the worktree venv: `PYTHONPATH=<worktree> DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib <venv>/bin/python`.
1. **Author** `content.json` (top-level: `title`, `file_title`, `phonics{...}`, `worksheet{...}`, `teacher_guide{...}`).
   The `phonics` block drives the gates:
   `{grade, lesson_order, target_grapheme, decodable_text:[...], image_words:[{word,src}], curriculum:[{code,text}], allowed_exceptions:[]}`.
2. **Decodability gate**: `decodability.check_unit(dir)` → `decodability_run.json` must have `passed:true`
   (every word decodable from graphemes ≤ lesson_order + cumulative heart words; target pattern present).
3. **Teacher-guide lint + grade**: `teacher_guide_rubric` (T1 plain-language = L4, T4 answer-key = L4).
4. **Rubric grade BEFORE render**: `language_rubric.record_grade(dir, grade, scores)` → must be `status:"pass"`
   (total ≥19/20, C2≥L3, C3=L4, C5=L4) AND `pre_grade_drift_check` clean (decodability + verbatim curriculum + image-word alignment).
5. **Render + combine + auto-fit (roomy for K/G1)**: `coding_build.fit_render(dir)` then `coding_build.combine_sheet(dir)`.
6. **Visual gate**: `coding_build.finalize_visual(dir, status='pass', notes=..., inspected_pages=[1,...])` (hard page-fill gate).
   READ every rendered page before passing.
7. Only a passing unit advances. Flip `topics.json` status to `built`.
8. Per batch: `add_grade_border` then (Phase 4, deferred) `drive_publish` + marketplace.

## Images
`phonics_images.resolve(word, backend)`:
- `openmoji` (default) — OpenMoji *black* B&W line SVGs (CC BY-SA), cached in `assets/openmoji_black/`. Free, deterministic.
- `ai` — per-word line-art via OpenRouter (`OPENROUTER_API_KEY`, model `google/gemini-2.5-flash-image-preview`),
  or OpenAI/Stability if their keys are set. Cached in `assets/ai_line_art/`.
Every image word MUST appear in the decodable text (drift gate enforces this).

## Gotchas
- WeasyPrint needs `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`.
- macOS Python lacks root certs → image fetch uses curl (handled in `phonics_images`).
- `drive_publish` only publishes topics with `status:"built"` — flip before publishing.
- Directions text in a `prose` part is HTML-escaped — do NOT put raw `<b>`; row-level bolding is automatic via `reading_rows.bold`.
- Mascot is optional in the header (language sheets may use an OpenMoji book/owl).
- Publish is a SEPARATE phase — never publish without explicit user approval.
