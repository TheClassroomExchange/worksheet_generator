#!/usr/bin/env python3
"""Re-run the units that aren't analyzed yet — SERIALLY (one at a time, wait for
each to complete) to avoid the Cloud Run worker's 512 MiB OOM under concurrency.
Idempotent; updates manifest.json in place."""
import json, os, ssl, time, subprocess, urllib.request

CTX = ssl._create_unverified_context()
WORK = os.path.expanduser("~/Desktop/TCE/catalogue_upload")
MANIFEST = os.path.join(WORK, "manifest.json")
COOKIE = json.load(open(os.path.join(WORK, ".cookie.json")))
TEACHER_ID = "33b660c6-83e3-4848-932c-ce60cbd6240d"
BASE = "https://www.theclassroomexchange.ca"

ENV = {}
for line in open(os.path.expanduser("~/Desktop/TCE/TCE/.env.local")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); ENV[k] = v.strip().strip('"')
SB_URL = ENV["NEXT_PUBLIC_SUPABASE_URL"]; SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}


def get(path):
    req = urllib.request.Request(f"{SB_URL}{path}", headers=H)
    return json.load(urllib.request.urlopen(req, context=CTX))


def upload(path):
    out = subprocess.run(["curl", "-s", "-X", "POST", f"{BASE}/api/upload",
        "-H", f"Cookie: {COOKIE}", "-F", f"file=@{path};type=application/pdf"],
        capture_output=True, text=True).stdout
    return json.loads(out)["job_id"]


def fetch_result(job_id):
    key = f"{TEACHER_ID}/{job_id}/result.json"
    req = urllib.request.Request(f"{SB_URL}/storage/v1/object/uploads/{key}", headers=H)
    return json.load(urllib.request.urlopen(req, context=CTX))


man = json.load(open(MANIFEST))
todo = [r for r in man["records"] if r.get("status") != "analyzed"]
print(f"{len(todo)} to finalize (serial)")
for r in todo:
    jid = upload(r["local_path"])
    r["job_id"] = jid; r["status"] = "uploaded"
    print(f"\nuploaded {os.path.basename(r['local_path'])} -> {jid}; waiting...")
    ok = False
    for _ in range(36):  # up to 3 min per unit
        time.sleep(5)
        row = get(f"/rest/v1/upload_jobs?id=eq.{jid}&select=status,error_message")
        st = row[0]["status"] if row else "?"
        if st == "complete":
            ok = True; break
        if st == "failed":
            r["status"] = "failed"; r["error"] = row[0].get("error_message"); break
        print(f"   {st}...")
    if not ok:
        if r["status"] != "failed":
            print(f"   still not complete; leaving as uploaded");
        continue
    res = fetch_result(jid)
    L, P, T = res.get("listing", {}), res.get("pricing", {}), res.get("taxonomy", {})
    r["ai_title"] = L.get("title"); r["description"] = L.get("description"); r["tags"] = L.get("tags")
    r["price_cad"] = P.get("price_cad"); r["price_band"] = [P.get("low_band_cad"), P.get("high_band_cad")]
    r["detected_grade"] = T.get("grade"); r["detected_subject"] = T.get("subject"); r["detected_strand"] = T.get("strand_name")
    r["preview_urls"] = res.get("preview_urls", []); r["status"] = "analyzed"
    print(f"   analyzed ${r['price_cad']} | {r['detected_grade']}/{r['detected_strand']}")
    json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)

json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
print(f"\n{sum(1 for r in man['records'] if r.get('status')=='analyzed')}/15 analyzed.")
