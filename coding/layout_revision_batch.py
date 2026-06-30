"""
layout_revision_batch.py — drive the K/G1 roomy-layout re-render with the
per-worksheet snapshot -> render -> content-lock -> (visual) -> swap protocol.

Phase A (mechanical, this script): for each of the 48 K/G1 topics, render the
roomy worksheet, combine, and run the hard content-lock against the snapshot
original. On a content-lock FAIL, restore the snapshot PDF over the topic dir
(revert) so a topic never holds an unvetted PDF. Writes batch_results.json.

Visual L1-L4 grading + layout_grade.json + Drive republish happen after, driven
by the operator (Claude) reading the rendered pages.

Run:
  DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python -m coding.layout_revision_batch
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import coding_build, layout_rubric  # noqa: E402

BACKUP = Path("/private/tmp/claude-501/-Users-anthonnymonterroso/"
              "f4e448ec-7968-4b20-9319-5bc89cf538b4/scratchpad/backup_originals")

BATCHES = [
    ("Kindergarten", "k_unplugged_ct"),
    ("Kindergarten", "k_sequencing"),
    ("Kindergarten", "k_intro_block"),
    ("Grade 1", "g1_block_sequential"),
    ("Grade 1", "g1_unplugged_sequencing"),
    ("Grade 1", "g1_intro_debugging"),
]


def topic_dirs(batch: str) -> list[Path]:
    return sorted(p for p in (ROOT / "coding" / batch).iterdir()
                  if p.is_dir() and p.name[0].isdigit())


def combined_pdf(d: Path) -> Path:
    return next(p for p in d.glob("*.pdf")
               if not p.name.endswith("— Worksheet.pdf")
               and not p.name.endswith("— Teacher Guide.pdf"))


def npages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages"):
            return int(line.split()[-1])
    return -1


def run() -> dict:
    results = []
    for grade, batch in BATCHES:
        for d in topic_dirs(batch):
            rel = f"{batch}/{d.name}"
            snap = next((BACKUP / batch / d.name).glob("*.pdf"))
            coding_build.render_sheet(d)
            coding_build.combine_sheet(d)
            new_pdf = combined_pdf(d)
            ok, detail = layout_rubric.content_unchanged(
                snap, new_pdf, layout_rubric.footers_for(d))
            if not ok:
                shutil.copy(snap, new_pdf)  # revert: never leave an unvetted PDF
            results.append({
                "grade": grade, "batch": batch, "topic": d.name,
                "pdf": new_pdf.name, "pages": npages(new_pdf),
                "content_lock": ok, "detail": detail,
                "reverted": (not ok),
            })
            print(f"{'OK ' if ok else 'FAIL'} {rel:48s} pages={results[-1]['pages']} "
                  f"{'' if ok else '| '+detail}")
    summary = {
        "total": len(results),
        "content_lock_pass": sum(r["content_lock"] for r in results),
        "reverted": [r for r in results if r["reverted"]],
        "results": results,
    }
    out = ROOT / "coding" / "batch_results.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n{summary['content_lock_pass']}/{summary['total']} content-lock PASS. "
          f"Wrote {out}")
    return summary


if __name__ == "__main__":
    run()
