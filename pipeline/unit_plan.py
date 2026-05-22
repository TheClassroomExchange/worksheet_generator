"""Canonical plan for the K-G3 Math unit programme.

Encodes every unit, its anchor expectation, the specific codes it covers,
and which wave it belongs to. The plan is the source of truth for "what's
next" across multi-session generation: each session reads this module +
each unit folder's manifest to find the next pending stage anywhere in
the programme.

Total surface area: 40 units (4 done as of 2026-05-02 — the Pattern Parade
family for K, G1, G2, G3 covers C1.x algebra/patterns).

Units are organised into 4 waves so character casts and worksheet
templates can be reused across grades. Generate one wave at a time so
sibling-grade reuse compounds (e.g. K Counting Crew animals show up
again in G1 Number Friends).

Contract:

* Each ``UnitPlanEntry`` ties a unit_id (matches the directory name under
  ``generated_units/batch_*/``) to its grade, strand, anchor code, list
  of codes to cover, and a one-line title.
* ``status`` reflects the canonical state: planned, generating, complete.
  Persisted in ``unit_plan.json`` (the checkpoint file) so future sessions
  resume exactly where the last one stopped.
* ``next_unit_to_generate()`` returns the next non-complete entry in
  programme order. ``init_unit_from_plan(entry)`` materialises its folder.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAN_STATE_PATH = PROJECT_ROOT / "unit_plan.json"


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON to ``path`` via a same-directory tmpfile + os.replace.

    A crash mid-write can otherwise leave ``unit_plan.json`` half-formed —
    next session can't parse it and refresh_state_from_disk silently
    initialises a fresh state, dropping audits and statuses. The cost
    of atomicity is two filesystem syscalls; well worth it for the
    single source of truth that drives the entire programme runner.
    """
    import os
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


UnitStatus = Literal["complete", "in_progress", "planned"]


@dataclass
class UnitPlanEntry:
    unit_id: str                # directory name under generated_units/batch_*/
    batch: str                  # batch_1, batch_2, batch_3, etc.
    wave: int                   # 1=Number, 2=Algebra, 3=Data/Spatial, 4=Money/Coding/Modelling
    grade: str                  # "Kindergarten" | "Grade 1" | "Grade 2" | "Grade 3"
    strand: str                 # one-letter code: A, B, C, D, E, F (G1-3) or A/B (K)
    anchor_code: str            # the OVERALL expectation that anchors the unit (e.g. "B1")
    codes: list[str]            # the specific codes the unit will teach
    title: str                  # thematic_title in the blueprint
    descriptive_title: str      # marketplace-friendly long version
    status: UnitStatus = "planned"
    notes: str = ""


# ── The 40-unit programme ─────────────────────────────────────────────────
#
# Order within each wave is K → G1 → G2 → G3 so character casts mature.

PLAN: list[UnitPlanEntry] = [
    # ── WAVE 1 — Number (K-G3) ─────────────────────────────────────────
    UnitPlanEntry(
        unit_id="k_number_counting_crew",
        batch="batch_3", wave=1, grade="Kindergarten", strand="A",
        anchor_code="A6",
        codes=["A6.1", "A6.2", "A6.3", "A6.4", "A6.5", "A6.6"],
        title="The Counting Crew",
        descriptive_title="Kindergarten — Numbers to 10: Counting, Comparing, and Subitizing",
    ),
    UnitPlanEntry(
        unit_id="k_number_coin_counters",
        batch="batch_3", wave=1, grade="Kindergarten", strand="A",
        anchor_code="A6",
        codes=["A6.7", "A6.8", "A6.9", "A6.10", "A6.11", "A6.12", "A6.13"],
        title="Coin Counters",
        descriptive_title="Kindergarten — Operations and Coins to 25¢",
        notes="A6 split into 2 K units; this one covers operations + money.",
    ),
    UnitPlanEntry(
        unit_id="g1_number_friends",
        batch="batch_3", wave=1, grade="Grade 1", strand="B",
        anchor_code="B1",
        codes=["B1.1", "B1.2", "B1.3", "B1.4", "B1.5", "B1.6", "B1.7", "B1.8"],
        title="Number Friends to 50",
        descriptive_title="Grade 1 — Numbers, Fractions, and Place Value to 50",
    ),
    UnitPlanEntry(
        unit_id="g1_number_adding_machine",
        batch="batch_3", wave=1, grade="Grade 1", strand="B",
        anchor_code="B2",
        codes=["B2.1", "B2.2", "B2.3", "B2.4", "B2.5"],
        title="The Adding Machine",
        descriptive_title="Grade 1 — Sums and Differences to 20",
    ),
    UnitPlanEntry(
        unit_id="g2_number_place_value_detectives",
        batch="batch_3", wave=1, grade="Grade 2", strand="B",
        anchor_code="B1",
        codes=["B1.1", "B1.2", "B1.3", "B1.4", "B1.5", "B1.6", "B1.7"],
        title="Place Value Detectives",
        descriptive_title="Grade 2 — Hundreds, Tens, and Ones",
    ),
    UnitPlanEntry(
        unit_id="g2_number_groups_of",
        batch="batch_3", wave=1, grade="Grade 2", strand="B",
        anchor_code="B2",
        codes=["B2.1", "B2.2", "B2.3", "B2.4", "B2.5", "B2.6"],
        title="Groups of",
        descriptive_title="Grade 2 — Multiplication and Division Beginnings",
    ),
    UnitPlanEntry(
        unit_id="g3_number_fraction_street",
        batch="batch_3", wave=1, grade="Grade 3", strand="B",
        anchor_code="B1",
        codes=["B1.1", "B1.2", "B1.3", "B1.4", "B1.5", "B1.6", "B1.7"],
        title="Fraction Street",
        descriptive_title="Grade 3 — Equal Parts in Real Life",
    ),
    UnitPlanEntry(
        unit_id="g3_number_times_table_toolkit",
        batch="batch_3", wave=1, grade="Grade 3", strand="B",
        anchor_code="B2",
        codes=["B2.1", "B2.2", "B2.3", "B2.4", "B2.5", "B2.6", "B2.7", "B2.8", "B2.9"],
        title="The Times Table Toolkit",
        descriptive_title="Grade 3 — Multiplication and Division Facts to 10×10",
    ),

    # ── WAVE 2 — Algebra non-patterns (K, G1-G3) ───────────────────────
    UnitPlanEntry(
        unit_id="k_patterns_pattern_parade",
        batch="batch_1", wave=2, grade="Kindergarten", strand="A",
        anchor_code="A7", codes=["A7.1", "A7.2", "A7.3", "A7.4"],
        title="The Pattern Parade",
        descriptive_title="Kindergarten — Pattern Recognition with Coco the Conductor",
        status="complete",
        notes="Already shipped — Pattern Parade K, 20/20 strict_imgalign.",
    ),
    UnitPlanEntry(
        unit_id="g1_patterns_pattern_parade",
        batch="batch_2", wave=2, grade="Grade 1", strand="C",
        anchor_code="C1", codes=["C1.1", "C1.2", "C1.3", "C1.4"],
        title="The Pattern Parade — Pattern Rules and Number Patterns to 50",
        descriptive_title="Grade 1 — Pattern Rules with Bea, Finn, Bibi & Moss",
        status="complete",
        notes="Already shipped.",
    ),
    UnitPlanEntry(
        unit_id="g1_algebra_balance_stories",
        batch="batch_3", wave=2, grade="Grade 1", strand="C",
        anchor_code="C2", codes=["C2.1", "C2.2", "C2.3"],
        title="Balance Scale Stories",
        descriptive_title="Grade 1 — Equalities, Inequalities, and Unknowns",
    ),
    UnitPlanEntry(
        unit_id="g1_algebra_loop_the_loop",
        batch="batch_3", wave=2, grade="Grade 1", strand="C",
        anchor_code="C3", codes=["C3.1", "C3.2"],
        title="Loop the Loop",
        descriptive_title="Grade 1 — Repeating Instructions: Coding without Screens",
    ),
    UnitPlanEntry(
        unit_id="g1_algebra_real_life_modelling",
        batch="batch_3", wave=2, grade="Grade 1", strand="C",
        anchor_code="C4", codes=["C4"],
        title="Real-Life Math",
        descriptive_title="Grade 1 — Mathematical Modelling at the Sugar Bush",
    ),
    UnitPlanEntry(
        unit_id="g2_patterns_pattern_parade",
        batch="batch_2", wave=2, grade="Grade 2", strand="C",
        anchor_code="C1", codes=["C1.1", "C1.2", "C1.3", "C1.4"],
        title="The Pattern Parade — Growing, Shrinking, and Numbers to 100",
        descriptive_title="Grade 2 — Repeating, Growing, and Shrinking Patterns",
        status="complete",
        notes="Already shipped.",
    ),
    UnitPlanEntry(
        unit_id="g2_algebra_whats_missing",
        batch="batch_3", wave=2, grade="Grade 2", strand="C",
        anchor_code="C2", codes=["C2.1", "C2.2", "C2.3"],
        title="What's Missing?",
        descriptive_title="Grade 2 — Equations with Unknowns",
    ),
    UnitPlanEntry(
        unit_id="g2_algebra_if_then_detectives",
        batch="batch_3", wave=2, grade="Grade 2", strand="C",
        anchor_code="C3", codes=["C3.1", "C3.2"],
        title="If-Then Detectives",
        descriptive_title="Grade 2 — Coding with Conditions",
    ),
    UnitPlanEntry(
        unit_id="g2_algebra_real_life_modelling",
        batch="batch_3", wave=2, grade="Grade 2", strand="C",
        anchor_code="C4", codes=["C4"],
        title="Real-Life Math",
        descriptive_title="Grade 2 — Planning the Grade 2 Picnic",
    ),
    UnitPlanEntry(
        unit_id="g3_patterns_pattern_parade",
        batch="batch_2", wave=2, grade="Grade 3", strand="C",
        anchor_code="C1", codes=["C1.1", "C1.2", "C1.3", "C1.4"],
        title="The Pattern Parade — Operations, Big Numbers, and Justifying the Rule",
        descriptive_title="Grade 3 — Compound Rules and Far-Term Prediction",
        status="complete",
        notes="Already shipped.",
    ),
    UnitPlanEntry(
        unit_id="g3_algebra_balanced_equations",
        batch="batch_3", wave=2, grade="Grade 3", strand="C",
        anchor_code="C2", codes=["C2.1", "C2.2", "C2.3"],
        title="Balanced Equations",
        descriptive_title="Grade 3 — Same on Both Sides",
    ),
    UnitPlanEntry(
        unit_id="g3_algebra_bug_busters",
        batch="batch_3", wave=2, grade="Grade 3", strand="C",
        anchor_code="C3", codes=["C3.1", "C3.2"],
        title="Bug Busters",
        descriptive_title="Grade 3 — Find the Error in the Code",
    ),
    UnitPlanEntry(
        unit_id="g3_algebra_real_life_modelling",
        batch="batch_3", wave=2, grade="Grade 3", strand="C",
        anchor_code="C4", codes=["C4"],
        title="Real-Life Math",
        descriptive_title="Grade 3 — Designing the School Garden",
    ),

    # ── WAVE 3 — Data, Spatial, Measurement (K-G3) ─────────────────────
    UnitPlanEntry(
        unit_id="k_data_detectives",
        batch="batch_3", wave=3, grade="Kindergarten", strand="A",
        anchor_code="A8",
        codes=["A8.1", "A8.2", "A8.3", "A8.4"],
        title="Data Detectives",
        descriptive_title="Kindergarten — Collecting and Displaying Data",
    ),
    UnitPlanEntry(
        unit_id="k_spatial_shape_safari",
        batch="batch_3", wave=3, grade="Kindergarten", strand="A",
        anchor_code="A9",
        codes=["A9.1", "A9.2", "A9.3", "A9.4", "A9.5", "A9.6", "A9.7"],
        title="Shape Safari",
        descriptive_title="Kindergarten — 2D and 3D Shapes Around Us",
    ),
    UnitPlanEntry(
        unit_id="k_measurement_bigger_smaller",
        batch="batch_3", wave=3, grade="Kindergarten", strand="A",
        anchor_code="A10",
        codes=["A10.1", "A10.2"],
        title="Bigger, Smaller, Same",
        descriptive_title="Kindergarten — Comparing Length, Mass, and Capacity",
    ),
    UnitPlanEntry(
        unit_id="g1_data_detectives",
        batch="batch_3", wave=3, grade="Grade 1", strand="D",
        anchor_code="D1",
        codes=["D1.1", "D1.2", "D1.3", "D1.4", "D1.5"],
        title="Data Detectives",
        descriptive_title="Grade 1 — Surveys, Tally Charts, and Pictographs",
    ),
    UnitPlanEntry(
        unit_id="g1_data_likelihood",
        batch="batch_3", wave=3, grade="Grade 1", strand="D",
        anchor_code="D2",
        codes=["D2.1", "D2.2"],
        title="Sometimes, Always, Never",
        descriptive_title="Grade 1 — A First Look at Likelihood",
    ),
    UnitPlanEntry(
        unit_id="g1_spatial_mapping",
        batch="batch_3", wave=3, grade="Grade 1", strand="E",
        anchor_code="E1",
        codes=["E1.1", "E1.2", "E1.3", "E1.4", "E1.5"],
        title="Mapping the Classroom",
        descriptive_title="Grade 1 — Geometric Shapes, Position, and Movement",
    ),
    UnitPlanEntry(
        unit_id="g1_measurement_how_long",
        batch="batch_3", wave=3, grade="Grade 1", strand="E",
        anchor_code="E2",
        codes=["E2.1", "E2.2", "E2.3"],
        title="How Long?",
        descriptive_title="Grade 1 — Non-Standard Measurement",
    ),
    UnitPlanEntry(
        unit_id="g2_data_detectives",
        batch="batch_3", wave=3, grade="Grade 2", strand="D",
        anchor_code="D1",
        codes=["D1.1", "D1.2", "D1.3", "D1.4", "D1.5"],
        title="Data Detectives",
        descriptive_title="Grade 2 — Bar Graphs, Pictographs, and Tally Charts",
    ),
    UnitPlanEntry(
        unit_id="g2_data_what_could_happen",
        batch="batch_3", wave=3, grade="Grade 2", strand="D",
        anchor_code="D2",
        codes=["D2.1", "D2.2"],
        title="What Could Happen?",
        descriptive_title="Grade 2 — Likelihood with Spinners and Dice",
    ),
    UnitPlanEntry(
        unit_id="g2_spatial_mirror_mirror",
        batch="batch_3", wave=3, grade="Grade 2", strand="E",
        anchor_code="E1",
        codes=["E1.1", "E1.2", "E1.3", "E1.4", "E1.5"],
        title="Mirror, Mirror",
        descriptive_title="Grade 2 — Lines of Symmetry",
    ),
    UnitPlanEntry(
        unit_id="g2_measurement_how_heavy_how_tall",
        batch="batch_3", wave=3, grade="Grade 2", strand="E",
        anchor_code="E2",
        codes=["E2.1", "E2.2", "E2.3", "E2.4"],
        title="How Heavy, How Tall",
        descriptive_title="Grade 2 — Standard Units of Measurement",
    ),
    UnitPlanEntry(
        unit_id="g3_data_detectives",
        batch="batch_3", wave=3, grade="Grade 3", strand="D",
        anchor_code="D1",
        codes=["D1.1", "D1.2", "D1.3", "D1.4", "D1.5"],
        title="Data Detectives",
        descriptive_title="Grade 3 — Reading and Interpreting Graphs",
    ),
    UnitPlanEntry(
        unit_id="g3_data_likely_unlikely",
        batch="batch_3", wave=3, grade="Grade 3", strand="D",
        anchor_code="D2",
        codes=["D2.1", "D2.2"],
        title="Likely, Unlikely, Impossible",
        descriptive_title="Grade 3 — Predicting Outcomes",
    ),
    UnitPlanEntry(
        unit_id="g3_spatial_map_it_move_it",
        batch="batch_3", wave=3, grade="Grade 3", strand="E",
        anchor_code="E1",
        codes=["E1.1", "E1.2", "E1.3", "E1.4"],
        title="Map It, Move It",
        descriptive_title="Grade 3 — Geometry in 2D and 3D",
    ),
    UnitPlanEntry(
        unit_id="g3_measurement_fencing_the_farm",
        batch="batch_3", wave=3, grade="Grade 3", strand="E",
        anchor_code="E2",
        codes=["E2.1","E2.2","E2.3","E2.4","E2.5","E2.6","E2.7","E2.8","E2.9"],
        title="Fencing the Farm",
        descriptive_title="Grade 3 — Perimeter and Area",
    ),

    # ── WAVE 4 — Coding (K) + Financial Literacy (K-G3) ───────────────
    UnitPlanEntry(
        unit_id="k_coding_little_programmers",
        batch="batch_3", wave=4, grade="Kindergarten", strand="B",
        anchor_code="B11",
        codes=["B11.1", "B11.2", "B11.3"],
        title="Little Programmers",
        descriptive_title="Kindergarten — Foundational Coding Concepts",
        notes="Rebuild on this pipeline of Michelle's existing 'Little Programmers' deck.",
    ),
    UnitPlanEntry(
        unit_id="g1_financial_classroom_market",
        batch="batch_3", wave=4, grade="Grade 1", strand="F",
        anchor_code="F1",
        codes=["F1.1"],
        title="Our Classroom Market",
        descriptive_title="Grade 1 — Canadian Coins and Their Values",
    ),
    UnitPlanEntry(
        unit_id="g2_financial_tap_to_pay",
        batch="batch_3", wave=4, grade="Grade 2", strand="F",
        anchor_code="F1",
        codes=["F1.1"],
        title="Tap to Pay",
        descriptive_title="Grade 2 — Modern Money in Canada",
    ),
    UnitPlanEntry(
        unit_id="g3_financial_plan_your_party",
        batch="batch_3", wave=4, grade="Grade 3", strand="F",
        anchor_code="F1",
        codes=["F1.1"],
        title="Plan Your Party",
        descriptive_title="Grade 3 — A Budgeting Challenge",
    ),
]


# ── Resume helpers ────────────────────────────────────────────────────────


def by_unit_id(unit_id: str) -> UnitPlanEntry | None:
    for e in PLAN:
        if e.unit_id == unit_id:
            return e
    return None


def load_state() -> dict:
    """Read unit_plan.json (the canonical checkpoint state). Returns
    {unit_id: status, ...}. Missing file or unknown ids fall back to the
    code-defined defaults in PLAN."""
    if not PLAN_STATE_PATH.exists():
        return {e.unit_id: e.status for e in PLAN}
    raw = json.loads(PLAN_STATE_PATH.read_text(encoding="utf-8"))
    state = {e.unit_id: e.status for e in PLAN}
    for k, v in (raw.get("statuses") or {}).items():
        if k in state:
            state[k] = v
    return state


def save_state(statuses: dict[str, str]) -> None:
    """Persist {unit_id: status} to unit_plan.json. Validates against PLAN.

    Preserves any sibling keys already on disk (most importantly ``audits``,
    written by ``record_audit``) — earlier revisions of this function did
    a write-without-read and silently wiped audit history every time
    ``refresh_state_from_disk`` ran at session start.
    """
    valid_ids = {e.unit_id for e in PLAN}
    cleaned = {k: v for k, v in statuses.items() if k in valid_ids}
    # Read-modify-write so we don't clobber `audits` (or future sibling keys).
    if PLAN_STATE_PATH.exists():
        try:
            existing = json.loads(PLAN_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    else:
        existing = {}
    existing.update({
        "schema_version": 1,
        "total_units": len(PLAN),
        "complete": sum(1 for v in cleaned.values() if v == "complete"),
        "in_progress": sum(1 for v in cleaned.values() if v == "in_progress"),
        "planned": sum(1 for v in cleaned.values() if v == "planned"),
        "statuses": cleaned,
    })
    _atomic_write_json(PLAN_STATE_PATH, existing)


def refresh_state_from_disk() -> dict[str, str]:
    """Scan generated_units/ and recompute statuses from manifests:
    - all 16 stages done AND deck file exists → complete
    - some stages done → in_progress
    - no folder yet → planned
    Persists the result to unit_plan.json and returns it."""
    statuses: dict[str, str] = {}
    units_dir = PROJECT_ROOT / "generated_units"
    for entry in PLAN:
        if entry.status == "complete":
            statuses[entry.unit_id] = "complete"
            continue
        # Look for an existing folder
        candidates = list(units_dir.glob(f"batch_*/{entry.unit_id}"))
        if not candidates:
            statuses[entry.unit_id] = "planned"
            continue
        ud = candidates[0]
        manifest_path = ud / "manifest.json"
        if not manifest_path.exists():
            statuses[entry.unit_id] = "planned"
            continue
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            statuses[entry.unit_id] = "in_progress"
            continue
        all_done = all(s.get("status") == "done" for s in m.get("stages", {}).values())
        deck_present = (ud / "validation_export.pdf").exists()
        # Unit completion ALSO requires rubric_grade to have status='pass' inside
        # the JSON. A schema-valid rubric_grade with status='fail' (e.g., due to
        # placeholder hero artwork) keeps the unit in_progress — without this
        # check, a "fail" rubric was being reported as complete because the
        # stage itself was marked done. Added 2026-05-03.
        rg_pass = False
        if all_done:
            rg_path = ud / "7_rubric_grade.json"
            if rg_path.exists():
                try:
                    rg_pass = json.loads(rg_path.read_text(encoding="utf-8")).get("status") == "pass"
                except Exception:
                    rg_pass = False
        statuses[entry.unit_id] = "complete" if (all_done and deck_present and rg_pass) else "in_progress"
    save_state(statuses)
    return statuses


def next_unit_to_generate() -> UnitPlanEntry | None:
    """Return the next unit to work on:
       1. any unit currently in_progress (resume)
       2. else the next planned unit in PLAN order
       Returns None if all units are complete."""
    statuses = load_state()
    # Prefer resuming an in_progress unit
    for e in PLAN:
        if statuses.get(e.unit_id) == "in_progress":
            return e
    # Then start the next planned one
    for e in PLAN:
        if statuses.get(e.unit_id, "planned") == "planned":
            return e
    return None


# ── Audit state (incremental QA) ─────────────────────────────────────────
#
# The weekly QA task can't audit all 40 units in one session — it would
# time out before finishing. So audit state is per-unit and persistent.
# Each `unit_plan.json` entry can carry:
#   - last_audited_at : ISO8601 UTC timestamp (string), or "" if never
#   - last_audit_status: "pass" | "fail" | "" if never audited
#   - last_audit_issues: list[str] of issues from the last audit, capped at 10
#
# `stalest_units(n)` returns the N units most overdue for re-audit:
# never-audited first, then oldest `last_audited_at`. Used by the daily
# deep-QA cron to pick its scope. Each fire records its results
# immediately so a timed-out session never costs progress.


def _audit_state() -> dict[str, dict]:
    """Read the audit-state portion of unit_plan.json."""
    if not PLAN_STATE_PATH.exists():
        return {}
    raw = json.loads(PLAN_STATE_PATH.read_text(encoding="utf-8"))
    return raw.get("audits") or {}


def _save_audit_state(audits: dict[str, dict]) -> None:
    """Persist {unit_id: {last_audited_at, last_audit_status, last_audit_issues}}.
    Reads-modifies-writes unit_plan.json so existing statuses survive."""
    if PLAN_STATE_PATH.exists():
        raw = json.loads(PLAN_STATE_PATH.read_text(encoding="utf-8"))
    else:
        raw = {"schema_version": 1, "statuses": {}}
    raw["audits"] = audits
    _atomic_write_json(PLAN_STATE_PATH, raw)


def stalest_units(n: int = 10, only_complete: bool = True) -> list[UnitPlanEntry]:
    """Return the N units most overdue for QA audit.

    Order: never-audited first (alphabetical for determinism), then by
    ascending `last_audited_at`. When ``only_complete=True`` (default),
    units still in_progress or planned are excluded — they get audited
    naturally as they finish stages, so QA focuses on shipped units that
    might have drifted since last check.
    """
    statuses = load_state()
    audits = _audit_state()
    pool: list[UnitPlanEntry] = []
    for e in PLAN:
        if only_complete and statuses.get(e.unit_id) != "complete":
            continue
        pool.append(e)

    def sort_key(e: UnitPlanEntry):
        a = audits.get(e.unit_id) or {}
        last = a.get("last_audited_at") or ""
        return (last, e.unit_id)

    pool.sort(key=sort_key)
    return pool[:n]


def record_audit(unit_id: str, *, status: str, issues: list[str]) -> None:
    """Persist the result of one audit pass against this unit.

    Uses the same tz-aware ISO-8601 form as ``manifest._utcnow``, so all
    timestamps in ``unit_plan.json`` and ``manifest.json`` files share a
    single format that any downstream tooling can parse with
    ``datetime.fromisoformat``.
    """
    import datetime as _dt
    if status not in ("pass", "fail"):
        raise ValueError(f"audit status must be 'pass' or 'fail', got {status!r}")
    audits = _audit_state()
    audits[unit_id] = {
        "last_audited_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "last_audit_status": status,
        "last_audit_issues": (issues or [])[:10],
    }
    _save_audit_state(audits)


def audit_summary() -> str:
    """Pretty programme-wide audit status. Used at QA-task end-of-run."""
    audits = _audit_state()
    statuses = load_state()
    lines = ["Audit status (complete units only):"]
    n_pass = n_fail = n_never = 0
    for e in PLAN:
        if statuses.get(e.unit_id) != "complete":
            continue
        a = audits.get(e.unit_id) or {}
        last = a.get("last_audited_at") or "(never)"
        st = a.get("last_audit_status") or "—"
        issues_n = len(a.get("last_audit_issues") or [])
        if st == "pass": n_pass += 1
        elif st == "fail": n_fail += 1
        else: n_never += 1
        mark = {"pass": "✓", "fail": "✗", "—": "○"}[st]
        lines.append(f"  {mark} {e.unit_id:38s} {last:22s}  "
                     f"{st:5s}  {issues_n} issue(s)")
    lines.append("")
    lines.append(f"  pass: {n_pass}   fail: {n_fail}   never-audited: {n_never}")
    return "\n".join(lines)


# ── Stage-generation in-flight detection ────────────────────────────────
#
# Scheduled tasks must not trample over each other or over an interactive
# session that is mid-stage. The detector below answers ONE narrow
# question: is there a stage currently being generated right now (by any
# session) that I would race on if I picked the next pending stage?
#
# It does NOT defer just because Claude Code is open. The user wants the
# programme to drain 24/7 regardless of whether they're using the app —
# only an actual content-generation collision should pause a fire.
#
# Detection signal: any manifest stage with status `in_progress` AND a
# `started_at` timestamp within the last `threshold_minutes` minutes.
# This is the precise signal of "stage generation in flight":
#   - in_progress is set when mark(stage, "in_progress") fires inside
#     complete_stage's lifecycle
#   - it gets cleared when the stage completes (status -> done) or fails
#     (status -> failed) or is reverted (status -> pending)
#   - a stale `in_progress` (started_at very old) is a crashed session,
#     not a live race — the cron should NOT defer for that
#
# Threshold default: 10 minutes. A real stage takes 5-15 min of session
# time to generate, so this catches in-flight work without being so long
# that a crashed session blocks future fires forever.
#
# Renamed 2026-05-02: was `is_user_session_active`, but the JSONL signal
# was too aggressive — having Claude Code open for any reason blocked the
# programme. The user explicitly does NOT want that. The new name reflects
# the actual question being answered.


def is_stage_generation_in_flight(threshold_minutes: int = 10) -> tuple[bool, str]:
    """Return (is_active, reason). True if any unit's manifest shows a
    stage in_progress with started_at less than ``threshold_minutes``
    minutes ago. Used by cron tasks to defer when a real content-
    generation race is in progress.

    Has nothing to do with whether the user has Claude Code open. The
    programme is meant to drain 24/7 regardless."""
    import json as _json
    from datetime import datetime as _dt, timezone as _tz

    threshold_s = threshold_minutes * 60
    now_utc = _dt.now(_tz.utc)

    units_root = PROJECT_ROOT / "generated_units"
    if not units_root.exists():
        return False, "no generated_units yet"

    for m_path in units_root.glob("batch_*/*/manifest.json"):
        try:
            m = _json.loads(m_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for stage_key, st in (m.get("stages") or {}).items():
            if st.get("status") != "in_progress":
                continue
            started = st.get("started_at")
            if not started:
                continue
            # manifest._utcnow emits the standard ISO-8601 form with a
            # ``+00:00`` offset (e.g. "2026-05-02T13:11:14+00:00"); some
            # older audit timestamps still use a trailing ``Z``. Accept
            # both — the previous parser only accepted ``Z`` and silently
            # skipped every real entry, breaking cron race protection.
            normalised = started.replace("Z", "+00:00") if started.endswith("Z") else started
            try:
                dt = _dt.fromisoformat(normalised)
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_tz.utc)
            age_s = (now_utc - dt).total_seconds()
            if age_s < threshold_s:
                return True, (
                    f"stage in flight: {m_path.parent.name}/{stage_key} "
                    f"in_progress for {int(age_s)}s (<{threshold_minutes}m threshold)"
                )

    return False, "no in-flight stage generation"


# Backwards-compat alias. The cron prompts call the old name; keep it as
# a thin wrapper so nothing breaks if a fire from before the rename hits.
def is_user_session_active(threshold_minutes: int = 10) -> tuple[bool, str]:
    """Deprecated alias for is_stage_generation_in_flight. Same semantics
    as the new function — JSONL signal removed 2026-05-02."""
    return is_stage_generation_in_flight(threshold_minutes=threshold_minutes)


def init_unit_from_plan(entry: UnitPlanEntry) -> Path:
    """Materialise the unit on disk: create the directory under
    generated_units/<batch>/<unit_id>/, write input_row.json (curriculum
    text pulled verbatim from pipeline.curriculum), and initialise the
    manifest with all 16 stages pending. Idempotent — re-running on an
    existing unit is a no-op (returns the existing path).

    The blueprint stage is NOT generated here; that's the runner's first
    Claude-in-chat job. This function just sets up the queue.
    """
    from pipeline import curriculum as _curr
    from pipeline import manifest as _manifest

    units_root = PROJECT_ROOT / "generated_units" / entry.batch
    unit_dir = units_root / entry.unit_id
    if (unit_dir / "manifest.json").exists():
        return unit_dir

    units_root.mkdir(parents=True, exist_ok=True)
    unit_dir.mkdir(exist_ok=True)

    # Pull verbatim Ontario text for every cited code
    expectations: dict[str, str] = {}
    for code in entry.codes:
        row = _curr.get(entry.grade, code)
        if row is None:
            raise ValueError(
                f"{entry.unit_id}: code {code!r} not in local Ontario reference "
                f"for {entry.grade!r}. Fix the plan or fetch the curriculum."
            )
        expectations[code] = row["text"]

    # Build the input_row.json — frozen spreadsheet snapshot per the
    # cardinal-rule contract.
    input_row = {
        "batch": entry.batch,
        "grade": entry.grade,
        "subject": "Mathematics",
        "strand": entry.strand,
        "anchor_code": entry.anchor_code,
        "thematic_title": entry.title,
        "descriptive_title": entry.descriptive_title,
        "curriculum_codes": list(entry.codes),
        "curriculum_expectations": expectations,
        "curriculum_source_url": (
            f"https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-mathematics/"
            f"grades/{'g' + entry.grade.split()[-1].lower() if 'Grade' in entry.grade else 'kindergarten'}-math"
        ),
        "duration_days": 5,
        "wave": entry.wave,
        "plan_notes": entry.notes,
    }
    (unit_dir / "input_row.json").write_text(
        json.dumps(input_row, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Init the manifest. batch is an int per the cardinal contract; we
    # parse it from "batch_N".
    batch_int = int(entry.batch.rsplit("_", 1)[-1]) if "_" in entry.batch else 0
    _manifest.init_unit(
        unit_dir=unit_dir,
        unit_id=entry.unit_id,
        batch=batch_int,
        row_number=None,             # programmatic creation; spreadsheet row not used
        runner="claude-multi-unit",
        prompt_version="2026-05-02",
        num_lessons=5,
        input_row=input_row,
    )
    return unit_dir


def status_table() -> str:
    """Pretty programme-wide status. Used at session start."""
    statuses = load_state()
    lines = [
        f"K-G3 Math programme: {len(PLAN)} units total",
        f"  complete:    {sum(1 for s in statuses.values() if s == 'complete')}",
        f"  in_progress: {sum(1 for s in statuses.values() if s == 'in_progress')}",
        f"  planned:     {sum(1 for s in statuses.values() if s == 'planned')}",
        "",
    ]
    waves: dict[int, list[UnitPlanEntry]] = {}
    for e in PLAN:
        waves.setdefault(e.wave, []).append(e)
    for w in sorted(waves):
        wave_name = {1: "Number", 2: "Algebra", 3: "Data/Spatial/Measurement",
                     4: "Coding & Financial Literacy"}.get(w, f"Wave {w}")
        lines.append(f"Wave {w} — {wave_name}:")
        for e in waves[w]:
            mark = {"complete": "✓", "in_progress": "…", "planned": "○"}[
                statuses.get(e.unit_id, "planned")]
            lines.append(f"  {mark} {e.grade:13s} {e.strand}  "
                         f"{e.anchor_code:5s}  {e.unit_id:38s}  {e.title}")
        lines.append("")
    return "\n".join(lines)
