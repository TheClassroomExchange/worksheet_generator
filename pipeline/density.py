"""
Grade-density validator for lesson plans.

Each Ontario grade we generate has different content-density expectations:
Kindergarten lessons should be shorter/lighter; Grade 3 lessons should be
the longest and most explicit. The schema doesn't enforce this — strings
can be any length — so this module provides non-blocking warnings, like
`pipeline.slides.validate_unit_for_slides()`.

Calibration (2026-04-28): targets in `GRADE_DENSITY` are calibrated to what
the K reference unit + the new G1/G2 units actually produce, not the
aspirational ~280-char-K rule that the older memory file referenced. The
ranges below match observed data with a 25% headroom.

Usage:
    from pipeline.density import validate_grade_density
    warns = validate_grade_density(unit_dir)
    for w in warns: print(w)

Returns a list of human-readable warning strings. An empty list means the
unit's lesson density looks normal for the blueprint's grade.

Wired into `pipeline.manifest.complete_stage()` for `lesson_NN` stages so
warnings surface alongside schema validation. Warnings do NOT mark the
stage failed — they're advisory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ── Calibrated grade-density targets ────────────────────────────────────────
#
# Calibrated 2026-04-28 from the K reference unit + G1/G2 new units. Values
# are RANGES (min, max) on each metric; warnings fire when a lesson lands
# outside the range. Soft bounds — designed to catch outliers, not enforce a
# narrow band.

GRADE_DENSITY: dict[str, dict[str, tuple[int, int]]] = {
    "Kindergarten": {
        "minds_on_script_chars":  (500, 1100),
        "action_steps_count":     (3, 5),
        "consolidation_prompts":  (2, 4),
    },
    "Grade 1": {
        "minds_on_script_chars":  (700, 1300),
        "action_steps_count":     (4, 5),
        "consolidation_prompts":  (2, 4),
    },
    "Grade 2": {
        "minds_on_script_chars":  (850, 1400),
        "action_steps_count":     (4, 6),
        "consolidation_prompts":  (3, 4),
    },
    "Grade 3": {
        "minds_on_script_chars":  (1000, 1600),
        "action_steps_count":     (5, 7),
        "consolidation_prompts":  (3, 5),
    },
}

# Cross-grade ordering check: each successive grade should have at minimum
# AT LEAST the same minds_on_script_chars lower bound as the previous, to
# enforce "lessons get more explanation as grades move up". Encoded as the
# expected non-decreasing sequence of lower bounds.
_GRADE_ORDER = ["Kindergarten", "Grade 1", "Grade 2", "Grade 3"]


def _bp_grade(unit_dir: Path) -> str | None:
    """Read the unit's grade from blueprint, or None if unavailable."""
    bp_path = unit_dir / "0_blueprint.json"
    if not bp_path.exists():
        return None
    try:
        return json.loads(bp_path.read_text(encoding="utf-8")).get("grade")
    except Exception:
        return None


def _check_lesson(grade: str, lesson_path: Path,
                  bounds: dict[str, tuple[int, int]]) -> list[str]:
    warns: list[str] = []
    try:
        lp: dict[str, Any] = json.loads(lesson_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{lesson_path.name}: failed to parse ({e})"]

    n = lp.get("lesson_number", "?")
    label = f"L{n}"

    # 1. Minds-on teacher script length
    script = (lp.get("minds_on") or {}).get("teacher_script", "") or ""
    sc = len(script)
    lo, hi = bounds["minds_on_script_chars"]
    if sc < lo:
        warns.append(
            f"{label}: minds_on.teacher_script is {sc} chars; below {grade} "
            f"floor of {lo} — consider adding pedagogical detail"
        )
    elif sc > hi:
        warns.append(
            f"{label}: minds_on.teacher_script is {sc} chars; above {grade} "
            f"ceiling of {hi} — consider tightening or splitting into steps"
        )

    # 2. Action step count
    steps = (lp.get("action") or {}).get("steps", []) or []
    n_steps = len(steps)
    lo, hi = bounds["action_steps_count"]
    if n_steps < lo:
        warns.append(
            f"{label}: action.steps has {n_steps} steps; below {grade} "
            f"floor of {lo}"
        )
    elif n_steps > hi:
        warns.append(
            f"{label}: action.steps has {n_steps} steps; above {grade} "
            f"ceiling of {hi}"
        )

    # 3. Consolidation prompt count
    prompts = (lp.get("consolidation") or {}).get("discussion_prompts", []) or []
    n_prompts = len(prompts)
    lo, hi = bounds["consolidation_prompts"]
    if n_prompts < lo:
        warns.append(
            f"{label}: consolidation.discussion_prompts has {n_prompts} "
            f"prompts; below {grade} floor of {lo}"
        )
    elif n_prompts > hi:
        warns.append(
            f"{label}: consolidation.discussion_prompts has {n_prompts} "
            f"prompts; above {grade} ceiling of {hi}"
        )

    return warns


def validate_grade_density(unit_dir: Path) -> list[str]:
    """
    Inspect every lesson_NN.json in the unit and return non-blocking warnings
    when their density (minds_on script length, action step count, consolidation
    prompt count) falls outside the calibrated band for the blueprint's grade.

    Returns an empty list when the unit's lesson density looks normal.
    """
    grade = _bp_grade(unit_dir)
    if grade is None:
        return ["density: blueprint missing or unreadable; cannot validate"]
    if grade not in GRADE_DENSITY:
        return [f"density: no calibrated bounds for grade {grade!r}"]

    bounds = GRADE_DENSITY[grade]
    warns: list[str] = []
    for lp_path in sorted(unit_dir.glob("1_lesson_*.json")):
        warns.extend(_check_lesson(grade, lp_path, bounds))
    return warns


def validate_lesson_density(unit_dir: Path, lesson_path: Path) -> list[str]:
    """
    Same as `validate_grade_density()` but for a single lesson file. Used by
    `pipeline.manifest.complete_stage()` to warn on a per-lesson basis.
    """
    grade = _bp_grade(unit_dir)
    if grade is None or grade not in GRADE_DENSITY:
        return []  # silent if no reference — blueprint check handles that
    return _check_lesson(grade, lesson_path, GRADE_DENSITY[grade])


def report_cross_grade_density(unit_dirs: list[Path]) -> list[str]:
    """
    Cross-grade audit: reads multiple unit directories and reports whether
    average minds_on.teacher_script length is non-decreasing in the canonical
    grade order (K → G1 → G2 → G3). Useful for diagnosing whether the
    differentiation rule is being honoured across a batch.
    """
    by_grade: dict[str, list[int]] = {}
    for ud in unit_dirs:
        grade = _bp_grade(ud)
        if grade is None:
            continue
        for lp in sorted(ud.glob("1_lesson_*.json")):
            try:
                d = json.loads(lp.read_text(encoding="utf-8"))
                sc = len((d.get("minds_on") or {}).get("teacher_script") or "")
                by_grade.setdefault(grade, []).append(sc)
            except Exception:
                pass

    findings: list[str] = []
    last_avg: int | None = None
    for g in _GRADE_ORDER:
        if g not in by_grade:
            continue
        scs = by_grade[g]
        avg = sum(scs) // len(scs) if scs else 0
        findings.append(f"  {g}: avg minds_on script = {avg} chars (n={len(scs)})")
        if last_avg is not None and avg < last_avg:
            findings.append(
                f"  ⚠ {g} avg ({avg}) is BELOW prior grade avg ({last_avg}) "
                f"— differentiation rule violated"
            )
        last_avg = avg
    return findings
