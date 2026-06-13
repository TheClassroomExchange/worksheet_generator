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

## Reorder (user direction, 2026-06-13)
User wants **content first → validate vs rubric → approve → THEN mascot cast +
scale-up + publish**. So Sheet-1 content is authored directly as renderer specs
(no full stage/manifest machinery yet — that's P2/P4, built after content sign-off).

## APPROVED PLAN 2026-06-13 → `coding/PILOT_BUILD_PLAN.md` (supersedes the P1–P7 sketch above)
Quality-first, checkpointed, batch-verified build. Key changes from the original sketch:
- **Grade BEFORE render** — `content_grade` gate sits before the PDF is built.
- **Higher bar, all grades** — every product graded by `pipeline/coding_rubric.py`
  (`select_rubric(grade)`); publish gate = **≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4**.
- **Recalibrate all 4 rubrics** so grade-3 simplicity can still hit C3=L4 (no forced Python bridge).
- **Reuse `manifest.py`** as the per-sheet checkpoint backbone (6 stages: solution → content
  → content_grade → render → visual_grade → publish).
- **Supervised autonomy** — human `batch_verification` gate per subject-batch (~7 sheets);
  G3·Block Coding = calibration batch.
- Process doc: `coding/AUTONOMOUS_BUILD.md`. Execution phases: 0 (land plan/push) → A
  (rubrics + coding_rubric.py + lift Sheet 1 + docs) → B (stages+schemas+adapter) → C (Sheet 2)
  → D (sheets 3–7, batch gate) → E (publish + next subject).

## Log
- 2026-06-13: env set up (fresh clone, venv, WeasyPrint), branch created. P1 cleared.
- 2026-06-13: **Sheet 1 content built + graded** — `coding/pilot_g3_block_coding/sheet_01_loops/`:
  `solution.py` (code-runs gate, all asserts PASS), `content.py` (worksheet + teacher-guide
  specs), `square_path.svg` (diagram), rendered `Loops — Worksheet.pdf` (2pp) +
  `Loops — Teacher Guide.pdf` (2pp) — all visually inspected clean. Self-graded vs
  rubric_coding_G3 = **20/20 PASS** (C2 hard gate cleared), `rubric_grade.md`.
  AWAITING USER REVIEW of the 2 PDFs before scaling up.
- 2026-06-13: **Sheet 1 rev. 2 per user feedback** ("is this really G3? simpler language,
  more concise teacher guide"). Refocused exercises on the REPEAT COUNT (count/change/write)
  not angle geometry; removed the Python bridge (text code → the separate Intro-Turtle
  subject); simplified all language; teacher guide now 1 page. Added `break-inside:avoid`
  to `worksheet_pdf.py` so exercise/figure/code boxes never split across page breaks.
  Honest re-grade vs rubric_coding_G3 = **17/20 PASS** (C1/C2 L4, C3/C4/C5 L3 — traded
  L4 extras for grade-3 simplicity; C2 hard gate cleared). run-gate still PASS.
- 2026-06-13: **Plan approved + Step 0** — wrote `coding/PILOT_BUILD_PLAN.md`, updated
  HANDOFF + this tracker, saved to memory, pushed branch. Under the NEW 19/20 bar Sheet 1's
  17/20 no longer publishes → Phase A will lift it to ≥19 (C3/C4/C5 → L4). Next = Phase A.
