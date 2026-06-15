# HANDOFF — Coding-Worksheet Pipeline (K–G3)

**Date:** 2026-06-11 (planned) · **Build started:** 2026-06-13 · **Status:** BUILD IN
PROGRESS — pilot Sheet 1 content built, awaiting grade-fit sign-off · **Owner:** Anthonny

> **Authoritative plan: `coding/MASTER_BUILD_PLAN.md`** (full ~100-worksheet K–G3 catalogue,
> NO human batch gate). `coding/PILOT_BUILD_PLAN.md` = proven-process record (G3 Block Coding).
> **Process: `coding/AUTONOMOUS_BUILD.md`. Machine queue: `coding/subjects.json`.
> Live state: `coding/BUILD_PROGRESS.md`.** Read those first; this handoff is stable context.
>
> **Status 2026-06-14 — ✅ CATALOGUE COMPLETE (12/12 subjects):** G3 ×3 + K ×3 + G1 ×3 + G2 ×3 = **93 worksheets,
> all 20/20, 186 PDFs in Drive.** The full autonomous build is DONE and the /loop is stopped. Full breakdown +
> per-grade Drive links = the **FINAL CATALOGUE SUMMARY** at the bottom of `coding/BUILD_PROGRESS.md`. Root Drive
> folder: https://drive.google.com/drive/folders/1HkbqjbPjSiQbZeW7OCJl7eZuAF_mvw7j
> **Per-grade lanes (proven):** K = K-frame symbol-only (no C3, no text/loops), solution.py MODELS+asserts. G1 =
> SEQUENTIAL number-path (0–5) clamped interpreter + step-cards + sequence-repair debug (NO loops/concurrency).
> G2 = + CONCURRENT (loops out): TWO sprites (Bit green `bit_wave` + Pixel purple `pixel_wave`) on a shared 0–5
> path, COMBINED-outcome questions; events/broadcast/receive triggers (subj 11); read+debug two parallel scripts
> (subj 12). G3 = + REPEATING (loops) + first typed code (Turtle path MODELLED). solution.py event-aware where
> needed: scripts=(trigger_event, home, moves), run only if fired. Renderer affordances: `blocks` blank-block
> write-slot, before/after stacks, `symbols` ★ path goal-marker, events=orange hats.
> **If extending later:** add a new subject = new row in `coding/subjects.json` (status!=done) + its own
> `topics.json` + per-sheet loop; the runner picks the lowest-order unfinished subject. Nothing else is pending.
> **G1 patterns (proven):** Block-Coding = number-path (0–5) program w/ Scratch text-label blocks + clamped
> interpreter; Unplugged = lettered step-cards + precedence model; Intro Debugging = debug the number-path
> programs (one bug type/sheet, run→find→fix→recheck).
> K primitives in `worksheet_pdf.py`: additive `symbols` part + `blocks` `size`/`blank`.
> Drive: G1 Intro Debugging https://drive.google.com/drive/folders/1Oa_aTV349ar5WyVyveW4AfA0b0l22Rsq ·
> G1 Unplugged Seq https://drive.google.com/drive/folders/11pddj1_n0w8CyxTmhDYD3LUMXeUzjEzx ·
> G1 Block (Seq) https://drive.google.com/drive/folders/1uKyzrks5wERumo_cwWTOTqOwWJvCrI7U ·
> K Intro Block https://drive.google.com/drive/folders/1cLIMiX8bsL__cwR-qiuMs_aBST3CsvmB ·
> K Sequencing https://drive.google.com/drive/folders/158bMnSexks_0TPZ1PCwH38jRWFb8c8Ug ·
> K Unplugged CT https://drive.google.com/drive/folders/1_yM25wZ-ix5EPvO-iUMy1eGAvJAA9Pv5 ·
> G2 Block Coding (Concurrent) https://drive.google.com/drive/folders/10Uejefrby6oatfuVU6ZNIOi-YgptSq_S ·
> G2 Events & Parallel Scripts https://drive.google.com/drive/folders/1T1vlAygogQnPONoERy2ab560lV9cHJXR ·
> G2 Debugging & Reading Code https://drive.google.com/drive/folders/1QmdeKPebuLLJmqDuhtyVYRlAv-wfYHFU
>
> **Quality model:** every product, every grade, graded by `pipeline/coding_rubric.py`
> (`select_rubric(grade)`) BEFORE render. Gate = **≥19/20 AND C2≥L3 (hard) AND C3=L4 AND C5=L4**.
> Per-sheet chain: code-runs → content schema → content_grade → render → visual_grade → publish.
> **Checkpoint cadence:** update MASTER_BUILD_PLAN + HANDOFF + BUILD_PROGRESS + memory at every
> completed subject (and BUILD_PROGRESS per sheet); commit + push. Per-grade arcs are grade-specific
> (loop-centric is G3-only; G1 sequential, G2 concurrent, K unplugged — see subjects.json ceilings).

One-line: adapt the `worksheet_generator` pipeline (today: K-3 Ontario **Math** →
Google Slides) to generate **original, Ontario-aligned K–G3 coding worksheets**
as **branded PDFs**, organized by grade → subject → topic in Google Drive, using
**original kawaii mascot SVGs** instead of the source's `ultimatecoders.ca`
character.

Full plan: **`~/Desktop/TCE/CODING_WORKSHEET_PIPELINE_PLAN.md`** (read it first).

## Decisions (locked)
1. **Same structure, original content** — mirror source layout/sequence/objectives; write fresh prose/code/exercises (IP-safe; source is ultimatecoders.ca + MIT Scratch, copyrighted).
2. **Output = PDF worksheets** (WeasyPrint), not Slides.
3. **Grade-banded K / G1 / G2 / G3 — K–3 ONLY** (no Grade 4+ band) → subject → topic. Advanced source content (Python Adv, web dev, Arduino) is reference only; concepts adapted **down** to Ontario C3 coding (grades 1–3) + Kindergarten computational-thinking frame.
   - **Subjects per grade (FINAL)** — Ontario C3 event-type progression:
     - **K:** Unplugged Computational Thinking · Sequencing & Algorithms · Intro Block Coding (ScratchJr-style)
     - **G1:** Block Coding (Sequential Events) · Unplugged Sequencing & Algorithms · Intro Debugging
     - **G2:** Block Coding (Concurrent Events) · Events & Parallel Scripts · Debugging & Reading Code
     - **G3:** Block Coding (incl. loops) · Intro Python Turtle · Debugging
4. **Publish rule:** only **2 PDFs per topic folder** — the teaching-content worksheet + a teacher-instructions guide. Homework/solutions/runnable code stay local (used for gates), never uploaded.
5. **Pilot:** Grade 3 · **Block Coding** (~6–9 topics) first; then the other two G3 subjects (Intro Python Turtle, Debugging); then K/G1/G2.
6. **Grade rubrics (BUILT):** `~/Desktop/TCE/coding_rubrics/rubric_coding_{K,G1,G2,G3}.md`. 5 criteria × L1–L4 = /20; **pass ≥15 AND Criterion 2 (concept correctness) ≥ L3 hard gate**. Become `assets/rubric_coding_<grade>.md`; `rubric.py` selects by grade. Per-grade calibration = concept scope + cognitive-load budgets.

## Source & destination (Google Drive)
- **Source corpus:** `Coding Resources-Kassandra/` → 2 zips (`JUNIOR CREATOR`, `ULTIMATE INNOVATOR`), **484 PDFs + 121 docx**: Scratch / Python / Arduino / Web (HTML/CSS/JS). Downloaded locally to `/tmp/tce_zips/` (ephemeral — re-download if gone; IDs below).
  - Junior Creator zip: `1giiSMqfknx_iHNjO-tJ8T1Lp9tWadIgL`
  - Ultimate Innovator zip: `1gaSS_a5QoWEQPqpaM8KMKvOxFgdS6EGA`
- **Destination:** `Product/Resources` folder = **`1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E`** (writable). Generated tree:
  `Product/Resources/Generated Coding Worksheets/<Grade>/<Subject>/<Topic>/{Worksheet.pdf, Teacher Guide.pdf}`

## Source sheet anatomy (what to reproduce in look)
Portrait page · header band = **mascot-in-circle (left) + centered title** ·
body = prose + monospace **code blocks** + screenshots/diagrams + exercises ·
footer = `N. Topic | site [page#]`. Solutions reuse the header with answer code.
(Reviewed: Python Turtle CW + solution, Scratch intro, HTML index.)

## Pipeline reuse map (what changes)
- **Reuse unchanged:** `pipeline/manifest.py` (checkpoint/resume state machine — `init_unit`/`mark`/`complete_stage`/`next_pending`/`status_table`), `clipart.py` LRU (→ mascot rotation), `image_alignment.py` gate. `schemas.py` already has `Worksheet`/`WorksheetPage`/`WorksheetPart`/`WorksheetHeader`/`ImagePlaceholder`/`PrintSpec` to build on.
- **Repoint:** `stages.py` (math 17-stage → coding: `course_blueprint` then per-topic `worksheet_NN`/`teacher_guide_NN`/`solution_NN`); curriculum gate → Ontario **C3 coding** cache; `rubric.py` → **per-grade** coding rubrics (`assets/rubric_coding_<grade>.md`, select by grade).
- **Build new:** `pipeline/worksheet_pdf.py` (WeasyPrint HTML→PDF), `assets/mascots/` (original kawaii SVG cast + INDEX), `pipeline/source_map.py` (source tree → worksheet queue), `pipeline/drive_publish.py` (push only the 2 PDFs; reuse `slides.py` Drive auth).
- **New gate:** **code-runs** — every solution code block executed in sandbox (python/node/lint), must run clean; assert expected output where deterministic.

## Build progress (as of 2026-06-13)
Canonical working clone is now **`~/Desktop/TCE/worksheet_generator`** (fresh clone off
origin/main `39266ce`, branch **`coding-worksheet-pilot`**, venv `./venv` with WeasyPrint
69.0). User reordered to **content-first**: build a reviewable sheet → validate vs rubric
→ sign-off → THEN mascot cast + scale + publish.

- ✅ **P1 — PDF template (the gating risk).** `pipeline/worksheet_pdf.py` (data-driven
  WeasyPrint renderer, house-style branded template: mascot-circle header, "I can" banner,
  5 part types prose/blocks/code/exercise/image, footer w/ page numbers, break-inside:avoid)
  + mascot **Bit** (`assets/mascots/bit_wave.svg`, original kawaii robot). Visually verified.
- ✅ **Pilot Sheet 1 — G3 · Block Coding · "Loops: Code That Repeats"** in
  `coding/pilot_g3_block_coding/sheet_01_loops/`: `content.py` (worksheet + teacher-guide
  specs), `solution.py` (run-gate, all asserts PASS), `square_path.svg`, rendered both PDFs,
  `rubric_grade.md` = **17/20 PASS** (rev. 2, simplified to true grade-3: repeat-count focus,
  no angle math, no Python bridge). **Awaiting user sign-off on grade-fit.**

## Next steps (resume here)
*(Scope RESOLVED: K–3 only; G3 = Block Coding · Intro Python Turtle · Debugging. K/G1/G2 subject lists still need sign-off before generating those grades.)*
1. **On Sheet-1 sign-off:** lock the renderer + sheet shape as the template.
2. Draw the rest of the original kawaii mascot cast (3–5 chars) + `assets/mascots/INDEX.json`.
3. Define the full **Grade 3 · Block Coding** topic list (~6–9: sequencing → events → loops
   → conditionals preview → debugging mini) and generate sheets 2–N through the proven loop
   (content.py-style spec → run-gate → render → rubric ≥15/20 + C2 → visual inspect).
4. Build `pipeline/drive_publish.py` (reuse `slides.py` Drive auth) → push ONLY the worksheet
   + teacher-guide PDFs to `Product/Resources/Generated Coding Worksheets/Grade 3/Block Coding/
   <topic>/`; hygiene-check folders. Then repeat for Intro Python Turtle + Debugging.
5. *(Infra fold-in, optional)* migrate the content-first specs into formal `stages.py` +
   `schemas.py` (code_block/exercise part types, CourseBlueprint, SolutionSheet) so the
   manifest checkpoint/resume engine drives generation like the math pipeline.

## Gotchas / environment
- **WeasyPrint:** installed in `./venv` (v69.0). **Must run python with
  `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`** or the native libs (pango/cairo/gdk-pixbuf,
  all present via Homebrew) won't load and import fails. Example:
  `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python coding/pilot_g3_block_coding/sheet_01_loops/content.py`.
- **Render-to-inspect loop:** `pdftoppm -png -r 150 "<x>.pdf" /tmp/v_pages/x` then read the PNGs.
- **Google auth:** live `token.json` copied into the new clone (full Drive + Slides scope).
  `auth_only.py` **bug**: a dead refresh token makes it crash instead of re-prompting —
  move `token.json` aside before re-running, or patch it to catch `RefreshError`.
- **Working clone:** **`~/Desktop/TCE/worksheet_generator`** is now canonical for this build
  (the old `~/Desktop/tce_migration_bundle_2026-05-03/...` clone is retired — cluttered + was
  behind origin).
- **Security:** older local clones embed a **GitHub PAT in their git remote URL** → rotate/revoke.

## IP / safety
Source = two companies' copyrighted curriculum + MIT Scratch cards. **Never
clone verbatim or reuse their mascot/art.** Original content + original mascots
only — this is the whole reason for the "same structure, original content"
decision.
