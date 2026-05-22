# Worksheet Generator — Runbook for Claude sessions

This project generates curriculum-aligned K-3 units for The Canadian Classroom
Exchange marketplace. **Claude (you) are the runner.** Python is plumbing only —
no Anthropic API calls. Use the Write tool to produce stage outputs.

For comprehensive context (architecture, schemas, fonts, layout, decisions),
see the memory file at `~/.claude/projects/-Users-anthonnymonterroso-Desktop-TCE-TCE/memory/project_worksheet_generator.md`.

## Multi-unit programme — read this FIRST

The programme has **40 K-G3 Math units** queued. Each session resumes from
wherever the previous one stopped via the checkpoint file `unit_plan.json`
(at the project root) and per-unit `manifest.json` files.

**At session start:**

```bash
./venv/bin/python -c "
from pipeline import unit_plan
unit_plan.refresh_state_from_disk()    # rescans every unit_dir, recomputes status
print(unit_plan.status_table())        # prints programme-wide checkbox view
nxt = unit_plan.next_unit_to_generate()
if nxt: print(f'\\nNEXT UNIT: {nxt.unit_id} (anchor {nxt.anchor_code}, {nxt.grade})')
"
```

**To pick up where the last session stopped:**

1. `next_unit_to_generate()` returns the unit to work on. Prefers
   resuming an `in_progress` unit; falls back to the next `planned` one.
2. If the unit's directory doesn't exist yet, run
   `unit_plan.init_unit_from_plan(entry)` — this creates the folder,
   writes `input_row.json` with verbatim Ontario curriculum text, and
   initialises the manifest with all 16 stages pending.
3. From there, the per-stage workflow below kicks in: read manifest,
   find next pending stage, generate it, run drift gates, mark done.
4. When the unit hits 7/7 done with rubric `status="pass"`, run the
   final-output protocol → deck publishes → mark unit `complete` in the
   plan state. Move to the next.

**Stop conditions for a session:**

- All four drift gates clean + a stage marked `done` → safe to stop.
- Never stop in the middle of a stage that's `in_progress`. Either finish
  it cleanly (`complete_stage` call returns `done`) or revert to
  `pending` so the next session restarts from a clean state.

**Best practices for the long-running programme:**

- One stage per turn. Don't try to draft multiple lessons in one tool call.
- Drift gates run automatically inside `complete_stage` — never bypass them.
- Visual inspection is mandatory before any deck ships (see "Mandatory
  visual inspection" section below).
- Always `refresh_state_from_disk()` at the top of a session — the
  canonical truth lives in the manifests, not in your memory.

## What you do at session start

1. **Read this file + memory file.** Then check state across all batches:
   ```bash
   cd /Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator
   ./venv/bin/python -c "
   from pathlib import Path
   from pipeline.manifest import status_table, list_failed
   from pipeline.curriculum_reference import report_reference_status
   from pipeline.density import report_cross_grade_density
   from pipeline.clipart import report_usage as report_clipart_usage
   from pipeline.image_alignment import report_alignment_status

   for batch in ['batch_1', 'batch_2', 'batch_3']:
       bd = Path(f'generated_units/{batch}')
       if bd.exists():
           print(f'\n=== {batch} ===')
           print(status_table(bd))

   # Surface any 'needs_human' / 'best_effort' curriculum reference statuses.
   print('\n=== Curriculum reference status ===')
   for line in report_reference_status(): print(line)

   # Cross-grade density audit so the differentiation rule is visible.
   units = []
   for batch in ['batch_1', 'batch_2', 'batch_3']:
       bd = Path(f'generated_units/{batch}')
       if bd.exists():
           units.extend(sorted(bd.iterdir()))
   units = [u for u in units if (u/'0_blueprint.json').exists()]
   print('\n=== Cross-grade density ===')
   for line in report_cross_grade_density(units): print(line)

   # Image-text alignment — every keyword in every ImagePlaceholder must
   # appear in surrounding student-facing text. Drift here is the third
   # rubric pre-gate component (alongside consistency_check + curriculum
   # verification); a unit cannot record a passing rubric grade with any
   # alignment issue. Surfaced at session-start so issues get fixed as
   # they're introduced, not at the publication gate.
   print('\n=== Image-text alignment ===')
   for line in report_alignment_status(): print(line)

   # Clipart rotation status — what's fresh, what's been recycled.
   print('\n=== Clipart library ===')
   print(report_clipart_usage())
   "
   ```
2. **Find the next pending stage** in any batch:
   ```bash
   ./venv/bin/python -c "
   from pathlib import Path
   from pipeline.manifest import load, next_pending
   for batch in ['batch_1', 'batch_2', 'batch_3']:
       bd = Path(f'generated_units/{batch}')
       if not bd.exists(): continue
       for ud in sorted(bd.iterdir()):
           if not (ud/'manifest.json').exists(): continue
           m = load(ud)
           n = next_pending(m)
           if n: print(f'NEXT: {ud} -> {n}'); raise SystemExit
   print('No pending stages found.')
   "
   ```

## Stage execution loop

For each pending stage:

1. **Read the unit's `input_row.json` and any prior stage outputs** in the unit
   folder (especially `0_blueprint.json` once it exists — every later stage
   depends on it).
2. **Read the stage prompt template** under `prompts/<NN>_<name>.md` (once
   templates exist; for Unit 1 we generate inline first and extract later).
3. **Mark the stage in_progress:**
   ```python
   from pathlib import Path
   from pipeline.manifest import mark
   mark(Path('generated_units/batch_1/<unit_slug>'), '<stage_key>', 'in_progress')
   ```
4. **Generate the stage JSON inline in the chat.** This is Model A — visible
   generation, user can interrupt and correct.
5. **Write the JSON** to the path specified by the stage's `output_filename` in
   the manifest.
6. **Call `complete_stage()`** — the canonical "finish a stage" call. It
   schema-validates the file against `pipeline/schemas.py`. On success, marks
   the stage `done`. On validation failure, it does NOT raise — it preserves
   the bad output as `<stage_key>.attempt_<N>.failed.json`, marks the stage
   `failed`, logs to `run.log.jsonl`, and returns. Always use this:
   ```python
   from pipeline.manifest import complete_stage
   m = complete_stage(unit_dir, '<stage_key>')
   assert m['stages']['<stage_key>']['status'] == 'done', \
       m['stages']['<stage_key>'].get('last_error')
   ```
   Do NOT call `mark(..., 'done')` directly — it raises on schema failure
   and leaves the manifest in a half-state.
7. **Run the cross-stage consistency check** to catch references that drift
   between the blueprint and downstream stages (manipulative IDs, vocabulary,
   lesson titles, expectation codes):
   ```python
   from pipeline.schemas import consistency_check
   issues = consistency_check(unit_dir)
   assert not issues, issues
   ```

7a. **Advisory checks fire automatically** inside `complete_stage()` and
    print warnings to stdout — they do NOT mark the stage failed. Three are
    wired in:
    - `pipeline.density.validate_lesson_density()` runs after every
      `lesson_NN` stage. It checks the minds_on `teacher_script` length,
      action steps count, and consolidation prompts count against the
      calibrated band for the blueprint's `grade` (see `GRADE_DENSITY` in
      that module).
    - `pipeline.curriculum_reference.verify_curriculum_text()` runs after
      the `blueprint` stage. It diffs `input_row.json` against the in-repo
      `REFERENCE[grade]` and surfaces text drift plus the verification
      status of the reference itself (verified / best_effort / needs_human).
    - `pipeline.image_alignment.validate_stage_alignment()` runs after
      every stage that ships `ImagePlaceholder`s — `worksheet_NN`,
      `manipulatives`, `formative_reflection`, `assessment_suite`. It
      flags any keyword that is not present in the surrounding
      student-facing text (and, when a clipart is referenced, any
      keyword missing from the clipart's caption+tags). Same checker
      runs as the third drift pre-gate at the rubric stage — surfacing
      it per-stage means issues are caught when context is fresh, not
      accumulated and dumped at the publication gate.

    Warnings are advisory — keep going. Don't ignore them silently though:
    if density says a lesson is out of band, ask whether you wrote too thin
    or too thick for the grade. If curriculum says `needs_human`, escalate
    before shipping a paid unit. **If alignment fires, fix it on the spot —
    the rubric drift gate WILL fail with the same error and block
    publication.** The fix is almost always one of: trim a keyword that
    refers to something only in the image description (not in the
    student-facing text), match the keyword spelling to the text token
    form (`tens-frame` vs `ten-frame`), or add a brief mention to the
    `student_instructions` / `visual_layout` if the keyword names something
    load-bearing the child must read.

    **Authoring rule for `ImagePlaceholder.keywords`:** write keywords
    from the words your `student_instructions` and `visual_layout` actually
    use, not from your description of the image. The image description
    can mention apron/spoon/decorative-object detail; the keyword list is
    the contract that "the child reads this word AND can see the thing".
8. **If this was the last stage** (`marketplace`): render `unit.md` and update
   the spreadsheet status column to `generated`.

## Failure protocol

There are two failure modes, and both are recoverable from a cold session:

**A. Schema validation fails** when you call `complete_stage()`:
- The bad output file is automatically copied to
  `<stage_key>.attempt_<N>.failed.json`.
- The stage is marked `failed` with the validator error in `last_error`.
- `run.log.jsonl` records the failure transition.
- Move on to the next pending stage in any *other* unit. Do NOT retry the
  same stage twice in a row in the same session — sleep on it.

**B. You spot a content issue mid-generation** (or the user rejects content):
- Save your draft inline so it's recoverable:
  `Path('<unit_dir>/<stage_key>.attempt_<N>.failed.json').write_text(draft)`
- Mark failed explicitly:
  ```python
  from pipeline.manifest import mark
  mark(unit_dir, '<stage_key>', 'failed', error='<short reason>')
  ```

**Resuming a failed stage** (this session or a future one):
```python
from pipeline.manifest import retry_failed, list_failed, status_table

# See what's failed across the batch:
print(status_table(Path('generated_units/batch_1')))   # surfaces failed stages
list_failed(Path('generated_units/batch_1'))           # detailed errors

# Reset a specific stage back to pending:
retry_failed(unit_dir, stage_key='lesson_04')
# Or reset all failed in this unit:
retry_failed(unit_dir)
```
The reset preserves attempt count and last_error. Then re-run the stage:
mark in_progress → write fresh JSON → complete_stage().

**Cardinal rule:** never block the batch. A unit failing on lesson_02 stays
failed; the runner moves on to other units. Failed stages converge across
sessions, not within one.

## Cardinal rules

- **One stage at a time.** Do not generate multiple stages in a single tool
  call. Checkpointing is the whole point.
- **Never edit a `done` stage without first marking it `pending`** and
  recording why in the manifest's `errors` list.
- **Atomic writes only.** Use `pipeline.manifest.save()` — never write
  `manifest.json` directly.
- **The spreadsheet is the queue.** Only operate on units whose row status is
  `pending`, `needs_regen`, or `in_progress`. Skip `deprecated` and `generated`.
- **Coherence beats throughput.** It is better to slow down and make the unit
  match the example PDF's quality than to produce 5 mediocre units.
- **No images, no PDFs, no quality scoring this week.** Image placeholders only.

## Grade-level differentiation rules

When generating a new unit (Grade 1, 2, 3, etc.), scale up the lesson content:

| Grade | Teacher script paragraph | Action steps | Consolidation prompts |
|---|---|---|---|
| K | ~280 chars | 3 short steps | 2 prompts |
| Grade 1 | ~400 chars | 4 steps | 2-3 prompts |
| Grade 2 | ~500 chars | 4-5 steps | 3 prompts |
| Grade 3 | ~600 chars + sub-bullets | 5 steps | 3+ prompts with justification asks |

The Pydantic schemas accept arbitrary-length strings — no schema changes
needed. As of 2026-04-28, lesson slide sections are dynamically sized to fit
content (no more fixed 2.20in budget), and `_lesson_section_summary()` shows
ALL action steps and ALL consolidation prompts regardless of count. Write
rich content; the layout adapts.

## Final-output protocol (after all 16 stages)

When a unit's last content stage (`marketplace`) is `done`, **the rubric
grade stage runs next as the publication gate**. The deck only lands in the
shared TCE Drive folder if the grade passes (≥ 17/20).

```python
from pathlib import Path
from pipeline.compose import compose_for_unit
from pipeline.render import render_unit
from pipeline.slides import build_unit_deck, validate_unit_for_slides
from pipeline import rubric, manifest

unit_dir = Path('generated_units/batch_<N>/<unit_slug>')

# 1. Pre-grade drift gate — MUST be 0 issues both for the grade to even
#    record a 'pass' status. (The schema rejects pass-with-drift.)
drift = rubric.pre_grade_drift_check(unit_dir)
assert drift['passed'], drift  # if not, fix consistency / curriculum text first

# 2. Run rubric grade — Claude reads every stage JSON, scores against
#    assets/rubric_product_assessment.md, writes 7_rubric_grade.json.
#    See `prompts/70_rubric_grade.md` for the grading prompt template.
#    Then mark the stage:
manifest.mark(unit_dir, 'rubric_grade', 'in_progress')
# ... write 7_rubric_grade.json with full per-criterion scores + status ...
m = manifest.complete_stage(unit_dir, 'rubric_grade')
grade = json.loads((unit_dir / '7_rubric_grade.json').read_text())

# 3a. PASS path — build deck, lands in shared TCE folder per-unit subfolder.
if grade['status'] == 'pass':
    warns = validate_unit_for_slides(unit_dir)
    compose_for_unit(unit_dir)
    (unit_dir / 'unit.md').write_text(render_unit(unit_dir), encoding='utf-8')
    url = build_unit_deck(unit_dir)
    print(f'\n✓ Deck: {url}  (overall {grade["overall_score"]}/20)')

# 3b. FAIL path — mark remediation, the runner picks up regen on next loop.
else:
    reset = manifest.mark_for_remediation(unit_dir)
    print(f'\n⚠ Failed grade {grade["overall_score"]}/20. '
          f'Reset {len(reset)} stages: {reset}. '
          f'Re-run pipeline; new grade required.')
```

If you call `build_unit_deck` without a passing grade (or with no grade at
all), the deck routes to a `_drafts/<unit>/` subfolder under the TCE folder
instead of the public per-unit folder. Visible for inspection, unmistakably
not shipped.

Then **mandatory** visual inspection — text pre-flights cannot see overlap,
truncation, or placeholder PNGs. Render every page and Read each one:

```python
from pipeline.slides import render_validation_pages, VISUAL_INSPECTION_CHECKLIST

pages = render_validation_pages(unit_dir, dpi=150)
# Returns one PNG path per slide, in slide order. Use the Read tool on
# each image. Match each slide to its slide-type entry in
# VISUAL_INSPECTION_CHECKLIST and verify every checkbox.
```

**Walk every slide, every checklist item.** If anything fails:
1. Fix the layout code in `pipeline/slides.py` (lesson body truncation,
   title auto-fit, hero picker, certificate sizing, manipulative prep
   overflow are all already wired — extend the same patterns for new
   issues you find).
2. OR shorten the offending content in the upstream JSON (mark the
   stage pending, edit, complete_stage).
3. Rebuild the deck (`build_unit_deck` again).
4. Re-render and re-inspect.
5. Iterate until every slide passes its checklist.

**The deck does NOT ship until visual inspection is clean.** This is the
last gate, and the only one that catches Slides-API rendering issues
that escape Pydantic + drift gates.

The G3 2026-05-02 inspection round caught five problems that text-only
pre-flight missed:
- Lesson Exit text truncated mid-word at the page edge (slides 4/5/6)
- Worksheet title wrapping into the Learning Goal box (slide 12)
- Hero image rendered as a grey placeholder PNG (slide 10)
- Certificate achievement_text overlapping skills header (slide 21)
- Manipulative TEACHER PREP overflowing the column box (slide 13)

All are now fixed in the layout code, and `validate_unit_for_slides`
catches their text-side signals as warnings — but the visual pass is
still mandatory because new content shapes can introduce new issues
the text heuristics don't anticipate.

## Stage list (per unit)

Defined authoritatively in `pipeline/stages.py`. As of v1.0:

| Order | Key | Output | Depends on |
|---|---|---|---|
| 0 | `blueprint` | `0_blueprint.json` | — |
| 1.1–1.5 | `lesson_NN` | `1_lesson_NN.json` | blueprint |
| 2.1–2.5 | `worksheet_NN` | `2_worksheet_NN.json` | blueprint + lesson_NN |
| 3 | `manipulatives` | `3_manipulatives.json` | blueprint + all lessons |
| 4 | `formative_reflection` | `4_formative_reflection.json` | blueprint + all lessons |
| 5 | `assessment_suite` | `5_assessment_suite.json` | blueprint + all lessons |
| 6 | `marketplace` | `6_marketplace.json` | everything above |
| 7 | `rubric_grade` | `7_rubric_grade.json` | everything above (publication gate) |

## Curriculum reference (USE WHILE GENERATING — not just at validation)

`curriculum/` holds a local cache of Ontario MOE expectations (K 2026 + G1-3
math 2020), pulled from the public Kontent.ai delivery API behind
dcp.edu.gov.on.ca. **This is the authoritative source of truth for expectation
codes and verbatim text.**

When generating a `blueprint` (or any stage that quotes expectation text):
- Pull `curriculum_codes` from valid codes for the grade. Verify with
  `curriculum.validate_codes(grade, codes)` — empty list = all valid.
- Copy `curriculum_expectations[code]` text **verbatim** from
  `curriculum.get(grade, code)['text']`. No paraphrasing.
- The downstream `assessment_suite` rubric reuses the same text — make sure
  it stays verbatim there too.

```python
from pipeline import curriculum
row = curriculum.get("Grade 1", "B1.1")          # row['text'] is the official text
unknown = curriculum.validate_codes("Grade 1", ["B1.1", "C1.4"])  # [] = all valid
```

`pipeline/schemas.py::consistency_check` calls `validate_codes` automatically
after every blueprint stage; `pipeline/curriculum_reference.py::verify_curriculum_text`
diffs each unit's `input_row.json` text against the official source. **Both
must return zero issues for the rubric_grade stage to even record a passing
score** (drift in upstream stages blocks publishing — enforced by the
RubricGrade schema).

## Clipart library (USE WHILE GENERATING — pick from existing, don't invent)

`sample_assets/clipart/` holds the local clipart library, seeded from
Michelle's Google Slides "Clipart" deck on 2026-05-01. Images are tagged
by category (people, animals, vehicles, plants, planets, sports, food,
places, random). 44 images at 1024-px resolution as of seed.

**When generating a `blueprint` for a new unit:**
1. Call `clipart.suggest_for_unit(tags=[...], n=N)` — NOT `list_by_tag`.
   `suggest_for_unit` enforces LRU rotation across the whole catalogue:
   never-used images come first, then oldest-used. This keeps the
   marketplace visually fresh and exhausts the catalogue before recycling.
2. **Record the chosen filenames in `Manipulative.clipart_files`** — this
   is how the rotation tracker knows the image was used. Skipping this
   field breaks LRU for the next unit.
3. Image-generation is NOT wired in. To add new clipart, drop a PNG in
   `sample_assets/clipart/` and append a row to `INDEX.json` (filename,
   path, pixels, tags, caption). Pipeline reads INDEX.json on import.

```python
from pipeline import clipart
clipart.report_usage()                 # session-start status
picks = clipart.suggest_for_unit(tags=["animals", "vehicles"], n=4)
# → list of dicts; record [r["filename"] for r in picks] into the
#    blueprint's manipulatives_index[*].clipart_files
clipart.absolute_path("slide06_animals_01.png")  # filesystem path
```

LRU rule:
- ``(use_count ASC, last_used_at ASC, filename)`` — never-used first;
  among ever-used, oldest first; alphabetical tie-break. Verified by
  `pipeline.clipart.usage_stats()` which scans every blueprint under
  `generated_units/` for `manipulatives_index[*].clipart_files`. No
  separately-maintained usage cache; source of truth is the blueprints
  themselves.

Captions: rows in `INDEX.json` start with `caption=""`. As you use an
image in a unit, add a 1-line caption so future sessions can pick by
meaning ("a fox in mail-carrier uniform") rather than slide position
("slide06_animals_03.png"). The catalogue gets richer over time.

## Lesson-slide layout (single-slide per lesson — for all grades)

Every lesson renders on **one** portrait slide regardless of grade,
including G3+. The single-slide layout was tried-and-rejected on a
two-slide split (deck grew 22 → 27); user preferred the one-page format
even at G3 density. The proportional-scaling code in
`build_lesson_slide` absorbs G3 content adequately when it has to.

The split-layout helpers (`build_lesson_slide_split`,
`build_lesson_slides`) are still present in `pipeline/slides.py` but
disabled — `lesson_should_split` returns False unconditionally. To
re-enable per-grade splits in the future, change that function and
the existing dispatcher in `build_unit_deck` will handle the two-slide
case automatically.

When generating dense G3 content: keep teacher_prompts focused so the
single-slide budget holds. The strict rubric requires substantive
prompts, but the bullet excerpts on the lesson slide are first-sentence
truncations — the full text remains in the JSON / unit.md / and the
expanded_walkthrough block.

## Per-unit Drive folder hygiene

After `build_unit_deck` finishes for a passing unit, it deletes every
non-deck file (composite PNGs, etc.) from the per-unit subfolder under
the TCE shared folder. Slides has already downloaded server-side copies
at insert time, so the originals aren't needed. Result: each per-unit
folder shows **only the .gslides deck** — the buyer/teacher-facing
artifact, nothing else.

This cleanup runs ONLY when grade.status == "pass". Failed/ungraded
units route to `_drafts/` and keep their composites for inspection.

## Image-text alignment (HARD drift gate, blocks publication)

Every `ImagePlaceholder` in any worksheet, manipulative, formative,
reflection, or certificate stage must populate **two** new fields:

- `keywords` — list of entities/objects that must be visually present in
  the image AND mentioned by the surrounding student-facing text.
- `text_image_alignment_check` — a sentence (≥40 chars) explaining which
  words in the surrounding text point to which visual elements.

If a `clipart_filename` is set, the validator additionally requires every
keyword to appear in the chosen clipart's `caption + tags` (see
`sample_assets/clipart/INDEX.json`). This catches "instructions say
squirrel but image shows fox."

Validation entry-point:

```python
from pipeline.image_alignment import validate_unit_alignment, report_for
issues = validate_unit_alignment(unit_dir)   # [] = clean
print(report_for(unit_dir))                  # pretty summary
```

The check is wired into `pipeline.rubric.pre_grade_drift_check` as the
**third** drift component (alongside `consistency_check` and
`verify_curriculum_text`). All three must return zero issues for the
RubricGrade schema to allow `status="pass"`. The rubric Part 2 also
flags any drift here as automatic Pedagogical Depth L1 — **double-
coverage so a misaligned image can never ship**.

When generating worksheets, the rule is: **for every image, write
`keywords` from the words your `student_instructions` actually use**
(not from your description of the image), then write
`text_image_alignment_check` showing how those words map to visual
elements. The validator's stemmer tolerates plurals / -ing / -ed forms
on both sides.

## Product-quality rubric (publication gate)

`assets/rubric_product_assessment.md` is the gold standard every unit must
clear. **Threshold: 17/20.** Below that, the deck is routed to a `_drafts`
subfolder rather than the public TCE shared folder.

The rubric has two parts:
1. **Original** (verbatim from the Concurrent Coders v3 Doc) — used for
   coding units.
2. **Non-coding extension rules** — concrete, non-interpretive checklists
   for math (and other future) units. Each level (1–4) is a closed set of
   checklist items; a unit earns a level only when every item is met.

When grading (the `rubric_grade` stage):
- Read `assets/rubric_product_assessment.md` first.
- For each criterion, walk the L1→L4 checklist top-down; stop at the highest
  level where every item is satisfied.
- Cite specific evidence from stage JSONs (e.g., `1_lesson_03.json::action.steps`)
  in `justification`.
- Sum to overall_score. Status = "pass" iff ≥ 17.
- If fail, populate `remediation[]` with which stages to regen for each
  criterion that needs lifting (see `pipeline/rubric.py::REMEDIATION_MAP`).

```python
from pipeline import rubric, manifest

# After regen, re-grade. To reset failed stages from a previous grade:
reset = manifest.mark_for_remediation(unit_dir)
# Returns the list of stages reset to pending. Then runner picks them up.
```

When you generate ANY new lesson/worksheet/etc., bias for the L4 descriptors
of the rubric — that's how you avoid expensive regen loops.

To re-fetch when Ontario revises the curriculum, run
`./venv/bin/python -m pipeline.curriculum_fetch`. Schema and coverage details
in `curriculum/README.md`.

## Where stuff lives

```
worksheet_generator/
├── canadian_classroom_content_batches.xlsx   ← input queue
├── assets/
│   └── rubric_product_assessment.md           ← gold-standard rubric (17/20 gate)
├── sample_assets/
│   └── clipart/                               ← shared clipart library (44+ images)
│       ├── INDEX.json                         ← catalogue (tags, captions, dims)
│       └── *.png
├── curriculum/                                ← Ontario MOE reference (cached)
│   ├── math.json                              ← G1-3 math (2020), 159 rows
│   ├── kindergarten.json                      ← K 2026, all 4 frames, 127 rows
│   ├── sources.json                           ← provenance per fetched course
│   ├── raw/                                   ← raw API responses (re-parsable)
│   └── README.md
├── pipeline/                                  ← orchestration helpers (no LLM)
│   ├── manifest.py                            ← state machine + mark_for_remediation
│   ├── stages.py
│   ├── curriculum.py                          ← read-only Ontario reference loader
│   ├── curriculum_fetch.py                    ← one-shot fetcher (re-runnable)
│   ├── rubric.py                              ← criteria, threshold, drift pre-gate
│   └── clipart.py                             ← read-only clipart catalogue
├── prompts/                                   ← stage prompt templates (built after Unit 1)
├── generated_units/batch_<N>/<unit_slug>/
│   ├── manifest.json                          ← state machine
│   ├── input_row.json                         ← frozen spreadsheet row
│   ├── run.log.jsonl                          ← every stage transition
│   ├── 0_blueprint.json
│   ├── 1_lesson_01.json … 1_lesson_05.json
│   ├── 2_worksheet_01.json … 2_worksheet_05.json
│   ├── 3_manipulatives.json
│   ├── 4_formative_reflection.json
│   ├── 5_assessment_suite.json
│   ├── 6_marketplace.json
│   ├── 7_rubric_grade.json                    ← publication gate (≥17/20)
│   └── unit.md                                ← assembled at end
└── CLAUDE.md                                  ← this file
```
