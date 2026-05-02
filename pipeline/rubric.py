"""Product-quality rubric — the gate every unit clears before publishing.

The authoritative rubric content lives in
``assets/rubric_product_assessment.md`` (verbatim original + non-coding
extension rules). This module exposes:

* ``THRESHOLD`` — minimum overall score to publish (17/20).
* ``CRITERIA`` — the five rubric criteria as ordered tuples.
* ``REMEDIATION_MAP`` — which stages must regen when each criterion fails.
* ``classify(scores)`` — pass/fail decision.
* ``rubric_path()`` — path to the markdown rubric (for grading sessions to read).
* ``required_score_to_pass(scores)`` — given current scores, what each
  criterion needs to lift to in order to hit the threshold.

The actual scoring is done by Claude in chat (the runner), not Python —
consistent with the project's "no Anthropic API calls in plumbing" rule.
This module is pure book-keeping.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_PATH = PROJECT_ROOT / "assets" / "rubric_product_assessment.md"

THRESHOLD = 17  # out of 20
MAX_PER_CRITERION = 4
N_CRITERIA = 5
MAX_SCORE = MAX_PER_CRITERION * N_CRITERIA  # 20

# Ordered for stable iteration / report layout.
CRITERIA: tuple[str, ...] = (
    "pedagogical_depth",
    "instructional_balance",
    "clarity_communication",
    "alignment",
    "appearance",
)

CRITERION_LABELS: dict[str, str] = {
    "pedagogical_depth": "Pedagogical Depth & Material Quality",
    "instructional_balance": "Instructional Balance (Floor vs. Desk)",
    "clarity_communication": "Clarity & Communication",
    "alignment": "Alignment",
    "appearance": "Appearance",
}

# Which stage outputs must regenerate to lift each criterion. The mapping is
# intentionally generous on the upper bound — better to regen one extra stage
# than miss a coupled fix. Order matters: stages are reset to needs_regen in
# pipeline order so the runner can pick them up sequentially.
REMEDIATION_MAP: dict[str, tuple[str, ...]] = {
    "pedagogical_depth": (
        "lesson_01", "lesson_02", "lesson_03", "lesson_04", "lesson_05",
        "worksheet_01", "worksheet_02", "worksheet_03", "worksheet_04", "worksheet_05",
        "formative_reflection",
    ),
    "instructional_balance": (
        "lesson_01", "lesson_02", "lesson_03", "lesson_04", "lesson_05",
    ),
    "clarity_communication": (
        "lesson_01", "lesson_02", "lesson_03", "lesson_04", "lesson_05",
    ),
    # Alignment failures cascade from blueprint downward — text drift in the
    # blueprint propagates to assessment_suite (rubric expectation_text).
    "alignment": (
        "blueprint",
        "assessment_suite",
    ),
    # Appearance is largely a slide-render concern, but marketplace text
    # (long_description, character cast, Canadian context) feeds the cover
    # and overview slides.
    "appearance": (
        "marketplace",
    ),
}


def classify(scores: dict[str, int]) -> tuple[int, str]:
    """Return (overall_score, status) where status is 'pass' or 'fail'."""
    if set(scores.keys()) != set(CRITERIA):
        raise ValueError(
            f"scores must contain exactly {CRITERIA}, got {sorted(scores.keys())}"
        )
    for k, v in scores.items():
        if not isinstance(v, int) or v < 1 or v > MAX_PER_CRITERION:
            raise ValueError(f"{k}: score must be int 1..{MAX_PER_CRITERION}, got {v!r}")
    total = sum(scores.values())
    return total, ("pass" if total >= THRESHOLD else "fail")


def required_lifts(scores: dict[str, int]) -> dict[str, int]:
    """For a failing grade, return per-criterion *minimum* additional points
    needed to hit THRESHOLD, distributed greedily on the lowest scores first.

    Example: scores={3,4,3,4,3} -> total 17, no lift needed -> all 0.
    Example: scores={3,4,3,4,2} -> total 16, need +1, lifts={appearance:+1}.
    Example: scores={2,4,2,4,3} -> total 15, need +2, lifts={pedagogical_depth:+1,
                                                              clarity_communication:+1}.
    """
    total, status = classify(scores)
    if status == "pass":
        return {k: 0 for k in CRITERIA}
    needed = THRESHOLD - total
    lifts = {k: 0 for k in CRITERIA}
    # Lift the lowest scores first (cheapest path to threshold). Tie-break
    # by criterion order so the result is deterministic.
    ranked = sorted(CRITERIA, key=lambda k: (scores[k], CRITERIA.index(k)))
    for k in ranked:
        room = MAX_PER_CRITERION - scores[k]
        if room <= 0:
            continue
        bump = min(room, needed)
        lifts[k] = bump
        needed -= bump
        if needed == 0:
            break
    if needed > 0:
        # All criteria already at 4 yet total < THRESHOLD — impossible for
        # THRESHOLD<=20, but guard anyway.
        raise RuntimeError("cannot reach threshold even at full marks")
    return lifts


def stages_needing_regen(scores: dict[str, int]) -> list[str]:
    """Union of REMEDIATION_MAP entries for every criterion that needs lift."""
    lifts = required_lifts(scores)
    seen: list[str] = []
    for crit, lift in lifts.items():
        if lift <= 0:
            continue
        for stage in REMEDIATION_MAP[crit]:
            if stage not in seen:
                seen.append(stage)
    return seen


def rubric_path() -> Path:
    if not RUBRIC_PATH.exists():
        raise FileNotFoundError(
            f"rubric markdown missing at {RUBRIC_PATH} — restore from git or the source Doc"
        )
    return RUBRIC_PATH


# Identifier of the rubric content the runner is grading against. Bump when
# assets/rubric_product_assessment.md changes substantively. Stored on every
# RubricGrade so old grades can be flagged stale by future passes.
RUBRIC_VERSION = "concurrent_coders_v3_2026_05_01_strict_imgalign"


def pre_grade_drift_check(unit_dir: Path) -> dict:
    """Run the cross-pipeline drift checks that MUST pass before a grade is
    written. Returns a dict suitable for the RubricGrade.pre_grade_drift_check
    field. ``passed=False`` blocks any 'pass' status — drift in upstream
    stages cannot be papered over with a high rubric score.

    The three checks are:
      1. ``schemas.consistency_check(unit_dir)`` — schema/cross-stage drift
         (lesson titles match blueprint, manipulative IDs reconcile,
         expectation codes match, rubric expectation_text matches blueprint,
         etc.).
      2. ``curriculum_reference.verify_curriculum_text(unit_dir)`` — diff
         input_row.json's curriculum text against the local Ontario reference.
      3. ``image_alignment.validate_unit_alignment(unit_dir)`` — every
         ImagePlaceholder must have ``keywords`` + ``text_image_alignment_check``
         populated, every keyword must appear in surrounding student text AND
         in the chosen clipart's caption+tags (when applicable).
    """
    # Local imports to avoid a circular at module-load time.
    from pipeline import schemas as _sc
    from pipeline import curriculum_reference as _cr
    from pipeline import image_alignment as _ia

    consistency_issues = _sc.consistency_check(unit_dir)
    curriculum_issues = _cr.verify_curriculum_text(unit_dir)
    image_text_issues = _ia.validate_unit_alignment(unit_dir)
    passed = (not consistency_issues
              and not curriculum_issues
              and not image_text_issues)
    return {
        "consistency_check_issues": len(consistency_issues),
        "curriculum_text_issues": len(curriculum_issues),
        "image_text_alignment_issues": len(image_text_issues),
        "passed": passed,
        "consistency_check_details": consistency_issues[:20],
        "curriculum_text_details": curriculum_issues[:20],
        "image_text_alignment_details": image_text_issues[:20],
    }
