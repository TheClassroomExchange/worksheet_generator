"""
Pydantic schemas for every stage output.

Every stage's JSON file MUST validate against the corresponding model before
it can be marked `done`. This eliminates ambiguity between Claude sessions:
the next session reading these files cannot misinterpret structure.

Cross-stage references (e.g. a Lesson's manipulative IDs must exist in the
Blueprint's manipulatives_index) are checked by `consistency_check()`.

Adding a new stage:
  1. Define the model below.
  2. Register it in STAGE_MODELS.
  3. Use `validate_stage_file(unit_dir, stage_key)` before mark(..., 'done').
"""

from __future__ import annotations
from pathlib import Path
from typing import Literal
import json

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# ── Shared atoms ─────────────────────────────────────────────────────────────

class _Strict(BaseModel):
    """Reject extra fields — catches typos and drift between sessions."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CharacterRef(_Strict):
    name: str
    role: str
    visual_description: str


class VocabTerm(_Strict):
    term: str
    child_friendly_definition: str


class Manipulative(_Strict):
    id: str = Field(pattern=r"^M\d+_[a-z0-9_]+$",
                    description="Manipulative ID, e.g. 'M1_animal_cards'")
    name: str
    description: str
    used_in_lessons: list[int] = Field(min_length=1)
    clipart_files: list[str] = Field(
        default_factory=list,
        description="Filenames (not paths) from sample_assets/clipart/INDEX.json "
                    "that this manipulative incorporates. Used by "
                    "pipeline.clipart.usage_stats() to drive LRU rotation when "
                    "future blueprints pick clipart. Empty list is fine for "
                    "manipulatives that use only hand-authored SVG assets.")


class LessonArcEntry(_Strict):
    lesson_number: int = Field(ge=1)
    lesson_title: str
    primary_expectations: list[str] = Field(min_length=1)
    secondary_expectations: list[str] = Field(default_factory=list)
    big_idea: str
    student_learning_goal: str = Field(
        description="Child-voice 'I can...' statement."
    )
    one_line_summary: str

    @field_validator("student_learning_goal")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal must start with 'I can'")
        return v


class AssessmentStrategy(_Strict):
    diagnostic: str
    formative: str
    summative: str


# ── Stage 0: Blueprint ──────────────────────────────────────────────────────

class Blueprint(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str = Field(pattern=r"^[a-z0-9_]+$")
    thematic_title: str
    descriptive_title: str
    grade: str
    subject: str
    strand: str
    curriculum_source_url: str = Field(pattern=r"^https?://")
    curriculum_codes: list[str] = Field(min_length=1)
    curriculum_expectations: dict[str, str]
    duration_days: int = Field(ge=3, le=10)
    unit_overview: str = Field(min_length=80)
    unit_learning_goal: str
    lesson_arc: list[LessonArcEntry] = Field(min_length=3)
    expectation_lesson_map: dict[str, list[int]]
    recurring_characters: list[CharacterRef] = Field(min_length=1)
    threaded_vocabulary: list[VocabTerm] = Field(min_length=2)
    manipulatives_index: list[Manipulative] = Field(min_length=1)
    materials_overview: list[str] = Field(min_length=1)
    assessment_strategy: AssessmentStrategy
    pedagogical_notes: list[str] = Field(min_length=1)
    canadian_context_notes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _internal_consistency(self) -> "Blueprint":
        # All curriculum_expectations keys must be in curriculum_codes.
        if set(self.curriculum_expectations.keys()) != set(self.curriculum_codes):
            raise ValueError(
                "curriculum_expectations keys must match curriculum_codes exactly"
            )
        # expectation_lesson_map keys must be in curriculum_codes.
        if not set(self.expectation_lesson_map.keys()).issubset(set(self.curriculum_codes)):
            raise ValueError(
                "expectation_lesson_map keys must be a subset of curriculum_codes"
            )
        # lesson_arc length must equal duration_days.
        if len(self.lesson_arc) != self.duration_days:
            raise ValueError(
                f"lesson_arc has {len(self.lesson_arc)} entries but duration_days={self.duration_days}"
            )
        # lesson_arc lesson_numbers must be 1..N consecutive.
        nums = [e.lesson_number for e in self.lesson_arc]
        if nums != list(range(1, len(nums) + 1)):
            raise ValueError("lesson_arc lesson_numbers must be 1..N consecutive")
        # Every primary/secondary expectation in lesson_arc must be a curriculum_code.
        for entry in self.lesson_arc:
            for code in entry.primary_expectations + entry.secondary_expectations:
                if code not in self.curriculum_codes:
                    raise ValueError(
                        f"lesson {entry.lesson_number} references unknown expectation {code!r}"
                    )
        return self


# ── Stage 1.N: Lesson plan ──────────────────────────────────────────────────

class TeacherStep(_Strict):
    step_number: int = Field(ge=1)
    instruction: str
    teacher_prompt: str


class Differentiation(_Strict):
    for_emerging: str
    for_extending: str
    for_ell_or_iep: str
    for_movement_learners: str


class FormativeCheck(_Strict):
    what_to_look_for: str
    how_to_record: str
    tracker_columns: list[str] = Field(min_length=2)


class MindsOnSection(_Strict):
    duration_minutes: int = Field(ge=5, le=20)
    activity_name: str
    hook: str
    teacher_script: str = Field(min_length=120,
                                description="Full script. No '[discuss]' placeholders.")
    student_actions: list[str] = Field(min_length=1)


class ActionSection(_Strict):
    duration_minutes: int = Field(ge=10, le=40)
    activity_name: str
    structure: Literal[
        "whole_group", "partner", "small_group", "centres",
        "whole_group_then_partner", "whole_group_then_centres", "individual"
    ]
    steps: list[TeacherStep] = Field(min_length=2)
    differentiation: Differentiation
    formative_check: FormativeCheck


class ConsolidationSection(_Strict):
    duration_minutes: int = Field(ge=5, le=15)
    activity_name: str
    discussion_prompts: list[str] = Field(min_length=1)
    exit_routine: str


class AssessmentInLesson(_Strict):
    type: Literal["diagnostic", "formative", "summative", "observational"]
    evidence_collected: str
    tracker_reference: str
    rationale: str


class ExpandedWalkthrough(_Strict):
    """Optional deep-dive script for a keystone lesson (cf. example PDF p.10)."""
    title: str
    rationale: str = Field(description="Why this lesson warrants extra scripting.")
    setup: str
    teacher_script: str = Field(min_length=200)
    expected_student_responses: list[str] = Field(min_length=1)
    common_misconceptions: list[str] = Field(min_length=1)
    recovery_moves: list[str] = Field(min_length=1)


ResponseType = Literal[
    "draw_or_sticker", "circle_or_loop", "create", "create_and_loop",
    "match", "cut_and_sort", "circle_yes_no", "self_rate", "write",
    "draw_or_write"
]


class WorksheetBriefPart(_Strict):
    part_number: int = Field(ge=1)
    task: str
    response_type: ResponseType


class WorksheetBrief(_Strict):
    worksheet_title: str
    purpose: str
    parts_outline: list[WorksheetBriefPart] = Field(min_length=1)
    expected_image_assets: list[str] = Field(min_length=1)


class LessonPlan(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    lesson_number: int = Field(ge=1)
    lesson_title: str
    duration_minutes: int = Field(ge=20, le=60)
    primary_expectations: list[str] = Field(min_length=1)
    secondary_expectations: list[str] = Field(default_factory=list)
    big_idea: str
    learning_intention: str = Field(
        description="Teacher voice. 'We are learning to...'"
    )
    student_learning_goal: str = Field(
        description="Child voice. 'I can...'"
    )
    success_criteria: list[str] = Field(min_length=2)
    vocabulary_introduced: list[str] = Field(default_factory=list)
    vocabulary_reinforced: list[str] = Field(default_factory=list)
    manipulatives_used: list[str] = Field(min_length=1,
        description="Must reference IDs from Blueprint.manipulatives_index"
    )
    lesson_specific_materials: list[str] = Field(default_factory=list)
    minds_on: MindsOnSection
    action: ActionSection
    consolidation: ConsolidationSection
    assessment_in_this_lesson: AssessmentInLesson
    expanded_walkthrough: ExpandedWalkthrough | None = None
    worksheet_brief: WorksheetBrief

    @field_validator("student_learning_goal")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal must start with 'I can'")
        return v

    @field_validator("learning_intention")
    @classmethod
    def _teacher_voice(cls, v: str) -> str:
        if not v.lower().startswith("we are learning"):
            raise ValueError("learning_intention must start with 'We are learning'")
        return v

    @field_validator("success_criteria")
    @classmethod
    def _success_child_voice(cls, v: list[str]) -> list[str]:
        for s in v:
            if not s.lower().startswith("i can"):
                raise ValueError(f"success criterion must start with 'I can': {s!r}")
        return v

    @field_validator("manipulatives_used")
    @classmethod
    def _manip_id_shape(cls, v: list[str]) -> list[str]:
        import re
        for mid in v:
            if not re.match(r"^M\d+_[a-z0-9_]+$", mid):
                raise ValueError(f"bad manipulative id shape: {mid!r}")
        return v


# ── Stage 2.N: Student worksheet ────────────────────────────────────────────

ImageSize = Literal[
    "thumbnail",      # ~1in / icon
    "small",          # ~2in
    "medium",         # ~3.5in
    "large",          # ~5in
    "full_width",     # spans the page (~7-8in)
]


class ImagePlaceholder(_Strict):
    """A specific image to be generated/composed in the worksheet/deck.

    Per-stage prefix conventions (enforced by consistency_check):
      • Worksheet images: WS<NN>_…  (e.g. WS01_P1_PARADE)
      • Manipulative images: M<N>_…  (e.g. M1_BEA_CARD)
      • Recurring-character images: CHAR_…  (e.g. CHAR_COCO_FRONT)

    Image-text alignment (enforced by validate_unit_alignment):
      • ``keywords`` — entities/objects that MUST be visually present in
        the image AND mentioned by the surrounding text. The validator
        cross-checks both directions: image keyword must appear in
        student_instructions/visual_layout, AND must appear in the chosen
        clipart's caption+tags (if a clipart asset was chosen).
      • ``text_image_alignment_check`` — Claude's per-image self-check
        explaining WHY this image matches the surrounding text, citing
        which words point to which visual elements.
      • ``clipart_filename`` — if pulled from sample_assets/clipart/INDEX.json,
        record the filename here so usage tracking + alignment checks work.
    """
    id: str = Field(pattern=r"^[A-Z][A-Z0-9_]+$",
                    description="Image ID in UPPER_SNAKE_CASE; per-stage prefixes enforced by consistency_check.")
    description: str = Field(min_length=20,
                             description="Precise description for image generation: subject, style, size, layout context.")
    placement: str = Field(description="Where on the page this image sits, e.g. 'top-right of header', 'spans Part 1 fully'.")
    approximate_size: ImageSize
    keywords: list[str] = Field(
        default_factory=list,
        description="Entities/objects that must be visually present in the image "
                    "AND named in the surrounding text. The image-text alignment "
                    "validator cross-references these against the part's "
                    "student_instructions and (when applicable) the chosen "
                    "clipart's caption+tags. Empty list is allowed at parse time "
                    "but BLOCKS the rubric grade gate.")
    text_image_alignment_check: str = Field(
        default="",
        description="Per-image self-check: which words in the surrounding text "
                    "point to which visual elements in this image. Empty string "
                    "is allowed at parse time but BLOCKS the rubric grade gate. "
                    "The drift pre-gate inspects this field directly.")
    clipart_filename: str | None = Field(
        default=None,
        description="If this image is sourced from sample_assets/clipart/INDEX.json, "
                    "the filename (e.g. 'slide06_animals_03.png'). Used by "
                    "pipeline.clipart.usage_stats() and the alignment validator. "
                    "None means the image is hand-authored or composed from SVG.")


class WorksheetPart(_Strict):
    part_number: int = Field(ge=1)
    part_title: str
    student_instructions: str = Field(
        min_length=10,
        description="Instructions printed on the worksheet for the student. Child voice, short, declarative.",
    )
    visual_layout: str = Field(
        min_length=20,
        description="Describes how the part is laid out on the page, e.g. 'parade strip horizontally centered, 5 cells, last cell with dotted outline'.",
    )
    image_placeholders: list[ImagePlaceholder] = Field(default_factory=list)
    student_response_type: ResponseType
    answer_key: str = Field(description="Correct answer(s) for teacher reference.")


class WorksheetHeader(_Strict):
    student_name_field: bool = True
    date_field: bool = True
    student_learning_goal_banner: str = Field(
        description="Child voice, 'I can...' phrasing, shown at the top of the worksheet."
    )
    character_watermark: str | None = Field(
        default=None,
        description="Optional: which recurring character appears in the header, and where."
    )

    @field_validator("student_learning_goal_banner")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal_banner must start with 'I can'")
        return v


class WorksheetPage(_Strict):
    page_number: int = Field(ge=1)
    parts: list[WorksheetPart] = Field(min_length=1)


class Worksheet(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    lesson_number: int = Field(ge=1)
    worksheet_title: str
    purpose: str = Field(min_length=20)
    student_learning_goal: str = Field(description="Child voice 'I can...'")
    header: WorksheetHeader
    pages: list[WorksheetPage] = Field(min_length=1)
    early_finisher_prompt: str | None = None
    teacher_notes: str = Field(
        min_length=20,
        description="Brief notes for the teacher: when to give this worksheet, what to look for, common pitfalls.",
    )

    @field_validator("student_learning_goal")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal must start with 'I can'")
        return v


# ── Stage 3: Manipulatives (printable teacher props) ────────────────────────

PageSize = Literal["letter", "tabloid"]
PageOrientation = Literal["portrait", "landscape"]
PageColor = Literal["bw", "color", "bw_or_color"]


class PrintSpec(_Strict):
    page_size: PageSize
    orientation: PageOrientation
    color: PageColor
    pages_per_set: int = Field(ge=1, le=20)
    laminate_recommended: bool


AssetCategory = Literal["manipulative", "character_puppet"]


class ManipulativeAsset(_Strict):
    asset_id: str = Field(
        pattern=r"^(M\d+_[a-z0-9_]+|char_[a-z0-9_]+)$",
        description="Either a manipulative id (M1_animal_cards) or a character id (char_coco_puppet).",
    )
    name: str
    category: AssetCategory
    purpose: str = Field(min_length=20)
    page_layout: str = Field(min_length=20,
        description="How the asset is laid out for printing, e.g. '8 cards per letter page in a 2x4 grid'.")
    print_specifications: PrintSpec
    image_placeholders: list[ImagePlaceholder] = Field(min_length=1)
    teacher_prep_steps: list[str] = Field(min_length=2)
    estimated_prep_minutes: int = Field(ge=1, le=60)
    quantity_per_class: str = Field(
        description="How many copies/sets a typical class of 20 needs.")
    used_in_lessons: list[int] = Field(min_length=1)


class Manipulatives(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    assets: list[ManipulativeAsset] = Field(min_length=1)
    overall_prep_notes: str = Field(
        min_length=30,
        description="One-paragraph summary for teachers: total prep time, when to prep, storage tips.")


# ── Stage 4: Formative + reflection sheets ──────────────────────────────────

class FormativePrompt(_Strict):
    prompt_number: int = Field(ge=1)
    prompt: str = Field(min_length=10,
        description="Student-facing prompt printed on the worksheet.")
    visual_layout: str = Field(min_length=20)
    image_placeholders: list[ImagePlaceholder] = Field(default_factory=list)
    response_type: ResponseType
    answer_key: str


class FormativeWorksheet(_Strict):
    title: str
    when_to_use: str = Field(
        min_length=10,
        description="When to administer, e.g. 'After Lesson 3, before Lesson 4'.")
    purpose: str = Field(min_length=20)
    expectations_assessed: list[str] = Field(min_length=1)
    student_learning_goal: str = Field(description="Child voice 'I can...'")
    header: WorksheetHeader
    prompts: list[FormativePrompt] = Field(min_length=2)
    teacher_notes: str = Field(min_length=20)

    @field_validator("student_learning_goal")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal must start with 'I can'")
        return v


class ReflectionPrompt(_Strict):
    prompt_number: int = Field(ge=1)
    prompt: str = Field(min_length=5)
    visual_layout: str = Field(min_length=15)
    image_placeholders: list[ImagePlaceholder] = Field(default_factory=list)
    response_type: ResponseType
    options: list[str] | None = Field(
        default=None,
        description="For self_rate or circle_yes_no: the labels children choose between.")


class ReflectionSheet(_Strict):
    title: str
    purpose: str = Field(min_length=20)
    student_learning_goal: str
    header: WorksheetHeader
    prompts: list[ReflectionPrompt] = Field(min_length=2)
    teacher_notes: str = Field(min_length=20)

    @field_validator("student_learning_goal")
    @classmethod
    def _child_voice(cls, v: str) -> str:
        if not v.lower().startswith("i can"):
            raise ValueError("student_learning_goal must start with 'I can'")
        return v


class FormativeReflection(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    formative_worksheets: list[FormativeWorksheet] = Field(min_length=1)
    reflection_sheet: ReflectionSheet


# ── Stage 5: Assessment suite (trackers + rubric + summative + certificate) ─

class ClassTracker(_Strict):
    tracker_id: str = Field(
        pattern=r"^(diagnostic_tracker|formative_tracker_lesson_\d{2})$",
        description="Stable id referenced by lessons via assessment_in_this_lesson.tracker_reference.",
    )
    title: str
    when_used: str = Field(min_length=10)
    expectation_focus: list[str] = Field(min_length=1)
    columns: list[str] = Field(min_length=2,
        description="Column names — MUST exactly match the lesson's action.formative_check.tracker_columns.")
    usage_notes: str = Field(min_length=20)
    layout_description: str = Field(min_length=20)
    image_placeholders: list[ImagePlaceholder] = Field(default_factory=list)


class RubricLevel(_Strict):
    level_number: int = Field(ge=1, le=4)
    level_name: Literal["Beginning", "Developing", "Achieving", "Exceeding"]
    descriptor: str = Field(min_length=20,
        description="K-friendly descriptor of what the child can do at this level.")


class RubricRow(_Strict):
    expectation_code: str
    expectation_text: str = Field(
        description="Full expectation text — must match blueprint.curriculum_expectations[code].")
    levels: list[RubricLevel] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def _levels_complete(self) -> "RubricRow":
        nums = sorted(l.level_number for l in self.levels)
        if nums != [1, 2, 3, 4]:
            raise ValueError(f"rubric row {self.expectation_code} must have exactly levels 1,2,3,4 (got {nums})")
        names = {l.level_number: l.level_name for l in self.levels}
        expected = {1: "Beginning", 2: "Developing", 3: "Achieving", 4: "Exceeding"}
        if names != expected:
            raise ValueError(f"rubric row {self.expectation_code} level names must match {expected}")
        return self


class SummativeRubric(_Strict):
    title: str
    purpose: str = Field(min_length=20)
    rows: list[RubricRow] = Field(min_length=1)
    usage_notes: str = Field(min_length=20)
    layout_description: str = Field(min_length=20)
    image_placeholders: list[ImagePlaceholder] = Field(default_factory=list)


class SummativeTaskScript(_Strict):
    title: str
    purpose: str = Field(min_length=30)
    administration_steps: list[str] = Field(min_length=3)
    scoring_guidance: str = Field(min_length=30)
    evidence_per_expectation: dict[str, str] = Field(
        description="Maps each expectation code to teacher guidance on what evidence supports each level.")


class Certificate(_Strict):
    title: str
    recipient_field_label: str = Field(min_length=10)
    achievement_text: str = Field(min_length=20)
    skills_demonstrated: list[str] = Field(min_length=3)
    layout_description: str = Field(min_length=20)
    image_placeholders: list[ImagePlaceholder] = Field(min_length=1)
    print_specifications: PrintSpec


class AssessmentSuite(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    diagnostic_tracker: ClassTracker
    formative_trackers: list[ClassTracker] = Field(min_length=1)
    summative_rubric: SummativeRubric
    summative_task_script: SummativeTaskScript
    certificate: Certificate


# ── Stage 6: Marketplace listing block ──────────────────────────────────────

class MarketplaceListing(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    thematic_title: str
    descriptive_title: str
    short_description: str = Field(min_length=50, max_length=400)
    long_description: str = Field(min_length=300)
    suggested_price_cad: float = Field(ge=2.99, le=29.99)
    tags: list[str] = Field(min_length=5, max_length=25)
    hidden_keywords: list[str] = Field(min_length=3)
    what_is_included: list[str] = Field(min_length=5,
        description="Derived list of artifacts in the package — must be justifiable from generated files on disk.")
    target_buyer: str = Field(min_length=20)
    grade_level: str
    subject: str
    strand: str
    curriculum_codes: list[str] = Field(min_length=1)
    pages_total_estimate: int = Field(ge=10, le=100)
    teacher_prep_time_minutes: int = Field(ge=10, le=300)
    classroom_time_total_minutes: int = Field(ge=30, le=600,
        description="Sum of duration_minutes across all lessons.")
    pedagogical_approach: str = Field(min_length=30)


# ── Stage 7: Rubric grade ───────────────────────────────────────────────────


class RubricCriterionScore(_Strict):
    score: int = Field(ge=1, le=4)
    justification: str = Field(min_length=40,
        description="Concrete reasoning citing evidence from stage JSONs. "
                    "No hand-waving; refer to specific lessons/sections.")
    evidence_refs: list[str] = Field(default_factory=list,
        description="Stage-file references like '1_lesson_03.json::action.steps' "
                    "that justify the score. Optional but recommended.")


class RemediationItem(_Strict):
    criterion: str  # one of the 5 criterion keys
    target_score: int = Field(ge=1, le=4)
    fix_summary: str = Field(min_length=20,
        description="Plain-English description of what changes to lift this criterion.")
    stages_to_regen: list[str] = Field(min_length=1,
        description="Stage keys that must move to needs_regen and be regenerated.")


class RubricGrade(_Strict):
    schema_version: int = Field(ge=1)
    unit_id: str
    rubric_version: str = Field(
        description="Identifier of the rubric content used (e.g., "
                    "'concurrent_coders_v3_2026_05_01'). Bumped whenever the "
                    "rubric markdown changes substantively.")
    pre_grade_drift_check: dict = Field(
        description="Snapshot of pre-grade integrity gate. Required: "
                    "{'consistency_check_issues': int, "
                    "'curriculum_text_issues': int, "
                    "'placeholder_artwork_count': int, 'passed': bool}. "
                    "RubricGrade with passed=False is itself a fail. "
                    "placeholder_artwork_count > 0 also forces a fail "
                    "(added 2026-05-03 after Counting Crew shipped "
                    "with placeholder hero images on every slide).")
    scores: dict[str, RubricCriterionScore] = Field(
        description="Keys must be the 5 rubric criteria.")
    overall_score: int = Field(ge=5, le=20)
    threshold: int = Field(ge=1, le=20,
        description="Must equal pipeline.rubric.THRESHOLD at write time (17).")
    status: str  # "pass" | "fail"
    remediation: list[RemediationItem] = Field(default_factory=list)
    graded_by: str
    graded_at: str

    @model_validator(mode="after")
    def _internal_consistency(self) -> "RubricGrade":
        from pipeline.rubric import CRITERIA, THRESHOLD as _THR
        # Criteria coverage
        if set(self.scores.keys()) != set(CRITERIA):
            raise ValueError(
                f"scores must contain exactly {sorted(CRITERIA)}, got {sorted(self.scores.keys())}"
            )
        # overall_score consistency
        s = sum(c.score for c in self.scores.values())
        if s != self.overall_score:
            raise ValueError(
                f"overall_score={self.overall_score} but sum(scores)={s}"
            )
        # threshold pinned
        if self.threshold != _THR:
            raise ValueError(
                f"threshold={self.threshold} differs from pipeline.rubric.THRESHOLD={_THR}"
            )
        # Status derived correctly (and pre-grade drift gate is upstream)
        expected_status = "pass" if self.overall_score >= self.threshold else "fail"
        # Pre-grade drift makes a "pass" impossible.
        gate_passed = bool(self.pre_grade_drift_check.get("passed"))
        # Placeholder artwork on hero slides also blocks pass — the
        # appearance criterion cannot legitimately be at L4 if the deck
        # is rendering labelled gray boxes where character art / scene
        # illustrations / manipulative imagery should be.
        ph_count = int(self.pre_grade_drift_check.get("placeholder_artwork_count", 0) or 0)
        if not gate_passed and self.status == "pass":
            raise ValueError(
                "status='pass' but pre_grade_drift_check.passed=False — "
                "drift in upstream stages blocks publishing"
            )
        if ph_count > 0 and self.status == "pass":
            raise ValueError(
                f"status='pass' but pre_grade_drift_check."
                f"placeholder_artwork_count={ph_count} — hero images are "
                f"labelled placeholder boxes; extend pipeline/compose.py "
                f"with real composites before re-grading."
            )
        if gate_passed and self.status != expected_status:
            raise ValueError(
                f"status={self.status!r} inconsistent with overall_score "
                f"{self.overall_score} vs threshold {self.threshold}"
            )
        # Remediation must be present for fails, empty for passes
        if self.status == "fail" and not self.remediation:
            raise ValueError("status='fail' requires non-empty remediation list")
        if self.status == "pass" and self.remediation:
            raise ValueError("status='pass' must have empty remediation list")
        # Remediation criteria must be valid keys
        for rem in self.remediation:
            if rem.criterion not in CRITERIA:
                raise ValueError(f"remediation references unknown criterion {rem.criterion!r}")
        return self


# ── Stage registry ──────────────────────────────────────────────────────────

# Maps stage key → Pydantic model. Lesson and worksheet stages share a model
# regardless of N, so we route by prefix.

_BASE_STAGE_MODELS: dict[str, type[BaseModel]] = {
    "blueprint": Blueprint,
    "manipulatives": Manipulatives,
    "formative_reflection": FormativeReflection,
    "assessment_suite": AssessmentSuite,
    "marketplace": MarketplaceListing,
    "rubric_grade": RubricGrade,
}

_PREFIX_STAGE_MODELS: list[tuple[str, type[BaseModel]]] = [
    ("lesson_", LessonPlan),
    ("worksheet_", Worksheet),
]


def model_for_stage(stage_key: str) -> type[BaseModel] | None:
    if stage_key in _BASE_STAGE_MODELS:
        return _BASE_STAGE_MODELS[stage_key]
    for prefix, model in _PREFIX_STAGE_MODELS:
        if stage_key.startswith(prefix):
            return model
    return None


# ── Validation API ──────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self, ok: bool, model: BaseModel | None, errors: str = ""):
        self.ok = ok
        self.model = model
        self.errors = errors

    def __bool__(self) -> bool:
        return self.ok


def validate_stage_file(unit_dir: Path, stage_key: str, output_filename: str) -> ValidationResult:
    """Load a stage's output file and validate it against its Pydantic model."""
    model_cls = model_for_stage(stage_key)
    if model_cls is None:
        return ValidationResult(True, None, "(no schema registered yet for this stage)")
    path = unit_dir / output_filename
    if not path.exists():
        return ValidationResult(False, None, f"file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        m = model_cls.model_validate(raw)
        return ValidationResult(True, m)
    except Exception as e:
        return ValidationResult(False, None, str(e))


def consistency_check(unit_dir: Path) -> list[str]:
    """
    Cross-stage consistency checks. Returns a list of issues (empty = clean).
    Run after marking any stage `done` to catch references that drift.
    """
    issues: list[str] = []

    bp_path = unit_dir / "0_blueprint.json"
    if not bp_path.exists():
        return ["blueprint not yet generated"]

    try:
        bp = Blueprint.model_validate_json(bp_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"blueprint failed schema validation: {e}"]

    valid_manip_ids = {m.id for m in bp.manipulatives_index}
    valid_codes = set(bp.curriculum_codes)
    bp_lesson_titles = {e.lesson_number: e.lesson_title for e in bp.lesson_arc}
    bp_student_goals = {e.lesson_number: e.student_learning_goal for e in bp.lesson_arc}

    # Verify every cited curriculum code exists in the local Ontario reference.
    # Skipped silently if the grade isn't covered yet (e.g. Grade 4+) — the
    # local data only spans K + G1-3 today.
    try:
        from pipeline import curriculum as _curr
        unknown = _curr.validate_codes(bp.grade, bp.curriculum_codes)
        for code in unknown:
            issues.append(
                f"blueprint: curriculum code {code!r} not found in Ontario "
                f"reference for grade {bp.grade!r}"
            )
    except ValueError:
        # Unrecognised grade — fall through; blueprint's internal validator
        # already enforces self-consistency.
        pass

    # Check every lesson file present.
    lesson_briefs: dict[int, WorksheetBrief] = {}
    lesson_goals: dict[int, str] = {}
    for lesson_path in sorted(unit_dir.glob("1_lesson_*.json")):
        try:
            lp = LessonPlan.model_validate_json(lesson_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"{lesson_path.name}: schema fail: {e}")
            continue

        n = lp.lesson_number
        lesson_briefs[n] = lp.worksheet_brief
        lesson_goals[n] = lp.student_learning_goal

        # 1. lesson_title matches blueprint's lesson_arc
        if bp_lesson_titles.get(n) and bp_lesson_titles[n] != lp.lesson_title:
            issues.append(
                f"L{n}: lesson_title {lp.lesson_title!r} differs from blueprint {bp_lesson_titles[n]!r}"
            )

        # 2. student_learning_goal matches blueprint's lesson_arc
        if bp_student_goals.get(n) and bp_student_goals[n] != lp.student_learning_goal:
            issues.append(
                f"L{n}: student_learning_goal differs from blueprint"
            )

        # 3. manipulatives_used must reference Blueprint.manipulatives_index
        for mid in lp.manipulatives_used:
            if mid not in valid_manip_ids:
                issues.append(f"L{n}: unknown manipulative id {mid!r}")

        # 4. expectations must be subset of blueprint codes
        for code in lp.primary_expectations + lp.secondary_expectations:
            if code not in valid_codes:
                issues.append(f"L{n}: unknown expectation {code!r}")

        # 5. unit_id must match blueprint
        if lp.unit_id != bp.unit_id:
            issues.append(f"L{n}: unit_id mismatch ({lp.unit_id} vs blueprint {bp.unit_id})")

    # ── Worksheets must reconcile with their lesson's worksheet_brief ──
    for ws_path in sorted(unit_dir.glob("2_worksheet_*.json")):
        try:
            ws = Worksheet.model_validate_json(ws_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"{ws_path.name}: schema fail: {e}")
            continue

        n = ws.lesson_number

        if ws.unit_id != bp.unit_id:
            issues.append(f"WS{n}: unit_id mismatch ({ws.unit_id} vs blueprint {bp.unit_id})")

        brief = lesson_briefs.get(n)
        if brief is None:
            issues.append(f"WS{n}: no lesson_{n:02d} found to reconcile worksheet against")
            continue

        # 1. worksheet_title must match the lesson's brief
        if ws.worksheet_title != brief.worksheet_title:
            issues.append(
                f"WS{n}: title {ws.worksheet_title!r} differs from lesson brief {brief.worksheet_title!r}"
            )

        # 2. student_learning_goal must match the lesson
        if lesson_goals.get(n) and ws.student_learning_goal != lesson_goals[n]:
            issues.append(
                f"WS{n}: student_learning_goal differs from lesson_{n:02d}"
            )

        # 3. Total parts across all pages must equal the brief's parts_outline length
        ws_parts = sum(len(p.parts) for p in ws.pages)
        if ws_parts != len(brief.parts_outline):
            issues.append(
                f"WS{n}: has {ws_parts} parts but brief expected {len(brief.parts_outline)}"
            )

        # 4. Per-part response_types must match the brief, in order
        flat_parts = [p for page in ws.pages for p in page.parts]
        for i, brief_part in enumerate(brief.parts_outline):
            if i >= len(flat_parts):
                break
            actual = flat_parts[i].student_response_type
            expected = brief_part.response_type
            if actual != expected:
                issues.append(
                    f"WS{n}.part_{i+1}: response_type {actual!r} ≠ brief {expected!r}"
                )

        # 5. Image placeholder IDs must follow the WS<NN>_ prefix convention for this worksheet
        ws_prefix = f"WS{n:02d}_"
        for page in ws.pages:
            for part in page.parts:
                for ph in part.image_placeholders:
                    if not ph.id.startswith(ws_prefix):
                        issues.append(
                            f"WS{n}.part_{part.part_number}: image id {ph.id!r} should start with {ws_prefix!r}"
                        )

    # ── Manipulatives must cover every M-id from the blueprint ──
    manip_path = unit_dir / "3_manipulatives.json"
    if manip_path.exists():
        try:
            mp = Manipulatives.model_validate_json(manip_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"manipulatives: schema fail: {e}")
        else:
            if mp.unit_id != bp.unit_id:
                issues.append(f"manipulatives: unit_id mismatch ({mp.unit_id} vs blueprint {bp.unit_id})")

            covered = {a.asset_id for a in mp.assets if a.category == "manipulative"}
            missing = valid_manip_ids - covered
            if missing:
                issues.append(
                    f"manipulatives: blueprint M-ids not produced as assets: {sorted(missing)}"
                )
            extra = covered - valid_manip_ids
            if extra:
                issues.append(
                    f"manipulatives: assets reference unknown M-ids: {sorted(extra)}"
                )

            # used_in_lessons must match blueprint
            bp_used = {m.id: set(m.used_in_lessons) for m in bp.manipulatives_index}
            for asset in mp.assets:
                if asset.category != "manipulative":
                    continue
                bp_lessons = bp_used.get(asset.asset_id)
                if bp_lessons is None:
                    continue
                if set(asset.used_in_lessons) != bp_lessons:
                    issues.append(
                        f"manipulatives.{asset.asset_id}: used_in_lessons {sorted(asset.used_in_lessons)} ≠ blueprint {sorted(bp_lessons)}"
                    )

            # image placeholder prefixes must match the asset
            for asset in mp.assets:
                if asset.category == "manipulative":
                    # M1_animal_cards → image IDs must start with "M1_"
                    expected_prefix = asset.asset_id.split("_", 1)[0] + "_"
                elif asset.category == "character_puppet":
                    expected_prefix = "CHAR_"
                else:
                    continue
                for ph in asset.image_placeholders:
                    if not ph.id.startswith(expected_prefix):
                        issues.append(
                            f"manipulatives.{asset.asset_id}: image id {ph.id!r} should start with {expected_prefix!r}"
                        )

            # Every recurring character in the blueprint must have a corresponding
            # character_puppet asset. Match by the character's FIRST NAME (lowercased)
            # appearing anywhere in a puppet asset's name — handles both
            # "Coco the Conductor" (parade) and "Mae" / "Theo" / "Buddy" (math K).
            bp_char_first_names = [
                c.name.split()[0].lower() for c in bp.recurring_characters if c.name.strip()
            ]
            puppet_names = {a.name.lower() for a in mp.assets if a.category == "character_puppet"}
            for first in bp_char_first_names:
                if not any(first in n for n in puppet_names):
                    issues.append(
                        f"manipulatives: no character_puppet asset for blueprint "
                        f"recurring character {first!r}"
                    )

    # ── FormativeReflection: expectations subset, image-prefix conventions ──
    fr_path = unit_dir / "4_formative_reflection.json"
    if fr_path.exists():
        try:
            fr = FormativeReflection.model_validate_json(fr_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"formative_reflection: schema fail: {e}")
        else:
            if fr.unit_id != bp.unit_id:
                issues.append(
                    f"formative_reflection: unit_id mismatch ({fr.unit_id} vs blueprint {bp.unit_id})"
                )
            # Each formative worksheet's expectations_assessed must be subset of curriculum_codes
            for i, fw in enumerate(fr.formative_worksheets, 1):
                bad = [c for c in fw.expectations_assessed if c not in valid_codes]
                if bad:
                    issues.append(
                        f"formative_reflection.worksheet_{i}: unknown expectations {bad}"
                    )
                # Image IDs must start with FORM_
                for prompt in fw.prompts:
                    for ph in prompt.image_placeholders:
                        if not ph.id.startswith("FORM_"):
                            issues.append(
                                f"formative_reflection.worksheet_{i}.prompt_{prompt.prompt_number}: image id {ph.id!r} should start with 'FORM_'"
                            )
            # Reflection sheet image IDs must start with REF_
            for prompt in fr.reflection_sheet.prompts:
                for ph in prompt.image_placeholders:
                    if not ph.id.startswith("REF_"):
                        issues.append(
                            f"formative_reflection.reflection.prompt_{prompt.prompt_number}: image id {ph.id!r} should start with 'REF_'"
                        )

    # ── AssessmentSuite: tracker columns must match lessons; rubric covers all expectations ──
    as_path = unit_dir / "5_assessment_suite.json"
    if as_path.exists():
        try:
            as_obj = AssessmentSuite.model_validate_json(as_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"assessment_suite: schema fail: {e}")
        else:
            if as_obj.unit_id != bp.unit_id:
                issues.append(
                    f"assessment_suite: unit_id mismatch ({as_obj.unit_id} vs blueprint {bp.unit_id})"
                )

            # Build a map of lesson tracker columns from disk
            lesson_tracker_cols: dict[int, list[str]] = {}
            for lp_path in sorted(unit_dir.glob("1_lesson_*.json")):
                try:
                    lp = LessonPlan.model_validate_json(lp_path.read_text(encoding="utf-8"))
                    lesson_tracker_cols[lp.lesson_number] = lp.action.formative_check.tracker_columns
                except Exception:
                    pass

            # diagnostic_tracker.columns must equal lesson_01's tracker_columns
            if 1 in lesson_tracker_cols:
                if as_obj.diagnostic_tracker.columns != lesson_tracker_cols[1]:
                    issues.append(
                        f"assessment_suite.diagnostic_tracker: columns differ from lesson_01.action.formative_check.tracker_columns"
                    )

            # Each formative_tracker_lesson_NN must match its lesson's tracker_columns
            for ft in as_obj.formative_trackers:
                # parse lesson number from id like "formative_tracker_lesson_02"
                try:
                    n = int(ft.tracker_id.split("_")[-1])
                except ValueError:
                    issues.append(f"assessment_suite.formative_trackers: bad tracker_id {ft.tracker_id!r}")
                    continue
                if n in lesson_tracker_cols:
                    if ft.columns != lesson_tracker_cols[n]:
                        issues.append(
                            f"assessment_suite.{ft.tracker_id}: columns differ from lesson_{n:02d}.action.formative_check.tracker_columns"
                        )

            # summative_rubric.rows must cover every blueprint curriculum_code exactly
            rubric_codes = {r.expectation_code for r in as_obj.summative_rubric.rows}
            if rubric_codes != valid_codes:
                missing = valid_codes - rubric_codes
                extra = rubric_codes - valid_codes
                if missing:
                    issues.append(f"assessment_suite.summative_rubric: missing rows for {sorted(missing)}")
                if extra:
                    issues.append(f"assessment_suite.summative_rubric: rows for unknown codes {sorted(extra)}")

            # Each rubric row's expectation_text must match blueprint
            for row in as_obj.summative_rubric.rows:
                expected_text = bp.curriculum_expectations.get(row.expectation_code)
                if expected_text and expected_text != row.expectation_text:
                    issues.append(
                        f"assessment_suite.summative_rubric.{row.expectation_code}: expectation_text differs from blueprint"
                    )

            # summative_task_script.evidence_per_expectation should cover all codes
            covered = set(as_obj.summative_task_script.evidence_per_expectation.keys())
            if covered != valid_codes:
                missing = valid_codes - covered
                if missing:
                    issues.append(f"assessment_suite.summative_task_script.evidence_per_expectation: missing {sorted(missing)}")

            # Image IDs across the suite must start with AS_
            def _check_imgs(scope: str, phs):
                for ph in phs:
                    if not ph.id.startswith("AS_"):
                        issues.append(f"assessment_suite.{scope}: image id {ph.id!r} should start with 'AS_'")

            _check_imgs("diagnostic_tracker", as_obj.diagnostic_tracker.image_placeholders)
            for ft in as_obj.formative_trackers:
                _check_imgs(ft.tracker_id, ft.image_placeholders)
            _check_imgs("summative_rubric", as_obj.summative_rubric.image_placeholders)
            _check_imgs("certificate", as_obj.certificate.image_placeholders)

    # ── Marketplace listing must match blueprint and disk truth ──
    mk_path = unit_dir / "6_marketplace.json"
    if mk_path.exists():
        try:
            mk = MarketplaceListing.model_validate_json(mk_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"marketplace: schema fail: {e}")
        else:
            if mk.unit_id != bp.unit_id:
                issues.append(f"marketplace: unit_id mismatch ({mk.unit_id} vs blueprint {bp.unit_id})")
            if mk.thematic_title != bp.thematic_title:
                issues.append(f"marketplace: thematic_title differs from blueprint")
            if mk.descriptive_title != bp.descriptive_title:
                issues.append(f"marketplace: descriptive_title differs from blueprint")
            if mk.grade_level != bp.grade:
                issues.append(f"marketplace: grade_level {mk.grade_level!r} differs from blueprint.grade {bp.grade!r}")
            if mk.subject != bp.subject:
                issues.append(f"marketplace: subject differs from blueprint")
            if mk.strand != bp.strand:
                issues.append(f"marketplace: strand differs from blueprint")
            if set(mk.curriculum_codes) != valid_codes:
                issues.append(f"marketplace: curriculum_codes {set(mk.curriculum_codes)} ≠ blueprint {valid_codes}")
            # classroom_time = sum of lesson durations
            total_classroom = 0
            for lp_path in sorted(unit_dir.glob("1_lesson_*.json")):
                try:
                    lp = LessonPlan.model_validate_json(lp_path.read_text(encoding="utf-8"))
                    total_classroom += lp.duration_minutes
                except Exception:
                    pass
            if total_classroom and mk.classroom_time_total_minutes != total_classroom:
                issues.append(
                    f"marketplace: classroom_time_total_minutes {mk.classroom_time_total_minutes} ≠ sum of lesson durations {total_classroom}"
                )

    return issues


# ── Gate verdict schemas (added 2026-05-08 with the new pair-gate / overall-gate / visual-inspection design) ────────

CategoryName = Literal[
    "pedagogical_depth", "alignment", "instructional_balance",
    "clarity_voice", "lesson_worksheet_consistency",
    "arc_coherence", "code_coverage", "capstone_integration",
    "vocabulary_progression", "character_continuity",
    "sor_alignment",              # Language only
    "mathematical_authenticity",  # Math only
]


class CategoryFeedback(_Strict):
    """Structured feedback for one rubric category that didn't meet target.

    Used by both PairRubricVerdict and OverallUnitVerdict — when status is
    'revise' (or any 'revise_*' variant) every below-target category MUST
    have a CategoryFeedback entry. Specific evidence + concrete required_fix
    are mandatory; vague feedback fails the schema.
    """
    category: CategoryName
    current_score: int = Field(ge=1, le=4)
    target_score: int = Field(ge=2, le=4,
        description="Lowest passing score for this category in this gate context")
    specific_evidence: str = Field(min_length=40, max_length=400,
        description="Exact field/line in the artefact that triggered the score")
    required_fix: str = Field(min_length=40, max_length=400,
        description="Concrete action the model must take to reach target_score")
    affected_stages: list[str] = Field(default_factory=list,
        description="Stage names that need rework, e.g. ['lesson_03', 'worksheet_03']")
    affected_pairs: list[int] = Field(default_factory=list,
        description="Pair numbers needing rework (overall gate only)")
    severity: Literal["blocking", "minor"] = "blocking"


# ── Pair rubric (per lesson + worksheet pair) ────────────────────────

class PairRubricScores(_Strict):
    """Six categories scored 1-4. sor_alignment XOR mathematical_authenticity
    is set per subject (the other is None).
    """
    alignment: int = Field(ge=1, le=4)
    pedagogical_depth: int = Field(ge=1, le=4)
    instructional_balance: int = Field(ge=1, le=4)
    clarity_voice: int = Field(ge=1, le=4)
    lesson_worksheet_consistency: int = Field(ge=1, le=4)
    sor_alignment: int | None = Field(default=None, ge=1, le=4)
    mathematical_authenticity: int | None = Field(default=None, ge=1, le=4)


class PairRubricVerdict(_Strict):
    schema_version: int = 1
    unit_id: str
    pair_number: int = Field(ge=1, le=5)
    graded_at: str
    graded_by: str
    status: Literal["pass", "revise_lesson", "revise_worksheet", "revise_both"]
    scores: PairRubricScores
    category_feedback: list[CategoryFeedback] = Field(default_factory=list)
    summary: str = Field(min_length=80, max_length=600)

    @model_validator(mode="after")
    def enforce_pair_rule(self) -> "PairRubricVerdict":
        scored = [self.scores.alignment, self.scores.pedagogical_depth,
                  self.scores.instructional_balance, self.scores.clarity_voice,
                  self.scores.lesson_worksheet_consistency]
        if self.scores.sor_alignment is not None:
            scored.append(self.scores.sor_alignment)
        if self.scores.mathematical_authenticity is not None:
            scored.append(self.scores.mathematical_authenticity)
        any_below_3 = any(s < 3 for s in scored)
        threes = sum(1 for s in scored if s == 3)
        # Pass bar: zero categories < 3 AND at most ONE category = 3
        # (rest must be 4). More than one ≤3 = revise.
        should_pass = (not any_below_3) and threes <= 1
        if should_pass and self.status != "pass":
            raise ValueError(
                f"Scores meet pair pass bar (no <3, threes={threes}) but "
                f"status={self.status!r}. Status must be 'pass'."
            )
        if not should_pass and self.status == "pass":
            reason = []
            if any_below_3:
                reason.append("at least one category < 3")
            if threes > 1:
                reason.append(f"{threes} categories = 3 (max 1 allowed)")
            raise ValueError(
                f"Pass not allowed: {'; '.join(reason)}. Scores: {scored}"
            )
        if self.status != "pass" and not self.category_feedback:
            raise ValueError(
                "Revise verdict must include at least one CategoryFeedback "
                "explaining what to fix."
            )
        # Subject-XOR sanity
        if (self.scores.sor_alignment is not None) and \
           (self.scores.mathematical_authenticity is not None):
            raise ValueError(
                "Set exactly one of sor_alignment (Language) or "
                "mathematical_authenticity (Math); not both."
            )
        return self


# ── Overall unit grader (whole-unit, strict bar) ──────────────────────

class OverallUnitScores(_Strict):
    """Foundational four MUST be 4. Arc-level: at most ONE may be 3."""
    # Foundational four — must all be 4
    pedagogical_depth: int = Field(ge=1, le=4)
    alignment: int = Field(ge=1, le=4)
    instructional_balance: int = Field(ge=1, le=4)
    clarity_voice: int = Field(ge=1, le=4)
    # Arc-level — at most ONE may be 3
    arc_coherence: int = Field(ge=1, le=4)
    code_coverage: int = Field(ge=1, le=4)
    capstone_integration: int = Field(ge=1, le=4)
    vocabulary_progression: int = Field(ge=1, le=4)
    character_continuity: int = Field(ge=1, le=4)
    sor_alignment: int | None = Field(default=None, ge=1, le=4)
    mathematical_authenticity: int | None = Field(default=None, ge=1, le=4)


class OverallUnitVerdict(_Strict):
    schema_version: int = 1
    unit_id: str
    graded_at: str
    graded_by: str
    status: Literal["pass", "revise"]
    scores: OverallUnitScores
    category_feedback: list[CategoryFeedback] = Field(default_factory=list)
    pairs_to_revise: list[int] = Field(default_factory=list)
    summary: str = Field(min_length=80, max_length=600)

    @model_validator(mode="after")
    def enforce_decision_rule(self) -> "OverallUnitVerdict":
        s = self.scores
        foundational = [s.pedagogical_depth, s.alignment,
                        s.instructional_balance, s.clarity_voice]
        arc_level = [s.arc_coherence, s.code_coverage, s.capstone_integration,
                     s.vocabulary_progression, s.character_continuity]
        if s.sor_alignment is not None:
            arc_level.append(s.sor_alignment)
        if s.mathematical_authenticity is not None:
            arc_level.append(s.mathematical_authenticity)

        foundational_all_4 = all(score == 4 for score in foundational)
        arc_threes = sum(1 for score in arc_level if score == 3)
        arc_below_3 = sum(1 for score in arc_level if score < 3)

        should_pass = foundational_all_4 and arc_threes <= 1 and arc_below_3 == 0

        if should_pass and self.status != "pass":
            raise ValueError(
                "Scores meet pass bar (all foundational=4, "
                f"arc threes={arc_threes}, arc <3={arc_below_3}) but "
                f"status={self.status!r}. Status must be 'pass'."
            )
        if not should_pass and self.status == "pass":
            failures = []
            if not foundational_all_4:
                failures.append(f"foundational not all 4 ({foundational})")
            if arc_threes > 1:
                failures.append(f"arc has {arc_threes} threes (max 1)")
            if arc_below_3 > 0:
                failures.append(f"arc has {arc_below_3} scores below 3")
            raise ValueError(f"Status='pass' but bar not met: {'; '.join(failures)}")
        if self.status == "revise" and not self.category_feedback:
            raise ValueError(
                "Revise verdict must include at least one CategoryFeedback."
            )
        if (s.sor_alignment is not None) and (s.mathematical_authenticity is not None):
            raise ValueError("Set exactly one subject-specific category, not both.")
        return self


# ── Visual inspection (Phase C, after deck build) ─────────────────────

VisualIssueCategory = Literal[
    "text_overflow", "image_misplacement", "character_unrecognizable",
    "low_contrast", "missing_asset", "title_clipping", "other",
]


class VisualInspectionIssue(_Strict):
    slide_number: int = Field(ge=1, le=27)
    category: VisualIssueCategory
    description: str = Field(min_length=20, max_length=400)
    suggested_fix: str = Field(min_length=20, max_length=400)
    severity: Literal["blocking", "minor"]


class VisualInspectionVerdict(_Strict):
    schema_version: int = 1
    unit_id: str
    deck_url: str
    pdf_path: str
    pdf_size_kb: int = Field(ge=0)
    slide_count: int = Field(ge=1)
    inspected_at: str
    inspected_by: str
    status: Literal["pass", "revise_assets", "revise_content", "revise_layout"]
    issues: list[VisualInspectionIssue] = Field(default_factory=list)
    blocking_count: int = Field(ge=0)
    summary: str = Field(min_length=80, max_length=600)

    @model_validator(mode="after")
    def enforce_inspection_rule(self) -> "VisualInspectionVerdict":
        actual_blocking = sum(1 for i in self.issues if i.severity == "blocking")
        if actual_blocking != self.blocking_count:
            raise ValueError(
                f"blocking_count={self.blocking_count} disagrees with "
                f"actual blocking issues={actual_blocking}"
            )
        if self.blocking_count == 0 and self.status != "pass":
            raise ValueError(
                f"Zero blocking issues but status={self.status!r}; must be 'pass'."
            )
        if self.blocking_count > 0 and self.status == "pass":
            raise ValueError(
                f"{self.blocking_count} blocking issues; status cannot be 'pass'."
            )
        return self
