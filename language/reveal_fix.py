"""Remove give-away underlines from the phonics "I Can Read Sentences" sheets.

Problem: find-task sheets say "underline/circle the X in each sentence" yet the
renderer pre-underlines the target in EVERY sentence — the answer is given away.
Fix: keep the target underlined on the FIRST sentence only (the worked example);
the rest render plain so the child finds the pattern.

This orchestrator, per impacted unit:
  1. snapshots the current combined PDF (revertible),
  2. sets reveal:"first" on the find-task reading_rows part in content.json,
  3. re-renders via language_build.build_unit (reuses cached images — no AI spend,
     runs the decodability + border gates internally),
  4. gates the result: HTML-structural (row0 keeps <b>, rows>0 lose it) +
     text-identity (pdftotext old==new) + page-count + visual-locality, and
  5. logs; on any gate failure it restores the snapshot and marks the unit failed.

Usage (from the wg-language dir, sibling venv, weasyprint env):
  PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
  ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.reveal_fix sweep
  ... reveal_fix.py <unit_dir>        # one unit (backtest)
  ... reveal_fix.py run [--limit N]   # all impacted units
"""
from __future__ import annotations
import json, re, sys, shutil, subprocess, tempfile
from pathlib import Path

LANG = Path(__file__).resolve().parent
ROOT = LANG.parent
BACKUP = LANG / "_reveal_fix_backup"
LOGMD = LANG / "REVEAL_FIX_LOG.md"


# ── sweep ────────────────────────────────────────────────────────────────────
def _grade_by_dir() -> dict:
    subs = json.loads((LANG / "subjects.json").read_text())["subjects"]
    return {s["dir"]: s["grade"] for s in subs}


def _is_find_task(parts: list) -> bool:
    prose = " ".join(p.get("text", "") for p in parts if p.get("type") == "prose").lower()
    return ("underline" in prose) or ("circle" in prose)


def _underlined_rows(part: dict) -> int:
    tgt = part.get("bold", part.get("target", ""))
    if not tgt:
        return 0
    return sum(1 for r in part.get("rows", []) if re.search(re.escape(tgt), r.get("text", ""), re.I))


def sweep() -> list[Path]:
    """Deterministic list of impacted unit dirs: find-task sheets where a
    reading_rows part underlines the target on more than one sentence."""
    impacted = []
    for f in sorted(LANG.glob("*/*/content.json")):
        if "_samples" in f.parts:
            continue
        parts = json.loads(f.read_text()).get("worksheet", {}).get("parts", [])
        if not _is_find_task(parts):
            continue
        if any(p.get("type") == "reading_rows" and _underlined_rows(p) > 1 for p in parts):
            impacted.append(f.parent)
    return impacted


# ── patch ────────────────────────────────────────────────────────────────────
def _patch_reveal(unit_dir: Path) -> bool:
    """Set reveal:'first' on every find-task reading_rows part. Returns True if
    the file changed."""
    cj = unit_dir / "content.json"
    content = json.loads(cj.read_text())
    changed = False
    for p in content.get("worksheet", {}).get("parts", []):
        if p.get("type") == "reading_rows" and p.get("reveal") != "first":
            p["reveal"] = "first"
            changed = True
    if changed:
        cj.write_text(json.dumps(content, indent=2, ensure_ascii=False))
    return changed


# ── gates ────────────────────────────────────────────────────────────────────
def _npages(pdf: Path) -> int:
    from pypdf import PdfReader
    return len(PdfReader(str(pdf)).pages)


def gate_html_structural(unit_dir: Path) -> tuple[bool, str]:
    """The strongest correctness proof: render the patched reading_rows part to
    HTML and confirm the FIRST row keeps a <b> (underlined target) and EVERY
    later row has none."""
    from pipeline import worksheet_pdf as wp
    content = json.loads((unit_dir / "content.json").read_text())
    parts = content.get("worksheet", {}).get("parts", [])
    rr = [p for p in parts if p.get("type") == "reading_rows"]
    if not rr:
        return False, "no reading_rows part"
    for p in rr:
        html = wp._render_reading_rows(p)
        trs = re.findall(r"<tr>.*?</tr>", html, re.S)
        if len(trs) < 2:
            return False, f"only {len(trs)} rows"
        if "<b>" not in trs[0]:
            return False, "row0 lost its underline"
        for i, tr in enumerate(trs[1:], 1):
            if "<b>" in tr:
                return False, f"row{i} still underlined"
    return True, f"row0 underlined, rows>0 plain ({sum(len(re.findall(r'<tr>', wp._render_reading_rows(p))) for p in rr)} rows)"


def gate_text_identical(old_pdf: Path, new_pdf: Path, unit_dir: Path) -> tuple[bool, str]:
    from pipeline import layout_rubric as lr
    return lr.content_unchanged(old_pdf, new_pdf, lr.footers_for(unit_dir))


def gate_visual_locality(old_pdf: Path, new_pdf: Path) -> tuple[bool, str]:
    """Render both to PNG and confirm: (a) something changed (fix took effect),
    (b) all changes sit in the left/body text region — never the header, footer,
    or the right-hand image column (which would signal layout damage)."""
    from PIL import Image, ImageChops
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        def render(pdf, tag):
            subprocess.run(["pdftoppm", "-png", "-r", "100", str(pdf), str(td / tag)],
                           check=True, capture_output=True)
            return sorted(td.glob(f"{tag}-*.png"))
        olds, news = render(old_pdf, "o"), render(new_pdf, "n")
        if len(olds) != len(news):
            return False, f"page count differs in render ({len(olds)} vs {len(news)})"
        total_changed = 0
        for op, np_ in zip(olds, news):
            a = Image.open(op).convert("L"); b = Image.open(np_).convert("L")
            if a.size != b.size:
                return False, "page raster size differs"
            diff = ImageChops.difference(a, b).point(lambda p: 255 if p > 40 else 0)
            bbox = diff.getbbox()
            if not bbox:
                continue
            w, h = a.size
            x0, y0, x1, y1 = bbox
            # changes must stay inside the body band and out of the image column
            if y0 < 0.14 * h or y1 > 0.93 * h:
                return False, f"change bleeds into header/footer (y {y0/h:.2f}-{y1/h:.2f})"
            if x1 > 0.86 * w:
                return False, f"change bleeds into image column (x-max {x1/w:.2f})"
            # count changed pixels
            total_changed += sum(1 for px in diff.getdata() if px)
        if total_changed < 50:
            return False, f"no meaningful change ({total_changed}px) — fix did not take effect"
        return True, f"{total_changed}px lightened, all in body text column"


# ── per-unit driver ──────────────────────────────────────────────────────────
def process_unit(unit_dir: Path, grade_map: dict | None = None) -> dict:
    unit_dir = Path(unit_dir)
    subject = unit_dir.parent.name
    grade_map = grade_map or _grade_by_dir()
    grade = grade_map[subject]
    r = {"unit": f"{subject}/{unit_dir.name}", "grade": grade, "gates": {}, "status": "?"}

    from pipeline import coding_build as cb  # find the current combined PDF
    old_pdf = unit_dir / json.loads((unit_dir / "render.json").read_text())["combined_pdf"] \
        if (unit_dir / "render.json").exists() else None
    if not old_pdf or not old_pdf.exists():
        pdfs = list(unit_dir.glob("*.pdf"))
        old_pdf = pdfs[0] if len(pdfs) == 1 else None
    if not old_pdf:
        r["status"] = "fail"; r["err"] = "cannot locate single existing PDF"; return r

    bkp_dir = BACKUP / subject; bkp_dir.mkdir(parents=True, exist_ok=True)
    snap = bkp_dir / f"{unit_dir.name}__{old_pdf.name}"
    if not snap.exists():
        shutil.copy2(old_pdf, snap)
    cj_snap = bkp_dir / f"{unit_dir.name}__content.json"
    if not cj_snap.exists():
        shutil.copy2(unit_dir / "content.json", cj_snap)

    try:
        _patch_reveal(unit_dir)
        from language import language_build as lb
        build = lb.build_unit(unit_dir, grade)
        new_pdf = Path(build["pdf"])

        ok, det = gate_html_structural(unit_dir); r["gates"]["html"] = det
        if not ok: raise RuntimeError(f"html gate: {det}")
        ok, det = gate_text_identical(snap, new_pdf, unit_dir); r["gates"]["text"] = det
        if not ok: raise RuntimeError(f"text gate: {det}")
        no, nn = _npages(snap), _npages(new_pdf); r["gates"]["pages"] = f"{no}->{nn}"
        if no != nn: raise RuntimeError(f"page-count gate: {no}!={nn}")
        ok, det = gate_visual_locality(snap, new_pdf); r["gates"]["visual"] = det
        if not ok: raise RuntimeError(f"visual gate: {det}")

        r["status"] = "pass"; r["pdf"] = str(new_pdf)
    except Exception as e:
        # restore snapshot + original content.json on any failure
        shutil.copy2(cj_snap, unit_dir / "content.json")
        shutil.copy2(snap, old_pdf)
        r["status"] = "fail"; r["err"] = str(e)
    return r


def _append_log(results: list[dict]):
    lines = ["# Reveal-fix run log\n"]
    ok = [x for x in results if x["status"] == "pass"]
    bad = [x for x in results if x["status"] != "pass"]
    lines.append(f"- Passed: {len(ok)}  Failed: {len(bad)}  Total: {len(results)}\n")
    for x in results:
        mark = "✅" if x["status"] == "pass" else "❌"
        g = x.get("gates", {})
        lines.append(f"{mark} `{x['unit']}` ({x.get('grade','')}) "
                     f"html=[{g.get('html','-')}] text=[{g.get('text','-')}] "
                     f"pages=[{g.get('pages','-')}] visual=[{g.get('visual','-')}]"
                     + (f" ERR={x['err']}" if x.get("err") else ""))
    LOGMD.write_text("\n".join(lines) + "\n")


# ── cli ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "sweep":
        units = sweep()
        import collections
        by = collections.Counter(u.parent.name for u in units)
        print(f"impacted units: {len(units)}")
        for k, c in sorted(by.items()):
            print(f"  {c:3}  {k}")
        for u in units:
            print("   ", u.relative_to(LANG))
    elif args[0] == "run":
        limit = None
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        units = sweep()
        if limit:
            units = units[:limit]
        gm = _grade_by_dir()
        results = []
        for i, u in enumerate(units, 1):
            res = process_unit(u, gm)
            results.append(res)
            print(f"[{i}/{len(units)}] {res['status'].upper()} {res['unit']}"
                  + (f"  ERR={res.get('err')}" if res["status"] != "pass" else ""))
            _append_log(results)
        _append_log(results)
        bad = [r for r in results if r["status"] != "pass"]
        print(f"\nDONE  pass={len(results)-len(bad)} fail={len(bad)}")
        sys.exit(1 if bad else 0)
    else:  # a single unit dir (backtest)
        res = process_unit(Path(args[0]))
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["status"] == "pass" else 1)
