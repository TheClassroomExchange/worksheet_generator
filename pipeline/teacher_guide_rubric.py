"""Teacher-Guide plain-language rubric — the gate every coding sheet's
``teacher_guide`` block clears before re-publish.

Sibling of ``pipeline/coding_rubric.py`` (which grades the *student worksheet*).
This module grades ONLY the teacher-facing guide for plain-language quality:
a teacher with zero coding experience must be able to teach the page cold.

Authoritative rubric *content* lives in
``coding/rubrics/rubric_teacher_guide.md``; this module is pure book-keeping +
the publish-gate decision + a lightweight jargon linter. Scoring itself is done
by Claude in chat (the runner) — no Anthropic API calls in plumbing.

Publish gate: **total ≥ 18/20 AND T1 = L4 AND T4 = L4.**
T1 = plain language, T4 = answer-key correctness — the two non-negotiables.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_DIR = PROJECT_ROOT / "coding" / "rubrics"
RUBRIC_FILE = RUBRIC_DIR / "rubric_teacher_guide.md"

THRESHOLD = 18           # out of 20 — the publish bar (one droppable point)
MAX_PER_CRITERION = 4
N_CRITERIA = 5
MAX_SCORE = MAX_PER_CRITERION * N_CRITERIA  # 20

CRITERIA: tuple[str, ...] = ("T1", "T2", "T3", "T4", "T5")

CRITERION_LABELS: dict[str, str] = {
    "T1": "Plain language / no-experience accessibility (hard gate)",
    "T2": "Step-by-step facilitation a first-timer can follow",
    "T3": "Tool / setup guidance",
    "T4": "Answer-key correctness & clarity (hard gate)",
    "T5": "Curriculum link + differentiation (plain)",
}

# T1 and T4 must both be L4 — the plain-language and answer-correctness floors.
CRITERION_FLOORS: dict[str, int] = {"T1": 4, "T4": 4}

# Lifting any criterion = re-author the teacher_guide block in content.json.
REMEDIATION_MAP: dict[str, tuple[str, ...]] = {c: ("content",) for c in CRITERIA}

RUBRIC_VERSION = "tg_plainlang_v1_2026_06_21"

# Tokens that signal the guide still reads technical. Advisory only — the runner
# decides T1, but these surface likely jargon so it isn't missed. Matched
# case-insensitively as substrings inside teacher_guide prose.
JARGON_TOKENS: tuple[str, ...] = (
    "for-loop", "for loop", "range(", "sprite", "run-gate", "run gate",
    "computational representation", "boolean", "variable",
    "concurrent", "iterate", "iteration", "syntax", "compile",
    "function call", "parameter", "increment",
)


def _validate(scores: dict[str, int]) -> None:
    if set(scores.keys()) != set(CRITERIA):
        raise ValueError(f"scores must contain exactly {CRITERIA}, got {sorted(scores)}")
    for k, v in scores.items():
        if not isinstance(v, int) or v < 1 or v > MAX_PER_CRITERION:
            raise ValueError(f"{k}: score must be int 1..{MAX_PER_CRITERION}, got {v!r}")


def floor_failures(scores: dict[str, int]) -> dict[str, tuple[int, int]]:
    """Return {criterion: (got, required)} for every per-criterion floor not met."""
    _validate(scores)
    return {
        crit: (scores[crit], req)
        for crit, req in CRITERION_FLOORS.items()
        if scores[crit] < req
    }


def classify(scores: dict[str, int]) -> tuple[int, str, list[str]]:
    """Return (total, status, reasons). status == 'pass' iff
    total >= THRESHOLD AND every per-criterion floor is met."""
    _validate(scores)
    total = sum(scores.values())
    reasons: list[str] = []
    if total < THRESHOLD:
        reasons.append(f"total {total}/{MAX_SCORE} < {THRESHOLD}")
    for crit, (got, req) in floor_failures(scores).items():
        reasons.append(f"{crit} ({CRITERION_LABELS[crit]}) = L{got}, needs L{req}")
    return total, ("pass" if not reasons else "fail"), reasons


def stages_needing_regen(scores: dict[str, int]) -> list[str]:
    """The teacher guide lives in content.json, so any shortfall regenerates
    that one stage. Returns ['content'] when anything is below target, else []."""
    _validate(scores)
    total = sum(scores.values())
    targets = {c: CRITERION_FLOORS.get(c, MAX_PER_CRITERION) for c in CRITERIA}
    short = total < THRESHOLD or any(scores[c] < targets[c] for c in CRITERIA)
    return ["content"] if short else []


def _is_verbatim_citation(line: str) -> bool:
    """A line that IS the protected verbatim Ontario quote (kept word-for-word).
    Jargon inside it ('computational representations', 'concurrent') is allowed —
    the plain-language gloss handles it — so it's excluded from jargon scanning."""
    s = line.strip().lower()
    return s.startswith("c3.") or s.startswith("k-frame") or s.startswith("c1.") \
        or s.startswith("c2.")


def _tg_lines(unit_dir: Path) -> list[str]:
    """All teacher_guide prose text + titles in a content.json, as a list of
    lowercase lines. Empty list if no teacher guide found."""
    cj = unit_dir / "content.json"
    if not cj.exists():
        return []
    tg = json.loads(cj.read_text()).get("teacher_guide", {})
    lines: list[str] = []
    for part in tg.get("parts", []):
        lines.append(str(part.get("title", "")))
        txt = part.get("text", "")
        lines.extend(str(t) for t in (txt if isinstance(txt, list) else [txt]))
    return [ln.lower() for ln in lines]


def lint_teacher_guide(unit_dir: Path) -> dict:
    """Advisory pre-grade lint of a sheet's teacher_guide block. Flags:
      - leftover jargon tokens in NON-citation prose (signals T1 not yet L4),
      - a verbatim citation present but NO 'in plain terms:' gloss
        (signals T5 missing its plain-language gloss).
    Verbatim Ontario quotes are excluded from jargon scanning (kept word-for-word).
    Returns {jargon_hits: [...], missing_gloss: bool, clean: bool}.
    Does not score — the runner scores; this just surfaces likely misses.
    """
    lines = _tg_lines(unit_dir)
    scannable = "\n".join(ln for ln in lines if not _is_verbatim_citation(ln))
    full = "\n".join(lines)
    jargon_hits = sorted({tok for tok in JARGON_TOKENS if tok in scannable})
    has_citation = any(_is_verbatim_citation(ln) for ln in lines)
    has_gloss = "in plain terms:" in full
    missing_gloss = bool(has_citation and not has_gloss)
    return {
        "jargon_hits": jargon_hits,
        "missing_gloss": missing_gloss,
        "clean": not jargon_hits and not missing_gloss,
    }


def record_grade(unit_dir: Path, grade: str, scores: dict[str, int]) -> dict:
    """Write tg_grade.json next to content_grade.json and return the record."""
    total, status, reasons = classify(scores)
    record = {
        "grade": grade,
        "rubric": RUBRIC_FILE.name,
        "rubric_version": RUBRIC_VERSION,
        "scores": scores,
        "total": total,
        "status": status,
        "gate_reasons": reasons,
        "lint": lint_teacher_guide(unit_dir),
    }
    (unit_dir / "tg_grade.json").write_text(json.dumps(record, indent=2) + "\n")
    return record
