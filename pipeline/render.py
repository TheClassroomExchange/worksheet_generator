"""
Render a completed unit's stage JSON files into a single human-readable
markdown packet. This is what a PM reviews; what gets shared with teachers
in a Google Doc; and what Week 2's image-generation pipeline reads to
discover image placeholders.

Pure Python. No LLM. Reads:
  generated_units/<batch>/<unit_slug>/
    0_blueprint.json
    1_lesson_NN.json (×N)
    2_worksheet_NN.json (×N)
    3_manipulatives.json
    4_formative_reflection.json
    5_assessment_suite.json
    6_marketplace.json
  → writes unit.md

Usage:
    from pipeline.render import render_unit
    md = render_unit(Path("generated_units/batch_1/k_patterns_pattern_parade"))
    (unit_dir / "unit.md").write_text(md)
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _h(level: int, text: str) -> str:
    return f"{'#' * level} {text}\n"


def _img_block(ph: dict) -> str:
    return (
        "```image-placeholder\n"
        f"id: {ph['id']}\n"
        f"description: {ph['description']}\n"
        f"placement: {ph['placement']}\n"
        f"size: {ph['approximate_size']}\n"
        "```\n"
    )


def _bullets(items: list[str], prefix: str = "- ") -> str:
    return "".join(f"{prefix}{i}\n" for i in items)


def _table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines) + "\n"


# ── Section renderers ──────────────────────────────────────────────────────

def render_cover(bp: dict, mk: dict) -> str:
    out = []
    out.append(_h(1, bp["thematic_title"]))
    out.append(f"> {bp['descriptive_title']}\n")
    out.append("")
    out.append(_table(
        ["Field", "Value"],
        [
            ["Grade", bp["grade"]],
            ["Subject", bp["subject"]],
            ["Strand", bp["strand"]],
            ["Curriculum codes", ", ".join(bp["curriculum_codes"])],
            ["Curriculum source", bp["curriculum_source_url"]],
            ["Duration", f"{bp['duration_days']} days × 40 min = {mk['classroom_time_total_minutes']} min"],
            ["Suggested price", f"${mk['suggested_price_cad']} CAD"],
            ["Estimated pages", str(mk["pages_total_estimate"])],
            ["Teacher prep time", f"~{mk['teacher_prep_time_minutes']} min (one-time)"],
            ["Generated", datetime.now().strftime("%Y-%m-%d")],
        ],
    ))
    return "\n".join(out)


def render_overview(bp: dict) -> str:
    out = []
    out.append(_h(2, "Unit overview"))
    out.append(bp["unit_overview"] + "\n")
    out.append(f"**Unit learning goal:** {bp['unit_learning_goal']}\n")

    out.append(_h(3, "At a glance"))
    rows = []
    for entry in bp["lesson_arc"]:
        ex_pri = ", ".join(entry["primary_expectations"])
        ex_sec = ", ".join(entry.get("secondary_expectations", []))
        ex = ex_pri + (f" (+{ex_sec})" if ex_sec else "")
        rows.append([
            f"Day {entry['lesson_number']}",
            entry["lesson_title"],
            entry["student_learning_goal"],
            ex,
        ])
    out.append(_table(["Day", "Lesson Title", "Student Goal", "Expectations"], rows))

    out.append(_h(3, "Curriculum expectations"))
    for code in bp["curriculum_codes"]:
        out.append(f"- **{code}** — {bp['curriculum_expectations'][code]}")
    out.append("")

    out.append(_h(3, "Recurring characters"))
    for c in bp["recurring_characters"]:
        out.append(f"- **{c['name']}** — {c['role']}")
        out.append(f"  *Visual:* {c['visual_description']}")
    out.append("")

    out.append(_h(3, "Threaded vocabulary"))
    for v in bp["threaded_vocabulary"]:
        out.append(f"- **{v['term']}** — {v['child_friendly_definition']}")
    out.append("")

    out.append(_h(3, "Manipulatives at a glance"))
    rows = []
    for m in bp["manipulatives_index"]:
        rows.append([m["id"], m["name"], ", ".join(map(str, m["used_in_lessons"]))])
    out.append(_table(["ID", "Name", "Used in lessons"], rows))

    out.append(_h(3, "Materials overview"))
    out.append(_bullets(bp["materials_overview"]))

    a = bp["assessment_strategy"]
    out.append(_h(3, "Assessment strategy"))
    out.append(f"- **Diagnostic:** {a['diagnostic']}")
    out.append(f"- **Formative:** {a['formative']}")
    out.append(f"- **Summative:** {a['summative']}")
    out.append("")

    out.append(_h(3, "Pedagogical notes"))
    out.append(_bullets(bp["pedagogical_notes"]))

    out.append(_h(3, "Canadian context notes"))
    out.append(_bullets(bp["canadian_context_notes"]))

    out.append("\n---\n")
    return "\n".join(out)


def render_lesson(lp: dict, bp: dict) -> str:
    out = []
    n = lp["lesson_number"]
    out.append(_h(2, f"Lesson {n}: {lp['lesson_title']}"))

    out.append(_table(
        ["Field", "Value"],
        [
            ["Grade", bp["grade"]],
            ["Strand", bp["strand"]],
            ["Duration", f"{lp['duration_minutes']} minutes"],
            ["Primary expectations", ", ".join(lp["primary_expectations"])],
            ["Secondary expectations", ", ".join(lp["secondary_expectations"]) or "—"],
        ],
    ))

    out.append(f"**Big idea:** {lp['big_idea']}\n")
    out.append(f"**Learning intention (teacher):** {lp['learning_intention']}\n")
    out.append(f"**Student learning goal:** {lp['student_learning_goal']}\n")
    out.append("**Success criteria:**")
    out.append(_bullets(lp["success_criteria"]))

    out.append(f"**Vocabulary introduced:** {', '.join(lp['vocabulary_introduced']) or '—'}")
    out.append(f"**Vocabulary reinforced:** {', '.join(lp['vocabulary_reinforced']) or '—'}")
    out.append(f"**Manipulatives used:** {', '.join(lp['manipulatives_used'])}")
    out.append("\n**Lesson-specific materials:**")
    out.append(_bullets(lp["lesson_specific_materials"]))

    # Minds On
    mo = lp["minds_on"]
    out.append(_h(3, f"Minds On ({mo['duration_minutes']} min) — {mo['activity_name']}"))
    out.append(f"**Hook:** {mo['hook']}\n")
    out.append("**Teacher script:**\n")
    out.append("> " + mo["teacher_script"].replace("\n", "\n> ") + "\n")
    out.append("**Student actions:**")
    out.append(_bullets(mo["student_actions"]))

    # Action
    ac = lp["action"]
    out.append(_h(3, f"Action ({ac['duration_minutes']} min) — {ac['activity_name']}"))
    out.append(f"*Structure:* `{ac['structure']}`\n")
    for step in ac["steps"]:
        out.append(f"**Step {step['step_number']}.** {step['instruction']}\n")
        out.append(f"> *Teacher prompt:* {step['teacher_prompt']}\n")

    diff = ac["differentiation"]
    out.append(_h(4, "Differentiation"))
    out.append(f"- **For emerging learners:** {diff['for_emerging']}")
    out.append(f"- **For extending learners:** {diff['for_extending']}")
    out.append(f"- **For ELL / IEP:** {diff['for_ell_or_iep']}")
    out.append(f"- **For movement learners:** {diff['for_movement_learners']}\n")

    fc = ac["formative_check"]
    out.append(_h(4, "Formative check"))
    out.append(f"- **What to look for:** {fc['what_to_look_for']}")
    out.append(f"- **How to record:** {fc['how_to_record']}")
    out.append(f"- **Tracker columns:** {', '.join(fc['tracker_columns'])}\n")

    # Consolidation
    co = lp["consolidation"]
    out.append(_h(3, f"Consolidation ({co['duration_minutes']} min) — {co['activity_name']}"))
    out.append("**Discussion prompts:**")
    out.append(_bullets(co["discussion_prompts"]))
    out.append(f"**Exit routine:** {co['exit_routine']}\n")

    # Assessment
    ai = lp["assessment_in_this_lesson"]
    out.append(_h(3, f"Assessment ({ai['type']})"))
    out.append(f"- **Evidence collected:** {ai['evidence_collected']}")
    out.append(f"- **Tracker:** `{ai['tracker_reference']}`")
    out.append(f"- **Rationale:** {ai['rationale']}\n")

    # Expanded walkthrough (optional)
    if lp.get("expanded_walkthrough"):
        ew = lp["expanded_walkthrough"]
        out.append(_h(3, f"Expanded walkthrough — {ew['title']}"))
        out.append(f"*Why this lesson warrants extra scripting:* {ew['rationale']}\n")
        out.append(f"**Setup:** {ew['setup']}\n")
        out.append("**Teacher script:**\n")
        out.append("> " + ew["teacher_script"].replace("\n", "\n> ") + "\n")
        out.append("**Expected student responses:**")
        out.append(_bullets(ew["expected_student_responses"]))
        out.append("**Common misconceptions:**")
        out.append(_bullets(ew["common_misconceptions"]))
        out.append("**Recovery moves:**")
        out.append(_bullets(ew["recovery_moves"]))

    # Worksheet brief
    wb = lp["worksheet_brief"]
    out.append(_h(3, f"Student worksheet brief — {wb['worksheet_title']}"))
    out.append(f"*{wb['purpose']}*\n")
    rows = []
    for p in wb["parts_outline"]:
        rows.append([str(p["part_number"]), p["task"], p["response_type"]])
    out.append(_table(["#", "Task", "Response"], rows))
    out.append("**Expected image assets:**")
    out.append(_bullets(wb["expected_image_assets"]))

    out.append("\n---\n")
    return "\n".join(out)


def render_worksheet(ws: dict) -> str:
    out = []
    n = ws["lesson_number"]
    out.append(_h(3, f"Worksheet {n}: {ws['worksheet_title']}"))
    out.append(f"*{ws['purpose']}*\n")
    out.append(f"**Student learning goal:** {ws['student_learning_goal']}\n")

    h = ws["header"]
    out.append("**Header:**")
    out.append(f"- Student name field: {'yes' if h['student_name_field'] else 'no'}")
    out.append(f"- Date field: {'yes' if h['date_field'] else 'no'}")
    out.append(f"- Banner: \"{h['student_learning_goal_banner']}\"")
    if h.get("character_watermark"):
        out.append(f"- Watermark: {h['character_watermark']}")
    out.append("")

    for page in ws["pages"]:
        out.append(_h(4, f"Page {page['page_number']}"))
        for part in page["parts"]:
            out.append(_h(5, part["part_title"]))
            out.append(f"**Student instructions:** {part['student_instructions']}\n")
            out.append(f"**Visual layout:** {part['visual_layout']}\n")
            for ph in part.get("image_placeholders", []):
                out.append(_img_block(ph))
            out.append(f"**Response type:** `{part['student_response_type']}`")
            out.append(f"**Answer key:** {part['answer_key']}\n")

    if ws.get("early_finisher_prompt"):
        out.append(f"**Early finisher prompt:** {ws['early_finisher_prompt']}\n")
    out.append(f"**Teacher notes:** {ws['teacher_notes']}\n")
    out.append("---\n")
    return "\n".join(out)


def render_manipulatives(mp: dict) -> str:
    out = []
    out.append(_h(2, "Manipulatives & teacher props"))
    for asset in mp["assets"]:
        out.append(_h(3, f"{asset['asset_id']} — {asset['name']}"))
        out.append(f"*{asset['purpose']}*\n")
        ps = asset["print_specifications"]
        out.append(_table(
            ["Field", "Value"],
            [
                ["Category", asset["category"]],
                ["Page size", ps["page_size"]],
                ["Orientation", ps["orientation"]],
                ["Colour", ps["color"]],
                ["Pages per set", str(ps["pages_per_set"])],
                ["Laminate?", "yes" if ps["laminate_recommended"] else "no"],
                ["Quantity per class", asset["quantity_per_class"]],
                ["Used in lessons", ", ".join(map(str, asset["used_in_lessons"]))],
                ["Prep time", f"~{asset['estimated_prep_minutes']} min"],
            ],
        ))
        out.append(f"**Page layout:** {asset['page_layout']}\n")
        out.append("**Teacher prep steps:**")
        out.append(_bullets(asset["teacher_prep_steps"]))
        out.append("**Image placeholders:**\n")
        for ph in asset["image_placeholders"]:
            out.append(_img_block(ph))

    out.append(_h(3, "Overall prep notes"))
    out.append(mp["overall_prep_notes"] + "\n")
    out.append("---\n")
    return "\n".join(out)


def render_formative_reflection(fr: dict) -> str:
    out = []
    out.append(_h(2, "Mid-unit formative & end-of-unit reflection"))

    for fw in fr["formative_worksheets"]:
        out.append(_h(3, f"Formative — {fw['title']}"))
        out.append(f"**When to use:** {fw['when_to_use']}\n")
        out.append(f"**Purpose:** {fw['purpose']}\n")
        out.append(f"**Expectations assessed:** {', '.join(fw['expectations_assessed'])}")
        out.append(f"**Student learning goal:** {fw['student_learning_goal']}\n")
        for prompt in fw["prompts"]:
            out.append(_h(4, f"Prompt {prompt['prompt_number']}"))
            out.append(f"*{prompt['prompt']}*\n")
            out.append(f"**Visual layout:** {prompt['visual_layout']}\n")
            for ph in prompt.get("image_placeholders", []):
                out.append(_img_block(ph))
            out.append(f"**Response type:** `{prompt['response_type']}`")
            out.append(f"**Answer key:** {prompt['answer_key']}\n")
        out.append(f"**Teacher notes:** {fw['teacher_notes']}\n")

    rs = fr["reflection_sheet"]
    out.append(_h(3, f"Reflection sheet — {rs['title']}"))
    out.append(f"**Purpose:** {rs['purpose']}\n")
    out.append(f"**Student learning goal:** {rs['student_learning_goal']}\n")
    for prompt in rs["prompts"]:
        out.append(_h(4, f"Prompt {prompt['prompt_number']}"))
        out.append(f"*{prompt['prompt']}*\n")
        out.append(f"**Visual layout:** {prompt['visual_layout']}\n")
        for ph in prompt.get("image_placeholders", []):
            out.append(_img_block(ph))
        out.append(f"**Response type:** `{prompt['response_type']}`")
        if prompt.get("options"):
            out.append(f"**Options:** {', '.join(prompt['options'])}")
        out.append("")
    out.append(f"**Teacher notes:** {rs['teacher_notes']}\n")
    out.append("---\n")
    return "\n".join(out)


def render_assessment_suite(as_obj: dict) -> str:
    out = []
    out.append(_h(2, "Assessment suite"))

    # Diagnostic + formative trackers
    all_trackers = [as_obj["diagnostic_tracker"]] + as_obj["formative_trackers"]
    out.append(_h(3, "Class observation trackers"))
    for tr in all_trackers:
        out.append(_h(4, tr["title"]))
        out.append(f"- **When used:** {tr['when_used']}")
        out.append(f"- **Expectation focus:** {', '.join(tr['expectation_focus'])}")
        out.append(f"- **Columns:** {', '.join(tr['columns'])}")
        out.append(f"\n**Layout:** {tr['layout_description']}")
        out.append(f"\n**Usage notes:** {tr['usage_notes']}\n")
        for ph in tr.get("image_placeholders", []):
            out.append(_img_block(ph))

    # Summative rubric
    sr = as_obj["summative_rubric"]
    out.append(_h(3, sr["title"]))
    out.append(f"*{sr['purpose']}*\n")
    header = ["Expectation", "Level 1 (Beginning)", "Level 2 (Developing)",
              "Level 3 (Achieving — goal)", "Level 4 (Exceeding)"]
    rows = []
    for r in sr["rows"]:
        levels_by_n = {l["level_number"]: l["descriptor"] for l in r["levels"]}
        rows.append([
            f"**{r['expectation_code']}** — {r['expectation_text']}",
            levels_by_n[1], levels_by_n[2], levels_by_n[3], levels_by_n[4],
        ])
    out.append(_table(header, rows))
    out.append(f"**Usage notes:** {sr['usage_notes']}\n")
    for ph in sr.get("image_placeholders", []):
        out.append(_img_block(ph))

    # Summative task script
    sts = as_obj["summative_task_script"]
    out.append(_h(3, sts["title"]))
    out.append(f"*{sts['purpose']}*\n")
    out.append(_h(4, "Administration steps"))
    for i, step in enumerate(sts["administration_steps"], 1):
        out.append(f"{i}. {step}")
    out.append(f"\n**Scoring guidance:** {sts['scoring_guidance']}\n")
    out.append(_h(4, "Evidence per expectation"))
    for code, evidence in sts["evidence_per_expectation"].items():
        out.append(f"- **{code}** — {evidence}")
    out.append("")

    # Certificate
    cert = as_obj["certificate"]
    out.append(_h(3, cert["title"]))
    out.append(f"**{cert['recipient_field_label']}** ___\n")
    out.append(f"*{cert['achievement_text']}*\n")
    out.append("**Skills demonstrated:**")
    out.append(_bullets(cert["skills_demonstrated"]))
    out.append(f"**Layout:** {cert['layout_description']}\n")
    for ph in cert.get("image_placeholders", []):
        out.append(_img_block(ph))
    ps = cert["print_specifications"]
    out.append(_table(
        ["Print spec", "Value"],
        [["Page size", ps["page_size"]], ["Orientation", ps["orientation"]],
         ["Colour", ps["color"]], ["Laminate?", "yes" if ps["laminate_recommended"] else "no"]],
    ))
    out.append("---\n")
    return "\n".join(out)


def render_marketplace(mk: dict) -> str:
    out = []
    out.append(_h(2, "Marketplace listing block"))
    out.append("```yaml")
    out.append(f"thematic_title: \"{mk['thematic_title']}\"")
    out.append(f"descriptive_title: \"{mk['descriptive_title']}\"")
    out.append(f"suggested_price_cad: {mk['suggested_price_cad']}")
    out.append(f"grade_level: \"{mk['grade_level']}\"")
    out.append(f"subject: \"{mk['subject']}\"")
    out.append(f"strand: \"{mk['strand']}\"")
    out.append(f"curriculum_codes: {json.dumps(mk['curriculum_codes'])}")
    out.append(f"pages_total_estimate: {mk['pages_total_estimate']}")
    out.append(f"teacher_prep_time_minutes: {mk['teacher_prep_time_minutes']}")
    out.append(f"classroom_time_total_minutes: {mk['classroom_time_total_minutes']}")
    out.append(f"tags: {json.dumps(mk['tags'])}")
    out.append(f"hidden_keywords: {json.dumps(mk['hidden_keywords'])}")
    out.append(f"target_buyer: \"{mk['target_buyer']}\"")
    out.append("```\n")

    out.append(_h(3, "Short description"))
    out.append(mk["short_description"] + "\n")

    out.append(_h(3, "Long description"))
    out.append(mk["long_description"] + "\n")

    out.append(_h(3, "What's included"))
    out.append(_bullets(mk["what_is_included"]))

    out.append(_h(3, "Pedagogical approach"))
    out.append(mk["pedagogical_approach"] + "\n")

    return "\n".join(out)


# ── Top-level entry point ──────────────────────────────────────────────────

def render_unit(unit_dir: Path) -> str:
    bp = _load(unit_dir / "0_blueprint.json")
    mk = _load(unit_dir / "6_marketplace.json")

    parts: list[str] = []
    parts.append(render_cover(bp, mk))
    parts.append(render_overview(bp))

    # Lesson plans
    parts.append(_h(1, "Lesson plans"))
    for lp_path in sorted(unit_dir.glob("1_lesson_*.json")):
        lp = _load(lp_path)
        parts.append(render_lesson(lp, bp))

    # Worksheets
    parts.append(_h(1, "Student worksheets"))
    for ws_path in sorted(unit_dir.glob("2_worksheet_*.json")):
        parts.append(render_worksheet(_load(ws_path)))

    # Manipulatives
    parts.append(render_manipulatives(_load(unit_dir / "3_manipulatives.json")))

    # Formative + reflection
    parts.append(render_formative_reflection(_load(unit_dir / "4_formative_reflection.json")))

    # Assessment suite
    parts.append(render_assessment_suite(_load(unit_dir / "5_assessment_suite.json")))

    # Marketplace
    parts.append(render_marketplace(mk))

    return "\n".join(parts)
