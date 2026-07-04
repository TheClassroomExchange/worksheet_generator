#!/usr/bin/env python3
"""Build a direct_upload manifest for the K-3 Language (Phonics) catalogue.

Walks the SAME source of truth the Drive publisher uses — subjects.json ->
each subject dir's topics.json (the canonical 112 topics) — and emits a
manifest.json for pdf-uploader/catalogue-upload/scripts/direct_upload.py.

Deterministic metadata only (no AI):
  * title  : "{Grade} Phonics: {target} — {Format}"  (<=60, DB CHECK)
  * desc   : keyword-rich (site full-text search runs on title+description)
  * price  : flat $2.99 (matches every existing TCE worksheet)
  * taxonomy: per-grade Language row, live-verified against prod

Walking topics.json (not the filesystem) yields exactly 112 and ignores the
4 stray PDFs on disk. Run:  python3 build_marketplace_manifest.py
"""
from __future__ import annotations
import json
import re
from pathlib import Path

LANG = Path(__file__).resolve().parent
OUT = LANG / "marketplace_manifest.json"

SELLER = {"teacher_id": "33b660c6-83e3-4848-932c-ce60cbd6240d",
          "seller_name": "TheClassroomExchange"}
PRICE = 2.99

# Live-verified against ontario_curriculum_taxonomy (subject=Language).
TAXO = {
    "Kindergarten": (1, "Foundations of Language"),
    "Grade 1":      (2, "Word-Level Reading"),
    "Grade 2":      (4, "Vocabulary"),
    "Grade 3":      (5, "Writing"),
}
FORMAT = {
    "letter_sound":  "Letter Sounds",
    "sentences":     "I Can Read Sentences",
    "word_building": "Word Building",
}


def strip_paren(s: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", " ", s).strip()


def listing_title(grade: str, topic: dict) -> str:
    """Deterministic, unique, <=60. keyword disambiguates repeated graphemes
    (e.g. two 'oo' topics: moon vs book)."""
    ttype = topic["type"]
    kw = topic.get("keyword", "")
    if ttype == "letter_sound":              # curated "The Letter Aa" is self-describing
        return f"{grade} Phonics: {topic['title'].strip()} ({kw})"
    if ttype == "word_building":             # curated title, gloss stripped, self-describing
        return f"{grade} Phonics: {strip_paren(topic['title'])}"
    tg = topic["target_grapheme"]            # sentences
    t = f"{grade} Phonics: {tg} ({kw}) — {FORMAT['sentences']}"
    if len(t) > 60:                          # last-resort: drop the keyword
        t = f"{grade} Phonics: {tg} — {FORMAT['sentences']}"
    return t


def sample_clause(entry: dict, ttype: str) -> str:
    if not entry:
        return ""
    if entry.get("build"):
        words = [p[-1] for p in entry["build"] if p][:4]
        if words:
            return f"Example words: {', '.join(words)}. "
    if entry.get("sentences"):
        texts = [s["text"] for s in entry["sentences"] if s.get("text")][:2]
        if texts:
            return f"Sample sentences: {' '.join(texts)} "
    if entry.get("words"):
        return f"Example words: {', '.join(entry['words'][:5])}. "
    return ""


# Language-specific, searchable keyword phrases woven per activity type (the site
# searches title+description; filters are grade/subject/strand/resource_type).
SKILL_KW = {
    "letter_sound": "letter recognition, letter formation, letter sounds, and blending",
    "word_building": "word building, morphology, prefixes and suffixes, and spelling",
    "sentences": "decoding, blending, decodable sentences, and reading fluency",
}


def learning_goal(topic: dict) -> str:
    tg = topic["target_grapheme"]
    ph = topic.get("phoneme", "")
    kw = topic.get("keyword", "")
    ttype = topic["type"]
    if ttype == "letter_sound":
        return f"I can hear, write, and read the letter {tg.upper()}{tg.lower()} and its {ph} sound (as in {kw})"
    if ttype == "word_building":
        return f"I can read and build words: {strip_paren(topic['title'])}"
    return f"I can read decodable words and sentences with the {ph} sound spelled '{tg}' (as in {kw})"


def description(grade: str, strand: str, subject_label: str, topic: dict, entry: dict) -> str:
    tg = topic["target_grapheme"]
    kw = topic.get("keyword", "")
    ttype = topic["type"]
    if ttype == "letter_sound":
        tdisp = f"the letter {tg.upper()}{tg.lower()}"
    elif ttype == "word_building":
        tdisp = strip_paren(topic["title"])
    else:
        tdisp = f"'{tg}' (as in {kw})"
    return (
        f"{grade} Ontario phonics worksheet (Language — {strand} strand). "
        f"Topic: {subject_label} — {tdisp}. {learning_goal(topic)}. "
        f"This is a print-ready, no-prep decodable reading / phonics activity from the "
        f"{subject_label} set, with a matching teacher guide and answer key included. "
        f"{sample_clause(entry, ttype)}"
        f"Great for {grade} phonics, {SKILL_KW[ttype]}, guided reading, small groups, "
        f"literacy centres, and Science-of-Reading practice. From The Classroom Exchange."
    )


def main() -> int:
    subs = json.loads((LANG / "subjects.json").read_text())["subjects"]
    records, problems = [], []
    for s in subs:
        d = LANG / s["dir"]
        topics = json.loads((d / "topics.json").read_text())["topics"]
        grade = s["grade"]
        tax_id, strand = TAXO[grade]
        data = {}
        dj = d / "data.json"
        if dj.exists():
            data = json.loads(dj.read_text())
        for t in topics:
            tdir = d / t["dir"]
            pdfs = sorted(tdir.glob("*.pdf"))
            if not pdfs:
                problems.append(f"NO PDF: {tdir}")
                continue
            if len(pdfs) > 1:
                problems.append(f"MULTI PDF ({len(pdfs)}): {tdir} -> using {pdfs[0].name}")
            title = listing_title(grade, t)
            if len(title) > 60:
                problems.append(f"TITLE >60 ({len(title)}): {title}")
            records.append({
                "local_path": str(pdfs[0]),
                "title": title,
                "description": description(grade, strand, s["subject"], t, data.get(t["dir"], {})),
                "price_cad": PRICE,
                "grade": grade,
                "subject": "Language",
                "strand_name": strand,
                "taxonomy_id": tax_id,
                "resource_type": "Worksheet",
            })

    manifest = {"seller": SELLER, "records": records}
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    by_grade = {}
    for r in records:
        by_grade[r["grade"]] = by_grade.get(r["grade"], 0) + 1
    longest = max(records, key=lambda r: len(r["title"]))
    print(f"records: {len(records)}  ->  {OUT}")
    print("by grade:", by_grade)
    print(f"longest title ({len(longest['title'])}): {longest['title']}")
    dup = len(set(r["title"] for r in records)) != len(records)
    print("duplicate titles:", "YES" if dup else "none")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(" ", p)
    return 1 if any("NO PDF" in p or "TITLE >60" in p for p in problems) else 0


if __name__ == "__main__":
    raise SystemExit(main())
