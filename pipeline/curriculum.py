"""Read-only loader for the local Ontario curriculum reference.

Files live in ``worksheet_generator/curriculum/`` and are produced by
``pipeline.curriculum_fetch``. Two files today:

  * ``math.json``         — Grades 1-3 mathematics (2020 curriculum)
  * ``kindergarten.json`` — Kindergarten 2026 framework, all 4 frames

Each row has ``grade``, ``subject``, ``strand_code``, ``code``,
``expectation_type`` ("overall" | "specific"), ``text``, and more.

The blueprint stage is the only place that introduces curriculum codes; this
loader exists so ``consistency_check`` can verify those codes are real.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable

CURRICULUM_DIR = Path(__file__).resolve().parent.parent / "curriculum"

# Spreadsheet uses friendly grade labels ("Grade 1", "Kindergarten"); the
# curriculum files use bare grade keys ("1", "K"). Normalise both ways.
_GRADE_ALIASES = {
    "k": "K", "kindergarten": "K",
    "1": "1", "grade 1": "1", "g1": "1",
    "2": "2", "grade 2": "2", "g2": "2",
    "3": "3", "grade 3": "3", "g3": "3",
}


def _norm_grade(grade: str) -> str:
    key = (grade or "").strip().lower()
    if key in _GRADE_ALIASES:
        return _GRADE_ALIASES[key]
    raise ValueError(f"unknown grade label: {grade!r}")


@lru_cache(maxsize=1)
def _all_rows() -> list[dict]:
    rows: list[dict] = []
    for fname in ("math.json", "kindergarten.json"):
        path = CURRICULUM_DIR / fname
        if not path.exists():
            continue
        rows.extend(json.loads(path.read_text())["expectations"])
    return rows


def _index() -> dict[tuple[str, str], dict]:
    """Map (normalised_grade, code) → row. Includes both overall and specific."""
    out: dict[tuple[str, str], dict] = {}
    for r in _all_rows():
        if r["code"]:
            out[(r["grade"], r["code"])] = r
    return out


def get(grade: str, code: str) -> dict | None:
    """Return the curriculum row for (grade, code), or None if not found."""
    return _index().get((_norm_grade(grade), code.strip()))


def expectation_text(grade: str, code: str) -> str | None:
    row = get(grade, code)
    return row["text"] if row else None


def validate_codes(grade: str, codes: Iterable[str]) -> list[str]:
    """Return the list of codes from ``codes`` that don't exist for the grade.

    Empty list = all codes valid. The caller decides what to do with misses;
    consistency_check turns them into validation issues.
    """
    g = _norm_grade(grade)
    idx = _index()
    return [c for c in codes if (g, c.strip()) not in idx]


def list_codes(grade: str, subject: str | None = None,
               strand_code: str | None = None,
               expectation_type: str | None = None) -> list[str]:
    """List curriculum codes matching the filters. Useful when debugging
    blueprints by hand."""
    g = _norm_grade(grade)
    out = []
    for r in _all_rows():
        if r["grade"] != g:
            continue
        if subject and r["subject"] != subject:
            continue
        if strand_code and r["strand_code"] != strand_code:
            continue
        if expectation_type and r["expectation_type"] != expectation_type:
            continue
        if r["code"]:
            out.append(r["code"])
    return out


def available_grades() -> list[str]:
    return sorted({r["grade"] for r in _all_rows()})
