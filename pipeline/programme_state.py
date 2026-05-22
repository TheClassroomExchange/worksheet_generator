"""Programme-level state for multi-unit drives.

A *programme* is a coordinated effort that spans multiple units (e.g. the
2026-05 math retrofit, or the K-G3 Language SoR rollout). One Claude
session may not finish the whole programme; the next session resumes by
reading this file.

Per-unit progress is still owned by `pipeline/manifest.py`. This file is a
**superset index**: which units exist, what phase each one is in, which
unit to work on next.

File location: ``<repo>/programme_state/<programme_name>.json``.

Phase model (the new pipeline's three phases):
    - ``content``      — JSON stages + pair gates + overall unit gate
    - ``svg``          — character SVG art for unit's recurring characters
    - ``build``        — compose worksheets, build deck, visual inspection
    - ``done``         — published, deck URL captured

Status values for a unit:
    - ``pending``      — declared but no work done yet
    - ``in_progress``  — currently being worked on
    - ``blocked``      — needs human attention (rubric stuck, drive error, etc.)
    - ``done``         — fully shipped (deck published, visual inspection passed)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "programme_state"

Phase = Literal["content", "svg", "build", "done"]
UnitStatus = Literal["pending", "in_progress", "blocked", "done"]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: Path, data: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def _state_path(programme_name: str) -> Path:
    STATE_DIR.mkdir(exist_ok=True)
    return STATE_DIR / f"{programme_name}.json"


# ── CRUD ──────────────────────────────────────────────────────────────


def init_programme(
    programme_name: str,
    *,
    subject: Literal["Mathematics", "Language"],
    grade_band: str,
    units: list[dict],
    description: str = "",
) -> dict:
    """Create a new programme state file.

    ``units`` is a list of dicts with keys ``unit_id`` and ``unit_dir``
    (absolute path string). Other per-unit fields are filled in with
    defaults.

    Idempotent: if the state file exists, returns it unchanged.
    """
    p = _state_path(programme_name)
    if p.exists():
        return load(programme_name)

    now = _utcnow()
    state = {
        "schema_version": 1,
        "programme_name": programme_name,
        "subject": subject,
        "grade_band": grade_band,
        "description": description,
        "created_at": now,
        "updated_at": now,
        "units": {
            u["unit_id"]: {
                "unit_id": u["unit_id"],
                "unit_dir": u["unit_dir"],
                "phase": "content",
                "status": "pending",
                "deck_url": None,
                "drive_folder_id": None,
                "last_event": None,
                "last_event_at": None,
                "blockers": [],
            }
            for u in units
        },
        "unit_order": [u["unit_id"] for u in units],
    }
    _atomic_write(p, json.dumps(state, indent=2))
    return state


def load(programme_name: str) -> dict:
    p = _state_path(programme_name)
    if not p.exists():
        raise FileNotFoundError(f"No programme state at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def save(programme_name: str, state: dict) -> None:
    state["updated_at"] = _utcnow()
    _atomic_write(_state_path(programme_name), json.dumps(state, indent=2))


def list_programmes() -> list[str]:
    if not STATE_DIR.exists():
        return []
    return sorted(p.stem for p in STATE_DIR.glob("*.json"))


# ── Updates ───────────────────────────────────────────────────────────


def update_unit(
    programme_name: str,
    unit_id: str,
    *,
    phase: Phase | None = None,
    status: UnitStatus | None = None,
    deck_url: str | None = None,
    drive_folder_id: str | None = None,
    event: str | None = None,
    blockers: list[str] | None = None,
) -> dict:
    """Update one unit's record. Only the kwargs you pass are touched."""
    state = load(programme_name)
    if unit_id not in state["units"]:
        raise KeyError(f"unit {unit_id!r} not in programme {programme_name!r}")
    u = state["units"][unit_id]
    if phase is not None:
        u["phase"] = phase
    if status is not None:
        u["status"] = status
    if deck_url is not None:
        u["deck_url"] = deck_url
    if drive_folder_id is not None:
        u["drive_folder_id"] = drive_folder_id
    if blockers is not None:
        u["blockers"] = blockers
    if event is not None:
        u["last_event"] = event
        u["last_event_at"] = _utcnow()
    save(programme_name, state)
    return u


def advance_phase(programme_name: str, unit_id: str) -> dict:
    """Move a unit to the next phase, marking the previous one done.

    content → svg → build → done

    The unit's ``status`` is reset to ``pending`` for the new phase, since
    a fresh phase always begins in pending until you start work on it.
    Once you reach ``done``, status flips to ``done`` automatically.
    """
    order = ["content", "svg", "build", "done"]
    state = load(programme_name)
    u = state["units"][unit_id]
    cur = u["phase"]
    if cur == "done":
        return u
    nxt = order[order.index(cur) + 1]
    u["phase"] = nxt
    u["status"] = "done" if nxt == "done" else "pending"
    u["last_event"] = f"advanced to {nxt}"
    u["last_event_at"] = _utcnow()
    save(programme_name, state)
    return u


# ── Queries ───────────────────────────────────────────────────────────


def next_unit(programme_name: str,
              target_phase: Phase | None = "content") -> dict | None:
    """Pick the next unit to work on.

    Priority:
      1. Any unit currently ``in_progress`` (resume it). When
         ``target_phase`` is set, only resume units in that phase.
      2. Any unit ``pending`` in earliest declared order. When
         ``target_phase`` is set, only pick units currently in that phase.
      3. None — no work left in the target phase (or programme complete).

    ``target_phase=None`` reverts to legacy behaviour (any phase).
    Default ``"content"`` means the breadth-first content drain skips units
    that have already passed content gates and are awaiting Phase C batch.
    """
    state = load(programme_name)
    def matches_phase(u: dict) -> bool:
        return target_phase is None or u.get("phase") == target_phase
    in_progress = [
        u for u in state["units"].values()
        if u["status"] == "in_progress" and matches_phase(u)
    ]
    if in_progress:
        return in_progress[0]
    for uid in state["unit_order"]:
        u = state["units"][uid]
        if u["status"] == "pending" and matches_phase(u):
            return u
    return None


def progress_summary(programme_name: str) -> dict:
    state = load(programme_name)
    counts: dict[str, int] = {
        "pending": 0, "in_progress": 0, "blocked": 0, "done": 0,
    }
    by_phase: dict[str, int] = {
        "content": 0, "svg": 0, "build": 0, "done": 0,
    }
    for u in state["units"].values():
        counts[u["status"]] = counts.get(u["status"], 0) + 1
        by_phase[u["phase"]] = by_phase.get(u["phase"], 0) + 1
    return {
        "programme_name": programme_name,
        "total": len(state["units"]),
        "by_status": counts,
        "by_phase": by_phase,
        "updated_at": state["updated_at"],
    }
