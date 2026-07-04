"""Language-worksheet build orchestration: materialize word->image (per backend),
run the decodability gate, and render/combine via the shared coding pipeline.

content.json authoring is backend-agnostic: parts reference a `word` (or `keyword`),
and this module resolves it to an `img`/`src` path with the chosen image backend
(``openmoji`` or ``ai``). The two sample image variants are the SAME content.json
built with different backends.
"""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from language import phonics_images as pi
from language import decodability as dc
from language import quality_gates as qg

ROOT = Path(__file__).resolve().parent.parent


def _resolve(word: str, backend: str):
    p = pi.resolve(word, backend)
    return str(p) if p else None


def materialize(content: dict, backend: str) -> tuple[dict, list[str]]:
    """Return (resolved_content, missing_words). Walks worksheet + teacher_guide
    parts and turns every `word`/`keyword` into a concrete image path."""
    out = copy.deepcopy(content)
    missing: list[str] = []

    def need(word):
        path = _resolve(word, backend)
        if not path:
            missing.append(word)
        return path

    for sec in ("worksheet", "teacher_guide"):
        spec = out.get(sec)
        if not spec:
            continue
        # header mascot
        mw = spec.pop("mascot_word", None)
        if mw and not spec.get("mascot"):
            mp = need(mw)
            if mp:
                spec["mascot"] = mp
        for part in spec.get("parts", []):
            t = part.get("type")
            if t in ("reading_rows", "sound_boxes"):
                for r in part.get("rows", []):
                    if r.get("word") and not r.get("img"):
                        ip = need(r["word"])
                        if ip:
                            r["img"] = ip
            elif t == "picture_row":
                for it in part.get("items", []):
                    if it.get("word") and not it.get("img"):
                        ip = need(it["word"])
                        if ip:
                            it["img"] = ip
                        it.setdefault("label", it["word"])
            elif t == "formation":
                w = part.get("word")
                if w and not part.get("img"):
                    ip = need(w)
                    if ip:
                        part["img"] = ip
            elif t == "image":
                w = part.get("word")
                if w and not part.get("src"):
                    ip = need(w)
                    if ip:
                        part["src"] = ip
    return out, missing


def build_variant(src_dir, out_dir, *, backend: str, grade: str) -> dict:
    """Materialize ``src_dir/content.json`` for ``backend`` into ``out_dir`` and
    render+combine the combined PDF. Runs the decodability gate first (hard).
    Returns a summary dict. Does NOT apply borders/publish."""
    from pipeline import coding_build as cb

    src_dir, out_dir = Path(src_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    content = json.loads((src_dir / "content.json").read_text())

    # decodability gate (uses the backend-agnostic phonics block)
    (out_dir / "content.json").write_text(json.dumps(content, indent=2))  # for check_unit
    dec = dc.check_unit(out_dir)
    if not dec["passed"]:
        raise RuntimeError(f"decodability FAILED for {src_dir.name}: "
                           f"{[f['word'] for f in dec['failures']]} target_present={dec.get('target_present')}")

    resolved, missing = materialize(content, backend)
    if missing:
        raise RuntimeError(f"unresolved images ({backend}) for {src_dir.name}: {missing}")
    (out_dir / "content.json").write_text(json.dumps(resolved, indent=2, ensure_ascii=False))
    (out_dir / "input_row.json").write_text(json.dumps({"grade": grade}, indent=2))

    fit = cb.fit_render(out_dir)  # renders + combines internally (roomy auto-fit)
    if fit.get("status") != "pass":
        raise RuntimeError(f"fit_render did not pass for {src_dir.name}: {fit}")
    pdf = out_dir / fit["combined_pdf"]
    qg.run_quality_gates(out_dir, resolved, grade, pdf)  # same standing gates as build_unit
    return {"pdf": str(pdf), "decodability": dec, "fit": fit, "backend": backend}


def build_unit(unit_dir, grade: str, *, backend: str = "ai", border: bool = True) -> dict:
    """In-place build for a real queue unit (DESIGN_STANDARD applies). Reads the
    authored content.json (with `word` refs), runs the decodability gate, resolves
    images, renders+combines, and stamps the grade border. Returns a summary."""
    from pipeline import coding_build as cb, add_grade_border as gb
    import shutil, tempfile

    unit_dir = Path(unit_dir)
    content = json.loads((unit_dir / "content.json").read_text())
    dec = dc.check_unit(unit_dir)
    if not dec["passed"]:
        raise RuntimeError(f"decodability FAILED {unit_dir.name}: "
                           f"{[f['word'] for f in dec['failures']]} target={dec.get('target_present')}")
    resolved, missing = materialize(content, backend)
    if missing:
        raise RuntimeError(f"unresolved images ({backend}) {unit_dir.name}: {missing}")
    (unit_dir / "content.json").write_text(json.dumps(resolved, indent=2, ensure_ascii=False))
    (unit_dir / "input_row.json").write_text(json.dumps({"grade": grade}, indent=2))
    fit = cb.fit_render(unit_dir)
    if fit.get("status") != "pass":
        raise RuntimeError(f"fit_render fail {unit_dir.name}: {fit}")
    pdf = unit_dir / fit["combined_pdf"]
    qg.run_quality_gates(unit_dir, resolved, grade, pdf)  # standing gates — raise on defect
    border_ok = None
    if border:
        work = Path(tempfile.mkdtemp())
        bkp = work / "b.pdf"; shutil.copy2(pdf, bkp)
        ov = work / "ov.pdf"; gb.build_overlay(gb.GRADE_HEX[grade], ov)
        gb.stamp(bkp, ov, pdf)
        border_ok, why = gb.gate(bkp, pdf, work)
        if not border_ok:
            raise RuntimeError(f"border gate fail {unit_dir.name}: {why}")
    return {"pdf": str(pdf), "decodability": dec, "fit": fit, "border_ok": border_ok}
