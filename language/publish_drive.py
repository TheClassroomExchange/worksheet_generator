"""Publish the built language catalogue to Google Drive:
  Product/Resources / Generated Language Worksheets / <Grade> / <Subject> / <N. Title> / <PDF>
Reuses the tested, idempotent pipeline.drive_publish (per-name update, stale cleanup,
1-PDF-per-folder hygiene). Drive only — NOT the marketplace.
  python -m language.publish_drive [dry]
"""
import json, sys
from pathlib import Path
from pipeline import drive_publish as dp

LANG = Path(__file__).resolve().parent
dp.GENERATED_ROOT_NAME = "Generated Language Worksheets"


def main(dry=False):
    subs = json.loads((LANG / "subjects.json").read_text())["subjects"]
    summary = []
    for s in subs:
        bd = LANG / s["dir"]
        if not (bd / "topics.json").exists():
            continue
        res = dp.publish_batch(bd, dry_run=dry)
        ok = sum(1 for r in (res.get("results") or []) if True)
        summary.append(s["id"])
    print("\nPUBLISHED SUBJECTS:", len(summary))


if __name__ == "__main__":
    main(dry=(len(sys.argv) > 1 and sys.argv[1] == "dry"))
