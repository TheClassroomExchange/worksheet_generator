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
- 2026-06-13: **Phase A DONE.** (1) Recalibrated all 4 rubrics — G3 C3-L4 no longer forces a
  Python bridge (grade-appropriate excellence = low-floor + challenge + real-world hook);
  consistent **PUBLISH GATE ≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4** added to all four. (2) Wrote
  `pipeline/coding_rubric.py` (`select_rubric(grade)`, THRESHOLD=19, floors C2≥3/C3=4/C5=4,
  classify/required_lifts/stages_needing_regen/pre_grade_drift_check) — unit-tested: rejects 18,
  rejects C3<L4/C5<L4, enforces C2 hard gate, accepts clean 19–20. (3) **Lifted Sheet 1 → 20/20**
  (added real-world hook + Ex4 Challenge [run-gate models 3×2=6] → C3-L4; Ex2 predict-then-check
  → C4-L4; teacher-guide success indicator → C5-L4); both PDFs re-rendered + visually inspected,
  teacher guide kept to 1 page; `classify()` confirms 20/20 pass. (4) Wrote process docs:
  `coding/AUTONOMOUS_BUILD.md`, `pilot_g3_block_coding/topics.json` (locked 7-topic arc),
  `pilot_g3_block_coding/STYLE_SPEC.md`. Next = Phase B (stages + schemas + manifest migration).
- 2026-06-13: **Phase B DONE.** Reused `manifest.py` as the checkpoint backbone:
  added `stages.coding_stages_for_sheet()` (6 stages: solution → content → content_grade →
  render → visual_grade → publish); gave `manifest.init_unit()` an optional `stage_objs`
  param (backward-compatible). New `pipeline/coding_build.py` — `run_solution()` (code-runs
  gate → `solution_run.json`) + `render_sheet()` (renders both PDFs from `content.json`, the
  renderer spec; clean filenames via `file_title`). **Content is now authored as `content.json`**
  (replaces the bootstrap `content.py`, which is kept git-tracked as reference; verified
  faithful — content.json renders byte-identical PDFs). Migrated Sheet 1 into a manifest unit:
  all 5 build stages `done`, `publish` pending (batch-gated), `next_pending → publish`, drift
  pre-check passed, content_grade 20/20. NOTE: full Pydantic part-type schemas deferred —
  coding stages pass manifest's "no schema registered" check; gates enforced by the
  gate-result files (solution_run/content_grade/visual_grade) + `coding_rubric`. Next = Phase C (Sheet 2).
- 2026-06-13: **Phase C DONE** — Sheet 2 "Loops That Make Patterns" through the full
  checkpointed pipeline (run-gate, 20/20, drift passed, visual-inspected). Added
  `build_to_render()` + `finalize_visual()` orchestration to coding_build.py. Revised
  topics.json to a loop-centric G3 arc (sequential/concurrent-only sheets can't clear C1 for G3).
- 2026-06-13: **Phase D DONE — full G3·Block Coding calibration batch (7 sheets) built.**
  01 Loops · 02 Loops That Make Patterns · 03 Start It, Then Repeat · 04 Two Scripts Both
  Repeating · 05 Read and Change a Loop · 06 Loop a Longer Pattern · 07 Find the Loop Bug.
  EVERY sheet: run-gate PASS, content_grade **20/20** (C1–C5 all L4) + drift passed,
  both PDFs rendered + visually inspected clean (each sheet has an original SVG diagram;
  teacher guides tightened to 1 page). All at 5/6 stages — **`publish` pending = the human
  `batch_verification` gate**. Per the goal, STOPPING here for user sign-off before publish
  + before the next subject. Next (Phase E, after sign-off) = drive_publish.py + push 14 PDFs.
- 2026-06-13: **Phase E DONE — batch PUBLISHED + signed off.** User approved the loop-centric
  arc + publish. `pipeline/drive_publish.py` pushed the **14 PDFs (2/topic)** to
  `Product/Resources/Generated Coding Worksheets/Grade 3/Block Coding/<N. Topic>/` — numbered
  folders for clear navigation; **only** the Worksheet + Teacher Guide per folder. Idempotent
  (update-in-place). Hygiene check + independent Drive-API audit: **7 folders, 14 PDFs, 0 strays**.
  All 7 manifests now 6/6 (publish=done). Block Coding Drive folder:
  https://drive.google.com/drive/folders/13ANbhJATvAjMNGqTn911h1jVnk6uMn4M
  **G3·Block Coding subject COMPLETE + SHIPPED.** Next (awaiting user go-ahead) = next subject
  **Intro Python Turtle** (its own ~7-sheet batch + batch gate); then G3 Debugging; then K/G1/G2.
- 2026-06-13: **SCOPE → FULL CATALOGUE, batch gating REMOVED (user).** Prepared for autonomous
  build of all ~96 worksheets: `coding/MASTER_BUILD_PLAN.md` (authoritative full-build plan),
  `coding/subjects.json` (12-subject machine queue, build order, per-grade concept ceilings,
  G3 Block Coding=done), `AUTONOMOUS_BUILD.md` §5 rewritten (continuous build + auto-publish, no
  human gate) + §6 (update plan+handoff at EVERY checkpoint), HANDOFF updated. Quality gates remain
  (run-gate, ≥19/20, visual). **READY — awaiting user to set the goal to start the full build.**
  Next subject = G3 Intro Python Turtle (order 2 in subjects.json).
- 2026-06-13: **G3 · Intro Python Turtle SHIPPED** (subject 2/12). 7 sheets, each run-gate
  PASS + **20/20** + visually inspected; loop-centric (every sheet a for-loop so C1 hits G3);
  solution.py MODELS the turtle path (no GUI). Sheets 1–2 keep the block→text bridge; 3–7 drop
  the block stack (C3-L4 via cross-strand/challenge) to stay 2 pages. Durable renderer fix:
  `compact` mode auto-applied to all teacher guides (1 page reliably). Published 14 PDFs to
  `…/Generated Coding Worksheets/Grade 3/Intro Python Turtle/<N. Topic>/` (hygiene OK).
  subjects.json: g3_python_turtle=done. **Next subject = G3 Debugging (order 3).**
- 2026-06-14: **G3 · Debugging SHIPPED** (subject 3/12). 7 sheets — 01 What Is a Bug? · 02 Off by
  One · 03 The Wrong Block Inside · 04 The Wrong Turn · 05 Extra or Missing Block · 06 Trace the Bug
  · 07 More Than One Fix. Every sheet: run-gate PASS + **20/20** (C1–C5 all L4) + drift passed +
  visually inspected clean. C3.2-centric (read/alter/fix code that involves a loop, so C1 reaches G3);
  mix of block + Turtle contexts; method on every sheet = say what it SHOULD do → spot the
  wrong/missing/extra part → fix it. Each buggy case AND its fix MODELLED + asserted in solution.py.
  Sheet 07 (the challenge) = a loop bug with TWO valid fixes (change repeat count OR change blocks
  inside); cross-strand Number hook `total = repeat × blocks inside`; Ex 4 = choose-and-justify.
  Published 14 PDFs to `…/Generated Coding Worksheets/Grade 3/Debugging/<N. Topic>/` (7 folders,
  hygiene OK, 0 strays). Drive: https://drive.google.com/drive/folders/1TMujDTIFUaZPnf3t_MjDb47m3UlOanLF
  subjects.json: g3_debugging=done. **G3 fully complete (3 subjects, 21 sheets, 42 PDFs).**
  **Next subject = K Unplugged CT (order 4)** — K-frame (no C3 codes), unplugged/symbol-only, no text/loops;
  arc must be designed against `rubric_coding_K.md` + the K `concept_ceiling`.
- 2026-06-14: **K · Unplugged Computational Thinking SHIPPED** (subject 4/12, first Kindergarten subject).
  8 sheets — 01 Sort by Shape · 02 Same and Different · 03 What Comes Next? · 04 Growing Patterns ·
  05 Which One Does Not Belong? · 06 Break It Into Parts · 07 Sort Two Ways · 08 Fix the Mix-Up. CT-thinking
  arc (classify→compare→pattern→pattern→abstract→decompose→multi-classify→debug); stays out of routine
  sequencing (subj 5) and arrow-blocks (subj 6). Every sheet: run-gate PASS (solution.py MODELS the
  answer — no executable text code at K) + **20/20** (C1–C5 all L4) + drift passed + visually inspected.
  **NEW renderer primitive (additive, zero regression risk):** `symbols` part in `pipeline/worksheet_pdf.py`
  — large geometric symbol cards (★ ● ▲ ■ ➡ ↻) + dashed 'what comes next' answer card; this is what makes
  K genuinely picture/symbol-driven (tested: color emoji render too small/inconsistent → not used as backbone).
  No reading required of the child (adult reads the short prompt; child draws/circles); Bit models each
  worked example. Published 16 PDFs to `…/Generated Coding Worksheets/Kindergarten/Unplugged Computational
  Thinking/<N. Topic>/` (8 folders, hygiene OK). Drive:
  https://drive.google.com/drive/folders/1_yM25wZ-ix5EPvO-iUMy1eGAvJAA9Pv5  subjects.json: k_unplugged_ct=done.
  **Catalogue now 4/12 subjects, 29 sheets, 58 PDFs.** **Next = K Sequencing & Algorithms (order 5)** —
  directional/routine sequencing, ≤4 steps, picture-driven; reuse the `symbols`/`blocks` primitives.
- 2026-06-14: **K · Sequencing & Algorithms SHIPPED** (subject 5/12). 8 sheets — 01 First, Next, Last ·
  02 What Comes First? · 03 Put It in Order · 04 Order Matters · 05 Follow the Arrows · 06 Which Way? ·
  07 Give Bit the Steps · 08 Fix the Order. Arc = ORDER (algorithm = ordered steps): ordering growing-count
  cards (1-4) + a 1D arrow-path board (boxes numbered L→R, ➡/⬅ moves, ★ goal) for follow/choose/compose/debug
  (5-8). Distinct lane from Unplugged CT (classify/pattern) and Intro Block (coloured block stacks) — here
  arrows are unplugged path directions, ≤4 steps, 1D. Every sheet: run-gate PASS (solution.py MODELS the
  order/landing-box/program + asserts) + **20/20** + drift + visually inspected. Published 16 PDFs to
  `…/Kindergarten/Sequencing & Algorithms/<N. Topic>/` (hygiene OK). Drive:
  https://drive.google.com/drive/folders/158bMnSexks_0TPZ1PCwH38jRWFb8c8Ug  subjects.json: k_sequencing=done.
  **Catalogue now 5/12 subjects, 37 sheets, 74 PDFs.** **Next = K Intro Block Coding (order 6)** — ScratchJr
  symbol-only coloured BLOCK stacks (use the `blocks` part), single short sequence, no text; last K subject.
- 2026-06-14: **K · Intro Block Coding SHIPPED** (subject 6/12 — **K COMPLETE**). 8 sheets — 01 Meet the Blocks ·
  02 Run It Top to Bottom · 03 Move Blocks · 04 Read Bit's Stack · 05 Finish the Stack · 06 Match the Stack ·
  07 Build Bit's Stack · 08 Fix the Stack. Distinct lane = the BLOCK-STACK metaphor (a program is a stack of
  coloured ScratchJr-style blocks that snap together + run TOP-TO-BOTTOM): green GO ⚑ start block (cat
  `operators`) + blue MOVE blocks (cat `motion`, single arrow glyph ➡⬅⬆⬇), vs Sequencing's loose arrow-path
  board and Unplugged CT's classify/pattern. Arc weights block STRUCTURE (what a block is → start block → run
  order → block vocab → trace → complete → match/abstraction → build → debug). Tracing uses the proven 1D
  `symbols` stage (boxes 1-5, Bit + ★), ≤4 move blocks, 1D (➡/⬅). Every sheet: run-gate PASS (solution.py MODELS
  the program/landing-box/bug-fix + asserts) + **20/20** (C1-C5 all L4) + drift + visually inspected.
  **Additive renderer work (zero regression — default unchanged):** `blocks` part now takes part-level `size`
  ("md"/"lg") so a single arrow/flag glyph reads large, plus a per-block `blank:true` dashed slot (the
  draw-the-missing-block answer). **Renderer BUGFIX:** `footer_topic` is used in CSS `content:` where HTML
  entities are NOT decoded — switched it from html.escape to a CSS-string escape so apostrophes render as `'`
  not `&#x27;` (surfaced by "Bit's"; only sheets with an apostrophe in footer_topic were affected — none shipped
  earlier had one). Published 16 PDFs to `…/Kindergarten/Intro Block Coding/<N. Topic>/` (8 folders, audited 0
  strays). Drive: https://drive.google.com/drive/folders/1cLIMiX8bsL__cwR-qiuMs_aBST3CsvmB  subjects.json:
  k_intro_block=done. **Catalogue now 6/12 subjects, 45 sheets, 90 PDFs. K (3 subjects) COMPLETE.**
  **Next = G1 · Block Coding (Sequential Events) (order 7)** — G1 rubric, SEQUENTIAL only (order matters, one
  actor, ≤6 blocks, NO loops/concurrency); design arc vs `rubric_coding_G1.md` + the G1 `concept_ceiling`.
- 2026-06-14: **G1 · Block Coding (Sequential Events) SHIPPED** (subject 7/12 — first Grade-1 subject). 8 sheets —
  01 Start and Go · 02 Order Matters · 03 Build the Code · 04 Forward and Back · 05 Predict, Then Run ·
  06 Change One Block · 07 Fix the Code · 08 Plan and Code. **Lane = a NUMBER-PATH (0–5) block program:**
  Scratch-style coloured blocks with DECODABLE TEXT labels (orange `events` "start at N" + blue `motion`
  "forward N"/"back N"), run top-to-bottom; result = the number Bit lands on — a computational representation of
  a mathematical situation (counting / add & subtract within 10), which is where Ontario C3 lives. Arc covers
  BOTH C3.1 (write & run) and C3.2 (order/predict/alter/describe/debug). **Order genuinely matters via the path
  BOUNDARY** (Bit can't pass 5 or go below 0 — it stops at the edge), so the same blocks reordered land
  differently — honest, not just value-changes. solution.py = a tiny clamped sequential interpreter; every
  landing/alter/fix MODELLED + asserted. G1 uses real text labels (light decodable reading), unlike symbol-only
  K. input_row cites **Grade-1 C3.1 + C3.2 verbatim** (drift check passes). Every sheet: I/we/you-do scaffold +
  predict-before-run + answer-key explaining why order works → run-gate + **20/20** + visually inspected.
  **Renderer: 0–5 path = clean single row** (7-card 0–6 wrapped → standardized to 0–5). Published 16 PDFs to
  `…/Grade 1/Block Coding (Sequential Events)/<N. Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/1uKyzrks5wERumo_cwWTOTqOwWJvCrI7U  subjects.json: g1_block_sequential=done.
  **Catalogue now 7/12 subjects, 53 sheets, 106 PDFs.** **Next = G1 · Unplugged Sequencing & Algorithms (order 8)**
  — unplugged sequences/algorithms, light decodable reading + icons, ≤6 steps, NO loops; arc vs `rubric_coding_G1.md`.
- 2026-06-14: **G1 · Unplugged Sequencing & Algorithms SHIPPED** (subject 8/12). 8 sheets — 01 Put It in Order ·
  02 First, Next, Then, Last · 03 Follow the Steps · 04 Write the Steps · 05 Does the Order Work? · 06 What Must
  Come First? · 07 Match the Algorithm · 08 Plan Your Algorithm. **Lane = UNPLUGGED ordered STEP-CARDS** (an
  algorithm = steps in order to do a job): lettered `blocks` chips (slate `value`) with short DECODABLE phrases;
  the child orders / follows / writes / reasons. NO on-screen program (that's the Block-Coding subject), NO loops.
  Covers C3.1 (order/follow/write algorithms) + C3.2 (sequence words, judge order, dependencies, abstraction).
  Several tasks are mathematical (AB/ABB pattern via `symbols` blank boxes, count/build) for C1 tie; rest are
  routines (plant seed, brush teeth, make tea). solution.py models canonical order + **precedence/dependency
  checks** (works()/must_precede via permutations) and asserts every answer; open write-tasks have a modelled
  sample. Distinct from next subject (Intro Debugging = dedicated sequence REPAIR). I/we/you-do + think/predict
  + answer-key explains why-order. Cite G1 C3.1/C3.2 verbatim. Published 16 PDFs to `…/Grade 1/Unplugged
  Sequencing & Algorithms/<N. Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/11pddj1_n0w8CyxTmhDYD3LUMXeUzjEzx  subjects.json: g1_unplugged_sequencing=done.
  **Catalogue now 8/12 subjects, 61 sheets, 122 PDFs. G1 2/3.** **Next = G1 · Intro Debugging (order 9)** —
  debugging = sequence REPAIR (re-order a 3–5 step sequence to fix it), NO loops, C3.2; arc vs `rubric_coding_G1.md`.
- 2026-06-14: **G1 · Intro Debugging SHIPPED** (subject 9/12 — **G1 COMPLETE**). 8 sheets — 01 What Is a Bug? ·
  02 Spot the Wrong Block · 03 Fix by Swapping · 04 Put It Back in Order · 05 The Extra Block · 06 The Missing
  Block · 07 Find and Fix · 08 Debug Detective. **Lane = DEBUGGING number-path block programs** (reuses the G1
  Block-Coding number-path 0–5 + clamped interpreter so a bug = the program lands on the WRONG number). ONE bug
  type per sheet, taught with the debug cycle (run → see it miss → find → fix → run again): identify-a-bug →
  spot-wrong-value (compare PLAN vs CODE) → swap-wrong-direction → RE-ORDER (start-block-not-first + boundary
  move-swap = the ceiling's sequence-repair) → remove-extra → add-missing (blank slot) → mixed find-and-fix →
  challenge (longer mystery program + explain + make-your-own). solution.py models the buggy run, the located
  bug, AND the fixed run + asserts all; C3.2-heavy w/ C3.1 (write corrected block). Cite G1 C3.1/C3.2 verbatim.
  Published 16 PDFs to `…/Grade 1/Intro Debugging/<N. Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/1Oa_aTV349ar5WyVyveW4AfA0b0l22Rsq  subjects.json: g1_intro_debugging=done.
  **Catalogue now 9/12 subjects, 69 sheets, 138 PDFs. G3 + K + G1 ALL COMPLETE.** **Next = G2 · Block Coding
  (Concurrent Events) (order 10)** — G2 rubric; the NEW concept is CONCURRENT — two scripts/sprites running at
  once, parallel green-flag starts, ≤8 blocks; loops still OUT. Cite Grade-2 C3.1/C3.2 verbatim (G2 C3 text =
  'sequential and concurrent events').
- 2026-06-14: **G2 · Block Coding (Concurrent Events) SHIPPED** (subject 10/12 — **G2 1/3**). 8 sheets — 01 Two
  Sprites at Once · 02 Read Both Scripts · 03 Who Is Ahead? · 04 Do They Meet? · 05 Build Pixel's Script · 06
  Predict Both · 07 Change One Script · 08 Debug the Pair. **NEW concept = CONCURRENT.** Lane = **TWO number-path
  sprites — Bit (green, `bit_wave`) and Pixel (purple, NEW `assets/mascots/pixel_wave.svg`)** — each with its OWN
  short block script (green-flag `▶ start at N` `operators` block + forward/back `motion` blocks) on a shared 0–5
  path; **one green flag starts BOTH** and every question is about the COMBINED outcome (both landings / who's
  ahead / do they MEET) — that combined reasoning is what makes the concurrency GENUINE (C2 hard gate), not two
  sequential tasks. Reuses the proven clamped 0–5 interpreter; solution.py runs BOTH scripts and asserts both
  landings + the combined answer. Arc: meet two sprites → read both 2-move scripts → compare (who's ahead) → do
  they meet → **BUILD Pixel's script** (write concurrent, C3.1, blank-block write-slot) → **predict BOTH** then
  run (C4-L4 'predict what happens when both start') → **change one script** & describe the effect (C3.2
  alter+describe, before/after stacks) → **debug the pair** (challenge: which of two parallel scripts is wrong;
  ★ goal-marker on path). Two mascots = the two sprites (C4-L3); TG answer key explains timing/interaction + the
  common error of mistaking sequential for concurrent. Scaffold introduces Pixel's 2nd script only after Bit's
  understood (C3-L4). Every sheet: run-gate PASS + **20/20** (C1–C5 all L4) + drift + every page visually
  inspected. Cite G2 C3.1/C3.2 verbatim. Published 16 PDFs to `…/Grade 2/Block Coding (Concurrent Events)/<N.
  Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/10Uejefrby6oatfuVU6ZNIOi-YgptSq_S  subjects.json: g2_block_concurrent=done.
  **Catalogue now 10/12 subjects, 77 sheets, 154 PDFs.** **Next = G2 · Events & Parallel Scripts (order 11)** —
  events + broadcasts + parallel scripts (two things triggered together), NO loops, C3.1; arc vs `rubric_coding_G2.md`.
- 2026-06-14: **G2 · Events & Parallel Scripts SHIPPED** (subject 11/12 — **G2 2/3**). 8 sheets — 01 When the Flag
  Is Clicked · 02 Two Scripts, One Event · 03 Send a Message · 04 When I Receive · 05 Match the Event · 06 Predict
  With Events · 07 Change the Event · 08 Debug the Events. **NEW angle = EVENTS** (the orange hat block that
  TRIGGERS a script) **+ PARALLEL SCRIPTS started by events.** Builds on the proven two-sprite number-path lane
  (Bit green + Pixel purple, shared 0–5 clamped path) but the new idea is a script runs ONLY when its event
  happens: (a) two scripts sharing 'when green flag clicked' start in PARALLEL from one click; (b) a script can
  `broadcast 'msg'` and a `when I receive 'msg'` script starts in response (and ONLY if the message matches).
  Arc: event hat = trigger → two scripts one event (parallel) → broadcast→receive → receive sets run ORDER →
  match event/script (+message-match) → **predict the event chain** (C4-L4) → **change the event** (C3.2
  alter+describe: receive→green-flag flips sequential→parallel, landings unchanged) → **debug a MESSAGE MISMATCH**
  (Bit sends 'go', Pixel waits 'jump' → Pixel stuck; fix = match the messages). **New solution.py model = an
  event-aware interpreter:** scripts = (trigger_event, home, moves); track fired events (green flag + broadcasts)
  + sent messages; run only triggered scripts; assert both landings + the event behaviour (runs/order/match).
  Event hats use the `events` (orange) block category; ⚑ glyph renders mono. Every sheet: run-gate PASS + **20/20**
  + every page visually inspected. Sheet 07 TG trimmed from 2pp→1pp (overflowed by one line). Cite G2 C3.1/C3.2
  verbatim. Published 16 PDFs to `…/Grade 2/Events & Parallel Scripts/<N. Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/1T1vlAygogQnPONoERy2ab560lV9cHJXR  subjects.json: g2_events_parallel=done.
  **Catalogue now 11/12 subjects, 85 sheets, 170 PDFs.** **Next = G2 · Debugging & Reading Code (order 12 — FINAL)**
  — read concurrent code; find which of two parallel scripts is wrong; predict combined behaviour; NO loops, C3.2;
  arc vs `rubric_coding_G2.md`. When 12/12 → final catalogue summary + final commit/push, STOP the loop.
- 2026-06-14: **G2 · Debugging & Reading Code SHIPPED** (subject 12/12 — **CATALOGUE COMPLETE 🎉**). 8 sheets —
  01 Read Two Scripts Carefully · 02 Which One Is Wrong? · 03 The Wrong Number · 04 The Wrong Direction · 05 The
  Mismatched Message · 06 The Missing Block · 07 Predict, Then Find · 08 Debug Detective. **Distinct angle = READING
  + DEBUGGING concurrent code:** every sheet states the intended COMBINED outcome (a goal), the student reads BOTH
  parallel scripts, runs them, finds which ONE of the two is buggy (the correct sprite already meets the goal), and
  fixes it. Spans the catalogue's bug types in a 2-script concurrent context: careful reading (no bug) →
  identify-which → wrong value → wrong direction → mismatched broadcast/receive message → missing block (dashed
  write-slot) → predict-then-find → mixed challenge (name which + bug TYPE + fix + explain). solution.py models BOTH
  the BUGGY run (one sprite misses the goal) AND the FIXED run + asserts both. ★ goal-marker on the path on every
  debug sheet. Every sheet: run-gate PASS + **20/20** + every page visually inspected. Cite G2 C3.1/C3.2 verbatim.
  Published 16 PDFs to `…/Grade 2/Debugging & Reading Code/<N. Topic>/` (8 folders, audited 0 strays):
  https://drive.google.com/drive/folders/1QmdeKPebuLLJmqDuhtyVYRlAv-wfYHFU  subjects.json: g2_debugging_reading=done.

---

## 🎉 FINAL CATALOGUE SUMMARY — K–G3 Ontario Coding Worksheets COMPLETE (2026-06-14)

**12 / 12 subjects shipped · 93 worksheets (each Worksheet + Teacher Guide) · 186 PDFs in Drive · every sheet 20/20 + run-gate PASS + every page visually inspected.**

Root Drive folder (`Product/Resources/Generated Coding Worksheets`):
https://drive.google.com/drive/folders/1HkbqjbPjSiQbZeW7OCJl7eZuAF_mvw7j

| Grade | Subjects (3 each) | Sheets | Distinct lane / concept | Grade folder |
|---|---|---|---|---|
| **Kindergarten** | Unplugged Computational Thinking · Sequencing & Algorithms · Intro Block Coding | 24 (8×3) | K-frame (no C3), symbol-only, no text/loops; solution.py MODELS the answer + asserts. Lanes: classify/pattern · arrow-path board · ScratchJr colour BLOCK-STACK | https://drive.google.com/drive/folders/1srMaNYVkpO5ZrHOUN5WI94-uLxmsgyNf |
| **Grade 1** | Block Coding (Sequential) · Unplugged Sequencing & Algorithms · Intro Debugging | 24 (8×3) | C3.1/C3.2 SEQUENTIAL only, NO loops/concurrency. Number-path (0–5) clamped interpreter w/ text-label blocks; lettered step-cards + precedence; debug = sequence repair | https://drive.google.com/drive/folders/1xglxNS0jqoN-uEX5f9OmKwunTAZ8TERo |
| **Grade 2** | Block Coding (Concurrent) · Events & Parallel Scripts · Debugging & Reading Code | 24 (8×3) | C3.1/C3.2 + CONCURRENT, loops still OUT. TWO sprites (Bit green + Pixel purple) on a shared 0–5 path; combined-outcome questions; events/broadcast/receive triggers; read+debug two parallel scripts | https://drive.google.com/drive/folders/1QXbz6EirXp-iv32wahEvaSx_Gd16mLx2 |
| **Grade 3** | Block Coding · Intro Python Turtle · Debugging | 21 (7×3) | C3.1/C3.2/C3.3 + REPEATING events (loops); Turtle = first typed code (path MODELLED, no GUI); loop-centric arc | https://drive.google.com/drive/folders/1KhkqtGe4ZSwZdhZGh6kxmOqBDhrEGkQJ |

**Quality model (held on every one of the 93 sheets):** per-sheet manifest chain solution(run-gate) → content.json → content_grade (≥19/20 AND C2≥L3 AND C3=L4 AND C5=L4, BEFORE render) → render → visual_grade (every page Read) → publish (only the 2 PDFs/topic, hygiene-checked). Per-grade rubric via `pipeline/coding_rubric.py`. Original kawaii mascots (Bit + Pixel), data-driven WeasyPrint renderer (`pipeline/worksheet_pdf.py`), idempotent Drive publish (`pipeline/drive_publish.py`). All curriculum codes cited verbatim from the Ontario cache (drift-checked).

**Build is COMPLETE — the /loop is stopped (no further reschedule).**
