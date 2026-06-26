"""
drive_publish.py — push a coding batch's PDFs to Google Drive.

Publishes ONE combined PDF per topic (the student Worksheet pages followed by
the Teacher Guide / answer key, merged by ``coding_build.combine_sheet``) into
a clearly-navigable folder tree:

    Product/Resources/
    └── Generated Coding Worksheets/
        └── Grade 3/
            └── Block Coding/
                ├── 1. Loops: Code That Repeats/
                │   └── Loops.pdf          ← worksheet + teacher guide combined
                ├── 2. Loops That Make Patterns/
                │   └── … (1 PDF)
                └── …

Rules (per the product owner):
  • each topic folder contains EXACTLY ONE PDF — nothing else (a hygiene check
    verifies this and reports any stray file);
  • any older component PDFs ("… — Worksheet.pdf" / "… — Teacher Guide.pdf")
    from a prior two-PDF build are DELETED from Drive on publish, so only the
    single combined copy remains;
  • topic folders are numbered ("1. …", "2. …") for clear navigation;
  • idempotent — re-running updates the existing combined PDF in place instead
    of creating duplicates.

Reuses the Drive auth + folder helpers from pipeline.slides.

Run (dry-run first):
    DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python -m pipeline.drive_publish --dry-run
    DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python -m pipeline.drive_publish
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Product/Resources (writable) — the publish destination root.
PRODUCT_RESOURCES_FOLDER_ID = "1VYSTBEmOAL3RCqSTCXZT4xtJimjRs9_E"
GENERATED_ROOT_NAME = "Generated Coding Worksheets"


def _q_escape(name: str) -> str:
    return name.replace("'", "\\'")


def _list_children(drive, folder_id: str) -> list[dict]:
    res = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id,name,mimeType)", pageSize=100,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute()
    return res.get("files", [])


def _upload_or_update_pdf(drive, folder_id: str, path: Path) -> tuple[str, str]:
    """Create the PDF in folder_id, or update it in place if a file of the same
    name already exists. Returns (file_id, 'created'|'updated')."""
    from googleapiclient.http import MediaFileUpload

    name = path.name
    q = (f"'{folder_id}' in parents and name = '{_q_escape(name)}' "
         f"and trashed = false")
    existing = drive.files().list(
        q=q, fields="files(id,name)", pageSize=5,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute().get("files", [])
    media = MediaFileUpload(str(path), mimetype="application/pdf", resumable=False)
    if existing:
        fid = existing[0]["id"]
        drive.files().update(fileId=fid, media_body=media,
                             supportsAllDrives=True).execute()
        return fid, "updated"
    created = drive.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id", supportsAllDrives=True,
    ).execute()
    return created["id"], "created"


def _topic_pdf(unit_dir: Path) -> Path:
    """Return the single combined ``<Title>.pdf`` for a unit dir (worksheet +
    teacher guide merged by combine_sheet). Component PDFs ("… — Worksheet.pdf"
    / "… — Teacher Guide.pdf") are excluded; raises unless exactly one combined
    PDF is present."""
    pdfs = sorted(unit_dir.glob("*.pdf"))
    combined = [p for p in pdfs
                if not (p.stem.endswith("Worksheet") or p.stem.endswith("Teacher Guide"))]
    if len(combined) != 1:
        raise RuntimeError(
            f"{unit_dir.name}: expected exactly 1 combined PDF, "
            f"found {[p.name for p in pdfs]} (run coding_build.combine_sheet first)")
    return combined[0]


def _delete_stale_pdfs(drive, folder_id: str, keep: str) -> list[str]:
    """Delete every PDF in folder_id whose name != keep — e.g. the old
    '… — Worksheet.pdf' / '… — Teacher Guide.pdf' from a prior two-PDF build —
    so the topic folder ends with exactly one combined PDF. Returns names removed."""
    removed = []
    for c in _list_children(drive, folder_id):
        if c["mimeType"] == "application/pdf" and c["name"] != keep:
            drive.files().delete(fileId=c["id"], supportsAllDrives=True).execute()
            removed.append(c["name"])
    return removed


def publish_batch(batch_dir: Path, *, parent_folder_id: str = PRODUCT_RESOURCES_FOLDER_ID,
                  dry_run: bool = False) -> dict:
    """Publish every built topic in ``batch_dir`` (read from topics.json) to Drive.
    Only the 2 PDFs per topic are uploaded. Returns a summary dict."""
    from googleapiclient.discovery import build
    from pipeline.slides import get_credentials, _find_or_create_subfolder
    from pipeline import manifest

    batch_dir = Path(batch_dir)
    topics = json.loads((batch_dir / "topics.json").read_text())
    grade = topics["grade"]; subject = topics["subject"]

    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    def mkfolder(parent, name):
        if dry_run:
            print(f"    [folder] {name}")
            return f"DRY[{name}]"
        return _find_or_create_subfolder(drive, parent, name)

    print(f"Publishing {grade} · {subject} → {GENERATED_ROOT_NAME}/{grade}/{subject}"
          + ("  (DRY RUN)" if dry_run else ""))
    gen_root = mkfolder(parent_folder_id, GENERATED_ROOT_NAME)
    grade_folder = mkfolder(gen_root, grade)
    subject_folder = mkfolder(grade_folder, subject)

    results = []
    for t in topics["topics"]:
        if t.get("status") != "built":
            print(f"  · skip {t['nn']} {t['title']} (status={t.get('status')})")
            continue
        unit_dir = batch_dir / t["dir"]
        pdf = _topic_pdf(unit_dir)
        folder_name = f"{int(t['nn'])}. {t['title']}"
        print(f"  · {folder_name}")
        topic_folder = mkfolder(subject_folder, folder_name)

        uploaded = []
        if dry_run:
            print(f"      [pdf] {pdf.name}")
            uploaded.append({"role": "combined", "name": pdf.name})
        else:
            # Remove any stale component PDFs from the prior 2-PDF build first.
            for stale in _delete_stale_pdfs(drive, topic_folder, keep=pdf.name):
                print(f"      removed old: {stale}")
            fid, action = _upload_or_update_pdf(drive, topic_folder, pdf)
            print(f"      {action}: {pdf.name}")
            uploaded.append({"role": "combined", "name": pdf.name, "id": fid})

        # Hygiene: the topic folder must contain EXACTLY ONE PDF, nothing else.
        hygiene = {"ok": True, "extras": []}
        if not dry_run:
            children = _list_children(drive, topic_folder)
            extras = [c["name"] for c in children if c["name"] != pdf.name]
            non_pdf = [c["name"] for c in children
                       if c["mimeType"] != "application/pdf"]
            hygiene = {"ok": not extras and len(children) == 1,
                       "count": len(children), "extras": extras, "non_pdf": non_pdf}
            flag = "OK" if hygiene["ok"] else f"⚠ {hygiene}"
            print(f"      hygiene: {len(children)} file(s) — {flag}")

            # Record publish stage in the manifest.
            pub = {"drive_folder_id": topic_folder,
                   "drive_path": f"{GENERATED_ROOT_NAME}/{grade}/{subject}/{folder_name}",
                   "files": uploaded, "hygiene": hygiene}
            (unit_dir / "publish.json").write_text(json.dumps(pub, indent=2, ensure_ascii=False))
            try:
                if manifest.next_pending(manifest.load(unit_dir)) == "publish":
                    manifest.mark(unit_dir, "publish", "in_progress", skip_validation=True)
                    manifest.complete_stage(unit_dir, "publish")
            except Exception as e:
                print(f"      (manifest publish-stage note: {e})")

        results.append({"topic": folder_name, "uploaded": [u["name"] for u in uploaded],
                        "hygiene": hygiene})

    summary = {"grade": grade, "subject": subject, "dry_run": dry_run,
               "published": len(results), "results": results}
    all_ok = all(r["hygiene"]["ok"] for r in results) if not dry_run else True
    print(f"\n{'DRY RUN complete' if dry_run else 'PUBLISH complete'}: "
          f"{len(results)} topic(s), {len(results)} combined PDF(s)"
          + ("" if all_ok else "  ⚠ HYGIENE ISSUES — see above"))
    return summary


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    batch = ROOT / "coding" / "pilot_g3_block_coding"
    publish_batch(batch, dry_run=dry)
