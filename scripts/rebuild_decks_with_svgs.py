"""Rebuild all 40 decks after introducing custom character SVGs.

Resumable, single-process driver. State lives in
.svg_rebuild_checkpoint.json at the project root. Re-running the script
skips units that have completed all phases.

Per-unit phases (in order):
  1. compose       — call compose_for_unit(unit_dir) so composed/*.png is
                     refreshed with the new SVG-derived character cards.
  2. preflight     — call validate_unit_for_slides(unit_dir); warnings are
                     logged but non-blocking (consistent with project
                     convention).
  3. clean_decks   — delete every prior Google Slides presentation in the
                     unit's Drive folder so only the newly built deck
                     remains afterwards.
  4. build_deck    — call build_unit_deck(run_preflight=False) and store
                     the deck URL.

The checkpoint records {phase: success|error, ...} per unit so a partially
processed unit picks up where it left off on the next run. The final
report is printed at the end.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.unit_plan import load_state, by_unit_id, init_unit_from_plan
from pipeline.compose import compose_for_unit
from pipeline.slides import (
    build_unit_deck,
    validate_unit_for_slides,
    UNIT_DECK_PARENT_FOLDER_ID,
    _find_or_create_subfolder,
    get_credentials,
)
from googleapiclient.discovery import build

CHECKPOINT = PROJECT_ROOT / ".svg_rebuild_checkpoint.json"
LOG = PROJECT_ROOT / ".svg_rebuild_log.txt"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_ckpt() -> dict:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text())
    return {"started_at": _now(), "units": {}}


def _save_ckpt(ckpt: dict) -> None:
    ckpt["updated_at"] = _now()
    CHECKPOINT.write_text(json.dumps(ckpt, indent=2) + "\n")


def _log(msg: str) -> None:
    print(msg, flush=True)
    with LOG.open("a") as f:
        f.write(f"[{_now()}] {msg}\n")


def _delete_prior_decks(drive, unit_folder_id: str, unit_id: str) -> int:
    """List and delete all Google Slides presentations in unit_folder_id.

    Returns the number deleted. Does not raise — best-effort cleanup, since
    a missing-folder or rate-limit hit shouldn't block the rebuild.
    """
    if not unit_folder_id:
        return 0
    q = (
        f"'{unit_folder_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.presentation' and "
        f"trashed = false"
    )
    try:
        res = drive.files().list(q=q, fields="files(id,name)", pageSize=50).execute()
    except Exception as e:
        _log(f"    (could not list decks for {unit_id}: {e})")
        return 0
    files = res.get("files", [])
    deleted = 0
    for f in files:
        try:
            drive.files().delete(fileId=f["id"]).execute()
            deleted += 1
            _log(f"    deleted prior deck '{f['name']}' ({f['id']})")
        except Exception as e:
            _log(f"    (could not delete {f['name']}: {e})")
    return deleted


def _resolve_unit_folder_id(drive, entry, bp: dict) -> str | None:
    """Mirror slides.build_unit_deck's folder logic so we can clean prior
    decks before the build runs (otherwise the new deck would coexist with
    the old one until build completed).

    The parent is UNIT_DECK_PARENT_FOLDER_ID. Published units land directly
    under it; ungraded/failed land under "_drafts". Since these 40 units are
    all 'complete' (per unit_plan), we resolve to the published path.
    """
    parent_id = UNIT_DECK_PARENT_FOLDER_ID or None
    if not parent_id:
        return None
    name = bp.get("thematic_title") or entry.unit_id
    try:
        return _find_or_create_subfolder(drive, parent_id, name)
    except Exception as e:
        _log(f"    (could not resolve unit folder for {entry.unit_id}: {e})")
        return None


def process_unit(drive, entry, ckpt: dict) -> None:
    unit_id = entry.unit_id
    state = ckpt["units"].setdefault(unit_id, {})

    # 1. compose
    if state.get("compose") != "ok":
        _log(f"[{unit_id}] composing images…")
        try:
            unit_dir = init_unit_from_plan(entry)
            compose_for_unit(unit_dir)
            state["compose"] = "ok"
            state["unit_dir"] = str(unit_dir)
            _save_ckpt(ckpt)
        except Exception as e:
            state["compose"] = f"error: {e}"
            _save_ckpt(ckpt)
            _log(f"  ✗ compose failed: {e}")
            return

    unit_dir = Path(state["unit_dir"])

    # 2. preflight
    if state.get("preflight") != "ok":
        _log(f"[{unit_id}] preflight…")
        warns = validate_unit_for_slides(unit_dir)
        state["preflight_warnings"] = warns
        state["preflight"] = "ok"  # warnings non-blocking
        _save_ckpt(ckpt)
        if warns:
            _log(f"  ⚠ {len(warns)} preflight warning(s) (non-blocking)")

    # 3. clean prior decks
    if state.get("clean_decks") != "ok":
        bp_path = unit_dir / "0_blueprint.json"
        bp = json.loads(bp_path.read_text())
        unit_folder_id = _resolve_unit_folder_id(drive, entry, bp)
        state["unit_folder_id"] = unit_folder_id
        deleted = _delete_prior_decks(drive, unit_folder_id, unit_id)
        state["prior_decks_deleted"] = deleted
        state["clean_decks"] = "ok"
        _save_ckpt(ckpt)
        _log(f"  ✓ deleted {deleted} prior deck(s)")

    # 4. build new deck (with retry on transient Drive-propagation errors)
    if state.get("build_deck") != "ok":
        _log(f"[{unit_id}] building deck…")
        last_err: Exception | None = None
        for attempt in range(1, 5):
            try:
                url = build_unit_deck(unit_dir, run_preflight=False)
                state["deck_url"] = url
                state["build_deck"] = "ok"
                state["build_attempts"] = attempt
                state["completed_at"] = _now()
                _save_ckpt(ckpt)
                _log(f"  ✓ {url}")
                last_err = None
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                # Drive sometimes hasn't finished propagating freshly-uploaded
                # public images by the time the Slides batchUpdate fires.
                # That surfaces as a 400 "publicly accessible" error. Retry
                # with backoff. Other errors fall through to the failure path.
                if "publicly accessible" in msg or "createImage" in msg:
                    backoff = 5 * attempt  # 5, 10, 15s
                    _log(f"  ⟲ build attempt {attempt} hit propagation error; "
                         f"retrying in {backoff}s")
                    time.sleep(backoff)
                else:
                    break
        if last_err is not None:
            state["build_deck"] = f"error: {last_err}"
            _save_ckpt(ckpt)
            _log(f"  ✗ build_unit_deck failed after retries: {last_err}")


def main():
    ckpt = _load_ckpt()
    state = load_state()
    unit_ids = sorted(state.keys())

    _log(f"=== Rebuild driver run @ {_now()} ===")
    _log(f"Total units: {len(unit_ids)}")

    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    for i, unit_id in enumerate(unit_ids, 1):
        # Skip completely done units
        s = ckpt["units"].get(unit_id, {})
        if (s.get("compose") == "ok" and s.get("preflight") == "ok"
                and s.get("clean_decks") == "ok" and s.get("build_deck") == "ok"):
            continue
        entry = by_unit_id(unit_id)
        if entry is None:
            _log(f"[{unit_id}] no plan entry; skipping")
            continue
        _log(f"\n--- [{i}/{len(unit_ids)}] {unit_id} ---")
        process_unit(drive, entry, ckpt)

    # Summary
    done = sum(1 for s in ckpt["units"].values() if s.get("build_deck") == "ok")
    failed = sum(1 for s in ckpt["units"].values()
                 if isinstance(s.get("build_deck"), str) and s["build_deck"].startswith("error"))
    _log(f"\n=== Summary: {done}/{len(unit_ids)} decks built, {failed} failed ===")


if __name__ == "__main__":
    main()
