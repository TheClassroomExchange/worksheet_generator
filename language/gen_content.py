"""Autonomous content generator for K-3 language worksheets.

Turns a COMPACT per-topic data entry into a full content.json that follows the
locked DESIGN_STANDARD (corner-tab big template, kawaii images, plain-language
teacher guide with verbatim Ontario citation). The decodability + rubric gates
then validate the generated content.

Data entry schemas (authored in language/<subject>/data.json, keyed by topic dir):
  sentences:     {"sub","sound","sentences":[{"text","pic"}]}            # 5 rows
  word_building: {"sub","sound","build":[["base","word"],...],"sentences":[{"text","pic"}],"note"}
  letter_sound:  {"keyword_pic","sort_yes":[w],"sort_no":[w],"cvc":[w]}
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "curriculum" / "language.json").read_text())
SCOPE = json.loads((ROOT / "language" / "phonics_scope.json").read_text())

# grade digit for curriculum lookup
def _gd(grade: str) -> str:
    return "K" if grade.lower().startswith("k") else grade.split()[-1]

def _cur(grade: str, codes: list[str]) -> list[dict]:
    gd = _gd(grade)
    out = []
    for e in CUR["expectations"]:
        if str(e["grade"]) == gd and e["code"] in codes:
            out.append({"code": e["code"], "text": e["text"]})
    return out

# curriculum codes by grade + worksheet type
def _codes(grade: str, wtype: str) -> list[str]:
    gd = _gd(grade)
    if gd == "K":
        return ["A2.4", "A2.2"] if wtype == "letter_sound" else ["A2.5", "A2.4"]
    if gd == "1":
        return ["B2.3", "B2.4"]
    if gd == "2":
        return ["B2.1"]
    return ["B2.3"]  # grade 3 morphology

# plain-language gloss per code
_GLOSS = {
    "A2.2": "children form the letter the correct way.",
    "A2.4": "children match a letter to the sound it makes.",
    "A2.5": "children read and spell simple words by blending the sounds.",
    "B2.3": "children read and spell the everyday letter-sounds (and word parts) quickly.",
    "B2.4": "children blend sounds to read words and break words into sounds to spell.",
    "B2.1": "children blend sounds to read and break words into sounds to spell — including longer words.",
}

GRADE_TAB = {"Kindergarten": "Kindergarten", "Grade 1": "Grade 1", "Grade 2": "Grade 2", "Grade 3": "Grade 3"}


def _words_with(target: str, text: str) -> list[str]:
    t = target.strip("-_").lower()
    return [w for w in re.findall(r"[A-Za-z]+", text) if t in w.lower()]


def _cur_block(grade: str, codes: list[str]) -> list[str]:
    out = []
    for c in _cur(grade, codes):
        out.append(f"{c['code']} — {c['text']}.")
        out.append(f"In plain terms: {_GLOSS.get(c['code'], 'children practise this reading skill.')}")
    return out


def gen_sentences(topic: dict, data: dict, grade: str) -> dict:
    target = topic["target_grapheme"]
    # `order` override lets a fluency sheet draw on a wider cumulative inventory
    # than the target's own intro order (e.g. early K digraphs use the full K set).
    order = data.get("order", topic["order"])
    sub = data.get("sub", f"/{target}/")
    sound = data.get("sound", f"Sound /{target}/")
    rows = data["sentences"]
    codes = _codes(grade, "sentences")
    decodable = [r["text"] for r in rows]
    img_words = [{"word": r["pic"]} for r in rows if r.get("pic")]
    # answer key: target words per sentence
    ak = []
    for i, r in enumerate(rows, 1):
        ww = _words_with(target, r["text"])
        ak.append(f"Sentence {i}: {', '.join(ww) if ww else '—'}.")
    title = "I Can Read Sentences"
    tab_main = data.get("tab_main", target)     # readable tab label (e.g. "a_e", "o")
    label = data.get("label", target)           # what to say in directions
    directions = data.get("directions",
                          f"Underline the {label} in each sentence. Then read each sentence out loud. "
                          "Colour a face each time you read the whole page.")
    bold = data.get("bold", target)             # row-level bold key (per-row `bold` still wins)
    return {
        "title": f"{title}: {tab_main}",
        "file_title": f"{title} - {re.sub('[^A-Za-z0-9]+','-',tab_main).strip('-')}",
        "phonics": {"grade": _gd(grade), "lesson_order": order, "target_grapheme": target,
                    "decodable_text": decodable,
                    "image_words": img_words,
                    "target_optional": ("_" in target or target.lower() in {"schwa"}),
                    "curriculum": _cur(grade, codes)},
        "worksheet": {
            "tab": {"main": tab_main, "sub": sub},
            "eyebrow": f"{grade} · Phonics · {tab_main}", "title": title, "subtitle": sound,
            "footer_topic": f"{tab_main} — I Can Read Sentences", "name_date": True,
            "parts": [
                {"type": "prose", "text": directions},
                {"type": "reading_rows", "bold": bold, "size": "lg",
                 "rows": [{"text": r["text"], **({"word": r["pic"]} if r.get("pic") else {})} for r in rows]},
                {"type": "read_tracker", "count": 3,
                 "label": "Read the page 3 times. Colour a face each time you read it."},
            ]},
        "teacher_guide": _tg(grade, target, sound,
                             teaches=f"Children read short, decodable sentences that practise the sound for "
                                     f"{target}. Every other word uses letter-sounds they already know, so they "
                                     f"can read each sentence on their own. Reading the page three times builds fluency.",
                             lead=[f"1. Say the sound for {target} together.",
                                   "2. Read the first sentence together, pointing under each word.",
                                   f"3. Children underline {target} in each sentence, then read each sentence on their own.",
                                   "4. Children read the whole page three times and colour one face each time."],
                             answer=ak + [f"Your turn / extension: any real word with {target}."],
                             codes=codes),
    }


def gen_word_building(topic: dict, data: dict, grade: str) -> dict:
    target = topic["target_grapheme"]
    order = data.get("order", topic["order"])
    sub = data.get("sub", "suffix")
    sound = data.get("sound", "")
    build = data.get("build", [])    # [[base, word], ...]  (base + affix)
    rows = data["sentences"]
    codes = _codes(grade, "word_building")
    blank = "______________"
    if data.get("build_lines"):      # explicit build strings (e.g. syllable splits)
        build_rows = [{"text": ln} for ln in data["build_lines"]]
    else:
        build_rows = [{"text": f"{b}  +  {target.strip('-')}  =  {blank}"} for b, _ in build]
    decodable = ([r["text"] for r in rows] + [w for _, w in build] + [b for b, _ in build]
                 + list(data.get("extra_words", [])))
    img_words = [{"word": r["pic"]} for r in rows if r.get("pic")]
    return {
        "title": f"Word Building: {target}",
        "file_title": f"Word Building - {target}",
        "phonics": {"grade": _gd(grade), "lesson_order": order, "target_grapheme": target,
                    "decodable_text": decodable, "image_words": img_words,
                    "target_optional": True,
                    "curriculum": _cur(grade, codes)},
        "worksheet": {
            "tab": {"main": data.get("tab_main", target), "sub": sub},
            "eyebrow": f"{grade} · Word Study · {data.get('tab_main', target)}",
            "title": data.get("title", f"Adding {target} to Words"), "subtitle": sound,
            "footer_topic": f"{target} — Word Building", "name_date": True,
            "parts": [
                {"type": "prose", "text": data.get("intro",
                 f"A word part can be added to a base word. Build each word, then read the sentences.")},
                {"type": "reading_rows", "size": "md", "title": "Build the word", "rows": build_rows},
                {"type": "reading_rows", "bold": target.strip("-"), "size": "lg", "title": "Read the sentences",
                 "rows": [{"text": r["text"], **({"word": r["pic"]} if r.get("pic") else {})} for r in rows]},
                {"type": "read_tracker", "count": 3, "label": "Read the sentences 3 times. Colour a face each time."},
            ]},
        "teacher_guide": _tg(grade, target, sound,
                             teaches=f"Children learn the word part {target} and build new words from base words, "
                                     f"then read them in decodable sentences.",
                             lead=[f"1. Explain the word part / pattern: {data.get('tab_main', target)}.",
                                   f"2. Model the first one: {build[0][0]} + {target.strip('-')} = {build[0][1]}."
                                   if build else f"2. Model the first one together: {build_rows[0]['text'].replace(blank, '?')}.",
                                   "3. Children build the rest, then read each sentence.",
                                   "4. Children read the page three times and colour a face each time."],
                             answer=[f"Build: {', '.join(w for _, w in build)}." if build
                                     else "Build: " + ", ".join(w for w in data.get("extra_words", [])[:6]) + ".",
                                     data.get("note", ""),
                                     "Sentences: " + " ".join(r["text"] for r in rows)],
                             codes=codes),
    }


def gen_letter_sound(topic: dict, data: dict, grade: str) -> dict:
    letter = topic["target_grapheme"]
    Lpair = letter.upper() + letter.lower()
    order = topic["order"]
    keyword = topic["keyword"].split("(")[-1].replace(")", "").strip() if "(" in topic["keyword"] else topic["keyword"]
    keyword = re.sub(r"^[^a-zA-Z]*", "", keyword).split()[0] if keyword else letter
    kw_pic = data.get("keyword_pic", keyword)
    sort_yes = data.get("sort_yes", [])
    sort_no = data.get("sort_no", [])
    cvc = data.get("cvc", [])
    codes = _codes(grade, "letter_sound")
    items = []
    import itertools
    # interleave yes/no for a natural sort row
    mixed = [w for pair in itertools.zip_longest(sort_yes, sort_no) for w in pair if w]
    for w in mixed:
        items.append({"word": w})
    parts = [
        {"type": "formation", "title": f"Trace and write {Lpair}", "letter": Lpair,
         "word": kw_pic, "keyword": kw_pic, "trace": f"{letter.upper()} {letter.lower()} {letter.upper()} {letter.lower()}",
         "lines": 1},
        {"type": "picture_row", "title": f"Colour each picture that starts with the /{letter}/ sound.", "items": items},
    ]
    decodable = []
    if cvc:
        parts.append({"type": "symbols", "title": "Read these words. Sound them out.", "size": "md", "items": cvc})
        decodable = cvc
    return {
        "title": f"Letter and Sound: {Lpair}",
        "file_title": f"Letter and Sound - {Lpair}",
        "phonics": {"grade": _gd(grade), "lesson_order": order, "target_grapheme": letter,
                    "decodable_text": decodable, "image_words": [],
                    "curriculum": _cur(grade, codes)},
        "worksheet": {
            "mascot_word": kw_pic,
            "eyebrow": f"{grade} · Letter & Sound", "title": f"The Letter {Lpair}",
            "subtitle": f"Sound /{letter}/ as in {kw_pic}", "footer_topic": f"{Lpair} — Letter & Sound",
            "name_date": True, "parts": parts},
        "teacher_guide": _tg(grade, letter, f"Sound /{letter}/",
                             teaches=f"Children learn that the letter {letter} makes its sound. They form the letter, "
                                     f"listen for the sound at the start of words, and read short words.",
                             lead=[f"1. Say the /{letter}/ sound together; the keyword is {kw_pic}.",
                                   f"2. Model writing {letter.upper()} and {letter.lower()}; children trace and write.",
                                   "3. Name each picture; children colour the ones that begin with the sound.",
                                   "4. Read the bottom words together, blending the sounds." if cvc else
                                   "4. Re-name the pictures and stretch the beginning sound."],
                             answer=[f"Pictures that start with /{letter}/: {', '.join(sort_yes)}. (Not: {', '.join(sort_no)}.)"]
                                    + ([f"Reading words: {', '.join(cvc)}."] if cvc else []),
                             codes=codes),
    }


def _tg(grade, target, sound, *, teaches, lead, answer, codes, target_g=None, **kw):
    return {
        "eyebrow": f"Teacher Guide · {grade} · {target}",
        "title": f"{target}", "subtitle": "Quick facilitation notes & answer key",
        "footer_topic": f"{target} — Teacher Guide", "name_date": False, "compact": True,
        "parts": [
            {"type": "prose", "title": "What this worksheet teaches", "text": teaches},
            {"type": "prose", "title": "How to lead it (about 15 minutes)", "text": lead},
            {"type": "prose", "title": "Answer key", "text": [a for a in answer if a]},
            {"type": "prose", "title": "Ontario curriculum link (official wording)", "text": _cur_block(grade, codes)},
            {"type": "prose", "title": "If children get stuck — and ways to adjust", "text": [
                f"Watch for: sounding out {target} part by part. Cover the rest of the word and say the target first.",
                "Make it easier: do fewer items together first; you read, the child echoes.",
                "Make it harder: ask the child to think of or write one more word with the target.",
                "You'll know it worked when: the child reads the page smoothly and spots the target on sight.",
            ]},
        ]}


GEN = {"sentences": gen_sentences, "word_building": gen_word_building, "letter_sound": gen_letter_sound}


def generate(topic: dict, data: dict, grade: str) -> dict:
    return GEN[topic["type"]](topic, data, grade)
