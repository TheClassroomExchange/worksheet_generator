#!/usr/bin/env python3
"""Phase 6 cleanup — guarded, with pre/post integrity checklist.

Actions (only if ALL pre-checks pass):
  1. Repoint 4 pending purchases to the new equivalent listings (#25->67, 26->68, 27->69, 28->81).
  2. Delete 5 superseded/broken listing rows (#25,26,27,28,55) + their storage objects.
  3. Delete orphan upload_jobs (status pending/processing).
Leaves #65 and the 15 new listings (#67-81) untouched.

Run:  python3 scripts/cleanup_listings.py          (preview only; prints checklist + plan)
      python3 scripts/cleanup_listings.py --apply   (executes after pre-checks pass)
"""
import sys, json, ssl, urllib.request

CTX = ssl._create_unverified_context()
APPLY = "--apply" in sys.argv
ENV = {}
for line in open(__import__("os").path.expanduser("~/Desktop/TCE/TCE/.env.local")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); ENV[k] = v.strip().strip('"')
URL = ENV["NEXT_PUBLIC_SUPABASE_URL"]; KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

DELETE_IDS = [25, 26, 27, 28, 55]
REPOINT = {25: 67, 26: 68, 27: 69, 28: 81}   # old purchase resource_id -> new listing
KEEP_NEW = list(range(67, 82))               # 15 official listings must survive
KEEP_OOS = 65                                 # out of scope, must survive


def req(method, path, body=None, base=None):
    url = (base or URL) + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers={**H, "Content-Type": "application/json"}, method=method)
    resp = urllib.request.urlopen(r, context=CTX)
    raw = resp.read()
    return resp.status, (json.loads(raw) if raw else None)


def get(path):
    return req("GET", path)[1]


def storage_path(public_url):
    # https://<>/storage/v1/object/public/<bucket>/<path>  -> (bucket, path)
    marker = "/storage/v1/object/public/"
    tail = public_url.split(marker, 1)[1]
    bucket, path = tail.split("/", 1)
    return bucket, path


def main():
    checks = []
    def chk(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("=== PRE-CHANGE CHECKLIST ===")
    er = get("/rest/v1/educational_resources?select=item_id,files,preview_images,seller_name")
    ids = {r["item_id"] for r in er}
    chk("snapshot dir exists", __import__("os").path.isdir(__import__("os").path.expanduser("~/Desktop/TCE/catalogue_upload/backup_pre_cleanup")))
    chk("all 5 targets present", all(i in ids for i in DELETE_IDS))
    chk("all 15 new listings present (#67-81)", all(i in ids for i in KEEP_NEW))
    chk("#65 (out-of-scope) present", KEEP_OOS in ids)
    chk("repoint destinations exist (67,68,69,81)", all(i in ids for i in REPOINT.values()))
    purch = get("/rest/v1/purchases?select=id,resource_id,status")
    repoint_rows = [p for p in purch if p["resource_id"] in REPOINT]
    chk("4 purchases reference #25-28", len(repoint_rows) == 4)
    chk("no purchases reference #55", not any(p["resource_id"] == 55 for p in purch))
    base_purchase_count = len(purch)
    target_rows = {r["item_id"]: r for r in er if r["item_id"] in DELETE_IDS}
    # gather storage objects to delete (only from the 5 targets)
    to_delete = {}   # bucket -> [paths]
    for i, row in target_rows.items():
        for u in (row.get("files") or []) + (row.get("preview_images") or []):
            try:
                b, p = storage_path(u); to_delete.setdefault(b, []).append(p)
            except Exception:
                pass
    new_storage = set()
    for r in er:
        if r["item_id"] in KEEP_NEW:
            for u in (r.get("files") or []) + (r.get("preview_images") or []):
                new_storage.add(u)
    overlap = any(u for i in DELETE_IDS for u in (target_rows.get(i, {}).get("files") or []) + (target_rows.get(i, {}).get("preview_images") or []) if u in new_storage)
    chk("target storage objects DON'T overlap new listings", not overlap)
    orphans = get("/rest/v1/upload_jobs?status=neq.complete&select=id,status")
    print(f"\n  plan: repoint {len(repoint_rows)} purchases {REPOINT}; delete listings {DELETE_IDS};")
    print(f"        delete storage objs: " + ", ".join(f"{b}={len(p)}" for b, p in to_delete.items()))
    print(f"        delete {len(orphans)} orphan upload_jobs (pending/processing)")

    if not all(c for _, c in checks):
        print("\nPRE-CHECKS FAILED — aborting, no changes made."); sys.exit(1)
    if not APPLY:
        print("\n(preview only) re-run with --apply to execute."); return

    print("\n=== APPLYING ===")
    # 1. repoint purchases
    for old, new in REPOINT.items():
        req("PATCH", f"/rest/v1/purchases?resource_id=eq.{old}", {"resource_id": new})
        print(f"  repointed purchases {old} -> {new}")
    # 2. delete storage objects
    for bucket, paths in to_delete.items():
        req("DELETE", f"/storage/v1/object/{bucket}", {"prefixes": paths})
        print(f"  deleted {len(paths)} objects from {bucket}")
    # 3. delete listing rows
    req("DELETE", f"/rest/v1/educational_resources?item_id=in.({','.join(map(str,DELETE_IDS))})")
    print(f"  deleted listings {DELETE_IDS}")
    # 4. delete orphan jobs
    req("DELETE", "/rest/v1/upload_jobs?status=neq.complete")
    print(f"  deleted {len(orphans)} orphan upload_jobs")

    print("\n=== POST-CHANGE CHECKLIST ===")
    er2 = get("/rest/v1/educational_resources?select=item_id")
    ids2 = {r["item_id"] for r in er2}
    post = []
    def pchk(name, cond): post.append(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    pchk("5 targets GONE", not any(i in ids2 for i in DELETE_IDS))
    pchk("15 new listings INTACT", all(i in ids2 for i in KEEP_NEW))
    pchk("#65 INTACT", KEEP_OOS in ids2)
    pchk("listing count = 16", len(ids2) == 16)
    purch2 = get("/rest/v1/purchases?select=id,resource_id,status")
    pchk("purchase count unchanged", len(purch2) == base_purchase_count)
    pchk("purchases repointed to 67,68,69,81", all(any(p["resource_id"] == n for p in purch2) for n in REPOINT.values()))
    pchk("no purchase still references 25-28", not any(p["resource_id"] in REPOINT for p in purch2))
    orph2 = get("/rest/v1/upload_jobs?status=neq.complete&select=id")
    pchk("orphan jobs cleared", len(orph2) == 0)
    print("\nRESULT:", "ALL POST-CHECKS PASS ✅" if all(post) else "SOME POST-CHECKS FAILED ❌")


if __name__ == "__main__":
    main()
