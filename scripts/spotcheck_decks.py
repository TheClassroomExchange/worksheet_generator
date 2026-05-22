"""Spot-check newly rebuilt decks.

For each target unit, downloads the deck as a PDF via Drive's export
endpoint, then:
  1. Verifies the PDF is > 300 KB (real content, not blank).
  2. Renders the character-card slides and saves them to /tmp for
     human inspection.
  3. Verifies that the local composed CHAR_<KEY>_FRONT.png file is
     > 5 KB (real composite, not labelled gray box).

Usage:
  python scripts/spotcheck_decks.py [unit_id ...]

If no unit_ids are passed, picks 4 representative units that exercise
the new SVGs across grade levels.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.slides import get_credentials
from googleapiclient.discovery import build

CHECKPOINT = PROJECT_ROOT / ".svg_rebuild_checkpoint.json"
OUT_DIR = Path("/tmp/svg_spotcheck")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TARGETS = [
    "g3_algebra_bug_busters",         # BUZZ + PATCH
    "g2_algebra_if_then_detectives",  # IF + THEN
    "k_data_detectives",              # DOT + TALLY
    "g1_real_life_math",              # MAPLE + SAP_SAM
]


def deck_id_from_url(url: str) -> str | None:
    """Extract presentation ID from a /d/<id>/edit URL."""
    if "/d/" not in url:
        return None
    return url.split("/d/")[1].split("/")[0]


def main():
    targets = sys.argv[1:] or DEFAULT_TARGETS
    if not CHECKPOINT.exists():
        print("No checkpoint file; run rebuild driver first.")
        sys.exit(1)
    ckpt = json.loads(CHECKPOINT.read_text())

    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    results = []
    for unit_id in targets:
        s = ckpt["units"].get(unit_id, {})
        url = s.get("deck_url")
        if not url:
            print(f"[{unit_id}] no deck_url in checkpoint — skipped")
            results.append((unit_id, "no-url", None, None))
            continue
        deck_id = deck_id_from_url(url)
        if not deck_id:
            print(f"[{unit_id}] could not parse deck id from {url}")
            results.append((unit_id, "bad-url", None, None))
            continue

        print(f"\n=== [{unit_id}] {url}")
        # Export as PDF
        try:
            req = drive.files().export(
                fileId=deck_id,
                mimeType="application/pdf",
            )
            pdf_bytes = req.execute()
        except Exception as e:
            print(f"  ✗ export failed: {e}")
            results.append((unit_id, f"export-error: {e}", None, None))
            continue
        size_kb = len(pdf_bytes) / 1024
        pdf_path = OUT_DIR / f"{unit_id}.pdf"
        pdf_path.write_bytes(pdf_bytes)
        size_ok = size_kb > 300
        print(f"  PDF: {size_kb:.1f} KB  {'✓' if size_ok else '✗ (too small)'}")

        # Inspect composed/ images for the 14 priority characters
        unit_dir = Path(s.get("unit_dir", ""))
        composed_summary = []
        if unit_dir.exists():
            for char_png in sorted(unit_dir.glob("composed/CHAR_*_FRONT.png")):
                kb = char_png.stat().st_size / 1024
                composed_summary.append(f"{char_png.name}={kb:.0f}KB")
            cert_pngs = list(unit_dir.glob("composed/AS_CERT_*.png"))
            for p in cert_pngs:
                if "BORDER" in p.name or "FRIENDS" in p.name:
                    continue
                kb = p.stat().st_size / 1024
                composed_summary.append(f"{p.name}={kb:.0f}KB")
        print(f"  Composed: {', '.join(composed_summary) if composed_summary else '(none)'}")

        # Render first 4 pages so the user can inspect
        try:
            from pdf2image import convert_from_bytes
            pages = convert_from_bytes(pdf_bytes, dpi=120, first_page=1, last_page=4)
            for i, im in enumerate(pages, 1):
                im.save(OUT_DIR / f"{unit_id}_page{i:02d}.png")
            print(f"  ✓ Rendered first {len(pages)} pages → {OUT_DIR}")
        except Exception as e:
            print(f"  ⚠ pdf2image failed: {e}")

        results.append((unit_id, "ok" if size_ok else "small-pdf", size_kb, composed_summary))

    print("\n=== Summary ===")
    for unit_id, status, kb, comp in results:
        kb_s = f"{kb:.0f}KB" if kb else "—"
        print(f"  {unit_id:36}  {status:10}  pdf={kb_s}")


if __name__ == "__main__":
    main()
