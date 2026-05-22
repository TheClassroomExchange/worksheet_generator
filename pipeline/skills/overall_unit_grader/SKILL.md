# Overall Unit Grader Skill — K-G3 (Math + Language)

## Why this exists

All 5 (lesson, worksheet) pairs in this unit have individually passed their pair_rubric_grader gate. Now you grade the **whole unit's arc**. Per-pair concerns (materials, voice, traps) are NOT your job — those are settled. Yours is whether the 5-day arc actually holds together pedagogically.

You apply the rubric below and emit a typed verdict that conforms to `pipeline.schemas.OverallUnitVerdict`. The Pydantic `model_validator` enforces the strict decision rule; verdicts that don't match their scores will be rejected.

## Inputs you receive

- `unit_dir/0_blueprint.json` — the blueprint
- `unit_dir/1_lesson_01.json` through `1_lesson_05.json` — all 5 lessons
- `unit_dir/2_worksheet_01.json` through `2_worksheet_05.json` — all 5 worksheets
- `unit_dir/3_manipulatives.json`, `5_assessment_suite.json` — supporting stages
- `unit_dir/pair_NN_verdict.json` for NN in 01..05 — per-pair gate verdicts (FYI, all pass)
- The unit's `subject` field is in `0_blueprint.json` — `"Mathematics"` or `"Language"`. Score `mathematical_authenticity` for Math, `sor_alignment` for Language; leave the other null.

## Output

Write `unit_dir/overall_unit_verdict.json` conforming to `OverallUnitVerdict`. No prose outside the JSON.

## The rubric — 9 or 10 categories scored 1–4

### Foundational four (MUST each score 4 to pass)

These re-aggregate the per-pair scores at the unit level. If a pair gate let something slide that the WHOLE-UNIT view exposes (e.g., character voice that's consistent within each lesson but drifts across the 5-day arc), this is where you catch it.

**1. PEDAGOGICAL_DEPTH (4 required)** — across all 5 lessons, are the named traps real and specific, with concrete recovery moves? At least one expanded_walkthrough should reach Level 4 (research-cited).

**2. ALIGNMENT (4 required)** — does the unit cover every code in `curriculum_codes` with named lesson activities, AND does the lesson_arc match the blueprint's progression? Verbatim expectation text byte-identical to the curriculum source throughout.

**3. INSTRUCTIONAL_BALANCE (4 required)** — across all 5 lessons + capstone, every required material is everyday classroom items. Puppets always optional. At least one lesson offers a no-paper variant. No specialty kits anywhere.

**4. CLARITY_VOICE (4 required)** — recurring characters anchor every minds_on and consolidation across all 5 days with consistent voice. The unit refrain (if any) appears in every lesson. Vocabulary defined child-friendly throughout.

### Arc-level (at most ONE may score 3; rest must be 4)

**5. ARC_COHERENCE** — does Day N pedagogically build on Day N-1?
*Math example (Level 4):* Day 1 segments (decompose), Day 2 maps representations, Day 3 composes (reverses Day 1's decomposition using Day 2's mappings), Day 4 applies in connected problems, Day 5 capstone integrates. Sequence aligns with research (Carpenter–Moser CGI for addition/subtraction, Empson for fractions, Battista for spatial).
*Language example (Level 4):* Day 1 PA → Day 2 letter-sound → Day 3 blending → Day 4 connected text → Day 5 capstone. Each day named explicitly as building on the previous.

**6. CODE_COVERAGE** — is every `curriculum_codes` entry addressed by a *named lesson activity*, not just mentioned in the title?
*Pass condition:* Every code shows up in at least one lesson's `primary_expectations` AND has an action-stage activity that targets it.

**7. CAPSTONE_INTEGRATION** — does Lesson 5 genuinely revisit Lessons 1–4?
*Level 4:* Lesson 5 has 4 stations explicitly mirroring Days 1, 2, 3, 4 each with a named skill from that day. Capstone template records evidence per station.

**8. VOCABULARY_PROGRESSION** — does threaded_vocabulary build cumulatively?
*Pass condition:* Each term in `threaded_vocabulary` is introduced on the day where its corresponding skill is taught, used in subsequent days, and not introduced before its underlying skill exists. Day 5 capstone uses unit vocabulary without re-defining.

**9. CHARACTER_CONTINUITY** — do recurring characters anchor every minds_on AND consolidation across all 5 days with consistent voice?
*Pass condition:* Each `recurring_character.role` description matches that character's actual presence across lessons. No character in the blueprint is missing from the lessons listed in `role`. The character's voice (mannerisms, refrain) is recognizable on every appearance.

**10. SUBJECT-SPECIFIC** (set ONE of):
- **`mathematical_authenticity`** (Math units) — across the unit, math is taught conceptually with progression: counting → cardinality → composition; equality as equivalence not action; place value as composing units; fractions as equal shares. Manipulatives carry meaning across days, not just decoration.
- **`sor_alignment`** (Language units) — across the unit, slash phoneme notation throughout, no three-cueing, sequence aligns with SoR consensus path.

## Decision rule (Pydantic-enforced)

```
PASS condition (ALL THREE must be true):
  • All 4 foundational categories score exactly 4
  • At most ONE arc-level/subject category scores 3
  • Zero arc-level/subject scores below 3
```

If `status = "pass"` doesn't match the scores, Pydantic rejects the verdict.

When status is `"revise"`:
- For every below-target category, emit a `CategoryFeedback` with concrete `specific_evidence` + `required_fix`.
- Set `pairs_to_revise` to the pair numbers that need rework. The pipeline will re-run those pair gates after the model fixes them.
- After all flagged pairs are revised AND their pair gates re-pass, the overall gate re-runs.

## Tone

Senior K-3 curriculum coach reviewing the entire unit before it ships to teachers. Catch the cross-lesson drift the per-pair gates couldn't see. Be specific about which lesson(s) to revise.
