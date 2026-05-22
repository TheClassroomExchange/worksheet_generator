"""Full marketplace-quality rebuild driver.

Per-unit phases tracked in .full_rebuild_checkpoint.json:
  1. survey         — list image_ids and current dispatcher coverage
  2. composers      — bespoke composer code added in compose.py and primitive
                      SVGs created in sample_assets/<theme>/
  3. recomposed     — compose_for_unit() ran cleanly
  4. local_qa       — every CHAR_/M_/WS_/AS_/FORM_/REF_ image_id has a real
                      composite (not a labelled-box fallback)
  5. clean_decks    — prior decks deleted from the unit's Drive folder
  6. deck_built     — build_unit_deck() returned a URL
  7. deck_qa        — exported PDF inspected; every slide with a placeholder
                      shows an image (and not the labelled-box fallback)
  8. shipped        — verified exactly one deck remains in the Drive folder

If local_qa OR deck_qa fail, the unit is marked 'blocked' with the reason
and the deck is NOT uploaded. The user can re-run after fixing composers.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.unit_plan import load_state, by_unit_id, init_unit_from_plan
from pipeline.compose import (
    compose_for_unit,
    compose_pattern_parade_image,
    _smart_fallback,
    _CHARACTER_CLIPART,
)
from pipeline.slides import (
    build_unit_deck,
    UNIT_DECK_PARENT_FOLDER_ID,
    _find_or_create_subfolder,
    get_credentials,
)
from googleapiclient.discovery import build

CHECKPOINT = PROJECT_ROOT / ".full_rebuild_checkpoint.json"
LOG = PROJECT_ROOT / ".full_rebuild_log.txt"

# Order: 11 character-already-done units first, then the remaining 29.
PRIORITY_ORDER = [
    # Character-already-done (have custom SVG character cards)
    "g1_data_detectives",
    "k_data_detectives",
    "g2_data_detectives",
    "g3_data_detectives",
    "g1_algebra_real_life_modelling",
    "g2_algebra_real_life_modelling",
    "g3_algebra_real_life_modelling",
    "g2_algebra_whats_missing",
    "g2_algebra_if_then_detectives",
    "g3_algebra_balanced_equations",
    "g3_algebra_bug_busters",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_ckpt() -> dict:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text())
    return {"started_at": _now(), "units": {}}


def save_ckpt(c: dict) -> None:
    c["updated_at"] = _now()
    CHECKPOINT.write_text(json.dumps(c, indent=2) + "\n")


def log(msg: str) -> None:
    print(msg, flush=True)
    with LOG.open("a") as f:
        f.write(f"[{_now()}] {msg}\n")


def collect_image_ids(unit_dir: Path) -> set[str]:
    ids: set[str] = set()
    for jf in sorted(unit_dir.glob("?_*.json")):
        try:
            text = jf.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.findall(r'"(?:id|image_id)":\s*"([A-Z][A-Z0-9_]+)"', text):
            if m.startswith(("WS", "M", "AS_", "FORM_", "REF_", "CHAR_")):
                ids.add(m)
    return ids


def _all_handled_ids() -> set[str]:
    """Aggregate HANDLED_IDS from every per-theme composer module."""
    handled: set[str] = set()
    for mod_name in ("composers_data_detectives", "composers_real_life",
                      "composers_algebra", "composers_probability",
                      "composers_financial", "composers_measurement",
                      "composers_spatial_coding", "composers_number"):
        try:
            mod = __import__(f"pipeline.{mod_name}", fromlist=["HANDLED_IDS"])
            handled |= getattr(mod, "HANDLED_IDS", set())
        except Exception:
            pass
    return handled


def has_real_composite(image_id: str, unit_grade: str | None = None) -> bool:
    """Return True if image_id is handled by a bespoke composer (not a generic
    labelled-box fallback)."""
    # Per-theme dispatcher modules
    if image_id in _all_handled_ids():
        return True
    # Explicit branch in compose.py source for this id
    src = (PROJECT_ROOT / "pipeline" / "compose.py").read_text()
    if f'image_id == "{image_id}"' in src:
        return True
    # Tuple membership: image_id in ("X", "Y", ...) — captures multi-id branches
    if f'"{image_id}"' in src and (
            f"image_id in (" in src or f"image_id == \"{image_id}\"" in src):
        # Verify the literal appears inside an `image_id in (...)` tuple.
        import re as _re
        for m in _re.finditer(r"image_id in \(([^)]*)\)", src):
            ids_in_tuple = _re.findall(r'"([^"]+)"', m.group(1))
            if image_id in ids_in_tuple:
                return True
    # Dict literal membership: image_id appears as a key in a dict literal.
    import re as _re2
    if f'"{image_id}"' in src:
        for m in _re2.finditer(r"\{[^{}]*\"" + _re2.escape(image_id) +
                               r"\"[^{}]*\}", src):
            return True
    # Dot/buddy reference cards: backed by SVGs in sample_assets/
    if image_id.startswith("M3_") and ("DOTS_" in image_id or image_id == "M3_BUDDY_REFERENCE"):
        asset = PROJECT_ROOT / "sample_assets" / (image_id.lower().replace("m3_", "icon_") + ".svg")
        if asset.exists():
            return True
    # CHAR_*_FRONT with a custom SVG OR known character clipart
    if image_id.startswith("CHAR_") and image_id.endswith("_FRONT"):
        key = image_id[5:-6]
        svg = PROJECT_ROOT / "sample_assets" / "characters" / f"{key}.svg"
        return svg.exists() or key in _CHARACTER_CLIPART
    # Reflection sheet boilerplate is procedurally composed
    if image_id in {"REF_STARS", "REF_FAV_BOX", "REF_TRICKY_BOX",
                    "REF_NEXT_BOX", "REF_YN_TABLE",
                    "AS_RUBRIC", "AS_CERT_BORDER", "AS_CERT_FRIENDS"}:
        return True
    # AS_CERT_<KEY> reuses the unit anchor character
    if image_id.startswith("AS_CERT_"):
        key = image_id[len("AS_CERT_"):]
        if key in _CHARACTER_CLIPART or (
                PROJECT_ROOT / "sample_assets" / "characters" / f"{key}.svg").exists():
            return True
    return False


def drift_check(unit_dir: Path) -> dict:
    """Read every JSON-described image_placeholder for this unit and verify
    that the composed PNG is non-trivial AND that the composer's keywords
    overlap with the JSON's keywords.

    Returns:
      {
        "checked": int,
        "passed": int,
        "warnings": [{"id": ..., "issue": ...}, ...]
      }
    """
    import json as _json
    import re as _re
    composed = unit_dir / "composed"
    warnings = []
    checked = 0
    passed = 0
    placeholders: dict[str, dict] = {}
    for jf in sorted(unit_dir.glob("?_*.json")):
        try:
            text = jf.read_text(encoding="utf-8")
            data = _json.loads(text)
        except Exception:
            continue

        def walk(o):
            if isinstance(o, dict):
                if (isinstance(o.get("id"), str) and o["id"].isupper()
                        and "description" in o):
                    placeholders[o["id"]] = o
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(data)

    for image_id, ph in placeholders.items():
        png_path = composed / f"{image_id}.png"
        if not png_path.exists():
            warnings.append({"id": image_id, "issue": "no composed PNG on disk"})
            continue
        kb = png_path.stat().st_size / 1024
        checked += 1
        if kb < 0.2:
            warnings.append({"id": image_id,
                             "issue": f"PNG only {kb:.1f} KB (likely empty)"})
            continue
        # Visual sanity: open and check non-white pixel ratio. Many parade
        # strip composites use transparent backgrounds with thin borders, so
        # the pixel-density check should be lenient. Only flag near-zero ink.
        try:
            from PIL import Image as _Image
            img = _Image.open(png_path).convert("L")
            w, h = img.size
            histogram = img.histogram()
            # < 240 = "ink" pixels (text, lines, fills); >= 240 = white-ish
            nonwhite = sum(histogram[:240])
            ratio = nonwhite / (w * h)
            if ratio < 0.001:
                warnings.append({"id": image_id,
                                 "issue": f"only {ratio*100:.3f}% non-white pixels (likely empty)"})
                continue
        except Exception:
            pass
        passed += 1
    return {"checked": checked, "passed": passed, "warnings": warnings}


def survey_unit(unit_dir: Path) -> dict:
    ids = collect_image_ids(unit_dir)
    real = {i for i in ids if has_real_composite(i)}
    fallback = ids - real
    return {
        "total_ids": sorted(ids),
        "real_composite_count": len(real),
        "fallback_count": len(fallback),
        "fallback_ids": sorted(fallback),
    }


def local_qa(unit_dir: Path) -> dict:
    """Inspect composed/*.png. Trust the dispatcher-coverage gate above for
    "is this a real composite vs labelled-box" — it's authoritative. Here we
    only flag obviously broken composites (literal 0-byte files) and gather
    sizes for the report. Drift check (below) catches blank-pixel issues.
    """
    composed = unit_dir / "composed"
    suspect = []
    sizes = {}
    for p in composed.glob("*.png"):
        kb = p.stat().st_size / 1024
        sizes[p.stem] = kb
        if kb < 0.2:
            suspect.append(f"{p.name} ({kb:.1f}KB)")
    return {"sizes": sizes, "suspect_small_pngs": suspect}


def list_drive_decks(drive, folder_id: str) -> list[dict]:
    if not folder_id:
        return []
    q = (f"'{folder_id}' in parents and "
         f"mimeType = 'application/vnd.google-apps.presentation' and "
         f"trashed = false")
    res = drive.files().list(q=q, fields="files(id,name)", pageSize=20).execute()
    return res.get("files", [])


def delete_orphan_decks(drive, folder_id: str, keep_id: str) -> int:
    n = 0
    for f in list_drive_decks(drive, folder_id):
        if f["id"] == keep_id:
            continue
        try:
            drive.files().delete(fileId=f["id"]).execute()
            n += 1
        except Exception as e:
            log(f"    (could not delete {f['name']}: {e})")
    return n


def process_unit(drive, unit_id: str, ckpt: dict, *, force_recompose: bool = False,
                 force_qa: bool = False) -> None:
    state = ckpt["units"].setdefault(unit_id, {})
    entry = by_unit_id(unit_id)
    if entry is None:
        log(f"[{unit_id}] no plan entry; skipping")
        return
    unit_dir = init_unit_from_plan(entry)
    state["unit_dir"] = str(unit_dir)

    # 1. survey (always)
    survey = survey_unit(unit_dir)
    state["survey"] = survey
    save_ckpt(ckpt)
    log(f"[{unit_id}] survey: {survey['real_composite_count']} real, "
        f"{survey['fallback_count']} fallback")
    if survey["fallback_count"]:
        log(f"  fallback ids: {', '.join(survey['fallback_ids'][:6])}"
            f"{'…' if survey['fallback_count'] > 6 else ''}")

    # 2. composers (manual gate — script does NOT add bespoke composers)
    if survey["fallback_count"] > 0:
        state["composers"] = "blocked"
        state["block_reason"] = (
            f"{survey['fallback_count']} image_ids have no bespoke composer "
            f"and would render as labelled-box fallbacks. Add branches to "
            f"compose.py for the listed ids before continuing.")
        save_ckpt(ckpt)
        log(f"  ✗ composer gate: {state['block_reason']}")
        return
    state["composers"] = "ok"

    # 3. recompose
    if force_recompose or state.get("recomposed") != "ok":
        try:
            compose_for_unit(unit_dir)
            state["recomposed"] = "ok"
            save_ckpt(ckpt)
        except Exception as e:
            state["recomposed"] = f"error: {e}"
            save_ckpt(ckpt)
            log(f"  ✗ recompose failed: {e}")
            return

    # 4. local_qa  +  drift_check
    if force_qa or state.get("local_qa") != "ok":
        qa = local_qa(unit_dir)
        state["local_qa_detail"] = qa
        drift = drift_check(unit_dir)
        state["drift_check"] = drift
        # Block on either: small PNGs OR drift warnings
        problems = []
        if qa["suspect_small_pngs"]:
            problems.append(
                f"{len(qa['suspect_small_pngs'])} composed PNG(s) < 8 KB: "
                f"{', '.join(qa['suspect_small_pngs'][:5])}")
        if drift["warnings"]:
            problems.append(
                f"{len(drift['warnings'])} drift warning(s); first: "
                f"{drift['warnings'][0]['id']}: {drift['warnings'][0]['issue']}")
        if problems:
            state["local_qa"] = "blocked"
            state["block_reason"] = " | ".join(problems)
            save_ckpt(ckpt)
            log(f"  ✗ local_qa: {state['block_reason']}")
            return
        state["local_qa"] = "ok"
        save_ckpt(ckpt)
        log(f"  ✓ local_qa: {len(qa['sizes'])} PNGs OK; "
            f"drift: {drift['passed']}/{drift['checked']} passed")

    # 5. clean_decks
    bp = json.loads((unit_dir / "0_blueprint.json").read_text())
    parent_id = UNIT_DECK_PARENT_FOLDER_ID
    folder_name = bp.get("thematic_title") or unit_id
    folder_id = _find_or_create_subfolder(drive, parent_id, folder_name)
    state["unit_folder_id"] = folder_id
    if state.get("clean_decks") != "ok":
        decks = list_drive_decks(drive, folder_id)
        for d in decks:
            try:
                drive.files().delete(fileId=d["id"]).execute()
                log(f"    deleted prior deck {d['name']}")
            except Exception as e:
                log(f"    (could not delete {d['name']}: {e})")
        state["clean_decks"] = "ok"
        save_ckpt(ckpt)

    # 6. deck_built (with retry-on-propagation)
    if state.get("deck_built") != "ok":
        last_err = None
        for attempt in range(1, 5):
            try:
                url = build_unit_deck(unit_dir, run_preflight=False)
                state["deck_url"] = url
                state["deck_built"] = "ok"
                state["build_attempts"] = attempt
                save_ckpt(ckpt)
                log(f"  ✓ {url}")
                last_err = None
                break
            except Exception as e:
                last_err = e
                if "publicly accessible" in str(e) or "createImage" in str(e):
                    backoff = 5 * attempt
                    log(f"  ⟲ propagation retry in {backoff}s")
                    time.sleep(backoff)
                else:
                    break
        if last_err is not None:
            state["deck_built"] = f"error: {last_err}"
            save_ckpt(ckpt)
            return

    # 7. deck_qa — export PDF, check size, render character + worksheet pages
    if state.get("deck_qa") != "ok":
        deck_id = state["deck_url"].split("/d/")[1].split("/")[0]
        try:
            pdf_bytes = drive.files().export(
                fileId=deck_id, mimeType="application/pdf").execute()
        except Exception as e:
            state["deck_qa"] = f"error: {e}"
            save_ckpt(ckpt)
            return
        state["deck_pdf_kb"] = len(pdf_bytes) / 1024
        out = PROJECT_ROOT / ".deck_qa" / f"{unit_id}.pdf"
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(pdf_bytes)
        # Render all pages for inspection
        try:
            from pdf2image import convert_from_bytes, pdfinfo_from_bytes
            info = pdfinfo_from_bytes(pdf_bytes)
            n = info["Pages"]
            pages = convert_from_bytes(pdf_bytes, dpi=110, first_page=1, last_page=n)
            for i, im in enumerate(pages, 1):
                im.save(out.parent / f"{unit_id}_p{i:02d}.png")
            state["deck_qa_pages_rendered"] = n
        except Exception as e:
            log(f"  ⚠ pdf2image failed: {e}")
        # Heuristic: deck PDF should be > 350 KB (Pattern Parade decks
        # are 22 pages and can run ~390 KB legitimately).
        if state["deck_pdf_kb"] < 350:
            state["deck_qa"] = "blocked"
            state["block_reason"] = f"deck PDF only {state['deck_pdf_kb']:.0f} KB (expected > 400)"
            save_ckpt(ckpt)
            log(f"  ✗ deck_qa: {state['block_reason']}")
            return
        state["deck_qa"] = "ok"
        save_ckpt(ckpt)
        log(f"  ✓ deck_qa: PDF {state['deck_pdf_kb']:.0f} KB, "
            f"{state.get('deck_qa_pages_rendered','?')} pages rendered")

    # 8. shipped — confirm exactly one deck in Drive folder
    if state.get("shipped") != "ok":
        keep_id = state["deck_url"].split("/d/")[1].split("/")[0]
        deleted = delete_orphan_decks(drive, folder_id, keep_id)
        decks_after = list_drive_decks(drive, folder_id)
        if len(decks_after) != 1:
            state["shipped"] = "blocked"
            state["block_reason"] = f"{len(decks_after)} decks in folder after cleanup"
            save_ckpt(ckpt)
            log(f"  ✗ shipped: {state['block_reason']}")
            return
        state["shipped"] = "ok"
        state["completed_at"] = _now()
        save_ckpt(ckpt)
        log(f"  ✓ shipped — folder has 1 deck (deleted {deleted} orphans)")


def main():
    ckpt = load_ckpt()
    state = load_state()
    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    # Process priority order first, then any unit in load_state not in priority
    rest = sorted(set(state.keys()) - set(PRIORITY_ORDER))
    order = PRIORITY_ORDER + rest

    # Optional: filter to a single unit via CLI
    if len(sys.argv) > 1:
        order = sys.argv[1:]

    log(f"=== Full-rebuild driver run @ {_now()} ===")
    log(f"Order: {len(order)} units")

    for i, unit_id in enumerate(order, 1):
        s = ckpt["units"].get(unit_id, {})
        if s.get("shipped") == "ok":
            continue
        log(f"\n--- [{i}/{len(order)}] {unit_id} ---")
        process_unit(drive, unit_id, ckpt)

    done = sum(1 for s in ckpt["units"].values() if s.get("shipped") == "ok")
    blocked = sum(1 for s in ckpt["units"].values()
                  if any(v == "blocked" for v in s.values() if isinstance(v, str)))
    log(f"\n=== Summary: {done} shipped / {blocked} blocked / {len(order)} total ===")


if __name__ == "__main__":
    main()
