"""K-3 phonics/language worksheet product-quality rubric — the gate every
language sheet clears. Language analogue of ``pipeline/coding_rubric.py``.

Authoritative rubric *content* lives in ``coding/rubrics/rubric_language_{K,G1,G2,G3}.md``;
this module is book-keeping + the publish-gate decision + the language drift check.

Publish gate (all grades): **total >= 19/20 AND C2 >= L3 AND C3 = L4 AND C5 = L4.**
Only droppable point is C1 or C4 -> L3. C2 is the hard decodability/phonetic gate,
tied to ``decodability_run.json``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_DIR = PROJECT_ROOT / "coding" / "rubrics"
LANG_CURRICULUM = PROJECT_ROOT / "curriculum" / "language.json"

THRESHOLD = 19
MAX_PER_CRITERION = 4
N_CRITERIA = 5
MAX_SCORE = MAX_PER_CRITERION * N_CRITERIA  # 20

CRITERIA: tuple[str, ...] = ("C1", "C2", "C3", "C4", "C5")

CRITERION_LABELS: dict[str, str] = {
    "C1": "Ontario Strand-B/A Alignment",
    "C2": "Decodability & Phonetic Accuracy (hard gate)",
    "C3": "Structured-Phonics Pedagogy & Grade Fit (hard gate)",
    "C4": "Clarity, Layout & Template Fidelity",
    "C5": "Teacher Guide Completeness (hard gate)",
}

CRITERION_FLOORS: dict[str, int] = {"C2": 3, "C3": 4, "C5": 4}

REMEDIATION_MAP: dict[str, tuple[str, ...]] = {
    "C1": ("content",),
    "C2": ("decodability", "content"),
    "C3": ("content",),
    "C4": ("content",),
    "C5": ("content",),
}

_GRADE_TO_FILE: dict[str, str] = {
    "k": "rubric_language_K.md", "kindergarten": "rubric_language_K.md",
    "g1": "rubric_language_G1.md", "grade 1": "rubric_language_G1.md", "1": "rubric_language_G1.md",
    "g2": "rubric_language_G2.md", "grade 2": "rubric_language_G2.md", "2": "rubric_language_G2.md",
    "g3": "rubric_language_G3.md", "grade 3": "rubric_language_G3.md", "3": "rubric_language_G3.md",
}


def rubric_path(grade_label: str) -> Path:
    key = str(grade_label).strip().lower()
    if key not in _GRADE_TO_FILE:
        raise ValueError(f"unknown grade label {grade_label!r}")
    return RUBRIC_DIR / _GRADE_TO_FILE[key]


def _validate(scores: dict[str, int]) -> None:
    missing = [c for c in CRITERIA if c not in scores]
    if missing:
        raise ValueError(f"missing criteria: {missing}")
    for k, v in scores.items():
        if k not in CRITERIA:
            raise ValueError(f"unknown criterion {k!r}")
        if not isinstance(v, int) or not (1 <= v <= MAX_PER_CRITERION):
            raise ValueError(f"{k}: score must be int 1..{MAX_PER_CRITERION}, got {v!r}")


def floor_failures(scores: dict[str, int]) -> dict[str, tuple[int, int]]:
    _validate(scores)
    return {c: (scores[c], req) for c, req in CRITERION_FLOORS.items() if scores[c] < req}


def classify(scores: dict[str, int]) -> tuple[int, str, list[str]]:
    _validate(scores)
    total = sum(scores.values())
    reasons: list[str] = []
    if total < THRESHOLD:
        reasons.append(f"total {total}/{MAX_SCORE} < {THRESHOLD}")
    for crit, (got, req) in floor_failures(scores).items():
        reasons.append(f"{crit} ({CRITERION_LABELS[crit]}) = L{got}, needs L{req}")
    return total, ("pass" if not reasons else "fail"), reasons


def stages_needing_regen(scores: dict[str, int]) -> list[str]:
    _validate(scores)
    total = sum(scores.values())
    need: list[str] = []
    targets = {c: CRITERION_FLOORS.get(c, MAX_PER_CRITERION) for c in CRITERIA}
    for crit in CRITERIA:
        below = scores[crit] < targets[crit]
        soft = crit in ("C1", "C4") and total < THRESHOLD and scores[crit] < MAX_PER_CRITERION
        if below or soft:
            for s in REMEDIATION_MAP[crit]:
                if s not in need:
                    need.append(s)
    return need


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def pre_grade_drift_check(unit_dir: Path) -> dict:
    """Drift checks that MUST pass before a language grade can record 'pass':
      1. decodability_run.json exists and passed == True
      2. every Ontario code cited in content.json exists in curriculum/language.json
         for this grade AND the quoted text matches the official text verbatim
      3. image-word alignment: each image's word appears in the decodable text
    """
    unit_dir = Path(unit_dir)
    checks: dict[str, dict] = {}

    # (1) decodability
    dr = unit_dir / "decodability_run.json"
    dec_ok = dr.exists() and json.loads(dr.read_text()).get("passed") is True
    checks["decodability"] = {"passed": dec_ok,
                              "detail": "decodability_run.json passed" if dec_ok
                              else "decodability gate not passed / not run"}

    content = json.loads((unit_dir / "content.json").read_text())
    grade = str(content.get("phonics", {}).get("grade", "")).strip()

    # (2) curriculum citation drift
    lib = {}
    if LANG_CURRICULUM.exists():
        for e in json.loads(LANG_CURRICULUM.read_text())["expectations"]:
            lib[(str(e["grade"]), e["code"])] = _norm(e["text"])
    cited = content.get("phonics", {}).get("curriculum", [])  # [{code, text}]
    cur_problems = []
    for c in cited:
        key = (grade, c.get("code", ""))
        if key not in lib:
            cur_problems.append(f"code {c.get('code')} not in curriculum for grade {grade}")
        elif _norm(c.get("text", "")) not in lib[key] and lib[key] not in _norm(c.get("text", "")):
            cur_problems.append(f"text for {c.get('code')} does not match official wording verbatim")
    checks["curriculum"] = {"passed": (len(cited) > 0 and not cur_problems),
                            "detail": cur_problems or f"{len(cited)} citation(s) verbatim-matched"}

    # (3) image-word alignment
    decod_text = " ".join(content.get("phonics", {}).get("decodable_text", [])).lower()
    img_words = content.get("phonics", {}).get("image_words", [])  # [{word, src}]
    img_problems = [iw.get("word") for iw in img_words
                    if iw.get("word", "").lower() not in decod_text]
    checks["image_alignment"] = {"passed": not img_problems,
                                 "detail": img_problems and f"image words not in text: {img_problems}"
                                 or "all image words appear in decodable text"}

    passed = all(c["passed"] for c in checks.values())
    return {"passed": passed, "checks": checks}


def record_grade(unit_dir: Path, grade_label: str, scores: dict[str, int],
                 *, notes: str = "") -> dict:
    total, status, reasons = classify(scores)
    drift = pre_grade_drift_check(unit_dir)
    if not drift["passed"]:
        status = "fail"
        reasons = reasons + [f"drift: {k}" for k, v in drift["checks"].items() if not v["passed"]]
    rec = {"grade": grade_label, "scores": scores, "total": total, "max": MAX_SCORE,
           "status": status, "reasons": reasons, "drift": drift, "notes": notes}
    Path(unit_dir, "content_grade.json").write_text(json.dumps(rec, indent=2))
    return rec
