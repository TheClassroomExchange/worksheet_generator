# HANDOFF — Coding-Worksheet Pipeline (K–G3)

**Date:** 2026-06-11 · **Status:** Planned (not yet built) · **Owner:** Anthonny

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

## Next steps (resume here)
*(Scope RESOLVED: K–3 only; G3 = Block Coding · Intro Python Turtle · Debugging. K/G1/G2 subject lists still need sign-off before generating those grades.)*
1. Branch `worksheet_generator`; scaffold the 4 new modules; `pip install weasyprint`.
2. Draw mascot SVG cast; nail the PDF template on a throwaway sheet (**pilot gates here**).
3. Cache Grade 3 C3 expectations; define the **Grade 3 · Block Coding** topic list (~6–9: sequencing → events → loops → conditionals → debugging mini).
4. Generate sheet 1 end-to-end (worksheet → teacher guide → solution+run-gate → PDFs → visual inspect); then roll sheets 2–N.
5. Publish 2 PDFs/topic to `Grade 3/Block Coding/<topic>/`; hygiene-check folders. Then repeat for Intro Python Turtle + Debugging.

## Gotchas / environment
- **Google auth:** tokens were all expired; **re-auth'd this session** → fresh `token.json` at `~/Desktop/tce_migration_bundle_2026-05-03/worksheet_generator/token.json` (full Drive + Slides scope, refresh token present). `auth_only.py` **bug**: a dead refresh token makes it crash instead of re-prompting — delete/move `token.json` before re-running, or patch it to catch `RefreshError` and fall through to the browser flow.
- **Working repo clone used:** `~/Desktop/tce_migration_bundle_2026-05-03/worksheet_generator` (origin/main fetched = `85555b0`). The canonical fresh clone should be re-cloned for real build work; this clone has untracked files.
- **Security:** older local clones embed a **GitHub PAT in their git remote URL** → rotate/revoke (unrelated to this task).
- System `python3` has `googleapiclient` + `weasyprint`? (verify — only google libs confirmed so far). No `venv` currently in the clone.

## IP / safety
Source = two companies' copyrighted curriculum + MIT Scratch cards. **Never
clone verbatim or reuse their mascot/art.** Original content + original mascots
only — this is the whole reason for the "same structure, original content"
decision.
