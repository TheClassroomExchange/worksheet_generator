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


# Grades that render in "roomy" mode — bigger images, more writing room for
# young learners. The worksheet spec is flagged by grade at render time, so no
# content.json edits are needed and G2/G3 are untouched.
ROOMY_GRADES = {"Kindergarten", "Grade 1"}


def _grade_of(unit_dir: Path) -> str | None:
    """The grade label for a topic dir: input_row.json first, else the parent
    batch's topics.json. Returns e.g. 'Kindergarten' / 'Grade 1', or None."""
    ir = unit_dir / "input_row.json"
    if ir.exists():
        g = json.loads(ir.read_text(encoding="utf-8")).get("grade")
        if g:
            return g
    tj = unit_dir.parent / "topics.json"
    if tj.exists():
        return json.loads(tj.read_text(encoding="utf-8")).get("grade")
    return None


def render_sheet(unit_dir: Path, *, roomy_level: int = 0) -> dict:
    """Render the worksheet + teacher-guide PDFs from content.json.

    ``roomy_level`` (0–3) controls roomy compaction for K/G1 sheets: 0 = full
    roomy (default), higher = progressively compacted so a too-tall question
    group fits its page (used by ``fit_render`` to kill near-empty pages)."""
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
    # K & G1 worksheets render roomy (bigger images, more writing room). The
    # teacher guide stays compact regardless of grade.
    ws_spec = _resolve_paths(content["worksheet"])
    if _grade_of(unit_dir) in ROOMY_GRADES:
        ws_spec["roomy"] = True
        ws_spec["roomy_level"] = int(roomy_level)
    render_pdf(ws_spec, ws_path)
    render_pdf(tg_spec, tg_path)

    render = {
        "worksheet_pdf": ws_path.name,
        "teacher_guide_pdf": tg_path.name,
    }
    (unit_dir / "render.json").write_text(json.dumps(render, indent=2, ensure_ascii=False))
    return render


def _fbase(unit_dir: Path) -> str:
    """The clean filename base for a sheet (matches render_sheet)."""
    content = json.loads((unit_dir / "content.json").read_text(encoding="utf-8"))
    title = content.get("title", "Worksheet")
    return content.get("file_title") or title.replace(": ", " — ").replace(":", "-")


def combine_sheet(unit_dir: Path) -> dict:
    """Append the two component PDFs into ONE ``<fbase>.pdf`` per folder:
    Worksheet pages first, Teacher Guide (instructions + answer key) last.

    Simple back-to-back append via poppler ``pdfunite`` — each half keeps its
    own footer + page numbering. Deletes the two component PDFs so the folder
    holds exactly one PDF (+ json/py metadata). Idempotent: same output name is
    overwritten on re-run. Returns {"combined_pdf": name, "pages_from": {...}}.
    """
    unit_dir = Path(unit_dir)
    fbase = _fbase(unit_dir)
    ws_path = unit_dir / f"{fbase} — Worksheet.pdf"
    tg_path = unit_dir / f"{fbase} — Teacher Guide.pdf"
    combined = unit_dir / f"{fbase}.pdf"
    if not ws_path.exists() or not tg_path.exists():
        raise FileNotFoundError(
            f"component PDFs missing in {unit_dir} — run render_sheet first")

    # pdfunite refuses to overwrite an input; combined name differs from both,
    # but guard against a prior combined of the same name lingering.
    if combined.exists():
        combined.unlink()
    proc = subprocess.run(
        ["pdfunite", str(ws_path), str(tg_path), str(combined)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0 or not combined.exists():
        raise RuntimeError(f"pdfunite failed for {unit_dir}: {proc.stderr.strip()}")

    # One PDF per folder — drop the components now that they're merged in.
    ws_path.unlink()
    tg_path.unlink()

    out = {"combined_pdf": combined.name,
           "pages_from": {"worksheet": ws_path.name, "teacher_guide": tg_path.name}}
    (unit_dir / "render.json").write_text(json.dumps(
        {"combined_pdf": combined.name}, indent=2, ensure_ascii=False))
    return out


def _combined_pdf(unit_dir: Path) -> Path:
    pdf = next((p for p in Path(unit_dir).glob("*.pdf")
                if not p.name.endswith("— Worksheet.pdf")
                and not p.name.endswith("— Teacher Guide.pdf")), None)
    if pdf is None:
        raise FileNotFoundError(
            f"no combined PDF in {unit_dir} — run fit_render(dir) (or "
            f"render_sheet+combine_sheet) before finalize_visual")
    return pdf


def fit_render(unit_dir: Path, baseline_pdf: Path | None = None, *,
               levels=(0, 1, 2, 3)) -> dict:
    """Render a sheet at the roomiest level that yields ZERO near-empty pages,
    combine, and return the result. Use for the render+combine step of the build
    loop (replaces bare render_sheet+combine_sheet).

    Walks the roomy compaction ladder (levels 0->3) and accepts the FIRST level
    whose combined PDF passes the gate(s):
      • page_fill_ok (no near-empty worksheet page) — ALWAYS, and
      • content_unchanged vs baseline — ONLY when ``baseline_pdf`` is given (a
        layout REVISION of an existing sheet). For a FRESH build pass None: the
        content is new, so there is nothing to diff and only the fill gate applies.

    For G2/G3 (non-roomy) the levels collapse to the single level-0 render
    (roomy_level is ignored unless the spec is roomy), so they settle immediately.
    Records {roomy_level, near_empty_before, content_ok} in render.json.
    Returns that dict (status='pass'); status='fail' if no level passes."""
    from pipeline import layout_rubric

    unit_dir = Path(unit_dir)
    footers = layout_rubric.footers_for(unit_dir)
    near_before = None
    content_ok, detail, near = True, "no baseline (fresh build)", None
    for level in levels:
        render_sheet(unit_dir, roomy_level=level)
        combine_sheet(unit_dir)
        pdf = _combined_pdf(unit_dir)
        if baseline_pdf is not None:
            content_ok, detail = layout_rubric.content_unchanged(baseline_pdf, pdf, footers)
        fill_ok, near = layout_rubric.page_fill_ok(pdf)
        if level == 0:
            near_before = near
        if content_ok and fill_ok:
            rec = {"combined_pdf": pdf.name, "roomy_level": level,
                   "near_empty_before": near_before, "content_ok": content_ok,
                   "status": "pass"}
            (unit_dir / "render.json").write_text(
                json.dumps(rec, indent=2, ensure_ascii=False))
            return rec
    rec = {"roomy_level": None, "near_empty_before": near_before,
           "last_near_empty": near, "content_ok": content_ok,
           "content_detail": detail, "status": "fail"}
    (unit_dir / "render.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return rec


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

    from pipeline import layout_rubric

    unit_dir = Path(unit_dir)
    # HARD page-fill gate (all grades): a sheet with a near-empty worksheet page
    # (header/goal-only, or a lone trailing line) can never finalize -> never
    # publishes. Catches the round-2 blank-page bug structurally on EVERY future
    # sheet, regardless of which render path produced it. Fix = re-render via
    # fit_render(dir) (auto-fit climbs the roomy compaction ladder for K/G1).
    fill_ok, near_empty = layout_rubric.page_fill_ok(_combined_pdf(unit_dir))
    vg = {"inspected_pages": inspected_pages,
          "c4_layout_ok": status == "pass",
          "page_fill_ok": fill_ok, "near_empty_pages": near_empty,
          "status": status, "notes": notes}
    (unit_dir / "visual_grade.json").write_text(json.dumps(vg, indent=2, ensure_ascii=False))
    if not fill_ok:
        vg["status"] = "failed"
        (unit_dir / "visual_grade.json").write_text(json.dumps(vg, indent=2, ensure_ascii=False))
        manifest.mark(unit_dir, "visual_grade", "failed",
                      error=f"near-empty page(s): {near_empty} — re-render via fit_render(dir)")
        raise RuntimeError(f"visual_grade FAILED — near-empty worksheet page(s) {near_empty}; "
                           f"re-render via coding_build.fit_render(dir)")
    if status != "pass":
        manifest.mark(unit_dir, "visual_grade", "failed", error=notes)
        raise RuntimeError(f"visual_grade FAILED: {notes}")
    manifest.mark(unit_dir, "visual_grade", "in_progress", skip_validation=True)
    manifest.complete_stage(unit_dir, "visual_grade")
    return vg
