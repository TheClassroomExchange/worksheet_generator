"""
Manifest read/write helpers.

The manifest is the single source of truth for "where is this unit in the pipeline."
Every stage transition is recorded atomically (write-temp + rename).

Usage from a Claude session:

    from pipeline.manifest import load, save, mark, init_unit, next_pending

    m = load(unit_dir)
    next_stage = next_pending(m)
    # ... generate the stage's JSON, write it ...
    mark(unit_dir, "blueprint", "done", extra={"output_path": "0_blueprint.json"})
"""

from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .stages import Stage, stages_for_unit
from .schemas import validate_stage_file, consistency_check
# Imported lazily inside complete_stage() to keep load-time light and avoid
# any future circular imports if density / curriculum modules grow:
#   from .density import validate_lesson_density
#   from .curriculum_reference import verify_curriculum_text


SCHEMA_VERSION = 1


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: Path, data: str) -> None:
    """Write `data` to `path` atomically. Survives crashes mid-write."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def init_unit(
    unit_dir: Path,
    *,
    unit_id: str,
    batch: int,
    row_number: int | None,
    input_row: dict,
    num_lessons: int = 5,
    runner: str = "claude_code_max",
    prompt_version: str = "v1.0",
) -> dict:
    """
    Create a unit folder + manifest + frozen input_row.json.
    Idempotent: if the manifest already exists, returns it untouched.
    """
    unit_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = unit_dir / "manifest.json"
    input_row_path = unit_dir / "input_row.json"

    if manifest_path.exists():
        return load(unit_dir)

    stage_objs = stages_for_unit(num_lessons=num_lessons)
    stage_states = {
        st.key: {
            "label": st.label,
            "short": st.short,
            "output_filename": st.output_filename,
            "depends_on": list(st.depends_on),
            "status": "pending",
            "attempts": 0,
        }
        for st in stage_objs
    }

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "unit_id": unit_id,
        "batch": batch,
        "row_number": row_number,
        "runner": runner,
        "prompt_version": prompt_version,
        "num_lessons": num_lessons,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
        "status": "pending",
        "stages": stage_states,
        "stage_order": [st.key for st in stage_objs],
        "errors": [],
    }

    _atomic_write(input_row_path, json.dumps(input_row, indent=2, ensure_ascii=False))
    _atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def load(unit_dir: Path) -> dict:
    return json.loads((unit_dir / "manifest.json").read_text(encoding="utf-8"))


def migrate_manifest(unit_dir: Path) -> list[str]:
    """Add any stages defined in ``stages_for_unit()`` that are missing from
    this unit's manifest. Existing stage state is preserved untouched. Used
    when new stages are added to the pipeline (e.g., ``rubric_grade``) and
    older units need to pick them up without re-init.

    Returns the list of stage keys that were added (empty if already current).
    """
    manifest = load(unit_dir)
    num_lessons = manifest.get("num_lessons", 5)
    canonical = stages_for_unit(num_lessons=num_lessons)
    added: list[str] = []
    for st in canonical:
        if st.key in manifest["stages"]:
            continue
        manifest["stages"][st.key] = {
            "label": st.label,
            "short": st.short,
            "output_filename": st.output_filename,
            "depends_on": list(st.depends_on),
            "status": "pending",
            "attempts": 0,
            "added_by_migration_at": _utcnow(),
        }
        added.append(st.key)
    # Refresh stage_order to canonical ordering.
    manifest["stage_order"] = [st.key for st in canonical]
    if added:
        save(unit_dir, manifest)
    return added


def save(unit_dir: Path, manifest: dict) -> None:
    manifest["updated_at"] = _utcnow()
    # Recompute top-level status from stage statuses.
    stage_statuses = [s["status"] for s in manifest["stages"].values()]
    if all(s == "done" for s in stage_statuses):
        manifest["status"] = "done"
    elif any(s == "failed" for s in stage_statuses):
        # Failed only if no stages remain that we could still try
        if any(s in ("pending", "in_progress") for s in stage_statuses):
            manifest["status"] = "in_progress"
        else:
            manifest["status"] = "failed"
    elif any(s in ("done", "in_progress") for s in stage_statuses):
        manifest["status"] = "in_progress"
    else:
        manifest["status"] = "pending"
    _atomic_write(unit_dir / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))


def mark(
    unit_dir: Path,
    stage_key: str,
    new_status: str,
    *,
    error: str | None = None,
    extra: dict | None = None,
    skip_validation: bool = False,
) -> dict:
    """
    Transition a stage to `new_status`. Valid statuses:
      pending → in_progress → done
      in_progress → failed → in_progress (retry) → done

    Records attempt count, completion timestamp, and any error.

    When transitioning to `done`, the stage's output file is validated against
    its Pydantic schema. Validation failure raises and prevents the transition.
    Pass `skip_validation=True` only for stages whose schema is not yet defined.
    """
    valid = {"pending", "in_progress", "done", "failed"}
    if new_status not in valid:
        raise ValueError(f"invalid status {new_status!r}; must be one of {valid}")

    manifest = load(unit_dir)
    if stage_key not in manifest["stages"]:
        raise KeyError(f"stage {stage_key!r} not in manifest for {unit_dir}")

    stage = manifest["stages"][stage_key]
    prev = stage["status"]

    # ── Schema gate before letting a stage become `done` ──
    if new_status == "done" and not skip_validation:
        result = validate_stage_file(unit_dir, stage_key, stage["output_filename"])
        if not result.ok and result.errors and result.errors != "(no schema registered yet for this stage)":
            raise ValueError(
                f"schema validation failed for {stage_key}: {result.errors}"
            )

    stage["status"] = new_status

    if new_status == "in_progress":
        stage["attempts"] = stage.get("attempts", 0) + 1
        stage["started_at"] = _utcnow()
        stage.pop("last_error", None)
    elif new_status == "done":
        stage["completed_at"] = _utcnow()
        stage.pop("last_error", None)
    elif new_status == "failed":
        stage["last_error"] = error or "(no error message)"
        stage["failed_at"] = _utcnow()
        manifest["errors"].append({
            "stage": stage_key,
            "attempt": stage.get("attempts", 1),
            "error": error,
            "timestamp": _utcnow(),
        })

    if extra:
        stage.update(extra)

    save(unit_dir, manifest)
    _append_log(unit_dir, {
        "ts": _utcnow(),
        "stage": stage_key,
        "transition": f"{prev}→{new_status}",
        "attempt": stage.get("attempts"),
        "error": error,
    })
    return manifest


def next_pending(manifest: dict) -> str | None:
    """
    Return the key of the next stage that is ready to run.
    A stage is ready when all its `depends_on` stages are `done`,
    and its own status is `pending` or `failed`.
    Returns None if nothing is runnable (either all done, or all blocked).
    """
    stages = manifest["stages"]
    for key in manifest["stage_order"]:
        st = stages[key]
        if st["status"] in ("done", "in_progress"):
            continue
        deps = st.get("depends_on", [])
        if all(stages[d]["status"] == "done" for d in deps):
            return key
    return None


def _append_log(unit_dir: Path, row: dict) -> None:
    log_path = unit_dir / "run.log.jsonl"
    line = json.dumps(row, ensure_ascii=False)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── High-level helpers: complete_stage and retry_failed ────────────────────


def _print_advisory_warnings(unit_dir: Path, stage_key: str,
                             output_path: Path) -> None:
    """
    Run non-blocking advisory checks for the stage that just passed schema
    validation. Prints any warnings to stdout. Never raises.

    Currently runs:
      - For lesson_NN stages: density check (teacher_script length, action
        step count, consolidation prompt count for the blueprint's grade).
      - For blueprint stage: curriculum-text check (input_row.json verbatim
        text vs the in-repo REFERENCE for the unit's grade).

    Add more advisory checks here as they're built — they should be cheap,
    idempotent, and non-blocking.
    """
    # Lesson density — only fire on lesson stages
    if stage_key.startswith("lesson_"):
        try:
            from .density import validate_lesson_density
            warns = validate_lesson_density(unit_dir, output_path)
            for w in warns:
                print(f"  [density] {w}")
        except Exception as e:  # never let advisory crash the stage
            print(f"  [density] advisory check failed: {e}")

    # Curriculum verification — fire on blueprint
    if stage_key == "blueprint":
        try:
            from .curriculum_reference import verify_curriculum_text
            issues = verify_curriculum_text(unit_dir)
            for i in issues:
                print(f"  [curriculum] {i}")
        except Exception as e:
            print(f"  [curriculum] advisory check failed: {e}")


def complete_stage(unit_dir: Path, stage_key: str, *, extra: dict | None = None) -> dict:
    """
    Canonical 'finish a stage' call. Use this instead of mark(..., 'done') directly.

    Validates the stage's output JSON against its Pydantic schema. On success,
    marks the stage `done`. On failure, preserves the bad output as
    `<stage_key>.attempt_<N>.failed.json`, marks the stage `failed` with the
    error message, logs the failure to run.log.jsonl, and returns the manifest
    (does NOT raise). The next session can call retry_failed() to reset and try
    again — full evidence is on disk.

    This is the contract: every stage transition is recoverable, and every
    failure leaves enough behind that a cold session can resume.
    """
    manifest = load(unit_dir)
    if stage_key not in manifest["stages"]:
        raise KeyError(f"stage {stage_key!r} not in manifest for {unit_dir}")
    stage = manifest["stages"][stage_key]
    output_filename = stage["output_filename"]
    output_path = unit_dir / output_filename

    if not output_path.exists():
        return mark(unit_dir, stage_key, "failed",
                    error=f"output file missing: {output_filename}")

    result = validate_stage_file(unit_dir, stage_key, output_filename)
    if result.ok or result.errors == "(no schema registered yet for this stage)":
        merged = {"output_path": output_filename}
        if extra:
            merged.update(extra)

        # Advisory checks — non-blocking. They print warnings to stdout so the
        # session-runner sees them, but they never mark the stage failed.
        # Stage still becomes `done` even if the advisory check has issues.
        _print_advisory_warnings(unit_dir, stage_key, output_path)

        # We pass skip_validation=True because we just validated above; this
        # avoids reading the file twice and double-running validators.
        return mark(unit_dir, stage_key, "done", extra=merged, skip_validation=True)

    # Validation failed: preserve the bad attempt and record failure.
    attempt_n = stage.get("attempts", 1)
    failed_copy = unit_dir / f"{stage_key}.attempt_{attempt_n}.failed.json"
    try:
        failed_copy.write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception:
        pass  # best effort; missing copy is fine — file is still on disk

    err_msg = result.errors[:500] if result.errors else "validation failed"
    return mark(unit_dir, stage_key, "failed",
                error=f"schema validation failed: {err_msg}")


def retry_failed(unit_dir: Path, stage_key: str | None = None) -> list[str]:
    """
    Reset failed stages back to `pending` so they can be picked up.
    Preserves attempt count and `last_error` for forensic context.

    Args:
        unit_dir: the unit folder to inspect.
        stage_key: if given, retry only that stage; otherwise retry all failed.

    Returns:
        List of stage keys reset.
    """
    manifest = load(unit_dir)
    reset: list[str] = []
    for key, st in manifest["stages"].items():
        if stage_key is not None and key != stage_key:
            continue
        if st["status"] != "failed":
            continue
        mark(unit_dir, key, "pending",
             extra={"reset_after_failure_at": _utcnow()},
             skip_validation=True)
        reset.append(key)
    return reset


def mark_for_remediation(unit_dir: Path) -> list[str]:
    """Reset stages flagged in this unit's RubricGrade as needing regen.

    Reads ``7_rubric_grade.json``. If its ``status`` is ``"fail"``, every
    stage listed in ``remediation[*].stages_to_regen`` is reset to
    ``pending`` (with the per-criterion fix_summary recorded in
    ``last_error``). The ``rubric_grade`` stage itself is also reset so a
    fresh grade is required after the regen completes.

    Returns the list of stage keys that were reset (deduplicated, in pipeline
    order). Empty list if the grade is missing or already passing.
    """
    grade_path = unit_dir / "7_rubric_grade.json"
    if not grade_path.exists():
        return []
    try:
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if grade.get("status") != "fail":
        return []

    # Order matters — reset in pipeline order so next_pending picks them up
    # in the right sequence. Dedupe while preserving order.
    seen: list[str] = []
    summaries: dict[str, list[str]] = {}
    for rem in grade.get("remediation", []):
        fix = rem.get("fix_summary", "(no summary)")
        crit = rem.get("criterion", "?")
        for stage_key in rem.get("stages_to_regen", []) or []:
            summaries.setdefault(stage_key, []).append(f"[{crit}] {fix}")
            if stage_key not in seen:
                seen.append(stage_key)

    manifest = load(unit_dir)
    reset: list[str] = []
    for stage_key in seen:
        if stage_key not in manifest["stages"]:
            continue
        msg = "rubric remediation: " + " ; ".join(summaries[stage_key])
        # Mark pending, skip schema validation (we're going TO pending, not done).
        # Note: mark() only stores `error` on 'failed' transitions, so we
        # record the fix_summary in `extra` so the runner sees it on next pickup.
        mark(unit_dir, stage_key, "pending",
             extra={
                 "reset_for_remediation_at": _utcnow(),
                 "remediation_fix_summary": msg,
             },
             skip_validation=True)
        reset.append(stage_key)

    # Reset rubric_grade itself so a fresh grade is required afterwards.
    if "rubric_grade" in manifest["stages"] and \
       manifest["stages"]["rubric_grade"]["status"] != "pending":
        mark(unit_dir, "rubric_grade", "pending",
             extra={
                 "reset_for_remediation_at": _utcnow(),
                 "remediation_fix_summary":
                     f"awaiting re-grade after remediation of {len(reset)} upstream stage(s)",
             },
             skip_validation=True)
        reset.append("rubric_grade")

    return reset


def list_failed(batch_dir: Path) -> list[tuple[str, str, str]]:
    """
    Return [(unit_id, stage_key, last_error)] for every failed stage in the batch.
    Used by sessions to see what needs human attention.
    """
    out: list[tuple[str, str, str]] = []
    if not batch_dir.exists():
        return out
    for unit_dir in sorted(p for p in batch_dir.iterdir() if p.is_dir()):
        if not (unit_dir / "manifest.json").exists():
            continue
        m = load(unit_dir)
        for key, st in m["stages"].items():
            if st["status"] == "failed":
                out.append((m["unit_id"], key, st.get("last_error", "(no message)")))
    return out


# ── Tiny status renderer (no CLI yet, just a function) ─────────────────────
def status_table(batch_dir: Path) -> str:
    """Render a quick text status table for all units in a batch dir."""
    if not batch_dir.exists():
        return f"(no batch dir at {batch_dir})"
    rows = []
    for unit_dir in sorted(p for p in batch_dir.iterdir() if p.is_dir()):
        if not (unit_dir / "manifest.json").exists():
            continue
        m = load(unit_dir)
        total = len(m["stages"])
        done = sum(1 for s in m["stages"].values() if s["status"] == "done")
        failed = sum(1 for s in m["stages"].values() if s["status"] == "failed")
        progress = f"{done}/{total}" + (f"  ⚠ {failed} failed" if failed else "")
        rows.append((m["unit_id"], m["status"], progress))
    if not rows:
        return f"(no units in {batch_dir})"
    width = max(len(r[0]) for r in rows)
    lines = [f"{'unit':<{width}}  {'status':<14}  progress",
             "─" * (width + 36)]
    for unit_id, status, progress in rows:
        lines.append(f"{unit_id:<{width}}  {status:<14}  {progress}")
    # Append failed details if any
    failed_rows = list_failed(batch_dir)
    if failed_rows:
        lines.append("")
        lines.append("Failed stages needing retry:")
        for uid, sk, err in failed_rows:
            lines.append(f"  • {uid} / {sk}: {err[:120]}")
        lines.append("")
        lines.append("To retry: from pipeline.manifest import retry_failed; retry_failed(unit_dir)")
    return "\n".join(lines)
