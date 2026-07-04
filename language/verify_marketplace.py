#!/usr/bin/env python3
"""Post-upload verification for the Language marketplace batch.

For each TCE Language listing (or a single --item-id):
  * field checks: title<=60, description non-empty, price==2.99, subject==Language,
    grade/strand/taxonomy_id match the live taxonomy map, >=1 preview, exactly 1 file.
  * grade-border pixel check: download the first preview PNG and confirm the expected
    per-grade border colour DOMINATES the other three grade colours (proves the right
    grade's border is baked into the image, not just present).
  * watermark check: confirm semi-transparent grey text pixels exist over the white page.

Usage:
  python3 verify_marketplace.py --item-id 175
  python3 verify_marketplace.py            # all TCE Language rows
"""
from __future__ import annotations
import argparse, io, json, os, ssl, urllib.request
from pathlib import Path
from PIL import Image

CTX = ssl._create_unverified_context()
ENV_PATH = os.path.expanduser("~/Desktop/TCE/TCE/.env.local")
ENV = {}
for line in open(ENV_PATH):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); ENV[k] = v.strip().strip('"')
SB = ENV["NEXT_PUBLIC_SUPABASE_URL"]; KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

TAXO = {                       # grade -> (taxonomy_id, strand_name)
    "Kindergarten": (1, "Foundations of Language"),
    "Grade 1":      (2, "Word-Level Reading"),
    "Grade 2":      (4, "Vocabulary"),
    "Grade 3":      (5, "Writing"),
}
GRADE_RGB = {                  # baked border colour per grade
    "Kindergarten": (244, 204, 204),
    "Grade 1":      (201, 218, 248),
    "Grade 2":      (252, 229, 205),
    "Grade 3":      (217, 234, 211),
}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=H), context=CTX)


def near(px, rgb, tol=10):   # tight: the 4 pastel grade colours differ by ~25 in a channel
    return all(abs(px[i] - rgb[i]) <= tol for i in range(3))


def analyse_png(url):
    raw = get(url).read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    W, Hh = im.size
    px = im.load()
    counts = {g: 0 for g in GRADE_RGB}
    wm = 0
    # sample a border frame band (outer ~6% of each edge) for grade colour,
    # and the whole image (stride) for watermark grey.
    band = max(6, int(min(W, Hh) * 0.06))
    for y in range(Hh):
        edge_y = y < band or y > Hh - band
        for x in range(0, W, 2):
            edge_x = x < band or x > W - band
            p = px[x, y]
            if edge_y or edge_x:
                for g, rgb in GRADE_RGB.items():
                    if near(p, rgb):
                        counts[g] += 1
            # watermark: greyish (r≈g≈b) mid-tone, not white/near-white, not ink-black
            r, gg, b = p
            if 150 < r < 240 and abs(r - gg) < 12 and abs(gg - b) < 12 and abs(r - b) < 12:
                wm += 1
    return counts, wm, (W, Hh)


def check_row(row):
    errs = []
    g = row.get("grade")
    if len(row.get("title", "")) > 60 or not row.get("title"):
        errs.append("title")
    if not row.get("description"):
        errs.append("description")
    if row.get("price_cad") != 2.99:
        errs.append(f"price={row.get('price_cad')}")
    if row.get("subject") != "Language":
        errs.append(f"subject={row.get('subject')}")
    exp = TAXO.get(g)
    if not exp or row.get("taxonomy_id") != exp[0] or row.get("strand_name") != exp[1]:
        errs.append(f"taxonomy({g},{row.get('taxonomy_id')},{row.get('strand_name')})")
    previews = row.get("preview_images") or []
    files = row.get("files") or []
    if len(previews) < 1:
        errs.append("no_preview")
    if len(files) != 1:
        errs.append(f"files={len(files)}")

    border_ok = wm_ok = None
    if previews:
        counts, wm, size = analyse_png(previews[0])
        want = GRADE_RGB[g]
        exp_count = counts[g]
        others = max(v for k, v in counts.items() if k != g)
        border_ok = exp_count > 200 and exp_count > others * 2
        wm_ok = wm > 500
        if not border_ok:
            errs.append(f"border({g}:{exp_count} vs others:{others})")
        if not wm_ok:
            errs.append(f"watermark({wm})")
    return errs, border_ok, wm_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item-id", type=int)
    args = ap.parse_args()
    q = (f"{SB}/rest/v1/educational_resources?select=*&"
         + (f"item_id=eq.{args.item_id}" if args.item_id
            else "seller_name=eq.TheClassroomExchange&subject=eq.Language")
         + "&order=item_id")
    rows = json.load(get(q))
    print(f"verifying {len(rows)} row(s)\n")
    fails = 0
    for r in rows:
        errs, b, w = check_row(r)
        tag = "OK " if not errs else "FAIL"
        if errs:
            fails += 1
        print(f"[{tag}] {r['item_id']} {r['grade']:12} border={b} wm={w}  {r['title']}")
        if errs:
            print("       ->", ", ".join(errs))
    print(f"\n{len(rows)-fails}/{len(rows)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
