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
    render_pdf(_resolve_paths(content["worksheet"]), ws_path)
    render_pdf(_resolve_paths(content["teacher_guide"]), tg_path)

    render = {
        "worksheet_pdf": ws_path.name,
        "teacher_guide_pdf": tg_path.name,
    }
    (unit_dir / "render.json").write_text(json.dumps(render, indent=2, ensure_ascii=False))
    return render
