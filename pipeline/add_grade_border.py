#!/usr/bin/env python3
"""Add a grade-coloured frame to every coding worksheet PDF, preserving all content.

The frame colour matches the live TCE marketplace per-grade palette (sampled from
existing listing preview images), so buyers can tell a worksheet's grade at a glance
when filtering/searching.

Method (NOT a re-render): a transparent WeasyPrint overlay holding only a coloured
border is stamped onto every page of each existing combined PDF via pypdf
``merge_page``. Original content streams are untouched; only the edge band changes.

Idempotent: originals are snapshotted once to ``coding/_pre_border_backup/`` and every
stamp is applied FROM the backup, so re-running never double-borders.

Hard per-PDF gate: ``pdftotext`` of backup vs bordered must be byte-identical AND the
interior (content) region must show zero changed pixels. Any failure restores that PDF
from backup and is reported; the run aborts on first failure unless ``--keep-going``.

Run from repo root with the venv that has weasyprint + pypdf + Pillow:
    DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib python -m pipeline.add_grade_border
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[1]
CODING = REPO / "coding"
BACKUP = CODING / "_pre_border_backup"

# Per-grade border colour — sampled from live theclassroomexchange.ca preview images.
GRADE_HEX = {
    "Kindergarten": "#F4CCCC",  # pink
    "Grade 1": "#C9DAF8",       # blue
    "Grade 2": "#FCE5CD",       # orange
    "Grade 3": "#D9EAD3",       # green
}

BORDER_MM = 7          # frame thickness
LETTER = (612.0, 792.0)  # pt
GATE_DPI = 100
GATE_INSET_PX = 40     # clears the ~28px border band at 100dpi


def grade_for_dir(dirname: str, subj_grade: dict[str, str]) -> str:
    if dirname in subj_grade:
        return subj_grade[dirname]
    # prefix fallback
    if dirname.startswith("k_"):
        return "Kindergarten"
    for n in (1, 2, 3):
        if dirname.startswith(f"g{n}_") or dirname.startswith(f"pilot_g{n}_"):
            return f"Grade {n}"
    raise ValueError(f"cannot infer grade for dir {dirname!r}")


def load_subject_grades() -> dict[str, str]:
    data = json.loads((CODING / "subjects.json").read_text())
    subs = data if isinstance(data, list) else data.get("subjects", data)
    return {s["dir"]: s["grade"] for s in subs if s.get("dir") and s.get("grade")}


def is_combined(p: Path) -> bool:
    name = p.name
    return p.suffix.lower() == ".pdf" and " — Worksheet." not in name and " — Teacher Guide." not in name


def find_pdfs(subj_grade: dict[str, str]) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for sub in sorted(CODING.iterdir()):
        if not sub.is_dir() or sub.name.startswith("_") or sub.name.startswith("."):
            continue
        if sub.name == "rubrics":
            continue
        try:
            grade = grade_for_dir(sub.name, subj_grade)
        except ValueError:
            continue
        for pdf in sorted(sub.rglob("*.pdf")):
            if is_combined(pdf):
                out.append((pdf, grade))
    return out


def build_overlay(hex_: str, out: Path) -> None:
    """Decorative grade-coloured page frame: a rounded solid outer band plus a
    rounded dashed inner line (a friendly double frame). Both stay within ~8.5mm
    of the edge so the content gate (40px ≈ 10.2mm inset) sees zero inner change."""
    from weasyprint import HTML
    html = (
        "<html><head><style>"
        "@page { size: Letter; margin: 0; }"
        "html,body { margin:0; padding:0; background: transparent; }"
        f".frame {{ position: fixed; top:0; left:0; right:0; bottom:0;"
        f" border: 4.5mm solid {hex_}; border-radius: 15mm; box-sizing: border-box; }}"
        f".frame-inner {{ position: fixed; top:6.6mm; left:6.6mm; right:6.6mm; bottom:6.6mm;"
        f" border: 1.1mm dashed {hex_}; border-radius: 9mm; box-sizing: border-box; }}"
        "</style></head><body><div class='frame'></div>"
        "<div class='frame-inner'></div></body></html>"
    )
    HTML(string=html).write_pdf(str(out))


def stamp(src: Path, overlay_pdf: Path, dst: Path) -> int:
    import pypdf
    reader = pypdf.PdfReader(str(src))
    ov = pypdf.PdfReader(str(overlay_pdf)).pages[0]
    writer = pypdf.PdfWriter()
    for pg in reader.pages:
        b = pg.mediabox
        if abs(float(b.width) - LETTER[0]) > 1 or abs(float(b.height) - LETTER[1]) > 1:
            raise ValueError(f"non-Letter page {float(b.width)}x{float(b.height)} in {src}")
        pg.merge_page(ov)
        writer.add_page(pg)
    tmp = dst.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as f:
        writer.write(f)
    os.replace(tmp, dst)
    return len(reader.pages)


def pdftotext(path: Path) -> str:
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def render_pages(path: Path, prefix: Path) -> list[Path]:
    subprocess.run(["pdftoppm", "-png", "-r", str(GATE_DPI), str(path), str(prefix)],
                   check=True, capture_output=True)
    return sorted(prefix.parent.glob(prefix.name + "-*.png"))


def gate(backup: Path, bordered: Path, workdir: Path) -> tuple[bool, str]:
    if pdftotext(backup) != pdftotext(bordered):
        return False, "pdftotext differs"
    o = render_pages(backup, workdir / "o")
    b = render_pages(bordered, workdir / "b")
    if len(o) != len(b):
        return False, f"page count {len(o)} vs {len(b)}"
    for op, bp in zip(o, b):
        oi = Image.open(op).convert("RGB")
        bi = Image.open(bp).convert("RGB")
        if oi.size != bi.size:
            return False, f"raster size mismatch {oi.size} vs {bi.size}"
        w, h = oi.size
        diff = ImageChops.difference(oi, bi)
        inner = diff.crop((GATE_INSET_PX, GATE_INSET_PX, w - GATE_INSET_PX, h - GATE_INSET_PX))
        changed = sum(1 for px in inner.get_flattened_data() if px[0] + px[1] + px[2] > 12)
        if changed:
            return False, f"{changed} inner content pixels changed on {op.name}"
    return True, "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-going", action="store_true", help="don't abort on first gate failure")
    ap.add_argument("--limit", type=int, default=0, help="process at most N PDFs (debug)")
    args = ap.parse_args()

    subj_grade = load_subject_grades()
    pdfs = find_pdfs(subj_grade)
    if args.limit:
        pdfs = pdfs[: args.limit]
    print(f"found {len(pdfs)} combined PDFs")

    BACKUP.mkdir(exist_ok=True)
    overlays: dict[str, Path] = {}
    ov_dir = BACKUP / "_overlays"
    ov_dir.mkdir(exist_ok=True)
    for grade, hex_ in GRADE_HEX.items():
        op = ov_dir / f"{grade.replace(' ', '')}.pdf"
        build_overlay(hex_, op)
        overlays[grade] = op

    results = []
    failures = []
    for i, (pdf, grade) in enumerate(pdfs, 1):
        rel = pdf.relative_to(CODING)
        bkp = BACKUP / rel
        bkp.parent.mkdir(parents=True, exist_ok=True)
        # snapshot once (never overwrite an existing backup)
        if not bkp.exists():
            shutil.copy2(pdf, bkp)
        # always stamp FROM backup -> idempotent
        npages = stamp(bkp, overlays[grade], pdf)
        with tempfile.TemporaryDirectory() as td:
            ok, msg = gate(bkp, pdf, Path(td))
        status = "PASS" if ok else "FAIL"
        results.append({"pdf": str(rel), "grade": grade, "pages": npages, "gate": status, "msg": msg})
        print(f"[{i:2}/{len(pdfs)}] {status} {grade:12} {rel}  ({npages}p) {('' if ok else '<- '+msg)}")
        if not ok:
            shutil.copy2(bkp, pdf)  # restore
            failures.append(str(rel))
            if not args.keep_going:
                break

    log = BACKUP / "border_run.json"
    log.write_text(json.dumps({"results": results, "failures": failures}, indent=2))
    print(f"\nlog -> {log}")
    npass = sum(1 for r in results if r["gate"] == "PASS")
    print(f"PASS {npass}/{len(results)}  FAIL {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
