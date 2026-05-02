"""One-shot fetcher for Ontario curriculum expectations.

Source: public Kontent.ai-backed API behind www.dcp.edu.gov.on.ca.
Project ID is exposed in the SPA's bundle; no auth or API key needed.

Hierarchy walked:
    L1 curriculum -> specific_courses -> L2 course
    L2 course -> sections -> ui___content_collection ("Expectations by strand")
                          -> sections -> L3 strand
    L3 strand -> overall_expectations -> L4 overall
    L4 overall -> specific_expectations -> L5 specific  (title_index = "B1.1")
"""
from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

API = "https://ws.api.dcp.edu.gov.on.ca/content/api/items"

# Phase 1 targets. (course_codename, grade_label, subject, curriculum_year, l1_codename)
TARGETS = [
    ("ele___math___grade_1", "1", "math", 2020, "elementary___math"),
    ("ele___math___grade_2", "2", "math", 2020, "elementary___math"),
    ("ele___math___grade_3", "3", "math", 2020, "elementary___math"),
    # Kindergarten 2026 is a single integrated framework; math content
    # is woven through all four frames (A-D), not a standalone strand.
    # We capture the whole K, tagged subject="kindergarten" — the pipeline
    # filters math-relevant expectations by keyword/frame.
    ("kindergarten", "K", "kindergarten", 2026, "elementary___health_and_physical_education__2019__"),
]


def _api_get(params: dict) -> dict:
    q = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    out = subprocess.run(
        ["curl", "-s", "--fail", f"{API}?{q}"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", "", html)
    entities = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'",
        "&rsquo;": "’", "&lsquo;": "‘",
        "&rdquo;": "”", "&ldquo;": "“",
        "&ndash;": "–", "&mdash;": "—",
    }
    for k, v in entities.items():
        text = text.replace(k, v)
    return re.sub(r"\s+", " ", text).strip()


def _fetch_course(course_codename: str) -> dict:
    return _api_get({
        "system.codename[eq]": course_codename,
        "language": "en-CA",
        "system.language[eq]": "en-CA",
        "depth": 5,
    })


def _normalize(payload: dict, course_codename: str, grade: str, subject: str, year: int) -> list[dict]:
    mc = payload.get("modular_content", {})
    course = next((it for it in payload.get("items", [])
                   if it["system"]["codename"] == course_codename), None) or mc.get(course_codename)
    if not course:
        raise RuntimeError(f"course {course_codename!r} not found in payload")

    rows: list[dict] = []
    section_cns = course.get("elements", {}).get("sections", {}).get("value", [])
    for sec_cn in section_cns:
        sec = mc.get(sec_cn, {})
        if sec.get("system", {}).get("type") != "ui___content_collection":
            continue
        # The strand-list wrapper has L3 strands under its own "sections" field.
        for strand_cn in sec.get("elements", {}).get("sections", {}).get("value", []):
            strand = mc.get(strand_cn, {})
            if strand.get("system", {}).get("type") != "l3___strand":
                continue
            se = strand["elements"]
            strand_letter = se.get("title_index", {}).get("value", "")
            strand_name = se.get("title", {}).get("value", "").strip()
            strand_note = _strip_html(se.get("note", {}).get("value", ""))

            for ov_cn in se.get("overall_expectations", {}).get("value", []):
                overall = mc.get(ov_cn, {})
                if overall.get("system", {}).get("type") != "l4___overall_expectation":
                    continue
                oe = overall["elements"]
                ov_code = oe.get("title_index", {}).get("value", "").strip()
                ov_title = oe.get("title", {}).get("value", "").strip()
                ov_text = _strip_html(oe.get("content", {}).get("value", ""))
                rows.append({
                    "grade": grade,
                    "subject": subject,
                    "curriculum_year": year,
                    "strand_code": strand_letter,
                    "strand_name": strand_name,
                    "strand_note": strand_note,
                    "code": ov_code,
                    "title": ov_title,
                    "text": ov_text,
                    "expectation_type": "overall",
                    "source_codename": ov_cn,
                })
                for sp_cn in oe.get("specific_expectations", {}).get("value", []):
                    sp = mc.get(sp_cn, {})
                    if sp.get("system", {}).get("type") != "l5___specific_expectation":
                        continue
                    spe = sp["elements"]
                    rows.append({
                        "grade": grade,
                        "subject": subject,
                        "curriculum_year": year,
                        "strand_code": strand_letter,
                        "strand_name": strand_name,
                        "strand_note": strand_note,
                        "code": spe.get("title_index", {}).get("value", "").strip(),
                        "title": spe.get("title", {}).get("value", "").strip(),
                        "text": _strip_html(spe.get("content", {}).get("value", "")),
                        "expectation_type": "specific",
                        "parent_overall_code": ov_code,
                        "source_codename": sp_cn,
                    })
    return rows


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "curriculum"
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    by_subject: dict[str, list[dict]] = {}
    sources: list[dict] = []

    for course_cn, grade, subject, year, l1_cn in TARGETS:
        print(f"  fetching {course_cn} ...", flush=True)
        payload = _fetch_course(course_cn)
        (raw_dir / f"{course_cn}.json").write_text(json.dumps(payload, indent=2))
        rows = _normalize(payload, course_cn, grade, subject, year)
        n_overall = sum(1 for r in rows if r["expectation_type"] == "overall")
        n_specific = sum(1 for r in rows if r["expectation_type"] == "specific")
        print(f"    -> {n_overall} overall + {n_specific} specific = {len(rows)} rows")
        by_subject.setdefault(subject, []).extend(rows)
        sources.append({
            "l1_codename": l1_cn,
            "course_codename": course_cn,
            "grade": grade,
            "subject": subject,
            "curriculum_year": year,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "row_count": len(rows),
            "n_overall": n_overall,
            "n_specific": n_specific,
        })

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for subject, rows in by_subject.items():
        path = out_dir / f"{subject}.json"
        path.write_text(json.dumps({
            "meta": {
                "subject": subject,
                "fetched_at": timestamp,
                "source": "https://ws.api.dcp.edu.gov.on.ca (Ontario MOE — Kontent.ai delivery API)",
                "row_count": len(rows),
            },
            "expectations": rows,
        }, indent=2, ensure_ascii=False))
        print(f"  wrote {path} ({len(rows)} rows)")

    (out_dir / "sources.json").write_text(json.dumps({
        "fetched_at": timestamp,
        "api": API,
        "sources": sources,
    }, indent=2))
    print("  wrote curriculum/sources.json")


if __name__ == "__main__":
    main()
