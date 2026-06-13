"""
drive_publish.py — push a coding batch's PDFs to Google Drive.

Publishes ONLY the two PDFs per topic (the student Worksheet + the Teacher
Guide) into a clearly-navigable folder tree:

    Product/Resources/
    └── Generated Coding Worksheets/
        └── Grade 3/
            └── Block Coding/
                ├── 1. Loops: Code That Repeats/
                │   ├── Loops — Worksheet.pdf
                │   └── Loops — Teacher Guide.pdf
                ├── 2. Loops That Make Patterns/
                │   └── … (2 PDFs)
                └── …

Rules (per the product owner):
  • each topic folder contains EXACTLY the 2 PDFs — nothing else (a hygiene
    check verifies this and reports any stray file);
  • topic folders are numbered ("1. …", "2. …") for clear navigation;
  • idempotent — re-running updates the existing PDFs in place instead of
    creating duplicates.

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


def _topic_pdfs(unit_dir: Path) -> dict:
    """Return {'worksheet': Path, 'teacher_guide': Path} for a unit dir.
    Raises if not exactly the two expected PDFs are present."""
    pdfs = sorted(unit_dir.glob("*.pdf"))
    ws = [p for p in pdfs if p.stem.endswith("Worksheet")]
    tg = [p for p in pdfs if p.stem.endswith("Teacher Guide")]
    if len(ws) != 1 or len(tg) != 1:
        raise RuntimeError(
            f"{unit_dir.name}: expected 1 Worksheet + 1 Teacher Guide PDF, "
            f"found {[p.name for p in pdfs]}")
    return {"worksheet": ws[0], "teacher_guide": tg[0]}


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
        pdfs = _topic_pdfs(unit_dir)
        folder_name = f"{int(t['nn'])}. {t['title']}"
        print(f"  · {folder_name}")
        topic_folder = mkfolder(subject_folder, folder_name)

        uploaded = []
        for role, path in pdfs.items():
            if dry_run:
                print(f"      [pdf] {path.name}")
                uploaded.append({"role": role, "name": path.name})
                continue
            fid, action = _upload_or_update_pdf(drive, topic_folder, path)
            print(f"      {action}: {path.name}")
            uploaded.append({"role": role, "name": path.name, "id": fid})

        # Hygiene: the topic folder must contain EXACTLY the 2 PDFs, nothing else.
        hygiene = {"ok": True, "extras": []}
        if not dry_run:
            children = _list_children(drive, topic_folder)
            expected = {p.name for p in pdfs.values()}
            extras = [c["name"] for c in children if c["name"] not in expected]
            non_pdf = [c["name"] for c in children
                       if c["mimeType"] != "application/pdf"]
            hygiene = {"ok": not extras and len(children) == 2,
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
          f"{len(results)} topic(s), {len(results)*2} PDFs"
          + ("" if all_ok else "  ⚠ HYGIENE ISSUES — see above"))
    return summary


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    batch = ROOT / "coding" / "pilot_g3_block_coding"
    publish_batch(batch, dry_run=dry)
