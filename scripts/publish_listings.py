#!/usr/bin/env python3
"""Phase 4 — publish the 15 analyzed units to educational_resources (admin).

Replicates src/lib/publish.ts::publishDraft faithfully, via the Supabase
service-role key:
  1. upload the local PDF to the `resource-files` bucket -> public URL (files[])
  2. taxonomy lookup by (grade, subject) -> taxonomy_id
  3. insert an educational_resources row (seller = TheClassroomExchange)
Reuses the pipeline-generated preview URLs for preview_images.

Idempotent: skips records already status="published" with an item_id.
Run:  python3 scripts/publish_listings.py            (dry-run: add --dry)
"""
import json
import os
import ssl
import sys
import time
import urllib.request

CTX = ssl._create_unverified_context()
DRY = "--dry" in sys.argv
WORK = os.path.expanduser("~/Desktop/TCE/catalogue_upload")
MANIFEST = os.path.join(WORK, "manifest.json")
TEACHER_ID = "33b660c6-83e3-4848-932c-ce60cbd6240d"
SELLER = "TheClassroomExchange"
SITE = "https://www.theclassroomexchange.ca"

ENV = {}
for line in open(os.path.expanduser("~/Desktop/TCE/TCE/.env.local")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        ENV[k] = v.strip().strip('"')
SB_URL = ENV["NEXT_PUBLIC_SUPABASE_URL"]
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

# Clean, <=60-char titles per (subject, grade). Quality gate: human-readable,
# grade-prefixed, named unit. Verified <=60 below.
SUBJECT_LABEL = {
    "3C. Coding": "Coding",
    "5. Spatial Sense": "Spatial Sense",
    "4b. Probability": "Probability",
    "6. Financial Literacy": "Financial Literacy",
}
UNIT_NAME = {
    ("3C. Coding", "Kindergarten"): "Little Programmers",
    ("3C. Coding", "Grade 1"): "Sequential Superstars",
    ("3C. Coding", "Grade 2"): "Sequential Superstars",
    ("3C. Coding", "Grade 3"): "Sequential Superstars",
    ("5. Spatial Sense", "Kindergarten"): "Bigger, Smaller, Same!",
    ("5. Spatial Sense", "Grade 1"): "How Long? How Big?",
    ("5. Spatial Sense", "Grade 2"): "Measure Maven",
    ("5. Spatial Sense", "Grade 3"): "Fencing the Farm",
    ("4b. Probability", "Grade 1"): "Will It? Maybe!",
    ("4b. Probability", "Grade 2"): "What Could Happen?",
    ("4b. Probability", "Grade 3"): "Likely, Unlikely, Impossible",
    ("6. Financial Literacy", "Kindergarten"): "Little Shoppers",
    ("6. Financial Literacy", "Grade 1"): "The Expert Shoppers",
    ("6. Financial Literacy", "Grade 2"): "The Mega Market",
    ("6. Financial Literacy", "Grade 3"): "The Mega Market",
}

# Correct taxonomy override — the pipeline's strand detection is unreliable
# (it tagged Coding-K as "Understanding Matter and Energy" etc.). All 15 are
# Ontario Mathematics units; map (subject, grade) -> (strand_name, taxonomy_id)
# from ontario_curriculum_taxonomy (verified rows).
STRAND = {
    "3C. Coding": "Algebra/Coding",
    "5. Spatial Sense": "Geometry and Spatial Sense",
    "4b. Probability": "Data Literacy",
    "6. Financial Literacy": "Financial Literacy",
}
TAX_ID = {
    ("3C. Coding", "Kindergarten"): 17, ("3C. Coding", "Grade 1"): 18,
    ("3C. Coding", "Grade 2"): 52, ("3C. Coding", "Grade 3"): 53,
    ("5. Spatial Sense", "Kindergarten"): 44, ("5. Spatial Sense", "Grade 1"): 45,
    ("5. Spatial Sense", "Grade 2"): 46, ("5. Spatial Sense", "Grade 3"): 47,
    ("4b. Probability", "Grade 1"): 37, ("4b. Probability", "Grade 2"): 38,
    ("4b. Probability", "Grade 3"): 39,
    ("6. Financial Literacy", "Kindergarten"): 19, ("6. Financial Literacy", "Grade 1"): 48,
    ("6. Financial Literacy", "Grade 2"): 3, ("6. Financial Literacy", "Grade 3"): 49,
}


def make_title(r):
    g = r["grade"]
    subj = SUBJECT_LABEL[r["subject"]]
    unit = UNIT_NAME[(r["subject"], r["grade"])]
    t = f"{g} {subj}: {unit}"
    return t[:60]


def http(method, url, headers, data=None):
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    return urllib.request.urlopen(req, context=CTX)


def upload_file(local_path):
    name = os.path.basename(local_path)
    ts = int(time.time() * 1000)
    path = f"{TEACHER_ID}/{ts}-{name}"
    with open(local_path, "rb") as f:
        body = f.read()
    hdr = dict(H); hdr["Content-Type"] = "application/pdf"; hdr["x-upsert"] = "true"
    http("POST", f"{SB_URL}/storage/v1/object/resource-files/{path}", hdr, body)
    return f"{SB_URL}/storage/v1/object/public/resource-files/{path}"


def taxonomy_id(grade, subject):
    if not (grade and subject):
        return None
    import urllib.parse
    q = urllib.parse.quote(grade); s = urllib.parse.quote(subject)
    r = http("GET", f"{SB_URL}/rest/v1/ontario_curriculum_taxonomy?grade=eq.{q}&subject=eq.{s}&select=taxonomy_id&limit=1", H)
    rows = json.load(r)
    return rows[0]["taxonomy_id"] if rows else None


def main():
    man = json.load(open(MANIFEST))
    for r in man["records"]:
        if r.get("status") == "published" and r.get("item_id"):
            print("skip (published):", r.get("title")); continue
        if r.get("status") != "analyzed":
            print("skip (not analyzed):", r["subject"], r["grade"], "->", r.get("status")); continue

        title = make_title(r)
        key = (r["subject"], r["grade"])
        tax_id = TAX_ID[key]               # corrected, not the AI's guess
        strand = STRAND[r["subject"]]
        previews = r.get("preview_urls", []) or []

        payload = {
            "user_id": TEACHER_ID,
            "seller_name": SELLER,
            "title": title,
            "description": r.get("description") or "",
            "price_cad": r.get("price_cad"),
            "resource_type": "Unit Plan",
            "taxonomy_id": tax_id,
            "grade": r["grade"],            # known-correct (Kindergarten / Grade N)
            "subject": "Mathematics",       # all 15 are Ontario math units
            "strand_name": strand,          # corrected strand
            "preview_images": previews,
        }
        print(f"\n{'DRY ' if DRY else ''}PUBLISH: {title!r}  ${r.get('price_cad')}  tax_id={tax_id}")
        print(f"   grade/subject/strand: {payload['grade']} / {payload['subject']} / {payload['strand_name']}")
        print(f"   tags: {r.get('tags')}")
        if DRY:
            continue

        file_url = upload_file(r["local_path"])
        payload["files"] = [file_url]
        hdr = dict(H); hdr["Content-Type"] = "application/json"; hdr["Prefer"] = "return=representation"
        resp = http("POST", f"{SB_URL}/rest/v1/educational_resources", hdr, json.dumps(payload).encode())
        row = json.load(resp)[0]
        r["item_id"] = row["item_id"]
        r["title"] = title
        r["taxonomy_id"] = tax_id
        r["files"] = [file_url]
        r["listing_url"] = f"{SITE}/products/{row['item_id']}"
        r["status"] = "published"
        print(f"   -> item_id {row['item_id']}  {r['listing_url']}")
        json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)

    json.dump(man, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
    pub = sum(1 for r in man["records"] if r.get("status") == "published")
    print(f"\n{pub}/15 published.")


if __name__ == "__main__":
    main()
