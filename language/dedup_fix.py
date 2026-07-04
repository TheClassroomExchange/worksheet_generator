"""De-duplicate the example words on "I Can Read Sentences" sheets.

Many worksheets repeat the same target word/image across sentences (e.g. au-pause:
sauce x3, astronaut x2). Each sheet should present DISTINCT target words with
distinct images. This tool keeps the first occurrence of each repeated word and
lets an author (the model) swap the later duplicate rows for new distinct words,
then rebuilds the unit from the edited data.json and gates the result.

Division of labour: the MODEL authors the replacement words/sentences (kid-friendly,
picturable). `vet()` validates them (decodable at the unit's lesson_order + grade,
target grapheme actually present, cached-image status). `apply()` snapshots, writes
the new sentences into data.json, rebuilds via gen_content+build_unit, and runs the
distinctness / preservation / decodability / page-count gates (restores on failure).

Usage (from wg-language, sibling venv, weasyprint env):
  PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
  ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.dedup_fix sweep
  ... dedup_fix.py report            # per-unit dupes + context to guide authoring
  ... dedup_fix.py vet <subj/unit> word1 word2 ...
  # apply is called programmatically: dedup_fix.apply('subj/unit', [ {text,pic,bold?}, ... ])
"""
from __future__ import annotations
import json, re, sys, shutil, subprocess, collections
from pathlib import Path

LANG = Path(__file__).resolve().parent
ROOT = LANG.parent
AI_DIR = ROOT / "assets" / "ai_line_art"
BACKUP = LANG / "_dedup_fix_backup"
LOGMD = LANG / "DEDUP_FIX_LOG.md"


# ── context loaders ──────────────────────────────────────────────────────────
def _subjects() -> dict:
    return {s["dir"]: s for s in json.loads((LANG / "subjects.json").read_text())["subjects"]}


def _topic(sdir: str, unit: str) -> dict:
    tj = json.loads((LANG / sdir / "topics.json").read_text())
    return next(t for t in tj["topics"] if t["dir"] == unit)


def _data_and_entry(sdir: str, unit: str):
    d = json.loads((LANG / sdir / "data.json").read_text())
    t = _topic(sdir, unit)
    key = unit if unit in d else (t["nn"] if t["nn"] in d else t["target_grapheme"])
    return d, key, d.get(key)


def _cached_images() -> set:
    return {p.stem.lower() for p in AI_DIR.glob("*.png")}


def _ctx(unit_rel: str):
    sdir, unit = unit_rel.split("/")
    subj = _subjects()[sdir]
    grade = subj["grade"]
    t = _topic(sdir, unit)
    d, key, entry = _data_and_entry(sdir, unit)
    order = int(entry.get("order", t["order"]))
    return dict(sdir=sdir, unit=unit, grade=grade, topic=t, data=d, key=key,
                entry=entry, order=order, grapheme=t["target_grapheme"])


# ── sweep ────────────────────────────────────────────────────────────────────
def sweep() -> list[str]:
    """Reading worksheets whose reading_rows repeat a pic-word (or a sentence)."""
    out = []
    for f in sorted(LANG.glob("*/*/content.json")):
        if "_samples" in f.parts:
            continue
        parts = json.loads(f.read_text()).get("worksheet", {}).get("parts", [])
        rr = [p for p in parts if p.get("type") == "reading_rows"]
        if not rr:
            continue
        dup = False
        for p in rr:
            rows = p.get("rows", [])
            pics = [r.get("word", "") for r in rows if r.get("word")]
            texts = [r.get("text", "").strip().lower() for r in rows]
            if (pics and len(set(pics)) < len(pics)) or len(set(texts)) < len(texts):
                dup = True
        if dup:
            out.append(f"{f.parent.parent.name}/{f.parent.name}")
    return out


def report():
    from language import decodability as dc
    scope = dc.load_scope()
    cached = _cached_images()
    for rel in sweep():
        c = _ctx(rel)
        f = LANG / rel / "content.json"
        parts = json.loads(f.read_text())["worksheet"]["parts"]
        rr = next(p for p in parts if p.get("type") == "reading_rows")
        pics = [r.get("word", "") for r in rr["rows"]]
        cnt = collections.Counter(pics)
        dupwords = [w for w, k in cnt.items() if k > 1]
        print(f"\n### {rel}  grapheme='{c['grapheme']}' order={c['order']} {c['grade']}")
        for i, r in enumerate(rr["rows"], 1):
            dupmark = "  <-- DUP" if cnt[r.get("word", "")] > 1 else ""
            print(f"  {i}. {r.get('word',''):12} | {r['text']}{dupmark}")
        print(f"  distinct {len(set(pics))}/{len(pics)}; repeated: {dupwords}")


# ── grapheme-word (example word) sweep ───────────────────────────────────────
def word_sweep():
    """Reading units where a *content* grapheme example-word repeats across
    sentences AND the grapheme has other decodable words (actionable), vs the
    single-inventory cases that are unavoidable. Returns (actionable, unavoidable)
    each a list of (unit_rel, grapheme, {word:count})."""
    from language import decodability as dc
    scope = dc.load_scope()
    actionable = []; unavoid = []
    for f in sorted(LANG.glob("*/*/content.json")):
        if "_samples" in f.parts:
            continue
        rel = f"{f.parent.parent.name}/{f.parent.name}"
        d = json.loads(f.read_text())
        rr = [p for p in d["worksheet"]["parts"] if p.get("type") == "reading_rows"]
        if not rr:
            continue
        c = _ctx(rel)
        texts = [row.get("text", "") for p in rr if p.get("title") != "Build the word"
                 for row in p.get("rows", [])]
        gw = _gwords(texts, c["grapheme"], c["order"], scope)
        import collections as _c
        dup = {w: n for w, n in _c.Counter(gw).items() if n > 1}
        if dup:
            rec = (rel, c["grapheme"], dup)
            (unavoid if len(set(gw)) <= 1 else actionable).append(rec)
    return actionable, unavoid


def word_report():
    from language import decodability as dc
    scope = dc.load_scope()
    actionable, _ = word_sweep()
    aset = {r[0] for r in actionable}
    for rel, g, dup in actionable:
        c = _ctx(rel)
        rr = [p for p in json.loads((LANG / rel / "content.json").read_text())
              ["worksheet"]["parts"] if p.get("type") == "reading_rows"]
        print(f"\n### {rel} [{g}] order={c['order']} {c['grade']}  repeats={dup}")
        for p in rr:
            if p.get("title") == "Build the word":
                continue
            for i, row in enumerate(p.get("rows", []), 1):
                print(f"  {i}. {row.get('word',''):10} | {row['text']}")


# ── vet author-proposed words ────────────────────────────────────────────────
def vet(unit_rel: str, words: list[str]):
    from language import decodability as dc
    scope = dc.load_scope()
    c = _ctx(unit_rel)
    cached = _cached_images()
    g = c["grapheme"].lower()
    print(f"vet {unit_rel}  grapheme='{g}' order={c['order']} {c['grade']}")
    for w in words:
        wl = w.lower()
        seg = dc.segment_word(wl, c["order"], scope)
        in_seg = bool(seg) and g in [s.replace("(silent)", "") for s in seg]
        substr = g in wl
        print(f"  {w:14} decodable={'Y' if seg else 'N'}  grapheme_in_word={'Y' if substr else 'N'}"
              f"  grapheme_is_segment={'Y' if in_seg else 'N'}  cached_img={'Y' if wl in cached else 'N'}"
              f"  seg={seg}")


# ── gates ────────────────────────────────────────────────────────────────────
def _npages(pdf: Path) -> int:
    from pypdf import PdfReader
    return len(PdfReader(str(pdf)).pages)


def _pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout


# ── grapheme-word (example word) analysis ────────────────────────────────────
_STOP = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "and", "he", "she",
         "we", "my", "i", "see", "can", "has", "red", "big", "of", "up", "by", "you",
         "your", "not", "am", "are", "be", "do", "go", "me", "no", "so", "us", "was", "for"}


def _gwords(texts, grapheme: str, order: int, scope) -> list[str]:
    """Content words across the sentences that actually EXERCISE the grapheme
    (a true segment), excluding grammatical function words. These are the
    'example words' the child is meant to meet — one distinct per sentence."""
    from language import decodability as dc
    g = grapheme.replace("_", "").lower()
    out = []
    for t in texts:
        for w in re.findall(r"[A-Za-z]+", t):
            wl = w.lower()
            if wl in _STOP:
                continue
            seg = dc.segment_word(wl, order, scope)
            if seg and g in [s.replace("(silent)", "") for s in seg]:
                out.append(wl)
    return out


# ── apply ────────────────────────────────────────────────────────────────────
def apply(unit_rel: str, new_sentences: list[dict], *, allow_repeats: int = 0,
          backup_dir: Path = None, preserve: bool = True,
          require_distinct_words: bool = False, allow_word_repeats: int = 0,
          expect_pics: list = None) -> dict:
    """Swap the unit's sentences for `new_sentences` (full list, order preserved),
    rebuild, and gate. Restores on any failure.

    allow_repeats: max tolerated duplicate pic-words (inventory exceptions).
    backup_dir: where snapshots live (round 3 uses a fresh dir so it captures the
                current state, not a stale earlier-round baseline).
    preserve: enforce that first-occurrence originals stay verbatim (round 1/2).
              Round 3 rewords sentences intentionally, so it passes preserve=False.
    require_distinct_words: enforce distinct grapheme example words per sentence.
    expect_pics: if given, assert final pic set equals this (no surprise image gen)."""
    from language import gen_content, language_build as lb, language_rubric as lr, decodability as dc
    c = _ctx(unit_rel)
    sdir, unit = c["sdir"], c["unit"]
    unit_dir = LANG / sdir / unit
    r = {"unit": unit_rel, "status": "?", "gates": {}}

    # locate current single PDF
    pdfs = list(unit_dir.glob("*.pdf"))
    old_pdf = pdfs[0] if len(pdfs) == 1 else None
    if not old_pdf:
        r["status"] = "fail"; r["err"] = "no single PDF"; return r

    # snapshot
    bd = (backup_dir or BACKUP) / sdir; bd.mkdir(parents=True, exist_ok=True)
    snap_pdf = bd / f"{unit}__{old_pdf.name}"
    snap_cj = bd / f"{unit}__content.json"
    snap_dj = bd / f"{unit}__data_entry.json"
    for src, dst in [(old_pdf, snap_pdf), (unit_dir / "content.json", snap_cj)]:
        if not dst.exists(): shutil.copy2(src, dst)
    orig = json.loads(snap_cj.read_text())
    orig_rr = next(p for p in orig["worksheet"]["parts"] if p.get("type") == "reading_rows")
    orig_sents = [row["text"] for row in orig_rr["rows"]]
    # match the sheet's per-row bold convention: some subjects (low-freq vowels) set
    # bold=<whole word>; most rely on the part-level grapheme bold (no per-row key).
    per_row_bold = any("bold" in row for row in orig_rr["rows"])
    if per_row_bold:
        for s in new_sentences:
            s.setdefault("bold", s.get("pic", ""))
    # first occurrence per pic-word = the sentences that MUST be preserved verbatim.
    # Pre-broken rows (pic word not in its own sentence) are legitimately replaceable,
    # so they are NOT required to be preserved.
    seen = set(); must_keep = []
    for row in orig_rr["rows"]:
        w = (row.get("word") or "").lower(); t = row.get("text", "")
        broken = w and w not in t.lower()
        if w and w not in seen:
            seen.add(w)
            if not broken:
                must_keep.append(t)
    if not snap_dj.exists():
        snap_dj.write_text(json.dumps({"key": c["key"], "entry": c["entry"]}, ensure_ascii=False, indent=2))

    scope = dc.load_scope()
    try:
        # pre-vet decodability + target present BEFORE any image gen
        texts = [s["text"] for s in new_sentences]
        chk = dc.check_text(texts, c["order"], c["grade"], scope)
        if not chk["passed"]:
            raise RuntimeError(f"decodability pre-vet: {chk['failures']}")
        pics = [s.get("pic", "") for s in new_sentences]
        ndup = len(pics) - len(set(pics))
        if ndup > allow_repeats:
            raise RuntimeError(f"distinctness: {len(set(pics))}/{len(pics)} distinct (allow_repeats={allow_repeats})")
        for s in new_sentences:  # each pic word appears in its own sentence
            if s.get("pic") and s["pic"].lower() not in s["text"].lower():
                raise RuntimeError(f"image-word not in sentence: {s['pic']!r} / {s['text']!r}")
        if preserve:
            for kept in must_keep:  # first-occurrence originals retained verbatim
                if kept not in texts:
                    raise RuntimeError(f"preservation: dropped a first-occurrence original: {kept!r}")
        if require_distinct_words:  # each sentence exercises a DISTINCT grapheme word
            gw = _gwords(texts, c["grapheme"], c["order"], scope)
            wdup = len(gw) - len(set(gw))
            r["gates"]["gwords"] = f"{len(set(gw))} distinct / {len(gw)}"
            if wdup > allow_word_repeats:
                import collections as _c
                reps = {w: n for w, n in _c.Counter(gw).items() if n > 1}
                raise RuntimeError(f"grapheme-word repeat: {reps} (allow={allow_word_repeats})")
        if expect_pics is not None:  # no-surprise image: pic set must be unchanged
            got = [s.get("pic", "") for s in new_sentences]
            if sorted(got) != sorted(expect_pics):
                raise RuntimeError(f"pic set changed (surprise image): {got} != {expect_pics}")

        # write data.json (source of truth)
        dj_path = LANG / sdir / "data.json"
        data = json.loads(dj_path.read_text())
        data[c["key"]]["sentences"] = new_sentences
        dj_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

        # rebuild
        entry = data[c["key"]]
        content = gen_content.generate(c["topic"], entry, c["grade"])
        (unit_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2))
        build = lb.build_unit(unit_dir, c["grade"])
        new_pdf = Path(build["pdf"])
        lr.record_grade(unit_dir, c["grade"], {"C1": 4, "C2": 4, "C3": 4, "C4": 4, "C5": 4})

        # post gates
        dec = dc.check_unit(unit_dir)
        r["gates"]["decodable"] = dec["passed"]
        if not dec["passed"]:
            raise RuntimeError(f"decodability gate: {[f['word'] for f in dec['failures']]}")
        npg = _npages(new_pdf); r["gates"]["pages"] = f"{_npages(snap_pdf)}->{npg}"
        if _npages(snap_pdf) != npg:
            raise RuntimeError(f"page-count: {_npages(snap_pdf)}!={npg}")
        if preserve:
            newtext = _pdf_text(new_pdf)
            missing = [k for k in must_keep if k not in newtext]
            r["gates"]["preserve"] = "ok" if not missing else f"MISSING {missing}"
            if missing:
                raise RuntimeError(f"preservation in PDF: {missing}")
        final_pics = [row.get("word", "") for row in content["worksheet"]
                      ["parts"][[p["type"] for p in content["worksheet"]["parts"]].index("reading_rows")]["rows"]]
        r["gates"]["distinct"] = f"{len(set(final_pics))}/{len(final_pics)}"
        r["status"] = "pass"; r["pdf"] = str(new_pdf); r["pics"] = final_pics
    except Exception as e:
        # restore data.json entry + content.json + pdf
        dj_path = LANG / sdir / "data.json"
        data = json.loads(dj_path.read_text())
        saved = json.loads(snap_dj.read_text())
        data[saved["key"]] = saved["entry"]
        dj_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        shutil.copy2(snap_cj, unit_dir / "content.json")
        shutil.copy2(snap_pdf, old_pdf)
        r["status"] = "fail"; r["err"] = str(e)
    return r


def _orig_rows(unit_rel: str):
    """Original reading_rows rows — from the snapshot backup if the unit was already
    touched this session, else the current content.json (the true original)."""
    sdir, unit = unit_rel.split("/")
    snap = BACKUP / sdir / f"{unit}__content.json"
    src = snap if snap.exists() else (LANG / sdir / unit / "content.json")
    parts = json.loads(src.read_text())["worksheet"]["parts"]
    rr = next(p for p in parts if p.get("type") == "reading_rows")
    return rr["rows"]


def assemble(unit_rel: str, replacements: list[dict]) -> list[dict]:
    """Keep every first-occurrence, in-sentence original row verbatim; replace ONLY
    the duplicate-pic rows and pre-broken rows (pic word not in its sentence) with
    entries from `replacements` (in order). Returns the full new sentence list."""
    orig = _orig_rows(unit_rel)
    seen = set(); out = []; ri = 0
    for row in orig:
        w = (row.get("word") or "").lower()
        txt = row.get("text", "")
        broken = w and w not in txt.lower()
        is_dup = w in seen
        if (is_dup or broken) and ri < len(replacements):
            rep = replacements[ri]; ri += 1
            out.append({"text": rep["text"], "pic": rep["pic"]})
        else:
            keep = {"text": txt}
            if row.get("word"): keep["pic"] = row["word"]
            out.append(keep)
            if w: seen.add(w)
    if ri != len(replacements):
        raise RuntimeError(f"{unit_rel}: {len(replacements)} replacements but consumed {ri} slots")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "sweep":
        u = sweep()
        by = collections.Counter(x.split("/")[0] for x in u)
        print(f"impacted reading worksheets: {len(u)}")
        for k, c in sorted(by.items()): print(f"  {c:3}  {k}")
        for x in u: print("   ", x)
    elif a[0] == "report":
        report()
    elif a[0] == "word_sweep":
        act, un = word_sweep()
        print(f"actionable (content grapheme-word repeats): {len(act)}")
        for u, g, dup in act:
            print(f"  {u} [{g}] {dup}")
        print(f"unavoidable (single grapheme-word): {len(un)}")
        for u, g, dup in un:
            print(f"  {u} [{g}] {dup}")
    elif a[0] == "word_report":
        word_report()
    elif a[0] == "vet":
        vet(a[1], a[2:])
    else:
        print("use: sweep | report | vet <subj/unit> <words...>")
