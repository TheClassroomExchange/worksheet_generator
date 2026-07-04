"""Standing quality gates for the language/phonics catalogue.

These gates promote the rules that were previously enforced ONLY by one-off
remediation sweeps (reveal_fix / dedup_fix / tg_fix / face_fix) into the durable
build path, so a fresh `build_unit` is correct-by-construction and FAILS LOUD on
any regression. `run_quality_gates()` is called by `language_build.build_unit`
after render (G6 needs the rendered PDF).

Gate roster (built incrementally):
  G1 kid-safe          — no blocked word in any student-facing token
  G3 image-in-sentence — every reading-row picture word appears in its sentence
  G6 page-count        — the combined PDF is <= 2 pages
  (G2 distinct word/picture, G4 face/object classification, G5 teacher-guide
   verification are added in following bites.)

Run standalone over the whole catalogue (positive control):
    python -m language.quality_gates            # scan every built unit
    python -m language.quality_gates <unit_dir> # scan one unit
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

_WORD_RE = re.compile(r"[a-zA-Z']+")
_SKIP_STR_KEYS = {"img", "src", "mascot", "file_title", "footer_topic"}


class QualityGateError(RuntimeError):
    """Raised when a unit fails a standing quality gate."""

    def __init__(self, unit: str, gate: str, detail: str):
        super().__init__(f"[{gate}] {unit}: {detail}")
        self.unit, self.gate, self.detail = unit, gate, detail


def _load_json(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def _tokens(s: str) -> list[str]:
    return [t.lower().strip("'") for t in _WORD_RE.findall(s)]


def _stem(w: str) -> str:
    """Loose stem so a picture word matches plural/-ing/-ed forms in its sentence."""
    w = w.lower()
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 1 and w.endswith(suf):
            return w[: -len(suf)]
    return w


# ── student-facing content collectors ───────────────────────────────────────

def _walk_strings(node):
    """Yield every student-facing string leaf under a content node, skipping file
    paths and non-content keys (img/src/mascot/...)."""
    if isinstance(node, str):
        if "/" not in node:  # a path is not student-facing text
            yield node
    elif isinstance(node, list):
        for v in node:
            yield from _walk_strings(v)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in _SKIP_STR_KEYS:
                continue
            yield from _walk_strings(v)


def student_text(content: dict) -> list[str]:
    """All student-facing strings: the worksheet block + the decodable sentences.
    Excludes the teacher_guide (adult-facing) and image paths."""
    out = list(content.get("phonics", {}).get("decodable_text", []))
    out += list(_walk_strings(content.get("worksheet", {})))
    return [s for s in out if isinstance(s, str) and s.strip()]


def reading_rows(content: dict) -> list[dict]:
    rows = []
    for part in content.get("worksheet", {}).get("parts", []):
        if part.get("type") in ("reading_rows", "sound_boxes"):
            rows += part.get("rows", [])
        elif part.get("type") == "picture_row":
            rows += part.get("items", [])
    return rows


def all_image_words(content: dict) -> list[str]:
    """Every word that resolves to an image (the way materialize walks the tree):
    reading/sound rows, picture-row items, formation/image parts, mascots, and the
    phonics.image_words list."""
    out = []
    for sec in ("worksheet", "teacher_guide"):
        spec = content.get(sec) or {}
        if spec.get("mascot_word"):
            out.append(spec["mascot_word"])
        for part in spec.get("parts", []):
            t = part.get("type")
            if t in ("reading_rows", "sound_boxes"):
                out += [r["word"] for r in part.get("rows", []) if r.get("word")]
            elif t == "picture_row":
                out += [it["word"] for it in part.get("items", []) if it.get("word")]
            elif t in ("formation", "image") and part.get("word"):
                out.append(part["word"])
    out += [iw["word"] for iw in content.get("phonics", {}).get("image_words", []) if iw.get("word")]
    return out


# ── gates ────────────────────────────────────────────────────────────────────

def gate_kidsafe(unit: str, content: dict) -> None:
    """G1 — no blocked word in any student-facing token."""
    cfg = _load_json("kidsafe_blocklist.json")
    blocked = {w.lower() for w in cfg["blocked"]}
    allow = {w.lower() for w in cfg.get("allow", {})}
    seen = set()
    for s in student_text(content):
        for tok in _tokens(s):
            if tok in blocked and tok not in allow:
                seen.add(tok)
    if seen:
        raise QualityGateError(unit, "G1-kidsafe",
                               f"blocked word(s) in student-facing text: {sorted(seen)}")


def gate_image_in_sentence(unit: str, content: dict) -> None:
    """G3 — every picture word must appear in its own sentence (stem-tolerant)."""
    bad = []
    for r in reading_rows(content):
        word, text = r.get("word"), r.get("text") or r.get("label")
        if not word or not text:
            continue
        toks = {_stem(t) for t in _tokens(text)}
        if _stem(word) not in toks:
            bad.append((word, text))
    if bad:
        raise QualityGateError(unit, "G3-image-in-sentence",
                               f"picture word not in its sentence: {bad}")


# Grammatical function words that don't count as "example words" (promoted from
# dedup_fix so build + sweep share one source of truth).
_STOP = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "and", "he", "she",
         "we", "my", "i", "see", "can", "has", "red", "big", "of", "up", "by", "you",
         "your", "not", "am", "are", "be", "do", "go", "me", "no", "so", "us", "was", "for"}


def _grapheme_words(texts: list[str], grapheme: str, order: int, scope) -> list[str]:
    """Content words across the sentences that actually EXERCISE the target
    grapheme (a true segment) — the distinct example words the child should meet."""
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


def _dups(items: list[str]) -> list[str]:
    return sorted({w for w in items if items.count(w) > 1})


def gate_distinct(unit: str, content: dict) -> None:
    """G2 — each reading sheet shows DISTINCT example words and DISTINCT pictures
    (beyond a per-grapheme inventory-limited allowance). Catches robot/robot,
    sauce×3, 'zip'×3-in-text-with-distinct-pics, etc."""
    ph = content.get("phonics", {})
    grapheme = ph.get("target_grapheme", "")
    order = ph.get("lesson_order", 0)
    allow = int(_load_json("allow_repeats.json").get(grapheme.replace("_", "").lower(), 0))
    rows = [r for r in reading_rows(content) if r.get("word") and (r.get("text") or r.get("label"))]
    problems = []
    pics = [r["word"].lower() for r in rows]
    if len(pics) - len(set(pics)) > allow:
        problems.append(f"duplicate picture(s) {_dups(pics)}")
    # Example-word distinctness is over the SENTENCE rows only — NOT decodable_text,
    # which on word-building sheets also lists the 'build the word' answers (jumped
    # appears both as a built word and in its sentence, by design).
    texts = [r.get("text") or r.get("label") for r in rows]
    if grapheme and texts:
        from language import decodability as dc
        gw = _grapheme_words(texts, grapheme, order, dc.load_scope())
        if len(gw) - len(set(gw)) > allow:
            problems.append(f"repeated example word(s) {_dups(gw)}")
    if problems:
        raise QualityGateError(unit, "G2-distinct", "; ".join(problems))


def _answer_lines(tg: dict) -> list[str]:
    for p in tg.get("parts", []):
        if isinstance(p.get("title"), str) and "answer key" in p["title"].lower():
            t = p.get("text")
            return t if isinstance(t, list) else [t]
    return []


def _step3(tg: dict) -> str:
    for p in tg.get("parts", []):
        if isinstance(p.get("title"), str) and "how to lead" in p["title"].lower():
            for line in (p.get("text") or []):
                if str(line).strip().startswith("3."):
                    return str(line)
    return ""


def gate_teacher_guide(unit: str, content: dict, grade: str) -> None:
    """G5 — the teacher-guide answer key must be populated (no blank '—') and must
    match the worksheet-projected truth (derive_teacher_guide), incl. the step-3
    verb (circle/underline/bold). Catches D1 blank key, D2 fabricated word-building
    key, D3 verb drift — the tg_fix rubric, now standing at build time."""
    tg = content.get("teacher_guide", {})
    ak = _answer_lines(tg)
    problems = []
    if any(re.search(r":\s*—", str(s)) for s in ak):
        problems.append("blank answer key ('—')")
    from language import gen_content as gc
    # A derive failure is a GATE FAILURE, not a silent skip — otherwise the drift
    # check quietly disappears on the exact sheet types G5 exists to verify.
    try:
        derived = gc.derive_teacher_guide(content, grade)
    except Exception as e:
        raise QualityGateError(unit, "G5-teacher-guide",
                               f"teacher-guide derivation failed ({e}) — cannot verify") from e
    if _answer_lines(derived) != ak:
        problems.append("answer key drifts from the worksheet")
    if _step3(derived) != _step3(tg):
        problems.append("step-3 verb does not match the worksheet")
    if problems:
        raise QualityGateError(unit, "G5-teacher-guide", "; ".join(problems))


def gate_face_object(unit: str, content: dict) -> None:
    """G4 — every image word must be classified animate (face) OR inanimate
    (faceless). An unclassified word would render silently faceless (the old bug),
    so it fails the build until it is added to image_words.json."""
    # Use the RENDERER's exact runtime sets (not image_words.json directly) so the
    # gate can never diverge from what phonics_images actually classifies.
    from language import phonics_images as pi
    animate, inanimate = pi._ANIMATE_SET, pi._INANIMATE_SET

    def known(w):
        wl = w.lower()
        return (wl in animate or wl.rstrip("s") in animate
                or wl in inanimate or wl.rstrip("s") in inanimate)

    unknown = sorted({w for w in all_image_words(content) if not known(w)})
    if unknown:
        raise QualityGateError(unit, "G4-face-object",
                               f"unclassified image word(s) {unknown} — add to image_words.json")


def gate_page_count(unit: str, pdf: Path, max_pages: int = 2) -> None:
    """G6 — the combined PDF must be <= max_pages (page_fill_ok only catches
    near-EMPTY pages, never a spill to a 3rd page)."""
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", info)
    n = int(m.group(1)) if m else -1
    if n < 1 or n > max_pages:
        raise QualityGateError(unit, "G6-page-count",
                               f"{n} pages (max {max_pages}) — {pdf.name}")


def run_quality_gates(unit_dir, content: dict, grade: str, pdf: Path) -> None:
    """Run every standing gate; raise QualityGateError on the first failure."""
    unit = Path(unit_dir).name
    gate_kidsafe(unit, content)
    gate_image_in_sentence(unit, content)
    gate_distinct(unit, content)
    gate_face_object(unit, content)
    gate_teacher_guide(unit, content, grade)
    gate_page_count(unit, Path(pdf))


# ── standalone scan (positive/negative control) ──────────────────────────────

def _combined_pdf(unit_dir: Path) -> Path | None:
    pdfs = sorted(unit_dir.glob("*.pdf"))
    return pdfs[0] if pdfs else None


def scan_unit(unit_dir: Path) -> list[str]:
    """Return a list of gate-failure messages for one built unit ([] = clean)."""
    fails = []
    content = json.loads((unit_dir / "content.json").read_text())
    grade = ""
    if (unit_dir / "input_row.json").exists():
        grade = json.loads((unit_dir / "input_row.json").read_text()).get("grade", "")
    if not grade:  # fall back to the phonics grade so G5's derive doesn't false-fail
        g = str(content.get("phonics", {}).get("grade", ""))
        grade = "Kindergarten" if g.upper() == "K" else (f"Grade {g}" if g.isdigit() else g)
    pdf = _combined_pdf(unit_dir)
    checks = [
        lambda: gate_kidsafe(unit_dir.name, content),
        lambda: gate_image_in_sentence(unit_dir.name, content),
        lambda: gate_distinct(unit_dir.name, content),
        lambda: gate_face_object(unit_dir.name, content),
        lambda: gate_teacher_guide(unit_dir.name, content, grade),
    ]
    if pdf:
        checks.append(lambda: gate_page_count(unit_dir.name, pdf))
    for c in checks:
        try:
            c()
        except QualityGateError as e:
            fails.append(str(e))
    return fails


def scan_all(root: Path | None = None) -> int:
    root = root or HERE
    units = sorted(p.parent for p in root.glob("*/*/content.json")
                   if "_samples" not in str(p) and "_backup" not in str(p))
    total_fail = 0
    for u in units:
        for msg in scan_unit(u):
            print(msg)
            total_fail += 1
    print(f"\n{len(units)} units scanned, {total_fail} gate failures")
    return 1 if total_fail else 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for msg in scan_unit(Path(sys.argv[1])):
            print(msg)
    else:
        raise SystemExit(scan_all())
