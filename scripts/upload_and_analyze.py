#!/usr/bin/env python3
"""Phase 2 — fire all 15 PDFs through the prod pipeline and capture metadata.

Uses the storefront session cookie (read from the browser) to POST each PDF to
the real /api/upload (so auth + PIPELINE_URL + PROCESS_AUTH_TOKEN are all the
prod path), polls upload_jobs (admin) until complete, downloads each result.json,
and writes the captured metadata back into manifest.json (status="analyzed").

Run:  python3 scripts/upload_and_analyze.py
Reads cookie from catalogue_upload/.cookie.json, Supabase creds from TCE/.env.local.
"""
import json
import os
import ssl
import time
import urllib.request
import urllib.error
import subprocess

CTX = ssl._create_unverified_context()  # py3.14 lacks local CA bundle; admin script over HTTPS

BASE = "https://www.theclassroomexchange.ca"
WORK = os.path.expanduser("~/Desktop/TCE/catalogue_upload")
MANIFEST = os.path.join(WORK, "manifest.json")
COOKIE = json.load(open(os.path.join(WORK, ".cookie.json")))
TEACHER_ID = "33b660c6-83e3-4848-932c-ce60cbd6240d"

# Supabase creds from the website .env.local
ENV = {}
for line in open(os.path.expanduser("~/Desktop/TCE/TCE/.env.local")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        ENV[k] = v.strip().strip('"')
SB_URL = ENV["NEXT_PUBLIC_SUPABASE_URL"]
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]


def sb_get(path):
    req = urllib.request.Request(f"{SB_URL}{path}", headers={
        "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    return json.load(urllib.request.urlopen(req, context=CTX))


def post_upload(path):
    """multipart POST to /api/upload via curl (robust multipart). Returns job_id or raises."""
    out = subprocess.run([
        "curl", "-s", "-X", "POST", f"{BASE}/api/upload",
        "-H", f"Cookie: {COOKIE}",
        "-F", f"file=@{path};type=application/pdf",
    ], capture_output=True, text=True).stdout
    data = json.loads(out)
    if "job_id" not in data:
        raise RuntimeError(f"upload failed for {os.path.basename(path)}: {out[:200]}")
    return data["job_id"]


def main():
    man = json.load(open(MANIFEST))
    recs = man["records"]

    # 1. Fire uploads (skip ones already uploaded/analyzed on resume — never double-fire).
    for r in recs:
        if r.get("job_id") and r.get("status") in ("uploaded", "analyzed"):
            continue
        jid = post_upload(r["local_path"])
        r["job_id"] = jid
        r["status"] = "uploaded"
        print(f"uploaded {os.path.basename(r['local_path']):55} -> job {jid}")
        time.sleep(2)  # gentle pacing; quota is 20/hr
    json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)

    # 2. Poll until every job is complete/failed.
    pending = {r["job_id"]: r for r in recs if r.get("status") != "analyzed"}
    print(f"\npolling {len(pending)} jobs...")
    for _ in range(60):  # up to ~5 min
        if not pending:
            break
        ids = ",".join(f'"{j}"' for j in pending)
        rows = sb_get(f"/rest/v1/upload_jobs?id=in.({ids})&select=id,status,error_message")
        for row in rows:
            if row["status"] in ("complete", "failed"):
                r = pending.pop(row["id"], None)
                if r:
                    r["job_status"] = row["status"]
                    if row["status"] == "failed":
                        r["status"] = "failed"
                        r["error"] = row.get("error_message")
                        print("  FAILED:", r["job_id"], row.get("error_message"))
        if pending:
            print(f"  waiting on {len(pending)}...")
            time.sleep(5)

    # 3. Fetch result.json for completed jobs, write metadata into manifest.
    for r in recs:
        if r.get("job_status") != "complete":
            continue
        key = f"{TEACHER_ID}/{r['job_id']}/result.json"
        req = urllib.request.Request(
            f"{SB_URL}/storage/v1/object/uploads/{key}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
        try:
            res = json.load(urllib.request.urlopen(req, context=CTX))
        except Exception as e:
            r["status"] = "failed"; r["error"] = f"result fetch: {e}"
            print("  result fetch failed:", r["job_id"], e); continue
        listing = res.get("listing", {})
        pricing = res.get("pricing", {})
        tax = res.get("taxonomy", {})
        r["ai_title"] = listing.get("title")
        r["description"] = listing.get("description")
        r["tags"] = listing.get("tags")
        r["price_cad"] = pricing.get("price_cad")
        r["price_band"] = [pricing.get("low_band_cad"), pricing.get("high_band_cad")]
        r["detected_grade"] = tax.get("grade")
        r["detected_subject"] = tax.get("subject")
        r["detected_strand"] = tax.get("strand_name")
        r["preview_urls"] = res.get("preview_urls", [])
        r["status"] = "analyzed"
        print(f"analyzed {r['subject']:22} {r['grade']:12} ${r['price_cad']} | {r['detected_grade']}/{r['detected_strand']}")

    json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
    done = sum(1 for r in recs if r.get("status") == "analyzed")
    print(f"\n{done}/15 analyzed. Manifest updated.")


if __name__ == "__main__":
    main()
