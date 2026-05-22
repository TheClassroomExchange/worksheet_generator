"""
Stage definitions for the unit-generation pipeline.

Each stage produces a single JSON file. Stages run in dependency order.
A unit is `done` only when every stage is `done`.

This file is the single source of truth for what stages exist.
Adding a new artifact = adding a stage here + a prompt template + a renderer hook.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Stage:
    key: str                      # e.g. "blueprint", "lesson_01"
    label: str                    # human-readable label for dashboards
    output_filename: str          # written under the unit folder
    prompt_template: str          # path under prompts/, relative
    depends_on: tuple = ()        # other stage keys that must be done first
    short: str = ""               # 2-letter code for the dashboard column


def stages_for_unit(num_lessons: int = 5, with_gates: bool = False) -> list[Stage]:
    """Build the ordered stage list for a unit with `num_lessons` lessons.

    When ``with_gates=True``, includes the new pair_NN_gate, overall_unit_gate,
    and visual_inspection stages introduced 2026-05-08 with the Language
    programme design. Existing math units can be retrofitted via
    ``manifest.extend_manifest_with_gates()``.
    """
    s: list[Stage] = []

    s.append(Stage(
        key="blueprint",
        label="Blueprint (anchors, lesson titles, expectation map)",
        output_filename="0_blueprint.json",
        prompt_template="00_blueprint.md",
        short="BP",
    ))

    for i in range(1, num_lessons + 1):
        s.append(Stage(
            key=f"lesson_{i:02d}",
            label=f"Lesson {i} plan",
            output_filename=f"1_lesson_{i:02d}.json",
            prompt_template="10_lesson.md",
            depends_on=("blueprint",),
            short=f"L{i}",
        ))

    for i in range(1, num_lessons + 1):
        s.append(Stage(
            key=f"worksheet_{i:02d}",
            label=f"Lesson {i} student worksheet",
            output_filename=f"2_worksheet_{i:02d}.json",
            prompt_template="20_worksheet.md",
            depends_on=("blueprint", f"lesson_{i:02d}"),
            short=f"W{i}",
        ))

    s.append(Stage(
        key="manipulatives",
        label="Teacher manipulatives & visual templates",
        output_filename="3_manipulatives.json",
        prompt_template="30_manipulatives.md",
        depends_on=("blueprint",) + tuple(f"lesson_{i:02d}" for i in range(1, num_lessons + 1)),
        short="MN",
    ))

    s.append(Stage(
        key="formative_reflection",
        label="Standalone formative + reflection sheets",
        output_filename="4_formative_reflection.json",
        prompt_template="40_formative_reflection.md",
        depends_on=("blueprint",) + tuple(f"lesson_{i:02d}" for i in range(1, num_lessons + 1)),
        short="FR",
    ))

    s.append(Stage(
        key="assessment_suite",
        label="Summative rubric, summative task, certificate",
        output_filename="5_assessment_suite.json",
        prompt_template="50_assessment_suite.md",
        depends_on=("blueprint",) + tuple(f"lesson_{i:02d}" for i in range(1, num_lessons + 1)),
        short="AS",
    ))

    s.append(Stage(
        key="marketplace",
        label="Marketplace listing block (derived)",
        output_filename="6_marketplace.json",
        prompt_template="60_marketplace.md",
        depends_on=tuple(st.key for st in s),  # depends on EVERYTHING above
        short="MK",
    ))

    # Stage 7 — Rubric grade. The publication gate.
    # Runs AFTER marketplace because it needs every artefact in place to grade.
    # Pre-condition (enforced by pipeline.rubric.pre_grade_drift_check):
    #   schemas.consistency_check(unit_dir) returns 0 issues
    #   curriculum_reference.verify_curriculum_text(unit_dir) returns 0 issues
    # Post-condition: status='pass' (overall_score >= 17/20).
    # On fail: stages listed in `remediation[*].stages_to_regen` are reset to
    # needs_regen via pipeline.manifest.mark_for_remediation.
    s.append(Stage(
        key="rubric_grade",
        label="Product-quality rubric grade (publication gate)",
        output_filename="7_rubric_grade.json",
        prompt_template="70_rubric_grade.md",
        depends_on=tuple(st.key for st in s),  # depends on every prior stage
        short="RG",
    ))

    if with_gates:
        # Pair gates — one after each (lesson_NN, worksheet_NN). Each gate
        # spawns the pair_rubric_grader skill, which writes a typed verdict.
        for i in range(1, num_lessons + 1):
            s.append(Stage(
                key=f"pair_{i:02d}_gate",
                label=f"Pair {i} rubric gate",
                output_filename=f"pair_{i:02d}_verdict.json",
                prompt_template="",
                depends_on=("blueprint", f"lesson_{i:02d}", f"worksheet_{i:02d}"),
                short=f"P{i}",
            ))

        # Overall unit gate — strict bar. Spawns overall_unit_grader skill.
        s.append(Stage(
            key="overall_unit_gate",
            label="Overall unit rubric gate (strict bar)",
            output_filename="overall_unit_verdict.json",
            prompt_template="",
            depends_on=tuple(st.key for st in s if st.key != "rubric_grade") + ("rubric_grade",),
            short="OU",
        ))

        # Visual inspection — Phase C, after deck is built.
        s.append(Stage(
            key="visual_inspection",
            label="Visual inspection (Phase C, post-deck-build)",
            output_filename="visual_inspection_verdict.json",
            prompt_template="",
            depends_on=("overall_unit_gate",),
            short="VI",
        ))

    return s
