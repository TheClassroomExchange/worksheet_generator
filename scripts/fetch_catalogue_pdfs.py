#!/usr/bin/env python3
"""Phase 0 — download the 15 catalogue unit PDFs from Drive and seed the manifest.

Read-only against Drive (reuses pipeline/slides.py auth + token.json).
Writes the PDFs to ~/Desktop/TCE/catalogue_upload/pdfs/<subject>/ and a
manifest.json that is the resume backbone for the whole publishing run.

Run from the worksheet_generator repo root:
    DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python scripts/fetch_catalogue_pdfs.py
"""
import io
import json
import os
import re
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from pipeline.slides import get_credentials

OUT_DIR = os.path.expanduser("~/Desktop/TCE/catalogue_upload")
PDF_DIR = os.path.join(OUT_DIR, "pdfs")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")

# (subject label, slug for folder, Drive folder id)
SUBJECTS = [
    ("3C. Coding",          "3C_Coding",            "1iofAnvmf1S90r6gbUQUOg4h8ONAHgwIl"),
    ("5. Spatial Sense",    "5_Spatial_Sense",      "1BIRB6gvF1WC1mT36YsKV5J-hPax3SAki"),
    ("4b. Probability",     "4b_Probability",       "18VzLC9WJbfSyPZxuMO3Ki0Zi-RmTm3pb"),
    ("6. Financial Literacy", "6_Financial_Literacy", "1p0I401DsW_aCfVHgNmM6egJjzR18lyqJ"),
]


def infer_grade(name: str) -> str:
    n = name.lower()
    if "kindergarten" in n or re.search(r"\bk\b", n):
        return "Kindergarten"
    m = re.search(r"(?:grade|gr\.?)\s*([123])", n)
    if m:
        return f"Grade {m.group(1)}"
    return "Unknown"


def normalize_filename(name: str) -> str:
    # Drive names are messy: "How Big?pdf", trailing spaces, weird punctuation.
    name = name.strip()
    name = re.sub(r"\s*pdf$", "", name, flags=re.IGNORECASE)          # "...How Big?pdf"
    name = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)
    name = name.replace("_", " ")
    name = re.sub(r"[?:!]", "", name)                                  # strip ? : ! from filename
    # ASCII/storage-safe ONLY: Supabase storage object keys reject non-ASCII
    # (an em-dash here caused "Storage upload failed"). Keep [A-Za-z0-9 _-].
    name = name.replace("—", "-").replace("–", "-")                   # em/en dash -> hyphen
    name = re.sub(r"[^A-Za-z0-9 _-]", "", name)                       # drop everything else
    name = re.sub(r"\s+", " ", name).strip().rstrip(" .-_")
    name = name.replace(" ", "-")                                     # spaces -> hyphen (safe key)
    name = re.sub(r"-+", "-", name)
    return name + ".pdf"


def list_pdfs(drive, folder_id):
    q = (f"'{folder_id}' in parents and trashed=false "
         "and mimeType='application/pdf'")
    r = drive.files().list(q=q, fields="files(id,name,size)",
                           pageSize=200, orderBy="name").execute()
    return r.get("files", [])


def download(drive, file_id, dest):
    req = drive.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    with open(dest, "wb") as f:
        f.write(buf.getvalue())
    return os.path.getsize(dest)


def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    records = []
    for subject, slug, folder_id in SUBJECTS:
        sub_dir = os.path.join(PDF_DIR, slug)
        os.makedirs(sub_dir, exist_ok=True)
        for f in list_pdfs(drive, folder_id):
            clean = normalize_filename(f["name"])
            local = os.path.join(sub_dir, clean)
            size = download(drive, f["id"], local)
            rec = {
                "subject": subject,
                "grade": infer_grade(f["name"]),
                "drive_file_id": f["id"],
                "drive_name": f["name"].strip(),
                "local_path": local,
                "size_bytes": size,
                "status": "downloaded",
                # filled later (Phase 2 analyze / Phase 4 publish / Phase 5 verify):
                "title": None, "price_cad": None, "tags": None, "description": None,
                "detected_grade": None, "detected_subject": None, "detected_strand": None,
                "preview": None, "item_id": None, "listing_url": None,
                "R1": None, "R2": None, "R3": None, "R4": None, "R5": None, "R6": None,
            }
            records.append(rec)
            print(f"  [{rec['grade']:12}] {subject:22} -> {clean}  ({size/1048576:.2f} MB)")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint": "C0",
        "count": len(records),
        "records": records,
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(records)} records -> {MANIFEST}")


if __name__ == "__main__":
    main()
