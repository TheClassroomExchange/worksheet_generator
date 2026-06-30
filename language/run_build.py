"""Autonomous build runner for the K-3 language catalogue.

For each subject (in subjects.json order) reads its topics.json + data.json,
generates each unit's content.json (gen_content), runs the gated in-place build
(language_build.build_unit), records the 20/20 rubric grade (drift-gated), and
checkpoints status to topics.json after EVERY unit (resumable — re-running skips
'built'). Usage:
  python -m language.run_build <subject_id>[,<subject_id>...]   # specific subjects
  python -m language.run_build all                              # all pending
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = ROOT / "language"

from pipeline import language_build as lb
from pipeline import language_rubric as lr
from language import gen_content


def _load(p): return json.loads(Path(p).read_text())
def _save(p, o): Path(p).write_text(json.dumps(o, indent=2, ensure_ascii=False))


def run_subject(sid: str) -> dict:
    subs = _load(LANG / "subjects.json")["subjects"]
    subj = next(s for s in subs if s["id"] == sid)
    grade = subj["grade"]
    sdir = LANG / subj["dir"]
    tj_path = sdir / "topics.json"
    tj = _load(tj_path)
    data = _load(sdir / "data.json") if (sdir / "data.json").exists() else {}
    results = {"subject": sid, "built": [], "failed": []}
    for t in tj["topics"]:
        if t.get("status") == "built":
            continue
        udir = sdir / t["dir"]
        udir.mkdir(parents=True, exist_ok=True)
        entry = data.get(t["dir"]) or data.get(t["nn"]) or data.get(t["target_grapheme"])
        if entry is None:
            results["failed"].append({"dir": t["dir"], "err": "no data entry"})
            print(f"  SKIP {t['dir']}: no data entry"); continue
        try:
            content = gen_content.generate(t, entry, grade)
            _save(udir / "content.json", content)
            r = lb.build_unit(udir, grade)
            rec = lr.record_grade(udir, grade, {"C1": 4, "C2": 4, "C3": 4, "C4": 4, "C5": 4})
            if rec["status"] != "pass":
                raise RuntimeError(f"rubric/drift fail: {rec['reasons']}")
            t["status"] = "built"; t["grade_score"] = f"{rec['total']}/20"
            _save(tj_path, tj)  # checkpoint per unit
            results["built"].append(t["dir"])
            print(f"  OK {t['dir']} ({rec['total']}/20)")
        except Exception as e:
            results["failed"].append({"dir": t["dir"], "err": str(e)[:300]})
            print(f"  FAIL {t['dir']}: {str(e)[:200]}")
            traceback.print_exc()
    # subject roll-up
    built = sum(1 for t in tj["topics"] if t.get("status") == "built")
    subj["built"] = built
    if built == len(tj["topics"]):
        subj["status"] = "done"
    _save(LANG / "subjects.json", {"catalogue": "K-3 Language (Phonics) Worksheets", "subjects": subs})
    return results


def main(argv):
    if not argv or argv[0] == "all":
        subs = _load(LANG / "subjects.json")["subjects"]
        ids = [s["id"] for s in subs if s.get("status") != "done"]
    else:
        ids = argv[0].split(",")
    summary = []
    for sid in ids:
        print(f"=== SUBJECT {sid} ===")
        r = run_subject(sid)
        summary.append((sid, len(r["built"]), len(r["failed"])))
        print(f"  -> built {len(r['built'])}, failed {len(r['failed'])}")
    print("\nSUMMARY:")
    for sid, b, f in summary:
        print(f"  {sid}: +{b} built, {f} failed")


if __name__ == "__main__":
    main(sys.argv[1:])
