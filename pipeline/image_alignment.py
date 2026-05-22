"""Image-text alignment validation.

Every ``ImagePlaceholder`` in a worksheet (or any other stage) must be:

1. Wired to a real asset (clipart from INDEX.json, hand-authored SVG in
   sample_assets/, or a composed image whose recipe lives in compose.py).
2. Captioned with ``keywords`` — the entities/objects that must be visible.
3. Justified with ``text_image_alignment_check`` — Claude's reasoning for
   why this image matches the surrounding text.
4. Coherent with the surrounding student_instructions: every keyword must
   appear (case-insensitive, stem-tolerant) in the part's instructions
   AND in the chosen clipart's caption+tags (if a clipart was chosen).

This validator is wired into ``pipeline.rubric.pre_grade_drift_check`` as a
hard gate — a unit cannot record ``status="pass"`` if any ImagePlaceholder
is mis-aligned.

Runs against:
- Every Worksheet's pages[*].parts[*].image_placeholders[*]
- Every Worksheet's pages[*].image_placeholders[*]   (page-level images)
- Every Manipulative's image_placeholders (in 3_manipulatives.json)
- Every Reflection/Formative sheet's image_placeholders
- Every AssessmentSuite Certificate/SummativeTask image_placeholders
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from pipeline import clipart as _clipart


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_ASSETS = _PROJECT_ROOT / "sample_assets"


# Tiny stemmer: keep words alphanumeric, lowercased, and trim common
# plural/possessive/-ing endings. Good enough for keyword overlap without
# pulling in NLTK. Order matters: longest matching suffix wins, and the
# resulting stem must remain ≥ 4 characters (avoids "miss"→"mis").
#
# The terminal "e" is included LAST so that "circle" and "circles" collapse
# to the same stem ("circl"): "circles" is trimmed to "circl" via "es" first;
# "circle" falls through every other suffix and finally trims "e" → "circl".
# Without the "e" rule the validator would reject keyword "circle" against
# a worksheet whose layout text uses "circles" (a real bug we hit in K math).
_TRIM_SUFFIXES = ("ies", "ing", "ed", "es", "'s", "s", "e")


def _stem(word: str) -> str:
    w = re.sub(r"[^a-z0-9]+", "", word.lower())
    for suf in _TRIM_SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def _tokens(text: str) -> set[str]:
    """Bag of stemmed tokens from arbitrary prose. Splits on hyphens and
    apostrophes so 'multi-step' becomes {'multi', 'step'}; 'don't' → {'dont'}."""
    return {_stem(t) for t in re.findall(r"[A-Za-z]+", text or "")}


def _keyword_in_text(keyword: str, text: str) -> bool:
    """Tolerant containment check: stemmed keyword appears in stemmed tokens.
    Multi-word keywords ('soccer ball') match if every word matches."""
    parts = re.findall(r"[A-Za-z]+", keyword.lower())
    if not parts:
        return True  # vacuous
    text_tokens = _tokens(text)
    return all(_stem(p) in text_tokens for p in parts)


def _validate_placeholder(
    label: str,                # human-readable location, e.g. "WS3.page1.part2.WS03_P2_PARADE"
    ph: dict,                  # the ImagePlaceholder dict
    surrounding_texts: list[str],   # all text around this image (instructions, layout, etc.)
) -> list[str]:
    issues: list[str] = []

    keywords = ph.get("keywords") or []
    align_check = (ph.get("text_image_alignment_check") or "").strip()
    clipart_fname = ph.get("clipart_filename")
    img_id = ph.get("id", "<no-id>")

    # 1. keywords required
    if not keywords:
        issues.append(
            f"{label}: image {img_id} has empty `keywords` (drift gate requires "
            f"≥1 entity/object that must be visible AND named in surrounding text)."
        )
        return issues  # without keywords nothing else can be checked

    # 2. alignment_check required
    if len(align_check) < 40:
        issues.append(
            f"{label}: image {img_id} has missing or too-short "
            f"`text_image_alignment_check` (got {len(align_check)} chars; "
            f"need ≥40 explaining which words map to which visual elements)."
        )

    # 3. keywords must appear in surrounding text (text→image direction)
    surrounding = " ".join(t for t in surrounding_texts if t)
    missing_in_text = [k for k in keywords if not _keyword_in_text(k, surrounding)]
    if missing_in_text:
        issues.append(
            f"{label}: image {img_id} keywords {missing_in_text!r} are NOT mentioned "
            f"in the surrounding student_instructions / visual_layout / description. "
            f"Either (a) the image promises something the text doesn't say, or "
            f"(b) the keyword list is wrong — fix one or the other."
        )

    # 4. asset existence + image→text direction (keywords match clipart caption/tags)
    if clipart_fname:
        row = _clipart.get(clipart_fname)
        if row is None:
            issues.append(
                f"{label}: image {img_id} references clipart_filename "
                f"{clipart_fname!r} which is NOT in sample_assets/clipart/INDEX.json."
            )
        else:
            haystack = " ".join(filter(None, [
                row.get("caption", ""),
                " ".join(row.get("tags", [])),
            ]))
            missing_in_clipart = [
                k for k in keywords if not _keyword_in_text(k, haystack)
            ]
            if missing_in_clipart:
                issues.append(
                    f"{label}: image {img_id} keywords {missing_in_clipart!r} are NOT "
                    f"in the chosen clipart's caption+tags ({clipart_fname!r}: "
                    f"{row.get('caption','')!r}). The image likely doesn't show what "
                    f"the worksheet text says."
                )

    return issues


def _walk_worksheet(ws_path: Path) -> list[str]:
    """Validate every ImagePlaceholder in a worksheet JSON."""
    issues: list[str] = []
    try:
        ws = json.loads(ws_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{ws_path.name}: cannot parse JSON ({e})"]

    ws_label = ws_path.stem  # e.g. "2_worksheet_03"
    instructions_pool = [ws.get("purpose", ""), ws.get("student_learning_goal", "")]

    for page in ws.get("pages", []) or []:
        page_n = page.get("page_number", "?")
        # page-level images
        for ph in page.get("image_placeholders", []) or []:
            label = f"{ws_label}.page{page_n}.{ph.get('id','?')}"
            issues += _validate_placeholder(label, ph, instructions_pool)
        for part in page.get("parts", []) or []:
            part_n = part.get("part_number", "?")
            part_texts = [
                part.get("student_instructions", ""),
                part.get("visual_layout", ""),
                part.get("part_title", ""),
            ] + instructions_pool
            for ph in part.get("image_placeholders", []) or []:
                label = f"{ws_label}.page{page_n}.part{part_n}.{ph.get('id','?')}"
                issues += _validate_placeholder(label, ph, part_texts)
    return issues


def _walk_manipulatives(unit_dir: Path) -> list[str]:
    """Validate every ImagePlaceholder in 3_manipulatives.json.

    Field names match the live ``Manipulatives`` Pydantic schema in
    ``pipeline.schemas`` — ``assets`` (top-level), ``asset_id`` /
    ``name`` / ``purpose`` / ``page_layout`` per asset. Older revisions
    of this walker used parade-era field names (``manipulatives`` /
    ``manipulative_id`` / ``how_to_use``) that no longer exist on the
    schema, which silently no-op'd the entire walker — a real bug we
    hit 2026-05-03 right after the K-math manipulatives stage shipped.
    """
    issues: list[str] = []
    p = unit_dir / "3_manipulatives.json"
    if not p.exists():
        return issues
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"3_manipulatives.json: cannot parse JSON ({e})"]
    for asset in m.get("assets", []) or []:
        a_id = asset.get("asset_id", "?")
        surrounding = [
            asset.get("name", ""),
            asset.get("purpose", ""),
            asset.get("page_layout", ""),
            " ".join(asset.get("teacher_prep_steps", []) or []),
        ]
        for ph in asset.get("image_placeholders", []) or []:
            label = f"manipulatives.{a_id}.{ph.get('id','?')}"
            issues += _validate_placeholder(label, ph, surrounding)
    return issues


def _walk_other_sheets(unit_dir: Path) -> list[str]:
    """Reflection/formative + assessment_suite + marketplace certificate art.

    Schema shapes (live in ``pipeline.schemas``):
      ``FormativeReflection.formative_worksheets: list[FormativeWorksheet]``
      ``FormativeReflection.reflection_sheet: ReflectionSheet``
      ``FormativeWorksheet.prompts: list[FormativePrompt]``
      ``ReflectionSheet.prompts: list[ReflectionPrompt]``
      ``FormativePrompt.image_placeholders: list[ImagePlaceholder]``
      ``ReflectionPrompt.image_placeholders: list[ImagePlaceholder]``
    Older revisions of this walker walked ``pages.parts.image_placeholders``
    (a worksheet-shaped traversal that doesn't exist on these schemas),
    which silently no-op'd the formative + reflection branch entirely.
    """
    issues: list[str] = []
    fr_path = unit_dir / "4_formative_reflection.json"
    if fr_path.exists():
        try:
            fr = json.loads(fr_path.read_text(encoding="utf-8"))
            for sheet_name in ("formative_worksheets", "reflection_sheet"):
                blocks = fr.get(sheet_name, [])
                if isinstance(blocks, dict):
                    blocks = [blocks]
                for sheet_idx, sheet in enumerate(blocks or []):
                    header = sheet.get("header") or {}
                    sheet_surrounding = [
                        sheet.get("purpose", ""),
                        sheet.get("student_learning_goal", ""),
                        sheet.get("title", ""),
                        sheet.get("when_to_use", ""),
                        header.get("student_learning_goal_banner", "") if isinstance(header, dict) else "",
                        header.get("character_watermark", "") if isinstance(header, dict) else "",
                    ]
                    for prompt in sheet.get("prompts", []) or []:
                        prompt_n = prompt.get("prompt_number", "?")
                        prompt_texts = sheet_surrounding + [
                            prompt.get("prompt", ""),
                            prompt.get("visual_layout", ""),
                        ]
                        for ph in prompt.get("image_placeholders", []) or []:
                            label = (
                                f"4_formative_reflection.{sheet_name}"
                                f"[{sheet_idx}].prompt{prompt_n}.{ph.get('id','?')}"
                            )
                            issues += _validate_placeholder(label, ph, prompt_texts)
        except Exception as e:
            issues.append(f"4_formative_reflection.json: cannot parse ({e})")

    asu_path = unit_dir / "5_assessment_suite.json"
    if asu_path.exists():
        try:
            asu = json.loads(asu_path.read_text(encoding="utf-8"))
            cert = asu.get("certificate", {})
            if cert:
                surrounding = [
                    cert.get("title", ""),
                    cert.get("recipient_field_label", ""),
                    cert.get("achievement_text", ""),
                    " ".join(cert.get("skills_demonstrated", []) or []),
                    cert.get("layout_description", ""),
                ]
                for ph in cert.get("image_placeholders", []) or []:
                    label = f"5_assessment_suite.certificate.{ph.get('id','?')}"
                    issues += _validate_placeholder(label, ph, surrounding)
            stask = asu.get("summative_task_script", {})
            if stask:
                # SummativeTaskScript field names vary; pull every str field
                surrounding = [v for v in stask.values() if isinstance(v, str)]
                for ph in stask.get("image_placeholders", []) or []:
                    label = f"5_assessment_suite.summative_task.{ph.get('id','?')}"
                    issues += _validate_placeholder(label, ph, surrounding)
        except Exception as e:
            issues.append(f"5_assessment_suite.json: cannot parse ({e})")

    return issues


def validate_unit_alignment(unit_dir: Path) -> list[str]:
    """The drift-gate entry point. Returns [] if every ImagePlaceholder has
    keywords + alignment_check populated AND every keyword has both
    text-side and (when relevant) clipart-side coverage.
    """
    issues: list[str] = []
    for ws_path in sorted(unit_dir.glob("2_worksheet_*.json")):
        issues += _walk_worksheet(ws_path)
    issues += _walk_manipulatives(unit_dir)
    issues += _walk_other_sheets(unit_dir)
    return issues


def validate_stage_alignment(unit_dir: Path, stage_key: str) -> list[str]:
    """Per-stage alignment validation — used as the at-write-time advisory
    guard inside ``manifest.complete_stage``. Walks ONLY the file owned by
    ``stage_key`` so the warning fires the moment a misaligned image lands,
    not three stages later when the full-unit drift gate runs.

    Returns [] for stages that have no ImagePlaceholders (blueprint, lessons,
    marketplace) — they are not the alignment validator's concern.
    """
    if stage_key.startswith("worksheet_"):
        n = stage_key.split("_", 1)[1]
        ws_path = unit_dir / f"2_worksheet_{n}.json"
        return _walk_worksheet(ws_path) if ws_path.exists() else []

    if stage_key == "manipulatives":
        return _walk_manipulatives(unit_dir)

    if stage_key in ("formative_reflection", "assessment_suite"):
        # _walk_other_sheets handles both — but only return the issues whose
        # label points to the stage we just completed.
        all_issues = _walk_other_sheets(unit_dir)
        prefix = "4_formative_reflection" if stage_key == "formative_reflection" else "5_assessment_suite"
        return [i for i in all_issues if i.startswith(prefix)]

    # blueprint, lesson_NN, marketplace, rubric_grade — no images to validate.
    return []


def report_for(unit_dir: Path) -> str:
    """Pretty-printed summary suitable for stdout / status checks."""
    issues = validate_unit_alignment(unit_dir)
    if not issues:
        return f"image-text alignment ({unit_dir.name}): ✓ clean"
    out = [f"image-text alignment ({unit_dir.name}): {len(issues)} issue(s)"]
    for i in issues:
        out.append(f"  - {i}")
    return "\n".join(out)


def report_alignment_status(units_root: Path | None = None) -> list[str]:
    """Multi-unit summary intended for the session-start daily check block.

    Walks every unit directory under ``generated_units/batch_*/`` (or the
    given ``units_root``) that has at least one of the alignment-gated
    stage outputs on disk and returns a one-line-per-unit status table.

    Output mirrors the shape of ``curriculum_reference.report_reference_status``
    so it can sit alongside it in the CLAUDE.md startup block.
    """
    if units_root is None:
        units_root = _PROJECT_ROOT / "generated_units"
    out: list[str] = []
    if not units_root.exists():
        return ["(no generated_units/ directory yet)"]
    for batch_dir in sorted(units_root.iterdir()):
        if not batch_dir.is_dir() or not batch_dir.name.startswith("batch_"):
            continue
        for unit_dir in sorted(batch_dir.iterdir()):
            if not unit_dir.is_dir():
                continue
            # Only report on units that have at least one image-bearing stage.
            has_images = any(
                (unit_dir / f).exists()
                for f in (
                    "2_worksheet_01.json", "2_worksheet_02.json",
                    "2_worksheet_03.json", "2_worksheet_04.json",
                    "2_worksheet_05.json", "3_manipulatives.json",
                    "4_formative_reflection.json", "5_assessment_suite.json",
                )
            )
            if not has_images:
                continue
            issues = validate_unit_alignment(unit_dir)
            label = f"{batch_dir.name}/{unit_dir.name}"
            if not issues:
                out.append(f"  ✓ {label}: clean")
            else:
                out.append(f"  ✗ {label}: {len(issues)} issue(s)")
                for i in issues[:3]:  # cap detail per unit
                    out.append(f"      - {i[:160]}")
                if len(issues) > 3:
                    out.append(f"      … and {len(issues) - 3} more (run report_for() for full list)")
    if not out:
        return ["(no image-bearing stages generated yet)"]
    return out
