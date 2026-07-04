"""Round 8 — faceless-image regen + augh distinct-example fix.

Two change types, each behind its own preservation gate (worksheet page is otherwise
untouched; TG answer key re-derived from the worksheet so it stays in sync):

  IMAGE units (ir-bird, ew-new, ly-slowly, gh-ghost): a shared cached image was
  regenerated with a face (bird.png / ghost.png). Content JSON is unchanged; only the
  picture cell changes. Gate: worksheet TEXT identical + raster change confined to the
  image column + 2pp.

  AUGH unit (augh-taught): sentence 5 "I caught the pup." → "I hug my granddaughter."
  (5 distinct augh words). content.json row + data.json synced; teacher_guide re-derived
  so the answer key shows "granddaughter" not a 2nd "caught". Gate: worksheet text
  changes ONLY in that row (removed ⊆ old-row tokens, added ⊆ new-row tokens) + the TG
  answer key reflects it + decodability/image-align (pic word in sentence) + 2pp.

Snapshots to _facefix_backup/; reverts on any gate failure. Run:
  PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
  ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.face_fix run
"""
from __future__ import annotations
import json, re, sys, shutil, subprocess, tempfile
from pathlib import Path

from language import gen_content as gc
from language import tg_fix as T
from language.reveal_fix import _grade_by_dir, _npages

LANG = T.LANG
BACKUP = LANG / "_facefix_backup"
LOGMD = LANG / "FACE_FIX_LOG.md"

IMAGE_UNITS = ["g1_rcontrolled/06_ir-bird", "g2_low_freq_vowels/05_ew-new",
               "g3_prefixes/01_ly-slowly", "g2_silent_letters/02_gh-ghost"]
AUGH_UNIT = "g2_low_freq_vowels/04_augh-taught"
AUGH_OLD = "I caught the pup."
AUGH_NEW = "I hug my granddaughter."
AUGH_PIC = "granddaughter"


def _combined_pdf(ud: Path) -> Path | None:
    return T._combined_pdf(ud)


def _snapshot(ud: Path):
    subj = ud.parent.name
    bk = BACKUP / subj; bk.mkdir(parents=True, exist_ok=True)
    pdf = _combined_pdf(ud)
    for src, name in [(pdf, f"{ud.name}__{pdf.name}"), (ud / "content.json", f"{ud.name}__content.json")]:
        dst = bk / name
        if not dst.exists():
            shutil.copy2(src, dst)
    return bk / f"{ud.name}__{pdf.name}", bk / f"{ud.name}__content.json", pdf


def _raster_change_region(old_pdf: Path, new_pdf: Path) -> tuple[float, float, float, float] | None:
    """Bounding box (fractions of W,H) of the page-1 raster change, or None if identical."""
    from PIL import Image, ImageChops
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        def r1(pdf, tag):
            subprocess.run(["pdftoppm", "-png", "-r", "100", "-f", "1", "-l", "1", str(pdf), str(td / tag)],
                           check=True, capture_output=True)
            return next(iter(sorted(td.glob(f"{tag}-*.png"))))
        a = Image.open(r1(old_pdf, "o")).convert("L"); b = Image.open(r1(new_pdf, "n")).convert("L")
        if a.size != b.size:
            return (0.0, 0.0, 1.0, 1.0)
        diff = ImageChops.difference(a, b).point(lambda p: 255 if p > 40 else 0)
        bb = diff.getbbox()
        if not bb:
            return None
        w, h = a.size
        return (bb[0] / w, bb[1] / h, bb[2] / w, bb[3] / h)


def _fix_image_unit(ud: Path, grade: str, snap_pdf: Path) -> dict:
    """Rebuild only (image cache already regenerated). Gate: text identical + change
    confined to the right-hand image column."""
    from language import language_build as lb
    r = {"gates": {}}
    new_pdf = Path(lb.build_unit(ud, grade)["pdf"])
    ok, det = T.gate_worksheet_preserved(snap_pdf, new_pdf, allow_removals=False)
    r["gates"]["text"] = det
    if not ok:
        raise RuntimeError(f"text gate: {det}")
    region = _raster_change_region(snap_pdf, new_pdf)
    if region is None:
        raise RuntimeError("no raster change — image did not update")
    x0, y0, x1, y1 = region
    r["gates"]["raster_region"] = f"x{x0:.2f}-{x1:.2f} y{y0:.2f}-{y1:.2f}"
    if x1 < 0.50:   # entire change left of centre = text area, not the image column
        raise RuntimeError(f"raster change not in image column: {r['gates']['raster_region']}")
    n = _npages(new_pdf); r["gates"]["pages"] = f"{n}"
    if n != 2:
        raise RuntimeError(f"page-count {n} != 2")
    r["pdf"] = str(new_pdf)
    return r


def _fix_augh(ud: Path, grade: str, snap_pdf: Path) -> dict:
    """Swap sentence 5 → granddaughter; re-derive TG; rebuild; gate row-local text
    change + answer-key sync + image-align + 2pp."""
    from language import language_build as lb
    r = {"gates": {}}
    content = json.loads((ud / "content.json").read_text())
    # edit worksheet row
    swapped = False
    for p in content["worksheet"]["parts"]:
        if p.get("type") != "reading_rows":
            continue
        for row in p["rows"]:
            if row.get("text") == AUGH_OLD:
                row["text"] = AUGH_NEW; row["word"] = AUGH_PIC; row.pop("img", None)
                swapped = True
    if not swapped:
        raise RuntimeError(f"augh row {AUGH_OLD!r} not found")
    # re-derive teacher guide so the answer key reflects the new sentence
    content["teacher_guide"] = gc.derive_teacher_guide(content, grade)
    (ud / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False))
    # sync data.json (durability)
    dpath = ud.parent / "data.json"
    data = json.loads(dpath.read_text())
    for entry in data.values():
        for s in entry.get("sentences", []) if isinstance(entry, dict) else []:
            if s.get("text") == AUGH_OLD:
                s["text"] = AUGH_NEW; s["pic"] = AUGH_PIC
    dpath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    # rebuild (build_unit runs decodability + border gates internally)
    new_pdf = Path(lb.build_unit(ud, grade)["pdf"])
    # text change must be row-local
    from collections import Counter
    o = Counter(T._tokens(T._page_text(snap_pdf, 1))); n = Counter(T._tokens(T._page_text(new_pdf, 1)))
    added, removed = n - o, o - n
    allow_add = set(re.findall(r"\S+", AUGH_NEW)); allow_rem = set(re.findall(r"\S+", AUGH_OLD))
    bad_add = [t for t in added if t not in allow_add]
    bad_rem = [t for t in removed if t not in allow_rem]
    r["gates"]["text"] = f"+{list(added.elements())} -{list(removed.elements())}"
    if bad_add or bad_rem:
        raise RuntimeError(f"text change not row-local: bad_add={bad_add} bad_rem={bad_rem}")
    # answer key synced: TG shows granddaughter, no 2nd 'caught'
    tg = T._page_text(new_pdf, _npages(new_pdf))
    if "granddaughter" not in tg.lower():
        raise RuntimeError("answer key missing 'granddaughter'")
    if len(re.findall(r"caught", tg.lower())) > 1:
        raise RuntimeError("answer key still repeats 'caught'")
    r["gates"]["answer"] = "granddaughter keyed; caught x1"
    # image-align: pic word in its sentence
    if AUGH_PIC.lower() not in AUGH_NEW.lower():
        raise RuntimeError("pic word not in sentence")
    n2 = _npages(new_pdf); r["gates"]["pages"] = f"{n2}"
    if n2 != 2:
        raise RuntimeError(f"page-count {n2} != 2")
    r["pdf"] = str(new_pdf)
    return r


def process(unit_rel: str, grade_map: dict) -> dict:
    ud = LANG / unit_rel
    grade = grade_map[ud.parent.name]
    r = {"unit": unit_rel, "grade": grade, "status": "?"}
    snap_pdf, snap_cj, live = _snapshot(ud)
    try:
        fn = _fix_augh if unit_rel == AUGH_UNIT else _fix_image_unit
        r.update(fn(ud, grade, snap_pdf))
        r["status"] = "pass"
    except Exception as e:
        shutil.copy2(snap_cj, ud / "content.json")
        shutil.copy2(snap_pdf, live)
        r["status"] = "fail"; r["err"] = str(e)
    return r


def _log(results):
    ok = [x for x in results if x["status"] == "pass"]
    lines = ["# Face-fix / augh run log\n", f"- pass {len(ok)}/{len(results)}\n"]
    for x in results:
        m = "✅" if x["status"] == "pass" else "❌"
        lines.append(f"{m} `{x['unit']}` " + " ".join(f"{k}=[{v}]" for k, v in x.get("gates", {}).items())
                     + (f" ERR={x['err']}" if x.get("err") else ""))
    LOGMD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    gm = _grade_by_dir()
    units = IMAGE_UNITS + [AUGH_UNIT]
    results = []
    for u in units:
        res = process(u, gm); results.append(res)
        print(f"{res['status'].upper():4} {u}" + (f"  ERR={res.get('err')}" if res["status"] != "pass" else ""))
        _log(results)
    _log(results)
    bad = [x for x in results if x["status"] != "pass"]
    print(f"\nDONE pass={len(results)-len(bad)} fail={len(bad)}")
    sys.exit(1 if bad else 0)
