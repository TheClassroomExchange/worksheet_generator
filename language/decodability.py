"""
Decodability run-gate for K-3 phonics worksheets — the language analog of the
coding pipeline's ``solution.py`` code-runs gate.

A phonics worksheet is only sound if every word a student is asked to *decode*
(read) is actually decodable from the graphemes taught up to that lesson, plus an
explicit cumulative "heart word" (high-frequency / temporarily-irregular) list.
This module proves that mechanically.

Public API
----------
- ``load_scope()``                         -> parsed language/phonics_scope.json
- ``segment_word(word, order, scope)``     -> list[grapheme] or None (can't decode)
- ``check_text(items, order, grade, scope)`` -> report dict
- ``check_unit(unit_dir)``                 -> reads content.json ``phonics`` block,
                                              writes decodability_run.json, returns report

content.json contract (worksheet authors add a top-level ``phonics`` block)::

    "phonics": {
      "grade": "1",
      "lesson_order": 28,            # position in phonics_scope (cumulative unlock point)
      "target_grapheme": "sh",       # the new pattern this sheet teaches
      "decodable_text": [            # EVERY string a student must read
        "The fish is in the dish.",
        "She has a big shell."
      ],
      "allowed_exceptions": []       # author-justified words outside scope (logged, must be rare)
    }
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOPE_PATH = ROOT / "language" / "phonics_scope.json"

VOWELS = set("aeiou")

# Pseudo-graphemes in the scope file that are markers, not literal substrings of
# words. They introduce a *pronunciation*, not a new spelling string, so they add
# no new literal grapheme to the segmenter (the underlying letters unlock earlier).
_NON_LITERAL = {
    "i_open", "a_open", "o_open", "e_open", "u_open",  # open-syllable long vowels (letters already unlocked)
    "schwa", "compound", "contraction", "closed-closed", "open-syllable",
}
# VCe split graphemes: map "a_e" -> vowel letter "a", with its unlock order.
_VCE_RE = re.compile(r"^([aeiou])_e$")


def load_scope(path: Path = SCOPE_PATH) -> dict:
    return json.loads(Path(path).read_text())


def _build_index(scope: dict):
    """Return (literal_unlock, letter_unlock, vce_unlock).

    literal_unlock: {multi-letter literal grapheme -> earliest unlock order}
    letter_unlock:  {single letter -> unlock order}
    vce_unlock:     {vowel letter -> unlock order of its _e split grapheme}
    """
    literal_unlock: dict[str, int] = {}
    letter_unlock: dict[str, int] = {}
    vce_unlock: dict[str, int] = {}
    for row in scope["graphemes"]:
        order = row["order"]
        for g in row["graphemes"]:
            m = _VCE_RE.match(g)
            if m:
                v = m.group(1)
                vce_unlock[v] = min(vce_unlock.get(v, order), order)
                continue
            if g in _NON_LITERAL:
                continue
            g2 = g.strip("-_")  # "-ing"->"ing", "_le"->"le"
            if not g2 or not g2.isalpha():
                continue
            if len(g2) == 1:
                letter_unlock[g2] = min(letter_unlock.get(g2, order), order)
            else:
                literal_unlock[g2] = min(literal_unlock.get(g2, order), order)
    return literal_unlock, letter_unlock, vce_unlock


def cumulative_heart_words(scope: dict, grade: str) -> set[str]:
    bands = {"K": ["K"], "1": ["K", "1"], "2": ["K", "1", "2"], "3": ["K", "1", "2", "3"]}
    out: set[str] = set()
    for b in bands.get(str(grade), ["K", "1", "2", "3"]):
        out.update(w.lower() for w in scope["heart_words"].get(b, []))
    return out


def segment_word(word: str, order: int, scope: dict):
    """Greedily decompose ``word`` into graphemes all unlocked at/before ``order``.

    Returns the grapheme list, or None if the word can't be fully decoded with
    the unlocked inventory. Handles VCe (magic-e): a trailing silent 'e' in a
    V-C-e pattern requires the matching ``<vowel>_e`` grapheme to be unlocked.
    """
    literal_unlock, letter_unlock, vce_unlock = _build_index(scope)
    w = word.lower()
    if not w or not all(c.isalpha() for c in w):
        return None

    graphemes: list[str] = []

    # --- magic-e detection: V C e  (final e silent) ---
    if len(w) >= 3 and w.endswith("e"):
        stem = w[:-1]
        if stem[-1] not in VOWELS and len(stem) >= 2 and stem[-2] in VOWELS:
            v = stem[-2]
            vo = vce_unlock.get(v)
            if vo is not None and vo <= order:
                seg = segment_word(stem, order, scope)
                if seg is not None:
                    return seg + ["e(silent)"]
            # magic-e needed but not unlocked -> not decodable yet
            return None

    # --- greedy longest-match left to right ---
    multis = sorted((g for g, o in literal_unlock.items() if o <= order),
                    key=len, reverse=True)
    i = 0
    n = len(w)
    while i < n:
        matched = None
        for g in multis:
            if w.startswith(g, i):
                matched = g
                break
        if matched:
            graphemes.append(matched)
            i += len(matched)
            continue
        ch = w[i]
        lo = letter_unlock.get(ch)
        if lo is None or lo > order:
            return None  # letter not taught yet
        # Untaught vowel-team guard: a single vowel immediately followed by another
        # vowel (a/e/i/o/u/y) is a vowel team. If no unlocked multi-grapheme matched
        # here, the team isn't taught yet -> not decodable (e.g. "boat"=oa, "rain"=ai).
        if ch in VOWELS and i + 1 < n and w[i + 1] in "aeiouy":
            return None
        graphemes.append(ch)
        i += 1
    return graphemes


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'']*")


def _tokens(text: str) -> list[str]:
    return [t.replace("’", "'") for t in _WORD_RE.findall(text)]


def check_text(items, order: int, grade: str, scope: dict,
               allowed_exceptions=None) -> dict:
    heart = cumulative_heart_words(scope, grade)
    allowed = {w.lower() for w in (allowed_exceptions or [])}
    failures = []
    counts = {"decodable": 0, "heart": 0, "exception": 0, "total": 0}
    seen_words = []
    for raw in items:
        for tok in _tokens(raw):
            counts["total"] += 1
            base = tok.lower()
            # contractions: split on apostrophe, the suffix (n't,'s,'ll,'re,'ve,'d,'m) is heart/morphology
            stem = base.split("'")[0]
            seen_words.append(base)
            if base in heart or stem in heart:
                counts["heart"] += 1
                continue
            if base in allowed:
                counts["exception"] += 1
                continue
            seg = segment_word(stem, order, scope)
            if seg is not None:
                counts["decodable"] += 1
                continue
            failures.append({"word": tok, "in_sentence": raw})
    passed = len(failures) == 0
    return {"passed": passed, "order": order, "grade": grade,
            "counts": counts, "failures": failures, "n_unique": len(set(seen_words))}


def check_unit(unit_dir, write: bool = True) -> dict:
    unit_dir = Path(unit_dir)
    content = json.loads((unit_dir / "content.json").read_text())
    ph = content.get("phonics")
    if not ph:
        raise ValueError(f"{unit_dir}/content.json has no 'phonics' block")
    scope = load_scope()
    order = int(ph["lesson_order"])
    grade = str(ph["grade"])
    target = ph.get("target_grapheme", "")
    items = list(ph.get("decodable_text", []))
    report = check_text(items, order, grade, scope,
                        allowed_exceptions=ph.get("allowed_exceptions"))
    # target-pattern-present check (the new grapheme must actually be exercised)
    tgt = target.strip("-_").lower()
    # Pseudo-graphemes (a_e magic-e, i_open open-syllable) are not literal substrings;
    # decodability itself already proves a magic-e/team is taught, so skip the
    # literal target-present check for them.
    is_pseudo = "_" in target or (not target.replace("-", "").isalpha()) or bool(ph.get("target_optional"))
    report["target_grapheme"] = target
    report["target_present"] = bool(tgt) and any(tgt in re.sub(r"[^a-z]", "", s.lower()) for s in items)
    report["passed"] = report["passed"] and (report["target_present"] or not tgt or is_pseudo)
    if write:
        (unit_dir / "decodability_run.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    import sys
    rep = check_unit(sys.argv[1])
    print(json.dumps(rep, indent=2))
    raise SystemExit(0 if rep["passed"] else 1)
