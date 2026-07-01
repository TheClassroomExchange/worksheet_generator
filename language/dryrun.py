"""Fast pre-build validation for a subject's data.json (no image gen, no render):
decodability + target-present + image-word-in-text. Run before run_build.
  python -m language.dryrun <subject_id>
"""
import json, re, sys
from pathlib import Path
from language import gen_content
from pipeline import decodability as dc

LANG = Path(__file__).resolve().parent


def check(sid: str) -> bool:
    scope = dc.load_scope()
    subj = next(s for s in json.loads((LANG / "subjects.json").read_text())["subjects"] if s["id"] == sid)
    grade = subj["grade"]
    tj = json.loads((LANG / sid / "topics.json").read_text())
    data = json.loads((LANG / sid / "data.json").read_text()) if (LANG / sid / "data.json").exists() else {}
    allok = True
    for t in tj["topics"]:
        entry = data.get(t["dir"]) or data.get(t["nn"]) or data.get(t["target_grapheme"])
        if entry is None:
            print(f"  {t['dir']:22} -- no data"); continue
        c = gen_content.generate(t, entry, grade)
        ph = c["phonics"]
        r = dc.check_text(ph["decodable_text"], ph["lesson_order"], ph["grade"], scope)
        text = " ".join(ph["decodable_text"]).lower()
        bad_imgs = [iw["word"] for iw in ph.get("image_words", []) if iw["word"].lower() not in text]
        tgt = ph["target_grapheme"].strip("-_").lower()
        tp = ("_" in ph["target_grapheme"]) or (bool(tgt) and any(tgt in re.sub("[^a-z]", "", s.lower()) for s in ph["decodable_text"]))
        ok = r["passed"] and tp and not bad_imgs
        allok &= ok
        flag = "OK" if ok else "XX"
        note = []
        if not r["passed"]: note.append(f"decode:{[f['word'] for f in r['failures']]}")
        if not tp: note.append("target-missing")
        if bad_imgs: note.append(f"img-not-in-text:{bad_imgs}")
        print(f"  {t['dir']:22} {flag} {' '.join(note)}")
    print("ALL OK" if allok else "FIX NEEDED")
    return allok


if __name__ == "__main__":
    ok = check(sys.argv[1])
    raise SystemExit(0 if ok else 1)
