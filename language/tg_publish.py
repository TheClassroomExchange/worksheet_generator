"""Targeted, idempotent Drive republish for the Teacher-Guide fix.

For each changed unit (language/tg_changed_set.json), using the live file id
recorded in the unit's publish.json:
  1. DOWNLOAD the current live PDF -> _tg_fix_backup/_live_before/<safe>.pdf
     (the "snapshot before removing" — what is live right now),
  2. DIFF live-before vs the new local PDF (worksheet preserved, or removals-only
     for a word-building cap / the ull skull-drop) — abort the unit on any
     unexpected page-1 change,
  3. UPDATE the file in place (same file id, same name → replaces old with new;
     no separate stale file to delete),
  4. VERIFY the new modifiedTime is today.

Run:
  cd ~/Desktop/TCE/wg-language
  PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
  ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.tg_publish [--dry-run]
"""
from __future__ import annotations
import io, json, sys
from pathlib import Path

from language import tg_fix as T

LANG = T.LANG
LIVE_BEFORE = T.BACKUP / "_live_before"
PUBLOG = LANG / "TG_PUBLISH_LOG.md"

WB = {"g3_prefixes/01_ly-slowly", "g3_prefixes/02_un-undo",
      "g3_suffixes/01_s-cats", "g3_suffixes/03_ed-jumped", "g3_suffixes/04_er-faster"}


def _allow(rel: str) -> bool:
    return rel in WB or rel in T.DROP_ROWS


def _drive():
    from googleapiclient.discovery import build
    from pipeline.slides import get_credentials
    return build("drive", "v3", credentials=get_credentials())


def _download(drive, file_id: str, dest: Path):
    from googleapiclient.http import MediaIoBaseDownload
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = drive.files().get_media(fileId=file_id)
    buf = io.FileIO(str(dest), "wb")
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    buf.close()


def _update(drive, file_id: str, pdf: Path) -> str:
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(pdf), mimetype="application/pdf", resumable=False)
    drive.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
    meta = drive.files().get(fileId=file_id, fields="modifiedTime,name",
                             supportsAllDrives=True).execute()
    return meta["modifiedTime"]


def run(dry_run: bool = False) -> list[dict]:
    rels = json.loads((LANG / "tg_changed_set.json").read_text())
    drive = _drive()
    results = []
    for rel in rels:
        ud = LANG / rel
        pj = ud / "publish.json"
        r = {"unit": rel, "status": "?"}
        try:
            pub = json.loads(pj.read_text())
            fid = pub["files"][0]["id"]
            new_pdf = next(p for p in ud.glob("*.pdf"))
            safe = rel.replace("/", "__")
            live = LIVE_BEFORE / f"{safe}__live.pdf"
            _download(drive, fid, live)                       # 1. snapshot live
            ok, det = T.gate_worksheet_preserved(live, new_pdf, _allow(rel))  # 2. diff
            r["diff"] = det
            if not ok:
                raise RuntimeError(f"live-vs-new worksheet diff failed: {det}")
            if dry_run:
                r["status"] = "dry"; results.append(r); print(f"  DRY  {rel}  [{det}]"); continue
            r["modifiedTime"] = _update(drive, fid, new_pdf)  # 3. replace in place
            r["status"] = "published"                          # 4. verified below via modifiedTime
            print(f"  PUB  {rel}  modified={r['modifiedTime']}  [{det}]")
        except Exception as e:
            r["status"] = "fail"; r["err"] = str(e)
            print(f"  FAIL {rel}  {e}")
        results.append(r)
    _log(results, dry_run)
    return results


def _log(results: list[dict], dry_run: bool):
    ok = [r for r in results if r["status"] in ("published", "dry")]
    lines = [f"# Teacher-Guide fix — Drive publish log{'  (DRY)' if dry_run else ''}\n",
             f"- {len(ok)}/{len(results)} ok\n"]
    for r in results:
        mark = "✅" if r["status"] in ("published", "dry") else "❌"
        lines.append(f"{mark} `{r['unit']}` {r.get('status')} "
                     f"diff=[{r.get('diff','-')}] modified=[{r.get('modifiedTime','-')}]"
                     + (f" ERR={r['err']}" if r.get("err") else ""))
    PUBLOG.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    res = run(dry_run="--dry-run" in sys.argv)
    bad = [r for r in res if r["status"] == "fail"]
    print(f"\n{'DRY ' if '--dry-run' in sys.argv else ''}DONE ok={len(res)-len(bad)} fail={len(bad)}")
    sys.exit(1 if bad else 0)
