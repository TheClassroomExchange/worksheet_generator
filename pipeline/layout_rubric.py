"""
layout_rubric.py — gate for the K & G1 "roomy layout" revision.

This sheet revision changes ONLY size and spacing (bigger images, more writing
room). Content and language must stay identical. Two things are gated here:

  1. content_unchanged(old_pdf, new_pdf, footers) — HARD content-invariance
     check. Extracts text from both PDFs (plain pdftotext, NOT -layout, which
     re-spaces centred/footer lines on any reflow and creates phantom diffs),
     strips the per-page footer artifacts (which repeat once per page, so a
     1→2 page reflow changes only their count), normalises whitespace, and
     requires the remaining body text to match exactly. ANY wording change
     fails. This is the L5 hard gate.

  2. classify(scores) / record_grade(...) — the L1–L5 layout rubric. Scoring
     (L1–L4) is done by the runner (Claude) reading the rendered pages, the
     same human-in-the-loop pattern as coding_rubric / teacher_guide_rubric.
     L5 is set mechanically from content_unchanged. record_grade writes
     layout_grade.json next to the topic, mirroring finalize_visual bookkeeping.

Rubric (each L1–L4 scored 1–4; L5 is pass/fail):
  L1 Writing room      — write-in slots large enough for K/G1 hands       (HARD: must = 4)
  L2 Image/target size — symbol cards, grids, icons, mascot enlarged
  L3 Breathing room    — generous vertical spacing, one idea per cluster
  L4 Render integrity  — nothing clipped/orphaned; mascot + colours intact
  L5 Content invariance— pdftotext(new) == pdftotext(old), footers aside  (HARD gate)

Gate: total(L1..L4) >= 14 (of 16) AND L1 == 4 AND L5 == pass.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

CRITERIA = {
    "L1": "Writing room (write-in slots large enough for young hands)",
    "L2": "Image/target size (symbol cards, grids, icons, mascot enlarged)",
    "L3": "Breathing room (generous vertical spacing, one idea per cluster)",
    "L4": "Render integrity (nothing clipped/orphaned; mascot + colours intact)",
}
SCORED = ("L1", "L2", "L3", "L4")  # 1..4 each (max 16)
PASS_TOTAL = 14                    # of 16


# ── content-invariance (L5) ─────────────────────────────────────────────────
def _pdftext(pdf: Path) -> str:
    """Plain text of a PDF (UTF-8). No -layout (it re-spaces on reflow)."""
    out = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def _normalise(text: str, footers: list[str]) -> str:
    """Drop per-page footer artifacts then collapse whitespace.

    Footers repeat once per page, so a layout change that reflows to a new page
    count would otherwise look like a content change. We strip:
      • "The Classroom Exchange" (centre footer, constant)
      • "page N" (right footer, page-count dependent)
      • each supplied footer_topic (left footer, e.g. "1. Start and Go")
    Body text — including header titles and decorative glyphs — is preserved.
    """
    drop_exact = {"The Classroom Exchange", *[f.strip() for f in footers if f]}
    kept = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in drop_exact:
            continue
        if re.fullmatch(r"page \d+", line):
            continue
        kept.append(line)
    return re.sub(r"\s+", " ", " ".join(kept)).strip()


def _token_multiset(norm: str) -> list[str]:
    """Sorted, hyphen-stripped word tokens — order- and hyphenation-insensitive.

    Two layout-only artifacts make the strict sequence diff a false positive even
    when no word changed: (1) pdftotext DEHYPHENATES a word wrapped at a line
    break ("mix-\\nups" -> "mixups"), and (2) a row of symbol/number cards that
    reflows to a new line is read in a different order. Both preserve the exact
    multiset of words; only a real add/remove/change of a word alters it. So the
    multiset is the right invariant to fall back on after the strict check.
    """
    return sorted(t.replace("-", "") for t in norm.split() if t)


def content_unchanged(old_pdf: Path, new_pdf: Path, footers: list[str]):
    """Return (ok: bool, detail: str). Passes when the body text is unchanged.

    Tier 1: exact normalised sequence match (strictest; preferred).
    Tier 2: identical word multiset (hyphen-stripped, order-insensitive) — accepts
            ONLY the two known layout artifacts above; any real word add / remove /
            change still differs and fails. A layout-only re-render legitimately
            passes here; a content edit cannot.
    """
    old_n = _normalise(_pdftext(Path(old_pdf)), footers)
    new_n = _normalise(_pdftext(Path(new_pdf)), footers)
    if old_n == new_n:
        return True, "content identical (exact, footers/whitespace aside)"
    if _token_multiset(old_n) == _token_multiset(new_n):
        return True, "content identical (word multiset; reflow/hyphenation only)"
    # Real divergence — report it. Use multiset symmetric difference for clarity.
    from collections import Counter
    co, cn = Counter(_token_multiset(old_n)), Counter(_token_multiset(new_n))
    removed = list((co - cn).elements())[:12]
    added = list((cn - co).elements())[:12]
    return False, f"WORDS CHANGED — removed={removed} added={added}"


def footers_for(unit_dir: Path) -> list[str]:
    """The footer_topic strings used by a topic's worksheet + teacher guide."""
    content = json.loads((Path(unit_dir) / "content.json").read_text(encoding="utf-8"))
    fs = []
    for key in ("worksheet", "teacher_guide"):
        spec = content.get(key, {})
        ft = spec.get("footer_topic") or spec.get("title")
        if ft:
            fs.append(ft)
    return fs


# ── page-fill oracle (no near-empty page) ───────────────────────────────────
import tempfile

HEADER_FRAC = 0.155   # top band occupied by the header on page 1
FOOTER_FRAC = 0.93    # below this is the page-number / wordmark footer
FILL_MIN = 0.30       # a worksheet page whose body ink ends above this is "near-empty"


def _page_ink_bottom(png) -> float:
    """Fraction of page height at which BODY ink ends (header/footer excluded).
    Returns ~HEADER_FRAC when the body band is empty (header/goal-only page)."""
    from PIL import Image
    im = Image.open(png).convert("L")
    w, h = im.size
    body = im.crop((0, int(h * HEADER_FRAC), w, int(h * FOOTER_FRAC)))
    bw = body.point(lambda p: 0 if p > 245 else 255)  # 255 = ink
    bbox = bw.getbbox()
    if not bbox:
        return HEADER_FRAC
    return (int(h * HEADER_FRAC) + bbox[3]) / h


def _tg_page_count(pdf: Path, npages: int) -> int:
    """How many trailing pages are the teacher guide, detected by the
    '— Teacher Guide' footer. Falls back to 1 (TGs are compact, 1 page by
    design) if detection finds none — never assumes a fixed count blindly."""
    n = 0
    for pg in range(npages, 0, -1):
        txt = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(pg), "-l", str(pg),
                              str(pdf), "-"], capture_output=True, text=True).stdout
        if "— Teacher Guide" in txt or "Teacher Guide" in txt:
            n += 1
        else:
            break
    return n or 1


def page_fill_ok(pdf: Path, *, exclude_tg_last: bool = True):
    """Return (ok, near_empty_pages). A worksheet page is near-empty if its body
    ink ends below FILL_MIN of page height (header/goal-only, or a lone line).
    Trailing teacher-guide pages (detected by footer, not a fixed count) are
    excluded so a multi-page TG can't be mis-checked as a worksheet page."""
    pdf = Path(pdf)
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    npages = next(int(l.split()[-1]) for l in out.splitlines() if l.startswith("Pages"))
    ws_last = (npages - _tg_page_count(pdf, npages)) if exclude_tg_last else npages
    if ws_last < 1:
        return True, []
    near_empty = []
    with tempfile.TemporaryDirectory() as td:
        stem = Path(td) / "p"
        subprocess.run(["pdftoppm", "-png", "-r", "72", "-f", "1", "-l", str(ws_last),
                        str(pdf), str(stem)], check=True)
        pngs = sorted(Path(td).glob("p-*.png"))
        for i, png in enumerate(pngs[:ws_last], start=1):
            frac = _page_ink_bottom(png)
            if frac < FILL_MIN:
                near_empty.append({"page": i, "ink_bottom": round(frac, 3)})
    return (len(near_empty) == 0), near_empty


# ── L1–L5 gate ──────────────────────────────────────────────────────────────
def classify(scores: dict, content_ok: bool) -> dict:
    """scores: {L1..L4 -> 1..4}. content_ok: the L5 hard gate. Returns the
    grade record with a pass/fail decision."""
    total = sum(int(scores[k]) for k in SCORED)
    l1 = int(scores["L1"])
    status = "pass" if (total >= PASS_TOTAL and l1 == 4 and content_ok) else "fail"
    reasons = []
    if total < PASS_TOTAL:
        reasons.append(f"total {total}/16 < {PASS_TOTAL}")
    if l1 != 4:
        reasons.append("L1 (writing room) must be 4")
    if not content_ok:
        reasons.append("L5 content invariance FAILED")
    return {
        "scores": {k: int(scores[k]) for k in SCORED},
        "L5_content_invariant": bool(content_ok),
        "total": total,
        "max": 16,
        "status": status,
        "fail_reasons": reasons,
    }


def record_grade(unit_dir: Path, *, scores: dict, content_detail: str,
                 content_ok: bool, notes: str = "") -> dict:
    """Write layout_grade.json for a topic and return the grade record."""
    unit_dir = Path(unit_dir)
    rec = classify(scores, content_ok)
    rec["content_detail"] = content_detail
    rec["notes"] = notes
    (unit_dir / "layout_grade.json").write_text(
        json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    return rec
