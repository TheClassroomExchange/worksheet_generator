"""Prose copy-edit linter — mechanical spelling / duplicate-word / punctuation
check over a coding sheet's reader-facing text (worksheet + teacher guide).

Sibling of the jargon linter in ``pipeline/teacher_guide_rubric.py`` (which only
scans the teacher guide for technical words). This module scans BOTH the
``worksheet`` and ``teacher_guide`` blocks of a ``content.json`` for the
copy-edit defects a teacher would notice:

  - duplicate adjacent words ("the the", "to to")
  - common misspellings (a fixed dictionary — zero false positives by design)
  - double punctuation (",,", ";;") that is not an ellipsis
  - space before punctuation ("word ,")
  - a/an article disagreement ("a apple", "an box")

Advisory, like the jargon linter: it returns the hits and a ``clean`` flag; the
runner decides. It is wired into the QA path so every future sheet is checked.

Deliberately scoped to MECHANICAL defects only. It does NOT attempt homophone
detection (its/it's, your/you're, their/there) — those need sentence-level
grammar context and a naive matcher false-positives heavily on correct usage;
that judgement stays with the human/LLM copy-edit pass.

Allowlisted (NOT flagged), because they are intentional layout/curriculum, not
errors — proven against the full 93-sheet catalogue:
  - fill-in-the-blank underscore runs ("____") and the double-spaces around them
  - source code (the ``code`` part field is never scanned)
  - symbol / emoji ``label`` values (never scanned)
  - ellipsis ("…" and "...") and the spaced ellipsis "… ."
  - the "?" used as an answer placeholder in prompts
  - legitimate intentional doublers (e.g. "two two-move", "that that")
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Reader-facing string fields. ``code`` (source) and ``label`` (symbols/emoji)
# are intentionally excluded; ``src``/``width``/``type``/``cat`` etc. are non-prose.
TEXT_KEYS: frozenset[str] = frozenset({
    "title", "subtitle", "eyebrow", "learning_goal", "file_title",
    "footer_topic", "prompt", "note", "caption", "output", "text",
})

# Adjacent identical words that are legitimately doubled in English. Lowercased.
DUP_ALLOW: frozenset[str] = frozenset({"that", "had"})

# Fixed misspelling -> correction. Conservative: only unambiguous typos so the
# gate never false-positives on a correctly-spelled word.
COMMON_TYPOS: dict[str, str] = {
    "teh": "the", "recieve": "receive", "seperate": "separate",
    "occured": "occurred", "untill": "until", "definately": "definitely",
    "thier": "their", "becuase": "because", "beleive": "believe",
    "wierd": "weird", "accross": "across", "tommorow": "tomorrow",
    "writting": "writing", "begining": "beginning", "enviroment": "environment",
    "sucessful": "successful", "neccessary": "necessary",
    "occurence": "occurrence", "reccomend": "recommend", "refered": "referred",
    "wether": "whether", "alot": "a lot", "alote": "a lot",
    "everytime": "every time", "no one's": "no one's", "noone": "no one",
    "didnt": "didn't", "doesnt": "doesn't", "wont": "won't", "cant": "can't",
    "dont": "don't", "isnt": "isn't", "arent": "aren't", "wasnt": "wasn't",
    "youre": "you're", "thats": "that's", "its'": "its",
    # NB: "lets"/"cant"/"wont" are deliberately NOT here — each is a valid word
    # (verb "lets", noun "cant"/"wont") and appears correctly in the corpus.
}

_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")
# duplicate adjacent word: same word twice, second not part of a hyphenated/longer
# token ("two two-move" excluded by the trailing (?![\w-])). Letters only so an
# underscore blank run ("____ ____") never matches. Case-insensitive backref.
_DUP = re.compile(r"\b([A-Za-z]{2,})\s+\1(?![\w\-])\b", re.IGNORECASE)
# double punctuation that is not an ellipsis ("..."/"…"): two+ of the same mark
# from , ; : ! ? (not "."), or a comma/semicolon directly repeated.
_DBL_PUNCT = re.compile(r"([,;:!?])\1+")
# space before , . ; : — but NOT when the char before the space is a symbol /
# placeholder ("…", arrows, geometric cards), a fill-in blank ("_"), or a digit,
# and NOT a spaced ellipsis. "?" and "!" are intentionally excluded as TARGETS
# (the corpus uses a standalone "?" as a "draw the shape here" placeholder, e.g.
# "box 1 → draw ?, box 2 → draw ?"), and they are rare real-typo signatures.
# Run on the RAW string: the letter-only dup regex ignores "____" already, so no
# blank-stripping is needed (stripping blanks would manufacture a phantom " .").
_SPACE_BEFORE = re.compile(r"(?<![…★●▲■➡↻⚑→_\d])\s[,.;:]")


def _iter_strings(node) -> list[str]:
    """Yield every reader-facing string under a worksheet/teacher_guide block."""
    out: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("code", "label", "src", "width"):
                    continue
                if k in TEXT_KEYS and isinstance(v, str):
                    out.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, str):
                    out.append(v)
                else:
                    walk(v)

    walk(node)
    return out


def _check_string(s: str) -> list[dict]:
    """Return a list of defect dicts for one raw reader-facing string."""
    hits: list[dict] = []

    # duplicate adjacent words (letters-only; ignores "____" blanks and
    # "two two-move" via the trailing boundary in _DUP)
    for m in _DUP.finditer(s):
        if m.group(1).lower() in DUP_ALLOW:
            continue
        hits.append({"kind": "dup_word", "match": m.group(0), "fix": m.group(1)})

    # common misspellings (whole-word, case-insensitive)
    for w in _WORD.finditer(s):
        low = w.group(0).lower()
        if low in COMMON_TYPOS:
            hits.append({"kind": "typo", "match": w.group(0),
                         "fix": COMMON_TYPOS[low]})

    # double punctuation that is not an ellipsis
    for m in _DBL_PUNCT.finditer(s):
        hits.append({"kind": "dbl_punct", "match": m.group(0), "fix": m.group(0)[0]})

    # space before punctuation
    for m in _SPACE_BEFORE.finditer(s):
        hits.append({"kind": "space_before_punct", "match": repr(m.group(0)),
                     "fix": m.group(0).strip()})

    return hits


def lint_prose(unit_dir: Path) -> dict:
    """Mechanical copy-edit lint over a sheet's worksheet + teacher_guide prose.

    Returns ``{hits: [{section, kind, match, fix}], clean: bool}``. Advisory —
    surfaces likely defects so the runner doesn't miss them; does not score.
    """
    cj = Path(unit_dir) / "content.json"
    if not cj.exists():
        return {"hits": [], "clean": True}
    content = json.loads(cj.read_text(encoding="utf-8"))
    hits: list[dict] = []
    for section in ("worksheet", "teacher_guide"):
        block = content.get(section)
        if not block:
            continue
        # the top-level display title also renders; check it once under worksheet
        strings = _iter_strings(block)
        if section == "worksheet" and isinstance(content.get("title"), str):
            strings.append(content["title"])
        for s in strings:
            for h in _check_string(s):
                hits.append({"section": section, **h})
    return {"hits": hits, "clean": not hits}


if __name__ == "__main__":  # quick manual run: python -m pipeline.prose_lint [glob]
    import sys
    pattern = sys.argv[1] if len(sys.argv) > 1 else "coding/*/*/content.json"
    root = Path(__file__).resolve().parent.parent
    dirty = 0
    total = 0
    for cj in sorted(root.glob(pattern)):
        total += 1
        res = lint_prose(cj.parent)
        if not res["clean"]:
            dirty += 1
            print(f"\n{cj.parent.relative_to(root)}")
            for h in res["hits"]:
                print(f"  [{h['section']}/{h['kind']}] {h['match']!r} -> {h['fix']!r}")
    print(f"\n{total} sheets scanned, {dirty} with >=1 hit.")
