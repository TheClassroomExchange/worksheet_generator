"""Coding-worksheet product-quality rubric — the gate every coding sheet clears.

Coding analogue of ``pipeline/rubric.py``. The authoritative rubric *content*
lives in ``coding/rubrics/rubric_coding_{K,G1,G2,G3}.md`` (one per grade band);
this module is pure book-keeping + the publish-gate decision. Scoring itself is
done by Claude in chat (the runner) — no Anthropic API calls in plumbing.

Publish gate (all grades): **total ≥ 19/20 AND C2 ≥ L3 AND C3 = L4 AND C5 = L4.**
The only droppable point is C1 or C4 → L3. C2 is also a hard concept-correctness
gate tied to the code-runs check.

Criteria are referred to by their stable keys C1..C5 (mapping below).
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_DIR = PROJECT_ROOT / "coding" / "rubrics"

THRESHOLD = 19            # out of 20 — the publish bar
MIN_VIABLE = 15           # documented minimum in the rubric md (not the publish bar)
MAX_PER_CRITERION = 4
N_CRITERIA = 5
MAX_SCORE = MAX_PER_CRITERION * N_CRITERIA  # 20

# Stable criterion keys, in report order.
CRITERIA: tuple[str, ...] = ("C1", "C2", "C3", "C4", "C5")

CRITERION_LABELS: dict[str, str] = {
    "C1": "Ontario C3 / K-frame Alignment",
    "C2": "Coding-Concept Correctness (hard gate)",
    "C3": "Grade-Appropriate Pedagogy & Cognitive Load",
    "C4": "Clarity, Structure & Mascot/Visual Integration",
    "C5": "Teacher Guide Completeness",
}

# Per-criterion *floors* enforced on top of the total. C2 must be >= L3 (hard
# concept gate); C3 and C5 must be == L4 (the user's higher-bar emphasis on
# pedagogy/cognitive-load and teacher-guide completeness).
CRITERION_FLOORS: dict[str, int] = {"C2": 3, "C3": 4, "C5": 4}

# Which content stage(s) must regenerate to lift each criterion. Coding sheets
# have a flatter stage set than math units (no separate lesson/worksheet split),
# so the map points at the per-sheet stages.
REMEDIATION_MAP: dict[str, tuple[str, ...]] = {
    "C1": ("solution", "content"),   # alignment: fix the task + its verified code
    "C2": ("solution", "content"),   # correctness: re-run the code gate, fix content
    "C3": ("content",),              # pedagogy/load: re-author the worksheet body
    "C4": ("content",),              # clarity/visual: re-author layout/exercise prose
    "C5": ("content",),              # teacher guide lives inside content.json
}

# Grade label -> rubric filename. Accepts a few spellings of each grade.
_GRADE_TO_FILE: dict[str, str] = {
    "k": "rubric_coding_K.md", "kindergarten": "rubric_coding_K.md",
    "g1": "rubric_coding_G1.md", "grade 1": "rubric_coding_G1.md", "1": "rubric_coding_G1.md",
    "g2": "rubric_coding_G2.md", "grade 2": "rubric_coding_G2.md", "2": "rubric_coding_G2.md",
    "g3": "rubric_coding_G3.md", "grade 3": "rubric_coding_G3.md", "3": "rubric_coding_G3.md",
}

RUBRIC_VERSION = "coding_v1_2026_06_13_strict19_allgrade"


def select_rubric(grade: str) -> Path:
    """Return the path to the band rubric for ``grade`` (every product, every
    grade, is graded against its band rubric — no product goes unmarked)."""
    key = str(grade).strip().lower()
    fname = _GRADE_TO_FILE.get(key)
    if fname is None:
        raise ValueError(
            f"unknown grade {grade!r}; expected one of K/G1/G2/G3 (got key {key!r})"
        )
    path = RUBRIC_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"rubric missing at {path} — restore from git")
    return path


def _validate(scores: dict[str, int]) -> None:
    if set(scores.keys()) != set(CRITERIA):
        raise ValueError(f"scores must contain exactly {CRITERIA}, got {sorted(scores)}")
    for k, v in scores.items():
        if not isinstance(v, int) or v < 1 or v > MAX_PER_CRITERION:
            raise ValueError(f"{k}: score must be int 1..{MAX_PER_CRITERION}, got {v!r}")


def floor_failures(scores: dict[str, int]) -> dict[str, tuple[int, int]]:
    """Return {criterion: (got, required)} for every per-criterion floor not met."""
    _validate(scores)
    out: dict[str, tuple[int, int]] = {}
    for crit, req in CRITERION_FLOORS.items():
        if scores[crit] < req:
            out[crit] = (scores[crit], req)
    return out


def classify(scores: dict[str, int]) -> tuple[int, str, list[str]]:
    """Return (total, status, reasons). status is 'pass' iff
    total >= THRESHOLD AND every per-criterion floor is met.
    ``reasons`` lists why a fail failed (empty on pass)."""
    _validate(scores)
    total = sum(scores.values())
    reasons: list[str] = []
    if total < THRESHOLD:
        reasons.append(f"total {total}/{MAX_SCORE} < {THRESHOLD}")
    for crit, (got, req) in floor_failures(scores).items():
        lvl = "L3" if req == 3 else f"L{req}"
        reasons.append(f"{crit} ({CRITERION_LABELS[crit]}) = L{got}, needs {lvl}")
    return total, ("pass" if not reasons else "fail"), reasons


def stages_needing_regen(scores: dict[str, int]) -> list[str]:
    """Union of REMEDIATION_MAP entries for criteria below their target.
    A criterion is 'below target' if it has a floor it misses, or (for C1/C4,
    which have no hard floor) if it sits below L4 while the total is short."""
    _validate(scores)
    total = sum(scores.values())
    need: list[str] = []
    targets = {c: CRITERION_FLOORS.get(c, MAX_PER_CRITERION) for c in CRITERIA}
    for crit in CRITERIA:
        below = scores[crit] < targets[crit]
        # C1/C4 only need lifting when the total is short of threshold.
        soft = crit in ("C1", "C4") and total < THRESHOLD and scores[crit] < MAX_PER_CRITERION
        if below or soft:
            for s in REMEDIATION_MAP[crit]:
                if s not in need:
                    need.append(s)
    return need


def pre_grade_drift_check(unit_dir: Path) -> dict:
    """Drift checks that MUST pass before a coding grade can record 'pass'.
    Mirrors ``rubric.pre_grade_drift_check`` but for the coding pipeline:

      1. **answer↔solution** — ``solution_run.json`` exists and ``passed`` is
         True (the code-runs gate executed clean). The answer key is derived
         from this, so a missing/failed run blocks the grade.
      2. **curriculum verbatim** — every cited C3 code in ``input_row.json`` is
         valid for the grade and its text matches the Ontario cache verbatim
         (K cites the K-frame, not C3 — skipped there).
      3. **image-text alignment** — every ImagePlaceholder keyword in
         ``content.json`` appears in the surrounding student text.

    Returns a dict with per-check counts + ``passed`` (all clear).
    """
    import json as _json

    details: dict[str, list] = {}

    # 1. answer <-> solution run-gate
    run_path = unit_dir / "solution_run.json"
    solution_ok = False
    if run_path.exists():
        try:
            solution_ok = bool(_json.loads(run_path.read_text()).get("passed"))
        except Exception:
            solution_ok = False
    if not solution_ok:
        details.setdefault("solution_run", []).append(
            "solution_run.json missing or passed!=true (code-runs gate not cleared)"
        )

    # 2. curriculum verbatim (best-effort; reuses the math curriculum loader)
    curriculum_issues: list[str] = []
    ir_path = unit_dir / "input_row.json"
    if ir_path.exists():
        try:
            ir = _json.loads(ir_path.read_text())
            grade = ir.get("grade", "")
            codes = ir.get("curriculum_codes", []) or []
            exp = ir.get("curriculum_expectations", {}) or {}
            if codes and str(grade).strip().lower() not in ("k", "kindergarten"):
                from pipeline import curriculum as _cur
                bad = _cur.validate_codes(grade, codes)
                for c in bad:
                    curriculum_issues.append(f"invalid code for {grade}: {c}")
                for c in codes:
                    if c in exp:
                        try:
                            official = _cur.get(grade, c)["text"].strip()
                            if exp[c].strip() != official:
                                curriculum_issues.append(f"text drift on {c}")
                        except Exception:
                            curriculum_issues.append(f"could not verify {c}")
        except Exception as e:  # don't let a parse error masquerade as clean
            curriculum_issues.append(f"input_row parse error: {e}")
    if curriculum_issues:
        details["curriculum"] = curriculum_issues

    passed = not details
    return {
        "solution_run_passed": solution_ok,
        "curriculum_issues": len(curriculum_issues),
        "passed": passed,
        "details": {k: v[:20] for k, v in details.items()},
    }
