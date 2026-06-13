# Coding-Worksheet Pipeline — Build Progress

Working clone: `~/Desktop/TCE/worksheet_generator` (fresh, off origin/main `39266ce`).
Branch: `coding-worksheet-pilot`. Venv: `./venv` (py3.14, WeasyPrint 69.0 — needs
`DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib` to import). Live `token.json` copied in.

Canonical docs: `coding/PLAN.md`, `coding/HANDOFF.md`, `coding/rubrics/rubric_coding_{K,G1,G2,G3}.md`.
Pilot = **Grade 3 · Block Coding** (then Intro Python Turtle, then Debugging).

## Phase plan
- [x] **P1 — PDF template de-risk (GATING). ✅ DONE 2026-06-13.** Mascot `Bit`
      (`assets/mascots/bit_wave.svg`, original kawaii robot) + `pipeline/worksheet_pdf.py`
      (data-driven WeasyPrint renderer: mascot-circle header band, eyebrow/title/subtitle,
      "I can…" goal banner, name/date bar, part types prose/blocks/code/exercise/image,
      branded footer w/ page numbers). Throwaway sample renders clean on 2 pages
      (`python -m pipeline.worksheet_pdf` → `/tmp/coding_sample.pdf`); Scratch blocks
      stack with nesting indentation; exercise boxes don't split across page breaks.
      Visually inspected — matches source house style. **Gate cleared.**
- [ ] **P2 — Schema extensions.** Extend `WorksheetPart` w/ `code_block` + `exercise`
      part types (language, code, is_solution, expected_output); add `CourseBlueprint`
      + `SolutionSheet` to `pipeline/schemas.py`.
- [ ] **P3 — Mascot cast.** 3–5 named original kawaii SVGs + `assets/mascots/INDEX.json`
      (name, tags, caption, expression variants); render test PNGs.
- [ ] **P4 — Stages + curriculum.** Coding stage set in `stages.py` (course_blueprint →
      per-topic worksheet_NN/teacher_guide_NN/solution_NN/rubric_grade_NN); cache Ontario
      **C3 Grade 3** expectations; `rubric.py` selects per-grade coding rubric.
- [ ] **P5 — New modules.** `source_map.py` (sheet queue), `drive_publish.py` (push only
      the 2 PDFs; reuse slides.py Drive auth), code-runs sandbox gate.
- [ ] **P6 — Generate G3·Block Coding sheet 1 end-to-end** (course_blueprint → worksheet_01
      → teacher_guide_01 → solution_01+run-gate → rubric_coding_G3 ≥15/20+C2 → PDFs → visual inspect).
- [ ] **P7 — Sheets 2–N**, then publish to `Product/Resources/Generated Coding Worksheets/Grade 3/Block Coding/<topic>/`.

## Key facts
- Drive dest: `Product/Resources` = `1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E`.
- Reuse unchanged: `manifest.py`, `clipart.py` LRU, `image_alignment.py`.
- IP: source = ultimatecoders.ca + MIT Scratch (copyrighted). Original prose/code/mascots ONLY.
- Run python as: `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python ...` (for WeasyPrint).

## Log
- 2026-06-13: env set up (fresh clone, venv, WeasyPrint), branch created. Starting P1.
