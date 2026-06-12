# Coding-Worksheet Pipeline — Adaptation Plan

Adapt the `worksheet_generator` pipeline (currently K-3 Ontario **Math** → Google
Slides) to generate **coding worksheets** that mirror the structure of the
Junior Creator / Ultimate Innovator PDF corpus, with **original Ontario-aligned
content**, **original kawaii mascot SVGs**, rendered as **branded PDF worksheets**.

## Locked decisions
- **Fidelity:** Same structure / sequence / learning objectives as each source sheet, but **original** prose, code, and exercises aligned to Ontario. (IP-safe → sellable on TCE.)
- **Output:** Page-based **PDF worksheets** that look like the source house style.
- **Grade banding:** Output is organized **K / Grade 1 / Grade 2 / Grade 3** → subject → worksheet. Source coding content (Python Advanced, web dev, Arduino) is *pedagogical reference only*; concepts are **adapted down** to each grade's Ontario coding expectations (Strand C3, grades 1–3; Kindergarten computational-thinking frame). We do **not** port advanced source content verbatim into K–3.
- **Output destination:** Google Drive **`Product/Resources`** (`1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E`), alongside the source `Coding Resources-Kassandra`.
- **Publish rule:** each worksheet's Drive folder keeps **only the teaching-content PDF + a teacher-instructions PDF**. Homework/solutions/required-files are generated internally (for the code-runs gate) but **not published** to these folders.
- **Scope:** **K–3 only.** Pilot one grade+subject first → *Grade 3 · Block Coding* (~6–9 sheets), then the other two G3 subjects (Intro Python Turtle, Debugging), then K/G1/G2.

---

## 1. What the source actually is (reviewed from the two zips)

`Coding Resources-Kassandra/` Drive folder → 2 zips, **484 PDFs + 121 docx**:

- **Junior Creator:** Scratch (4 levels), Python (Intro/Beginner/Intermediate/Advanced, ~9–12 wk each), Arduino (18 lessons), Web Design (HTML, CSS Pt1/Pt2, JavaScript 8 modules).
- **Ultimate Innovator:** Python Advanced (11 topics), Web-Design & Development (HTML/CSS/JS).

**Two house styles in the corpus:**
1. **`ultimatecoders.ca` branded sheets** (the majority): portrait page; header band = **mascot-in-a-circle (left) + centered title**; footer = `N. Topic | www.ultimatecoders.ca [page]`; body = prose + monospace **code blocks** + screenshots/diagrams + exercises. Solutions reuse the same header with answer code.
2. **MIT Scratch activity cards** (`scratch.mit.edu`) — third-party MIT material. *Exclude from cloning; if a Scratch track is wanted, author original cards.*

**A "sheet" unit of work** (Python Intro, per week) = **4 PDFs**: classwork (CW), homework (HW), Solution-CW, Solution-HW. 9 weeks → ~36 PDFs for the pilot.

> **IP note:** the source is two companies' copyrighted curriculum. The "same
> structure, original content" decision keeps us clear. The mascot swap is part
> of that — do **not** reuse the green-haired ultimatecoders character or MIT's
> Scratch art. Original kawaii cast only.

## 1b. Output structure (Drive) & publish rule

Built under `Product/Resources/` (`1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E`). Proposed
generated root to avoid colliding with the source folder:

```
Product/Resources/
└── Generated Coding Worksheets/        ← created by the pipeline (Drive)
    ├── Kindergarten/
    │   └── <Subject>/                  ← e.g. "Unplugged Coding", "Block Coding"
    │       └── <Worksheet topic>/
    │           ├── <topic> — Worksheet.pdf        ← teaching content (PUBLISHED)
    │           └── <topic> — Teacher Guide.pdf    ← teacher instructions (PUBLISHED)
    ├── Grade 1/<Subject>/<topic>/ …
    ├── Grade 2/<Subject>/<topic>/ …
    └── Grade 3/<Subject>/<topic>/ …
```

**Only two files per worksheet folder ship:** the teaching-content PDF and the
teacher-instructions PDF. Everything else (homework, solution PDFs, runnable
code, required files) stays in the local `generated_units/` working tree for the
gates and is **never uploaded** here. The Drive push step filters to exactly
those two artifacts; a post-publish hygiene check asserts the folder contains
nothing else (mirrors today's `slides.py` per-unit cleanup behavior).

**Scope: K–3 only** (no Grade 4+ band). Advanced source content (Python Adv, web
dev, Arduino) is reference only and does not get its own grade band.

**Subjects per grade (FINAL)** — built on the Ontario C3 event-type progression
(K: no C3 → unplugged CT; G1: sequential → G2: +concurrent → G3: +repeating/loops + text bridge):
- **Kindergarten:** *Unplugged Computational Thinking* · *Sequencing & Algorithms* (daily-routine / directional) · *Intro Block Coding* (ScratchJr-style, symbol-only)
- **Grade 1:** *Block Coding — Sequential Events* · *Unplugged Sequencing & Algorithms* · *Intro Debugging* (re-order a sequence)
- **Grade 2:** *Block Coding — Concurrent Events* · *Events & Parallel Scripts* · *Debugging & Reading Code*
- **Grade 3:** *Block Coding* (sequential+concurrent+repeating/loops) · *Intro Python Turtle* · *Debugging*

## 2. Ontario alignment

Coding maps cleanly to Ontario:
- **Math (2020), Strand C3 "Coding"** — grades 1–9 (e.g. C3.1 write/execute code w/ sequential, concurrent, repeating, nested events; C3.2 read/alter/debug). Covers Scratch + intro Python/Turtle for the Junior Creator band.
- **Secondary Computer Studies (ICS2O/3U/4U)** and **Tech Ed (TEJ)** — for Python Advanced / full Web-Dev (Ultimate Innovator band).

Action: extend the existing `pipeline/curriculum_fetch.py` + `curriculum/` cache
(today: K + G1-3 math) to also cache the **C3 coding expectations** and the
relevant secondary CS expectation codes. Each generated course gets an
expectation map in its blueprint, same pattern as the math units.

## 3. Reuse / change / build (gap analysis vs current pipeline)

**Reuse as-is (domain-agnostic):**
- `pipeline/manifest.py` — state machine (`init_unit`, `mark`, `complete_stage`, `next_pending`, `retry_failed`, `status_table`, `run.log.jsonl`, atomic writes). The whole checkpoint/resume model carries over unchanged.
- `pipeline/clipart.py` LRU model — repurpose for the mascot/asset library.
- `pipeline/image_alignment.py` — keyword↔caption drift gate still valuable.
- The **schema scaffolding already has** `Worksheet`, `WorksheetPage`, `WorksheetPart`, `WorksheetHeader`, `ImagePlaceholder`, `PrintSpec` (`schemas.py:347-428`) — a strong starting point for code worksheets.

**Change / repoint:**
- `pipeline/stages.py` — replace the 17 math stages (blueprint→5 lessons→5 worksheets→manipulatives→…→rubric) with a **coding stage set** (below).
- `pipeline/schemas.py` — extend `WorksheetPart` with a `code_block` part type (language, code, `is_solution`, expected-output) and an `exercise` part type; add a `CourseBlueprint` + `SolutionSheet` schema. Drop math-only schemas (Manipulatives/Formative/AssessmentSuite) from the active stage list (leave classes in place, just unused).
- `pipeline/curriculum*.py` — point the curriculum-text drift gate at the coding expectation cache.
- `pipeline/rubric.py` — swap the single math product rubric for the **per-grade coding rubrics** (`assets/rubric_coding_<grade>.md`, see §5b); select by the unit's grade; keep the pre-grade drift gate + remediation-map mechanism.

**Build new:**
- `pipeline/worksheet_pdf.py` — **HTML+CSS → PDF renderer (WeasyPrint)**. One reusable page template: mascot header band, title, body parts (prose / code block / exercise / image), branded footer with page numbers. This is the single biggest new piece and the thing the pilot must prove first. (Alt: reportlab; WeasyPrint chosen for precise CSS control of the branded layout + code blocks.)
- `assets/mascots/` — **original kawaii mascot SVG cast** (3–5 named characters: e.g. a round "byte" buddy, a cat-ish "Pixel", etc.), drawn as SVGs, rendered via the existing `compose.py`/`rsvg-convert` path. Plus `INDEX.json` (name, tags, caption, expression variants) reusing the clipart LRU pattern so mascots vary across sheets.
- `pipeline/source_map.py` — walk a source course folder, emit the **sheet queue** (the coding analogue of `unit_plan.json`): one entry per CW/HW pair with its topic + week, so "sheet for sheet" is literally driven by the source tree.

## 4. New stage set (per course → per week)

Driven by `source_map.py`. Two levels:

**Course level (once per course):**
- `course_blueprint` — Ontario expectation map for the course, mascot cast assignment, vocabulary, week-by-week topic list (derived from the source folder names + a read of each source sheet for *topic/objective only*, not content).

**Worksheet level (the repeating loop — one "sheet" stage each):**
- `worksheet_NN` — the teaching-content worksheet (original content for the topic). **PUBLISHED.**
- `teacher_guide_NN` — teacher instructions (objective, Ontario expectation cited, materials, step-by-step facilitation, answer key summary, extension). **PUBLISHED.**
- `solution_NN` — runnable solution(s) for the worksheet's code, executed/validated (see §5). **Internal only — not published.**
- `rubric_grade_NN` — grade the sheet against the grade's rubric (§5b); ≥15/20 + C2 hard gate to publish, else writes `remediation[]`. **Internal only.**

Each stage = one JSON file, one tool turn, validated by `complete_stage()` →
checkpoint/resume exactly like today. Final per-subject gate = rubric +
mandatory visual (PDF) inspection. Only the worksheet + teacher-guide PDFs are
uploaded to Drive.

## 5. Drift / quality gates (adapted)

1. **Schema validation** (`complete_stage`) — unchanged mechanism.
2. **Curriculum reference** — code worksheet's cited expectation codes must be valid for the grade band (repointed gate).
3. **Image/mascot alignment** — every mascot/diagram placeholder populates `keywords` + alignment check (existing gate).
4. **NEW — code-runs gate:** every `code_block` marked `is_solution` is **executed in a sandbox** (Python via subprocess; JS via node; HTML/CSS lint) and must run without error; for deterministic outputs, expected-output is asserted. This is the coding analogue of the math "verbatim curriculum" gate and is the single most important correctness check.
5. **Rubric gate** — the **per-grade coding rubric** (§5b) must score ≥ 15/20 **and** clear its hard gate (Criterion 2, concept-correctness) for a sheet to ship. Drives `remediation[]` on failure.
6. **Mandatory visual inspection** — render each PDF page → Read it → checklist (header/mascot present, code block not truncated, no overflow, footer/page numbers correct) before a course is "done."

## 5b. Grade rubrics (built — `~/Desktop/TCE/coding_rubrics/`)

One rubric per grade band, authored to the existing pipeline's gradable shape
(criteria with **L1→L4 closed checklists**; grader stops at the highest fully-met
level). Files: `rubric_coding_K.md`, `rubric_coding_G1.md`, `rubric_coding_G2.md`,
`rubric_coding_G3.md` → become `assets/rubric_coding_<grade>.md` at build time;
`pipeline/rubric.py` selects by the unit's grade.

**Shared model:** 5 criteria × L1–L4 (1–4 pts) = **/20**. **Pass = total ≥ 15
AND Criterion 2 (concept correctness) ≥ L3** (hard gate — ties into the §5
code-runs gate; a sheet whose solution code/blocks are wrong can never ship).

| # | Criterion | What it measures |
|---|---|---|
| C1 | Ontario C3 / K-frame Alignment | Cites & actually exercises the grade's expectation (K: CT frame; G1 sequential → G2 +concurrent → G3 +repeating) |
| C2 | Coding-Concept Correctness *(hard gate)* | Blocks/code/sequence correct; Turtle solutions execute clean |
| C3 | Grade-Appropriate Pedagogy & Cognitive Load | Reading level, step/block budget, one-idea-per-page, scaffold |
| C4 | Clarity, Structure & Mascot/Visual Integration | Example→practice→challenge flow; mascot as the actor; image↔text alignment |
| C5 | Teacher Guide Completeness | Objective, facilitation, answer key, expectation cited, differentiation |

**Per-grade calibration** lives in each file — the difference is concept scope
(K unplugged/symbol-only, no text/loops → G3 typed Turtle + loops) and the
cognitive-load budgets. Remediation maps each failing criterion to which stage
to regen (`worksheet_NN` / `teacher_guide_NN` / `solution_NN`).

## 6. Pilot plan — *Grade 3 · Block Coding* (concrete steps)
*(G3 subjects = Block Coding, Intro Python Turtle, Debugging; pilot does Block Coding, then the other two.)*

1. **Branch & scaffold.** New branch in `worksheet_generator`; add `assets/mascots/`, `pipeline/worksheet_pdf.py`, `pipeline/source_map.py`, `pipeline/drive_publish.py`; install WeasyPrint; extend stages/schemas.
2. **Mascots.** Draw the original kawaii SVG cast + `INDEX.json`. Render test PNGs via `compose.py`.
3. **PDF template.** Build the one-page WeasyPrint template (worksheet + teacher-guide variants); produce a throwaway sample; iterate until it matches the house style (branded header w/ mascot, code block, exercise, footer). **Gate the pilot on this looking right.**
4. **Curriculum cache.** Fetch/curate the Ontario **C3 coding** expectations for **Grade 3** (block-based: sequential/concurrent/repeating/nested events, read/alter/debug).
5. **Subject map.** Define the Grade 3 · Block Coding subject = ~6–9 topics (sequencing → events → loops → conditionals → debugging mini), pitched to G3. `source_map.py` emits the worksheet queue.
6. **Generate sheet 1 end-to-end:** `course_blueprint` → `worksheet_01` → `teacher_guide_01` → `solution_01` (run-gate) → **grade vs `rubric_coding_G3.md` (≥15/20 + C2 hard gate)** → PDFs → visual inspect. Fix renderer/schema where reality bites.
7. **Run sheets 2–N** through the proven loop (one stage per turn, resumable).
8. **Publish** to `Product/Resources/Generated Coding Worksheets/Grade 3/Block Coding/<topic>/` — **only** the worksheet + teacher-guide PDFs per topic, via `drive_publish.py` (reuses `slides.py` Drive auth/upload helpers). Post-publish hygiene check: folders contain exactly those two files. Then repeat for **Intro Python Turtle** and **Debugging**.

**Pilot definition of done:** Grade 3 · Block Coding (~6–9 topics); each topic =
an original worksheet PDF + teacher-guide PDF published to
`Grade 3/Block Coding/<topic>/`; all internal solution code executes clean; all
pages pass visual inspection; mascots original; published folders contain only
the two intended PDFs. Then the other two G3 subjects follow the same loop.

## 7. Risks / open questions
- **WeasyPrint fidelity** to the source look is the top risk → that's why step 3 gates the pilot.
- **Output destination — RESOLVED:** `Product/Resources/` (`1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E`); generated tree under a `Generated Coding Worksheets/` parent → grade → subject → topic; only worksheet + teacher-guide PDFs published.
- **Grade-band scope — RESOLVED:** **K–3 only.** No Grade 4+ band; advanced source content (Python Adv, web dev, Arduino) is reference only and is adapted *down* into the K–3 C3 expectations.
- **Subjects-per-grade — RESOLVED (all K–3):** finalized in §1b. Per-grade rubrics built (§5b, `~/Desktop/TCE/coding_rubrics/`). You can still tweak topic counts per subject before mass generation.
- **Scratch tracks:** source uses MIT's own cards → if wanted, author original cards rather than mirror MIT. Out of pilot scope.
- **docx activities/projects:** 121 docx (projects, required files) — reference only; decide later whether to regenerate companion project docs.

## 8. Housekeeping noticed (separate from this task)
- The older local clones (`~/Desktop/tce_migration_bundle_2026-05-03/...`, `~/Documents/TheClassroomExchange/...`) have a **GitHub PAT embedded in their git remote URL** → rotate/revoke.
- The Google OAuth token was expired; re-auth done this session (`token.json` refreshed). `auth_only.py` has a bug: a dead refresh token makes it crash instead of re-prompting — worth a one-line fix (catch `RefreshError` → fall through to browser flow).
