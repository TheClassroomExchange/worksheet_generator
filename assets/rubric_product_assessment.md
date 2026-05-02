# Product Assessment Rubric

This file is the authoritative source for the product-quality gate that
every unit deck must clear before being published to the TCE Drive folder.

**Threshold to publish: 17 / 20.**

The rubric has two parts:

1. **Original rubric (verbatim from Concurrent Coders v3 Doc)** — the gold
   standard the user shared on 2026-05-01. Coding-specific phrasing is kept
   intact for reference.
2. **Non-coding extension rules** — concrete, non-interpretive rules for
   applying the rubric to math (and other future) units where coding-specific
   L4 descriptors don't literally apply.

When grading any unit, **use the original rubric for coding units and apply
the extension rules for everything else**. The extension rules are
exhaustive — there is no judgement call left.

---

## Part 1 — Original rubric (verbatim, Concurrent Coders v3)

Source Doc:
`https://docs.google.com/document/d/1MI5zs1CuoCCi9fBH9fIqdQsmGgpETtpewLqFhQhhDTc/`
(captured 2026-05-01)

| Criterion | 1 — Needs Improvement | 2 — Satisfactory | 3 — Good | 4 — Excellent |
|---|---|---|---|---|
| **Pedagogical Depth & Material Quality** | Tasks are repetitive or too simple. Worksheets focus on rote memorization rather than logic or problem-solving. | Content covers the basics of coding. Worksheets are functional but lack variety in difficulty or "real-world" context. | High-quality content. Includes "Code Surgery" or debugging tasks. Worksheets require students to predict and analyze, not just copy. | Exceptional depth. Content scaffolds from simple logic to complex "concurrent" problem-solving. Worksheets include diverse challenges like "The Grand Festival" which require multi-step planning. |
| **Instructional Balance (Floor vs. Desk)** | Relies almost entirely on one mode (e.g., all worksheets). Lacks physical movement to ground the coding concepts. | Includes both floor and desk work, but the transition feels disconnected or jarring. | Good mix of "unplugged" floor movement and desk tasks. Physical activity prepares students for written work. | Masterful balance. Movement-based "Minds On" activities seamlessly bridge into complex paper-and-pencil "Action" tasks. |
| **Clarity & Communication** | Instructions are difficult to follow or missing key components like "Consolidation" tasks. | Instructions are generally clear but lack depth in teacher prompts or discussion hooks. | Well-detailed. Provides clear hooks, activities, and discussion questions for each of the 4+ days. | Professional & Comprehensive. Includes specific scripts/prompts for the teacher and clear, student-friendly language for all tasks. |
| **Alignment** | Does not explicitly reference the Ontario Curriculum or uses incorrect expectations. | References Ontario expectations (C3.1, C3.2, E1.5) but activities only loosely align. | Strong alignment. Activities directly teach sequential vs. concurrent events as required by Grade 2. | Perfect Alignment. Every activity and assessment is mapped to a specific Ontario expectation (e.g., C3.1, E1.5). |
| **Appearance** | Layout is cluttered. Lacks visual aids or consistent branding. Hard to navigate. | Layout is functional. Includes basic templates but lacks a cohesive or "finished" aesthetic. | Presentable and organized. Includes useful clip art and clear headings for each section. | Store-Ready Aesthetic. Features consistent branding, professional templates, and a scannable, "ready-to-print" layout. |

---

## Part 2 — Non-coding extension rules

Use these rules instead of the original L1–L4 descriptors **when the unit's
subject is anything other than coding**. They preserve the same five
criteria, the same 1–4 scale, and the same 17/20 threshold. Each rule is a
checklist; a unit earns a level only when every item at that level is met.

### Pedagogical Depth & Material Quality

**Score 1 — Needs Improvement.** Any one of:
- More than half the worksheet tasks are pure recall/copying.
- No worksheet asks the student to predict, extend, or justify.
- The unit has no error-finding ("what's wrong here?") activity.
- **Image-text drift in any worksheet part** — the part's
  `student_instructions` describes one entity but the chosen image
  depicts a different one (e.g., text says "help the squirrel" but
  the image shows a fox). Detected mechanically by
  `pipeline.image_alignment.validate_unit_alignment`. Any drift = L1.

**Score 2 — Satisfactory.** All of:
- At least one worksheet asks for prediction or extension.
- At least one open-construction task where the student generates an example.
- BUT no error-finding/repair task, OR no scaffolding from concrete to abstract.

**Score 3 — Good.** All of:
- At least one prediction/extension task across the unit.
- At least one error-finding/repair task (the math equivalent of "debugging" — e.g., "find the mistake in this number sentence and fix it").
- At least one open-construction task.
- The unit's lesson arc shows visible progression in cognitive demand from L1 to L5 (each lesson builds on the previous; not five interchangeable activities).

**Score 4 — Excellent.** All of L3, plus all of:
- The L5 (or final) lesson is an open-ended summative challenge with all four of: (a) multi-step planning where the student commits to a plan in writing **before** building, (b) **student self-checking** as a labelled action by the student themselves on their own work (not partner-only verification — e.g., "loop your core to show you can spot it", "fill in the missing element and check by counting"), (c) a **justification step** where the student explains their reasoning aloud or in writing, and (d) an explicit **revision opportunity** where the student is told to look for and fix at least one error in their own work after testing it.
- Across the five worksheets there are at least **four** distinct response types from the schema's `ResponseType` enum.
- The unit includes **both** a mid-unit formative gate (`4_formative_reflection.formative_worksheets`, ≥1 worksheet) **and** a unit-level reflection sheet (`4_formative_reflection.reflection_sheet`, ≥3 prompts).

### Instructional Balance (Floor vs. Desk)

**Score 1.** Any one of:
- Three or more lessons have no movement, manipulative, or partner-talk Minds On.
- The Action phase is paper-only in three or more lessons.

**Score 2.** All of:
- Every lesson has a Minds On with movement / manipulatives / partner-talk.
- BUT in at least two lessons the Minds On topic doesn't connect to the Action task that follows (jarring transition).

**Score 3.** All of:
- Every lesson has a Minds On of ≥ 5 minutes that uses movement, manipulatives, or partner-talk.
- Every lesson's Action phase includes at least one non-paper component (manipulatives, partner work, or movement).
- The Minds On in each lesson topically previews the Action.

**Score 4.** All of L3, plus:
- The unit explicitly progresses Concrete → Representational → Abstract (CRA) within or across lessons. Concrete = manipulatives/movement. Representational = drawing/symbols. Abstract = numbers/equations.
- At least one lesson uses an **explicit four-stage** plan-on-paper → test-with-manipulatives-or-movement → **refine-on-paper** → reflect cycle, where each of the four stages is a separately-numbered action step in the lesson JSON (not implicit). The "refine-on-paper" step must direct the student to return to their paper plan and revise it after the physical test, named explicitly in the step's instruction (e.g., "Phase 4 — Revise: go back to your worksheet and change one thing that didn't work when you tested it").

### Clarity & Communication

**Score 1.** Any one of:
- Two or more lessons lack a Consolidation phase.
- Teacher prompts are missing or generic ("discuss the activity") in three or more lessons.

**Score 2.** All of:
- Every lesson has Minds On / Action / Consolidation with timings.
- Every lesson has at least one teacher hook prompt verbatim.
- BUT teacher prompts in the Action phase are sparse (≤ 1 per lesson on average).

**Score 3.** All of:
- Every lesson has Minds On / Action / Consolidation with timings.
- Every lesson has a verbatim teacher hook in Minds On.
- Every lesson has ≥ 2 teacher prompts in Action.
- Every lesson has ≥ 2 consolidation discussion prompts.
- Every lesson has an "I can…" student learning goal.

**Score 4.** All of L3, plus:
- The unit includes at least one keystone lesson with a fully-scripted Detailed Action (`expanded_walkthrough` field) of ≥ 200 words.
- Every lesson includes ≥ 2 anticipated misconceptions with recovery moves (in `lesson.expanded_walkthrough.common_misconceptions` + `recovery_moves`, OR in `lesson.action.formative_check.what_to_look_for` + a paired remediation note).
- Every lesson has ≥ 3 specific Action-phase teacher prompts each with at least one expected student response (in any form Lesson schema permits).

### Alignment

**Score 1.** Any one of:
- A cited code is not in the local Ontario reference (`pipeline.curriculum.validate_codes` returns it as unknown).
- `5_assessment_suite.json` rubric covers fewer than half the cited expectations.
- Lesson `primary_expectations` cite codes that aren't in `0_blueprint.json::curriculum_codes`.

**Score 2.** All of:
- Every cited code exists in the local Ontario reference.
- BUT `expectation_text` in `0_blueprint.json` differs from official Ontario text (`pipeline.curriculum_reference.verify_curriculum_text` reports text drift).
- OR the rubric's `expectation_text` doesn't match the blueprint's.

**Score 3.** All of:
- Every cited code exists in the local Ontario reference.
- `expectation_text` in `0_blueprint.json` matches official Ontario text verbatim (whitespace-insensitive).
- `5_assessment_suite.json` summative rubric covers every cited expectation with grade-appropriate descriptors.
- BUT one or more cited expectations are not the primary focus of any lesson.

**Score 4.** All of L3, plus:
- Every cited expectation appears as `primary_expectations` in at least one lesson.
- Every lesson cites at least one primary expectation from the blueprint's `curriculum_codes`.
- `pipeline.schemas.consistency_check(unit_dir)` returns zero issues.
- `pipeline.curriculum_reference.verify_curriculum_text(unit_dir)` returns zero issues.

### Appearance

**Score 1.** Any one of:
- `pipeline.slides.validate_unit_for_slides(unit_dir)` returns ≥ 5 warnings.
- Marketplace listing has no `descriptive_title` or `short_description`.
- No certificate slide; no Terms of Use slide.

**Score 2.** All of:
- ≤ 4 layout warnings from `validate_unit_for_slides`.
- Marketplace fields populated.
- BUT no recurring character cast OR no consistent visual theme across worksheets.

**Score 3.** All of:
- ≤ 2 layout warnings from `validate_unit_for_slides`.
- Marketplace listing complete (title, short, long, target_buyer, pedagogical_approach).
- Recurring characters consistent across the unit (same names, same descriptions in `0_blueprint.json::recurring_characters`).
- Certificate slide present.
- Terms of Use slide present.

**Score 4.** All of L3, plus:
- `pipeline.slides.validate_unit_for_slides(unit_dir)` returns 0 warnings.
- `pipeline.density.report_cross_grade_density([unit])` returns no out-of-band warnings for this unit's grade.
- `pipeline.image_alignment.validate_unit_alignment(unit_dir)` returns 0 issues (every ImagePlaceholder has populated `keywords` + `text_image_alignment_check`; every keyword appears in the surrounding text AND in the chosen clipart's caption+tags).
- Canadian-context references appear in `0_blueprint.json::canadian_context_notes` (≥ 1) AND in `marketplace.long_description`.
- Marketplace `long_description` ≥ 1000 characters AND lists at least 3 differentiators ("What makes this unit different" or equivalent).
- The unit reuses recurring characters from a sibling-grade unit when one exists (e.g., G1 Pattern Parade reuses K Pattern Parade's Coco/Bea/Finn/Bibi/Moss cast — recognised by the visual_description matching).

---

## How to grade

1. Read the rubric (this file).
2. Determine subject. If "coding" or coding-adjacent → Part 1. Else → Part 2.
3. For each of the 5 criteria, walk the L1→L4 checklist top-down. Stop at the highest level where every checklist item is satisfied. That's the score.
4. Cite **specific evidence** from the unit's stage JSONs in the `justification` field for each criterion (file path + section).
5. Sum to overall_score (max 20). Status = "pass" iff ≥ 17.
6. If fail, list per-criterion remediation: which stages must regenerate to bring that criterion to ≥ the minimum needed for an overall 17.

The schema (`pipeline.schemas.RubricGrade`) enforces structure; the
rubric module (`pipeline.rubric`) enforces threshold and remediation routing.
