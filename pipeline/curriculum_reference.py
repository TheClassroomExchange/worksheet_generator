"""Curriculum-text verification.

Each unit's ``input_row.json`` carries the codes and verbatim expectation text
that flows into rubrics, marketplace listings, and lesson plans. This module
diffs that text against the authoritative Ontario MOE reference cached at
``curriculum/`` (see ``pipeline.curriculum`` and ``pipeline.curriculum_fetch``).

Until 2026-04-29 the reference here was a hand-curated dict of best-effort
guesses, because the Ontario site is JS-rendered and we couldn't fetch it.
We now pull from the public Kontent.ai delivery API behind dcp.edu.gov.on.ca,
so the reference is authoritative for the grades that have been fetched
(K + G1-3 today).

Usage::

    from pipeline.curriculum_reference import verify_curriculum_text
    issues = verify_curriculum_text(unit_dir)
    for i in issues: print(i)

Issues are non-blocking — they're advisory, like density warnings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline import curriculum as _curr


def _load_input_row(unit_dir: Path) -> dict[str, Any] | None:
    p = unit_dir / "input_row.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _normalize(text: str) -> str:
    return " ".join((text or "").split()).lower()


def verify_curriculum_text(unit_dir: Path) -> list[str]:
    """Diff the unit's input_row.json curriculum text against the local
    Ontario reference. Returns a list of human-readable issues; empty list
    means no diffs found."""
    row = _load_input_row(unit_dir)
    if row is None:
        return [f"curriculum: input_row.json missing or unreadable in {unit_dir.name}"]

    grade = row.get("grade")
    if grade is None:
        return ["curriculum: input_row.json has no 'grade' field"]

    try:
        _curr._norm_grade(grade)
    except ValueError:
        return [f"curriculum: grade {grade!r} not covered by local reference (only K, G1-3 fetched)"]

    issues: list[str] = []
    row_codes = row.get("curriculum_codes") or []
    row_exps = row.get("curriculum_expectations") or {}

    unknown = _curr.validate_codes(grade, row_codes)
    for code in unknown:
        issues.append(
            f"curriculum [{grade}].{code}: code does not exist in Ontario reference"
        )

    for code in row_codes:
        if code in unknown:
            continue
        ref = _curr.get(grade, code)
        if code not in row_exps:
            issues.append(
                f"curriculum [{grade}].{code}: missing from input_row.curriculum_expectations"
            )
            continue
        if _normalize(row_exps[code]) != _normalize(ref["text"]):
            issues.append(
                f"curriculum [{grade}].{code}: text differs from Ontario reference\n"
                f"    input_row : {row_exps[code]!r}\n"
                f"    reference : {ref['text']!r}"
            )

    return issues


def report_reference_status() -> list[str]:
    """One-line summary per grade currently covered by the local reference."""
    out: list[str] = []
    for grade in _curr.available_grades():
        n_overall = len(_curr.list_codes(grade, expectation_type="overall"))
        n_specific = len(_curr.list_codes(grade, expectation_type="specific"))
        out.append(
            f"  {grade:<3}  {n_overall:>3} overall + {n_specific:>4} specific  "
            f"(source: ws.api.dcp.edu.gov.on.ca, cached locally)"
        )
    return out
