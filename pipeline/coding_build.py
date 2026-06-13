"""
coding_build.py — per-sheet build helpers for the coding pipeline.

Two operations the manifest stages call:
  • run_solution(unit_dir)  → execute solution.py (the code-runs gate), write
    solution_run.json {passed, returncode, stdout}. Returns passed: bool.
  • render_sheet(unit_dir)  → load content.json, render the worksheet +
    teacher-guide PDFs via pipeline.worksheet_pdf, write render.json. Returns
    the two PDF paths.

content.json shape:
    {
      "title": "Loops: Code That Repeats",
      "worksheet":     { <worksheet_pdf spec> },
      "teacher_guide": { <worksheet_pdf spec> }
    }
Asset paths inside the specs (``mascot`` and each image part's ``src``) are
stored **repo-relative** (e.g. "assets/mascots/bit_wave.svg") and resolved to
absolute here, so content.json stays machine-independent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _resolve_paths(spec: dict) -> dict:
    """Return a copy of a worksheet_pdf spec with mascot + image srcs made
    absolute (relative to repo root if not already absolute)."""
    out = dict(spec)
    if "mascot" in out and not Path(out["mascot"]).is_absolute():
        out["mascot"] = str((ROOT / out["mascot"]).resolve())
    parts = []
    for part in out.get("parts", []):
        p = dict(part)
        if p.get("type") == "image" and "src" in p and not Path(p["src"]).is_absolute():
            p["src"] = str((ROOT / p["src"]).resolve())
        parts.append(p)
    out["parts"] = parts
    return out


def run_solution(unit_dir: Path) -> bool:
    """Execute solution.py and record the result. The code-runs gate."""
    unit_dir = Path(unit_dir)
    sol = unit_dir / "solution.py"
    if not sol.exists():
        (unit_dir / "solution_run.json").write_text(
            json.dumps({"passed": False, "error": "solution.py missing"}, indent=2))
        return False
    proc = subprocess.run(
        [sys.executable, str(sol)],
        capture_output=True, text=True, timeout=60,
    )
    passed = proc.returncode == 0
    (unit_dir / "solution_run.json").write_text(json.dumps({
        "passed": passed,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-2000:],
    }, indent=2, ensure_ascii=False))
    return passed


def render_sheet(unit_dir: Path) -> dict:
    """Render the worksheet + teacher-guide PDFs from content.json."""
    from pipeline.worksheet_pdf import render_pdf  # lazy: needs WeasyPrint libs

    unit_dir = Path(unit_dir)
    content = json.loads((unit_dir / "content.json").read_text(encoding="utf-8"))
    title = content.get("title", "Worksheet")
    # Clean filename base: a colon in the display title (e.g. "Loops: Code That
    # Repeats") is poor in a filename / Drive URL. Use file_title if given, else
    # turn ": " into " — " and strip any stray colons.
    fbase = content.get("file_title") or title.replace(": ", " — ").replace(":", "-")

    ws_path = unit_dir / f"{fbase} — Worksheet.pdf"
    tg_path = unit_dir / f"{fbase} — Teacher Guide.pdf"
    # Teacher guides render in compact mode so a full guide (incl. the two
    # verbatim C3 citations) reliably fits one page — no per-sheet hand-trimming.
    tg_spec = _resolve_paths(content["teacher_guide"])
    tg_spec.setdefault("compact", True)
    render_pdf(_resolve_paths(content["worksheet"]), ws_path)
    render_pdf(tg_spec, tg_path)

    render = {
        "worksheet_pdf": ws_path.name,
        "teacher_guide_pdf": tg_path.name,
    }
    (unit_dir / "render.json").write_text(json.dumps(render, indent=2, ensure_ascii=False))
    return render


def build_to_render(unit_dir: Path, *, unit_id: str, input_row: dict,
                    scores: dict, grade_label: str, rubric_file: str) -> dict:
    """Walk a sheet's manifest from init through `render`, enforcing the gates:
    code-runs (solution) → content schema → content_grade (≥19/20 + floors +
    drift) → render. Stops BEFORE visual_grade (which needs human/visual
    inspection of the rendered PDFs). Requires solution.py + content.json to
    already exist in unit_dir. Returns a summary dict.

    Raises RuntimeError if the run-gate or the content_grade gate fails — the
    sheet does NOT render ungraded.
    """
    from pipeline import manifest, stages, coding_rubric

    unit_dir = Path(unit_dir)
    manifest.init_unit(unit_dir, unit_id=unit_id, batch=1, row_number=None,
                       input_row=input_row,
                       stage_objs=stages.coding_stages_for_sheet())

    # stage 0 — solution (code-runs gate)
    manifest.mark(unit_dir, "solution", "in_progress", skip_validation=True)
    if not run_solution(unit_dir):
        manifest.mark(unit_dir, "solution", "failed", error="run-gate failed")
        raise RuntimeError(f"{unit_id}: solution run-gate FAILED — see solution_run.json")
    manifest.complete_stage(unit_dir, "solution")

    # stage 1 — content (content.json must exist; passes manifest no-schema check)
    if not (unit_dir / "content.json").exists():
        raise RuntimeError(f"{unit_id}: content.json missing")
    manifest.mark(unit_dir, "content", "in_progress", skip_validation=True)
    manifest.complete_stage(unit_dir, "content")

    # stage 2 — content_grade (BEFORE render): rubric + floors + drift
    total, status, reasons = coding_rubric.classify(scores)
    drift = coding_rubric.pre_grade_drift_check(unit_dir)
    grade_rec = {
        "grade": grade_label, "rubric": rubric_file,
        "scores": scores, "total": total, "status": status,
        "gate_reasons": reasons, "drift": drift,
        "rubric_version": coding_rubric.RUBRIC_VERSION,
    }
    (unit_dir / "content_grade.json").write_text(
        json.dumps(grade_rec, indent=2, ensure_ascii=False))
    if status != "pass" or not drift["passed"]:
        manifest.mark(unit_dir, "content_grade", "failed",
                      error=f"gate fail: {reasons}; drift={drift['passed']}")
        for s in coding_rubric.stages_needing_regen(scores):
            manifest.mark(unit_dir, s, "pending", skip_validation=True)
        raise RuntimeError(f"{unit_id}: content_grade FAILED {total}/20 {reasons} "
                           f"drift={drift['passed']} — render blocked")
    manifest.mark(unit_dir, "content_grade", "in_progress", skip_validation=True)
    manifest.complete_stage(unit_dir, "content_grade")

    # stage 3 — render (only reached because content_grade passed)
    manifest.mark(unit_dir, "render", "in_progress", skip_validation=True)
    r = render_sheet(unit_dir)
    manifest.complete_stage(unit_dir, "render")

    return {"unit_id": unit_id, "content_grade": f"{total}/20 {status}",
            "drift_passed": drift["passed"], "render": r}


def finalize_visual(unit_dir: Path, *, status: str, notes: str,
                    inspected_pages: list) -> dict:
    """Record the visual_grade after PDF inspection and complete the stage.
    The sheet is 'done' (publish stays pending until the batch gate)."""
    from pipeline import manifest

    unit_dir = Path(unit_dir)
    vg = {"inspected_pages": inspected_pages, "c4_layout_ok": status == "pass",
          "status": status, "notes": notes}
    (unit_dir / "visual_grade.json").write_text(json.dumps(vg, indent=2, ensure_ascii=False))
    if status != "pass":
        manifest.mark(unit_dir, "visual_grade", "failed", error=notes)
        raise RuntimeError(f"visual_grade FAILED: {notes}")
    manifest.mark(unit_dir, "visual_grade", "in_progress", skip_validation=True)
    manifest.complete_stage(unit_dir, "visual_grade")
    return vg
