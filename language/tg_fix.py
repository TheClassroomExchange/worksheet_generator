"""Teacher-Guide QA sweep + remediation for the K-3 phonics catalogue.

The page-2 "Teacher Guide" (answer key + facilitation notes) was added after the
round-1..6 remediation and shipped with four category-specific bugs:
  D1  blank answer key ("Sentence i: —") on split-VCe (a_e…) + pseudo (schwa) targets
  D2  word-building answer key lists FABRICATED sentences, not the worksheet's real rows
  D3  "How to lead it" step 3 hardcodes "underline" even on circle / bold-aid sheets
  D4  word-building worksheet overflowed to 2 pages → TG pushed to page 3 (sparse spill)

Root cause + durable fix live in ``gen_content``:
  ``derive_teacher_guide(content, grade)`` rebuilds the guide FROM the worksheet block
  (the live truth) — fixing D1/D2/D3 — and ``cap_reading_sentences`` restores the
  one-page word-building layout (D4). This orchestrator applies them per unit behind
  hard gates, never touching the worksheet page except the D4 sentence cap.

Per impacted unit:
  1. snapshot combined PDF + content.json to ``_tg_fix_backup/`` (revertible),
  2. rewrite ONLY content["teacher_guide"] via derive_teacher_guide (+ D4 cap on
     word-building), never regenerating worksheet rows from data.json,
  3. re-render via language_build.build_unit (cached images -> $0; decodability +
     border gates run internally),
  4. gate: page-1 preservation (worksheet identical, or removals-only for a D4 cap),
     answer-key correctness (no "—"; every answer word is in its sentence), verb match,
     page-count (<=2, TG is the last single page),
  5. log; on any gate failure restore the snapshot and mark the unit failed.

Usage (from wg-language, sibling venv, weasyprint env):
  PYTHONPATH=. DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
  ~/Desktop/TCE/worksheet_generator/venv/bin/python -m language.tg_fix sweep
  ... tg_fix.py <unit_rel>            # one unit (backtest)
  ... tg_fix.py run [--limit N]       # all impacted units
  ... tg_fix.py only <rel> <rel> ...  # a named subset
"""
from __future__ import annotations
import json, re, sys, shutil, subprocess, tempfile
from pathlib import Path

from language import gen_content as gc
from language.reveal_fix import _grade_by_dir, _npages

LANG = Path(__file__).resolve().parent
ROOT = LANG.parent
BACKUP = LANG / "_tg_fix_backup"
LOGMD = LANG / "TG_FIX_LOG.md"
QAMD = LANG / "TG_QA_LOG.md"
IMPACTED = LANG / "tg_impacted.json"

WB_SENTENCE_CAP = 3  # one-page word-building layout: build table + 3 sentences + tracker

# Track 2 (kids-safe): sentence rows to drop from a worksheet, keyed by unit rel,
# matched on the pictured word. User-approved: G1 'ull' sheet drops the "I see a
# skull." row (skull is the most morbid flag; 'ull' has no other safe picturable
# noun, so we drop to 4 sentences rather than force an awkward/obscure swap).
DROP_ROWS: dict[str, list[str]] = {
    "g1_doubles_blends/08_ull-full": ["skull"],
}


# ── content helpers ────────────────────────────────────────────────────────────
def _load(unit_dir: Path) -> dict:
    return json.loads((unit_dir / "content.json").read_text())


def _combined_pdf(unit_dir: Path) -> Path | None:
    rj = unit_dir / "render.json"
    if rj.exists():
        p = unit_dir / json.loads(rj.read_text())["combined_pdf"]
        if p.exists():
            return p
    pdfs = [p for p in unit_dir.glob("*.pdf")]
    return pdfs[0] if len(pdfs) == 1 else None


def _wtype(content: dict) -> str:
    ws = content["worksheet"]
    ptypes = [p.get("type") for p in ws["parts"]]
    if "formation" in ptypes or "picture_row" in ptypes:
        return "letter_sound"
    return "word_building" if gc._is_word_building(ws) else "sentences"


def _answer_lines(tg: dict) -> list[str]:
    for p in tg.get("parts", []):
        if str(p.get("title", "")).startswith("Answer"):
            t = p.get("text", [])
            return list(t) if isinstance(t, list) else [t]
    return []


def _step3(tg: dict) -> str:
    for p in tg.get("parts", []):
        if str(p.get("title", "")).startswith("How to"):
            t = p.get("text", [])
            for line in (t if isinstance(t, list) else [t]):
                if str(line).strip().startswith("3."):
                    return str(line)
    return ""


# ── the 8-check rubric mark ─────────────────────────────────────────────────────
def _defects(unit_dir: Path, grade: str) -> dict:
    """Per-unit rubric mark. A FAIL in any check flags the unit impacted."""
    content = _load(unit_dir)
    wtype = _wtype(content)
    stored_tg = content.get("teacher_guide", {})
    derived_tg = gc.derive_teacher_guide(content, grade)
    stored_ak, derived_ak = _answer_lines(stored_tg), _answer_lines(derived_tg)
    pdf = _combined_pdf(unit_dir)
    npages = _npages(pdf) if pdf else -1

    d = {
        "unit": f"{unit_dir.parent.name}/{unit_dir.name}", "grade": grade, "type": wtype,
        "pages": npages, "classes": [],
    }
    # check 1: answer-key completeness (no blank "—")
    if any(re.search(r":\s*—", s) for s in stored_ak):
        d["classes"].append("D1_blank_key")
    # check 2/3: guide drift vs the worksheet-projected truth (answer + verb)
    if stored_ak != derived_ak:
        if wtype == "word_building":
            d["classes"].append("D2_key_mismatch")
        else:
            d["classes"].append("key_drift")
    if _step3(stored_tg) != _step3(derived_tg):
        d["classes"].append("D3_verb")
    # check 4: page count / fill
    if npages > 2:
        d["classes"].append("D4_overflow")
    d["stored_tg_ok"] = (stored_tg == derived_tg)
    d["impacted"] = bool(d["classes"]) or not d["stored_tg_ok"]
    return d


def sweep() -> list[dict]:
    gm = _grade_by_dir()
    out = []
    for f in sorted(LANG.glob("*/*/content.json")):
        if "_samples" in f.parts:
            continue
        subject = f.parent.parent.name
        if subject not in gm:
            continue
        out.append(_defects(f.parent, gm[subject]))
    return out


def write_mark_table(rows: list[dict]):
    imp = [r for r in rows if r["impacted"]]
    lines = ["# Teacher-Guide QA — full catalogue mark\n",
             f"Scanned **{len(rows)}** units · impacted **{len(imp)}** · clean **{len(rows)-len(imp)}**.\n",
             "| # | unit | grade | type | pages | defect classes |",
             "|---|------|-------|------|-------|----------------|"]
    for i, r in enumerate(sorted(rows, key=lambda x: (not x["impacted"], x["unit"])), 1):
        cls = ", ".join(r["classes"]) or ("tg_drift" if not r["stored_tg_ok"] else "—")
        mark = "" if r["impacted"] else "✅ "
        lines.append(f"| {i} | {mark}`{r['unit']}` | {r['grade']} | {r['type']} | {r['pages']} | {cls} |")
    QAMD.write_text("\n".join(lines) + "\n")
    IMPACTED.write_text(json.dumps([r for r in rows], indent=2) + "\n")


# ── apply ────────────────────────────────────────────────────────────────────────
def _apply_fix(unit_dir: Path, grade: str) -> dict:
    """Rewrite teacher_guide from the worksheet; cap word-building sentences (D4).
    Returns {'page1_changed': bool} — True iff the D4 cap removed worksheet rows."""
    content = _load(unit_dir)
    page1_changed = False
    rel = f"{unit_dir.parent.name}/{unit_dir.name}"
    drops = [d.lower() for d in DROP_ROWS.get(rel, [])]
    if drops:  # Track-2 kids-safe row removal (by pictured word)
        for p in content["worksheet"].get("parts", []):
            if p.get("type") != "reading_rows":
                continue
            kept = [r for r in p["rows"]
                    if str(r.get("word", "")).lower() not in drops]
            if len(kept) != len(p["rows"]):
                p["rows"] = kept
                page1_changed = True
    is_wb = _wtype(content) == "word_building"
    if is_wb:
        gc.cap_reading_sentences(content, WB_SENTENCE_CAP)
    content["teacher_guide"] = gc.derive_teacher_guide(content, grade)
    (unit_dir / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False))
    # allow_removals is a per-unit POLICY (word-building sheets are capped; a DROP_ROWS
    # unit sheds a row), not a function of whether THIS idempotent run happened to trim —
    # otherwise a re-run against the original snapshot would demand impossible identity.
    return {"page1_changed": is_wb or bool(drops)}


# ── gates ──────────────────────────────────────────────────────────────────────
def _page_text(pdf: Path, page: int) -> str:
    out = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    return out


def _tokens(s: str) -> list[str]:
    return re.findall(r"\S+", s)


def _worksheet_text(pdf: Path) -> str:
    """All worksheet pages = every page except the last (the Teacher Guide is always
    the final single page). Robust to a D4 cap changing the worksheet page count."""
    n = _npages(pdf)
    return "".join(_page_text(pdf, p) for p in range(1, max(1, n)))  # pages 1..n-1


def gate_worksheet_preserved(old_pdf: Path, new_pdf: Path, allow_removals: bool) -> tuple[bool, str]:
    """The worksheet (every non-TG page) must be preserved. Pure-TG fix → worksheet
    text identical. D4 cap → worksheet tokens are a multiset SUBSET of the old
    (capped sentences removed via reflow; nothing added or altered)."""
    from collections import Counter
    o, n = _tokens(_worksheet_text(old_pdf)), _tokens(_worksheet_text(new_pdf))
    if not allow_removals:
        return (o == n, "worksheet text identical" if o == n
                else f"worksheet changed (+{sorted(set(n)-set(o))[:6]} / -{sorted(set(o)-set(n))[:6]})")
    co, cn = Counter(o), Counter(n)
    added = cn - co
    if added:
        return False, f"worksheet added tokens: {list(added.elements())[:8]}"
    removed = co - cn
    return True, f"worksheet removals only ({sum(removed.values())} tokens: {list(removed)[:8]})"


def gate_worksheet_raster(old_pdf: Path, new_pdf: Path, allow_removals: bool) -> tuple[bool, str]:
    """Page-1 raster identity — only meaningful for a pure-TG fix (page count and
    layout unchanged). A D4 cap reflows pages, so raster identity does not apply;
    the token-subset check above is the preservation proof there."""
    if allow_removals:
        return True, "raster identity N/A (D4 reflow) — worksheet-text subset verified"
    from PIL import Image, ImageChops
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        def r1(pdf, tag):
            subprocess.run(["pdftoppm", "-png", "-r", "100", "-f", "1", "-l", "1", str(pdf), str(td / tag)],
                           check=True, capture_output=True)
            return next(iter(sorted(td.glob(f"{tag}-*.png"))), None)
        op, np_ = r1(old_pdf, "o"), r1(new_pdf, "n")
        a = Image.open(op).convert("L"); b = Image.open(np_).convert("L")
        if a.size != b.size:
            return False, "page-1 raster size differs"
        diff = ImageChops.difference(a, b).point(lambda p: 255 if p > 40 else 0)
        bbox = diff.getbbox()
        if not bbox:
            return True, "page-1 raster identical"
        return False, f"page-1 raster changed at {bbox} (expected identical)"


def gate_answer_key(unit_dir: Path) -> tuple[bool, str]:
    """No blank '—'; every listed answer word actually occurs in its sentence."""
    content = _load(unit_dir)
    tg = content["teacher_guide"]
    ak = _answer_lines(tg)
    for s in ak:
        if re.search(r":\s*—", s):
            return False, f"blank answer remains: {s!r}"
    if _wtype(content) == "sentences":
        rows = (gc._sentence_part(content["worksheet"]) or {}).get("rows", [])
        for i, line in enumerate([s for s in ak if s.startswith("Sentence ")]):
            m = re.match(r"Sentence \d+:\s*(.+?)\.?$", line)
            if not m or i >= len(rows):
                continue
            sent = rows[i]["text"].lower()
            for w in [x.strip() for x in m.group(1).split(",")]:
                if w and w.lower() not in sent:
                    return False, f"answer '{w}' not in sentence {i+1}: {rows[i]['text']!r}"
    return True, f"{sum(1 for s in ak if s.startswith('Sentence'))} sentences keyed, no blanks"


def gate_verb(unit_dir: Path, grade: str) -> tuple[bool, str]:
    content = _load(unit_dir)
    want = gc._lead_step3(content["phonics"]["target_grapheme"],
                          next((p.get("text", "") for p in content["worksheet"]["parts"]
                                if p.get("type") == "prose"), ""))
    got = _step3(content["teacher_guide"])
    if _wtype(content) == "word_building":
        return True, "word-building lead (build steps, no find-verb)"
    return (got == want, "step-3 verb matches directions" if got == want
            else f"verb mismatch: {got!r} != {want!r}")


def gate_pages(new_pdf: Path) -> tuple[bool, str]:
    n = _npages(new_pdf)
    return (n <= 2, f"{n} pages" if n <= 2 else f"still {n} pages (>2)")


# ── per-unit driver ──────────────────────────────────────────────────────────────
def process_unit(unit_dir: Path, grade_map: dict | None = None) -> dict:
    unit_dir = Path(unit_dir)
    subject = unit_dir.parent.name
    grade_map = grade_map or _grade_by_dir()
    grade = grade_map[subject]
    r = {"unit": f"{subject}/{unit_dir.name}", "grade": grade, "gates": {}, "status": "?"}

    old_pdf = _combined_pdf(unit_dir)
    if not old_pdf:
        r["status"] = "fail"; r["err"] = "cannot locate single existing PDF"; return r

    bkp = BACKUP / subject; bkp.mkdir(parents=True, exist_ok=True)
    snap_pdf = bkp / f"{unit_dir.name}__{old_pdf.name}"
    snap_cj = bkp / f"{unit_dir.name}__content.json"
    if not snap_pdf.exists():
        shutil.copy2(old_pdf, snap_pdf)
    if not snap_cj.exists():
        shutil.copy2(unit_dir / "content.json", snap_cj)

    try:
        info = _apply_fix(unit_dir, grade)
        allow = info["page1_changed"]
        r["page1_changed"] = allow
        from language import language_build as lb
        build = lb.build_unit(unit_dir, grade)
        new_pdf = Path(build["pdf"])

        for name, fn in [
            ("ws_text", lambda: gate_worksheet_preserved(snap_pdf, new_pdf, allow)),
            ("ws_raster", lambda: gate_worksheet_raster(snap_pdf, new_pdf, allow)),
            ("answer", lambda: gate_answer_key(unit_dir)),
            ("verb", lambda: gate_verb(unit_dir, grade)),
            ("pages", lambda: gate_pages(new_pdf)),
        ]:
            ok, det = fn(); r["gates"][name] = det
            if not ok:
                raise RuntimeError(f"{name} gate: {det}")
        r["status"] = "pass"; r["pdf"] = str(new_pdf)
    except Exception as e:
        shutil.copy2(snap_cj, unit_dir / "content.json")
        shutil.copy2(snap_pdf, old_pdf)
        r["status"] = "fail"; r["err"] = str(e)
    return r


def _append_log(results: list[dict]):
    ok = [x for x in results if x["status"] == "pass"]
    bad = [x for x in results if x["status"] != "pass"]
    lines = ["# Teacher-Guide fix — run log\n",
             f"- Passed: {len(ok)}  Failed: {len(bad)}  Total: {len(results)}\n"]
    for x in results:
        mark = "✅" if x["status"] == "pass" else "❌"
        g = x.get("gates", {})
        p1 = " (page1 capped)" if x.get("page1_changed") else ""
        lines.append(f"{mark} `{x['unit']}`{p1} "
                     + " ".join(f"{k}=[{v}]" for k, v in g.items())
                     + (f" ERR={x['err']}" if x.get("err") else ""))
    LOGMD.write_text("\n".join(lines) + "\n")


# ── cli ──────────────────────────────────────────────────────────────────────────
def _units_from_rels(rels: list[str]) -> list[Path]:
    return [LANG / rel for rel in rels]


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "sweep":
        rows = sweep()
        write_mark_table(rows)
        imp = [r for r in rows if r["impacted"]]
        import collections
        by = collections.Counter(c for r in imp for c in (r["classes"] or ["tg_drift"]))
        print(f"scanned {len(rows)} · impacted {len(imp)}")
        for k, c in sorted(by.items()):
            print(f"  {c:3}  {k}")
        print(f"wrote {QAMD.name} + {IMPACTED.name}")
    elif args[0] == "run":
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
        rows = [r for r in sweep() if r["impacted"]]
        units = [LANG / r["unit"] for r in rows][:limit]
        gm = _grade_by_dir()
        results = []
        for i, u in enumerate(units, 1):
            res = process_unit(u, gm); results.append(res)
            print(f"[{i}/{len(units)}] {res['status'].upper()} {res['unit']}"
                  + (f"  ERR={res.get('err')}" if res["status"] != "pass" else ""))
            _append_log(results)
        _append_log(results)
        bad = [r for r in results if r["status"] != "pass"]
        print(f"\nDONE pass={len(results)-len(bad)} fail={len(bad)}")
        sys.exit(1 if bad else 0)
    elif args[0] == "only":
        gm = _grade_by_dir()
        results = [process_unit(u, gm) for u in _units_from_rels(args[1:])]
        for res in results:
            print(json.dumps({k: res[k] for k in ("unit", "status", "gates", "err") if k in res}, indent=2))
        _append_log(results)
        sys.exit(0 if all(r["status"] == "pass" for r in results) else 1)
    else:  # single unit backtest
        res = process_unit(LANG / args[0])
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["status"] == "pass" else 1)
