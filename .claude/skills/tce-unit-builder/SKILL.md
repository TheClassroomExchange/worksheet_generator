---
name: TCE Unit Builder
description: |
  Use when the user wants to build, resume, or continue work on a TCE (The Canadian Classroom Exchange) curriculum unit — Pattern Parade, the K-G3 Math programme, or any related K-3 Ontario unit. Triggers on phrases like "continue the unit", "next stage", "next unit", "continue the math programme", "resume the worksheet generator", "pick up where you left off", "generate the next stage", "work on the units", or when invoked from a scheduled cron task. Also triggers on "make a new unit" if the project context is TCE / worksheet generator.
---

# TCE Unit Builder

You are continuing work on the TCE Worksheet Generator pipeline. The project runbook is at
`CLAUDE.md` (project root) and the operator-facing documentation is at `README.md`. Read both
if you have not already this session.

## Your job

Pick up the pipeline where the last session left off and make as much progress as possible
before the session budget runs out. The pipeline produces curriculum-aligned K-3 Ontario units,
each with 17 schema-validated stages, ~76 composed PNG images, and a portrait Google Slides
deck.

## Cardinal rules

1. **Read `CLAUDE.md` first.** It documents the architecture, schemas, fonts, layout
   decisions, drift gates, the publication gate, and the resumption protocol.
2. **Claude is the runner. Python is plumbing.** Do not reintroduce `anthropic` SDK calls.
   Generate JSON content via the Write tool, validate via `complete_stage()`.
3. **Every transition is checkpointed.** If you crash mid-stage, the next session resumes
   via the manifest. Schema validation is the gate.
4. **Never block the batch.** If a stage fails, mark it failed (auto-handled by
   `complete_stage`) and move to the next pending stage in any other unit.
5. **All shell commands assume the project root is the current working directory.**
   The skill never hardcodes user-specific absolute paths.

## Session start protocol (do this every time)

1. **Multi-unit programme status — RUN THIS FIRST.** The project executes a 40-unit K-G3
   Math programme. The plan, status per unit, and "next-up" logic live in
   `pipeline/unit_plan.py`. Always refresh from disk:
   ```bash
   ./venv/bin/python -c "
   from pipeline import unit_plan, manifest
   from pathlib import Path
   unit_plan.refresh_state_from_disk()
   print(unit_plan.status_table())
   nxt = unit_plan.next_unit_to_generate()
   if nxt:
       ud = Path('generated_units') / nxt.batch / nxt.unit_id
       try:
           m = manifest.load(ud); ns = manifest.next_pending(m)
       except FileNotFoundError:
           ns = '(unit not initialised; call unit_plan.init_unit_from_plan(nxt))'
       print(f'\\nNEXT UNIT:  {nxt.unit_id}  ({nxt.grade}, anchor {nxt.anchor_code})')
       print(f'NEXT STAGE: {ns}')
   else:
       print('\\nProgramme complete — all 40 units shipped.')
   "
   ```

2. Print the runbook reminder:
   ```bash
   cat CLAUDE.md
   ```

3. Print the status table for all batches AND the curriculum/density audits:
   ```python
   from pathlib import Path
   from pipeline.manifest import status_table, list_failed
   from pipeline.curriculum_reference import report_reference_status
   from pipeline.density import report_cross_grade_density

   for batch in ['batch_1', 'batch_2', 'batch_3']:
       bd = Path('generated_units') / batch
       if bd.exists():
           print(f'\n=== {batch} ===')
           print(status_table(bd))

   # Reference status (verified / best_effort / needs_human per grade)
   print('\n=== Curriculum reference status ===')
   for line in report_reference_status(): print(line)

   # Cross-grade density audit so the differentiation rule is visible.
   units = []
   for batch in ['batch_1', 'batch_2', 'batch_3']:
       bd = Path('generated_units') / batch
       if bd.exists():
           units.extend(u for u in sorted(bd.iterdir()) if (u/'0_blueprint.json').exists())
   print('\n=== Cross-grade density ===')
   for line in report_cross_grade_density(units): print(line)
   ```

4. Decide what to work on:
   - **If failed stages exist:** address them first via `retry_failed(unit_dir, stage_key=...)` then regenerate
   - **Otherwise:** find the next pending stage of the next pending unit

5. Generate that stage following the patterns from
   `generated_units/batch_1/k_patterns_pattern_parade/` (the canonical reference unit).

6. **Treat curriculum advisory as gating for paid units.** If
   `verify_curriculum_text(unit_dir)` reports `needs_human` for the blueprint's grade, escalate
   to the user before generating downstream stages.

## How to generate a new stage

### Stage 0: Blueprint
Read `input_row.json`. Generate the unit blueprint matching the `Blueprint` Pydantic schema.
Reuse the Pattern Parade narrative (Coco the Conductor + Bea/Finn/Bibi/Moss) for grade 1-3
Pattern Parade units. Adjust:
- `curriculum_codes` to the grade-appropriate Ontario codes (G1/2/3 = C1.1–C1.4)
- `curriculum_expectations` text from the official Ontario curriculum (verbatim — use
  `pipeline.curriculum.get(grade, code)['text']`)
- Lesson arc complexity (more sophisticated patterns at higher grades)
- `grade` field

### Stages 1.N: Lesson plans
Match the `LessonPlan` schema. Pay attention to grade-level differentiation — calibrated bands
enforced (non-blocking) by `pipeline/density.py`:

| Grade | minds_on teacher_script chars | Action steps | Consolidation prompts |
|---|---|---|---|
| Kindergarten | 500–1100 | 3–5 | 2–4 |
| Grade 1 | 700–1300 | 4–5 | 2–4 |
| Grade 2 | 850–1400 | 4–6 | 3–4 |
| Grade 3 | 1000–1600 | 5–7 | 3–5 |

`complete_stage()` automatically prints density warnings for any lesson outside its grade's
band. Aim for the middle of each band.

The `_lesson_section_summary()` function in `pipeline/slides.py` shows ALL action steps and
ALL consolidation prompts. Lesson slides dynamically size each section's body height from
content via `_est_lines`. The pre-flight check (`validate_unit_for_slides`) warns at 6+ steps
or 5+ prompts because those compress the layout.

**For the keystone lesson (typically L3), include `expanded_walkthrough`** with full teacher
script, expected student responses, common misconceptions, and recovery moves. For G1+ Pattern
Parade, the L5 number-translation reveal often warrants a second `expanded_walkthrough`.

Required fields in every lesson:
- `lesson_number`, `lesson_title`, `duration_minutes`
- `primary_expectations`, `secondary_expectations`
- `big_idea`, `learning_intention` (starts with "We are learning"),
  `student_learning_goal` (starts with "I can"), `success_criteria` (each starts with "I can")
- `vocabulary_introduced`, `vocabulary_reinforced`, `manipulatives_used` (from blueprint),
  `lesson_specific_materials`
- `minds_on` (with `teacher_script` ≥ 120 chars), `action`, `consolidation`,
  `assessment_in_this_lesson`
- `expanded_walkthrough`: only on the keystone lesson per unit; `null` for others
- `worksheet_brief`: title, purpose, 3 parts with response_types

### Stages 2.N: Worksheets
Match the `Worksheet` schema. Title in playful voice. 3 parts referenced in `worksheet_brief`.
Image placeholders prefixed `WS<NN>_`. Use the same character set (Bea, Finn, Bibi, Moss) and
parade strip metaphor — at higher grades, add number/symbol overlays. Every `ImagePlaceholder`
must populate `keywords` and `text_image_alignment_check` (drift gate enforces this).

### Stage 3: Manipulatives
For grades 1-3 Pattern Parade, REUSE M1-M6 + char_coco_puppet from the K unit. Higher grades
may need ADDITIONAL manipulatives (e.g., M7_number_strip for G2). If you add new ones, also
extend `compose_pattern_parade_image()` in `pipeline/compose.py` and add the SVG to
`sample_assets/`. Use `clipart.suggest_for_unit()` (LRU rotation) for new clipart picks and
record chosen filenames in `Manipulative.clipart_files`.

### Stage 4: Formative + reflection
Mid-unit formative (after the keystone lesson) + end-of-unit reflection sheet.

### Stage 5: Assessment suite
Diagnostic tracker (L1) + 3 formative trackers (L2/3/4) + summative rubric (4 expectations × 4
levels) + summative task script + Junior Pattern Conductor certificate.

The summative rubric levels should reflect grade-level expectations. The `SHORT_LEVEL` and
`SHORT_EXP` curated dictionaries in `pipeline/slides.py` cover K (A7.x) and G1/G2/G3 (C1.x)
with grade-specific overrides:
- **Default keys**: `(code, level)` — generic fallback for any grade.
- **Override keys**: `(grade, code, level)` — preferred when a code means meaningfully
  different things at different grades.

Lookup precedence is `(grade, code, level) → (code, level) → first-sentence fallback`.

**Tracker-column rule:** the columns you write in
`lesson.action.formative_check.tracker_columns` MUST exactly match the
`assessment_suite.formative_tracker_lesson_NN.columns` for the same lesson. The consistency
check enforces this.

### Stage 6: Marketplace
Listing block. `classroom_time_total_minutes` MUST equal sum of lesson durations (consistency
check enforces this).

### Stage 7: Rubric grade (publication gate)
Read `assets/rubric_product_assessment.md`. For each criterion, walk the L1→L4 checklist
top-down; stop at the highest level where every item is satisfied. Cite specific evidence from
stage JSONs (e.g., `1_lesson_03.json::action.steps`) in `justification`. Sum to overall_score.
Status = "pass" iff ≥ 17. If fail, populate `remediation[]` with which stages to regen.

The schema rejects `status="pass"` if any of the three hard drift gates
(`consistency_check`, `verify_curriculum_text`, `validate_unit_alignment`) has issues.

## After a unit's rubric_grade stage passes

```python
from pathlib import Path
from pipeline.compose import compose_for_unit
from pipeline.render import render_unit
from pipeline.slides import build_unit_deck, validate_unit_for_slides

unit_dir = Path('generated_units/batch_<N>/<unit_slug>')

# 1. Pre-flight slide-layout check (warns about content that will overflow).
warns = validate_unit_for_slides(unit_dir)
for w in warns:
    print(f'  ⚠ {w}')

# 2. Compose all images
compose_for_unit(unit_dir)

# 3. Render unit.md
md = render_unit(unit_dir)
(unit_dir / 'unit.md').write_text(md, encoding='utf-8')

# 4. Build the Slides deck. Routes to per-unit Drive folder if grade.status == "pass",
#    or to _drafts/<unit>/ otherwise.
url = build_unit_deck(unit_dir)
print(f'\n✓ Deck: {url}')
```

Then **mandatory** visual inspection — render every page and Read each one:

```python
from pipeline.slides import render_validation_pages, VISUAL_INSPECTION_CHECKLIST

pages = render_validation_pages(unit_dir, dpi=150)
# Read every PNG in `pages` (Claude's Read tool) and walk
# VISUAL_INSPECTION_CHECKLIST per slide-type. The deck does NOT ship until
# every checkbox passes.
```

**Critical slides to inspect:**
- **slide-01 (cover):** title shows the right grade and the subtitle box is not split by a border.
- **slide-02 (overview):** title does not overlap the Grade/Strand line; the lesson-arc table fits.
- **slide-03 to slide-07 (lessons):** sections (Minds On / Action / Consolidation) flow without dead-air gaps; ALL action steps and ALL discussion prompts are visible.
- **slide-08 to slide-12 (worksheets):** hero image renders (not a grey placeholder); instructions readable; title not overlapping the Learning Goal box.
- **slide-20 (rubric):** descriptors are short — if they are full first sentences you forgot to extend the SHORT_LEVEL dict.
- **slide-21 (certificate):** dashed border, Coco bottom-right, all skill bullets visible, achievement_text not overlapping skills header.
- **slide-22 (marketplace):** all 12 inclusions visible.

Compare against the K reference at
`generated_units/batch_1/k_patterns_pattern_parade/` for any layout doubt.

## End-of-session protocol

Before responding to the user, always run the status table so the chat closes with a clear
"next pickup":

```python
from pathlib import Path
from pipeline.manifest import status_table
for batch in ['batch_1', 'batch_2', 'batch_3']:
    bd = Path('generated_units') / batch
    if bd.exists():
        print(f'=== {batch} ==='); print(status_table(bd))
```

## When everything is broken

- Venv path is broken → `rm -rf venv && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt`
- Token expired → the OAuth flow refreshes automatically via `pipeline.slides.get_credentials()`. If refresh fails, delete `token.json` and the next run triggers a browser auth flow (user must click through).
- Schema validation rejecting valid-looking content → the schema in `pipeline/schemas.py` is the source of truth. If the schema is wrong, update it carefully and re-run. Do NOT bypass with `skip_validation=True` for production stages.

## Where the canonical reference unit lives

`generated_units/batch_1/k_patterns_pattern_parade/` (relative to project root).

When generating a new unit, refer to this folder's JSON files for the exact shape and content
density expected. Do NOT copy verbatim — the new unit needs its own grade-appropriate content.
But the structure and field expectations should match.
