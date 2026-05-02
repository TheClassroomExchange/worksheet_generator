"""Read-only catalogue of the local clipart library.

Source of truth: ``sample_assets/clipart/INDEX.json``. The catalogue was
seeded from Michelle's ``Clipart`` Google Slides deck on 2026-05-01 and is
intended to grow over time as new clipart is added (drop the PNG into
``sample_assets/clipart/`` and append a row to INDEX.json with caption and
tags).

The blueprint stage of the pipeline must browse this catalogue when
populating ``manipulatives_index`` for any new unit. Reusing existing
clipart keeps the visual style consistent across the marketplace and
avoids generating ad-hoc art the pipeline can't actually render.

Tags are open-vocabulary; the seed tags are the slide categories from
Michelle's deck (people, animals, vehicles, plants, planets, sports,
food, places, random). New units may add their own.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

CLIPART_DIR = Path(__file__).resolve().parent.parent / "sample_assets" / "clipart"
INDEX_PATH = CLIPART_DIR / "INDEX.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    if not INDEX_PATH.exists():
        return {"meta": {}, "images": []}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def list_all() -> list[dict]:
    """Return every clipart row. Each row has at minimum: filename, path,
    size_in, tags, caption, context_hints."""
    return list(_load().get("images", []))


def list_by_tag(tag: str) -> list[dict]:
    """Return all clipart rows that carry ``tag`` (case-insensitive)."""
    t = tag.lower().strip()
    return [r for r in list_all() if t in [x.lower() for x in r.get("tags", [])]]


def available_tags() -> list[str]:
    """Sorted list of every tag present in the catalogue, with counts."""
    from collections import Counter
    c = Counter(t.lower() for r in list_all() for t in r.get("tags", []))
    return sorted(c.keys(), key=lambda t: (-c[t], t))


def get(filename: str) -> dict | None:
    """Look up a clipart row by filename."""
    for r in list_all():
        if r.get("filename") == filename:
            return r
    return None


def absolute_path(filename: str) -> Path | None:
    """Filesystem path for a clipart image, suitable for compose pipelines."""
    r = get(filename)
    if not r:
        return None
    return (Path(__file__).resolve().parent.parent / r["path"]).resolve()


def summary() -> str:
    """Human-readable one-screen catalogue summary for new sessions."""
    rows = list_all()
    if not rows:
        return f"clipart catalogue: empty ({INDEX_PATH} missing or has no images)"
    from collections import Counter
    tag_counts = Counter(t for r in rows for t in r.get("tags", []))
    captioned = sum(1 for r in rows if r.get("caption"))
    lines = [
        f"clipart catalogue: {len(rows)} images   "
        f"({captioned} captioned, {len(rows)-captioned} unlabelled)",
        f"  source: {_load().get('meta',{}).get('source_deck','?')}",
        "  tags (count):",
    ]
    for t, c in tag_counts.most_common():
        lines.append(f"    {t:<14} {c}")
    return "\n".join(lines)


# ── LRU rotation ──────────────────────────────────────────────────────────
#
# Goal: when a new unit picks clipart, prefer images that have NEVER been
# used over images that have been used many times, and among ever-used
# images prefer the ones that haven't been touched for the longest time.
# This keeps the marketplace visually fresh and exhausts the catalogue
# before recycling.
#
# Source of truth: every blueprint's ``manipulatives_index[*].clipart_files``
# under ``generated_units/``. Scanning is cheap at current scale (~3-50
# units) and avoids drift from a separately-maintained usage cache.

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def usage_stats() -> dict[str, dict]:
    """Scan generated_units/ and report clipart-usage signals per filename.

    Returns ``{filename: {use_count, units, last_used_at}}`` where
    ``use_count`` is the number of distinct units that referenced the
    image, ``units`` is the list of unit_ids, and ``last_used_at`` is the
    most recent unit's ``manifest.created_at`` (ISO8601 string; "" if
    we couldn't read a timestamp).

    Filenames that have never been referenced are NOT in the returned
    dict — callers should treat absence as ``use_count=0``.
    """
    import json
    stats: dict[str, dict] = {}
    units_dir = _PROJECT_ROOT / "generated_units"
    if not units_dir.exists():
        return stats
    for unit_dir in sorted(units_dir.glob("batch_*/*/")):
        bp_path = unit_dir / "0_blueprint.json"
        if not bp_path.exists():
            continue
        try:
            bp = json.loads(bp_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        manifest_path = unit_dir / "manifest.json"
        unit_created = ""
        if manifest_path.exists():
            try:
                m = json.loads(manifest_path.read_text(encoding="utf-8"))
                unit_created = m.get("created_at", "") or ""
            except Exception:
                pass
        unit_id = bp.get("unit_id", unit_dir.name)
        for manip in bp.get("manipulatives_index", []) or []:
            for cf in manip.get("clipart_files", []) or []:
                row = stats.setdefault(cf, {
                    "use_count": 0, "units": [], "last_used_at": "",
                })
                if unit_id not in row["units"]:
                    row["units"].append(unit_id)
                    row["use_count"] += 1
                if unit_created and unit_created > row["last_used_at"]:
                    row["last_used_at"] = unit_created
    return stats


def suggest_for_unit(tags: list[str] | None = None, n: int = 5,
                     exclude: list[str] | None = None,
                     prefer_uncaptioned: bool = False) -> list[dict]:
    """Suggest ``n`` clipart rows for a new unit, biased to unused images.

    Selection rule (applied in order):
      1. **Tag filter** — if ``tags`` is non-empty, keep only rows whose
         ``tags`` overlap with the requested tags (case-insensitive).
      2. **Exclude filter** — drop any filename in ``exclude`` (e.g.
         already chosen for this same unit).
      3. **LRU sort** — ``(use_count ASC, last_used_at ASC, filename)``.
         Result: never-used images come first; among ever-used, oldest-
         touched first; alphabetical tie-break for determinism.
      4. **Take top n.**

    Set ``prefer_uncaptioned=True`` to lift uncaptioned images up the
    queue (useful for dogfooding the catalogue: pick + caption-as-you-go).
    """
    rows = list_all()
    if tags:
        wanted = {t.lower().strip() for t in tags if t.strip()}
        rows = [
            r for r in rows
            if any(t.lower() in wanted for t in r.get("tags", []))
        ]
    if exclude:
        ex = set(exclude)
        rows = [r for r in rows if r.get("filename") not in ex]

    stats = usage_stats()

    def rank_key(r):
        u = stats.get(r["filename"], {})
        use_count = u.get("use_count", 0)
        last_used = u.get("last_used_at", "") or ""
        # Push uncaptioned to the front by negating the boolean (False<True
        # so we want the False bucket first iff prefer_uncaptioned).
        captioned_penalty = 0
        if prefer_uncaptioned and r.get("caption"):
            captioned_penalty = 1
        return (use_count, captioned_penalty, last_used, r["filename"])

    rows.sort(key=rank_key)
    return rows[:n]


def report_usage() -> str:
    """Printable usage summary; goes in the session-start status check."""
    stats = usage_stats()
    rows = list_all()
    used_set = set(stats.keys())
    used_count = sum(1 for r in rows if r["filename"] in used_set)
    unused_count = len(rows) - used_count
    lines = [
        f"clipart usage: {used_count}/{len(rows)} ever used "
        f"({unused_count} fresh in queue)",
    ]
    if used_set:
        ranked = sorted(stats.items(), key=lambda kv: -kv[1]["use_count"])
        lines.append("  most-referenced:")
        for fn, u in ranked[:5]:
            tail = f" (latest: {u['units'][-1]})" if u["units"] else ""
            lines.append(f"    {u['use_count']}× {fn}{tail}")
    if unused_count:
        # Show a few never-used candidates the next unit could grab
        next_up = suggest_for_unit(n=5)
        lines.append("  next-up (LRU):")
        for r in next_up:
            tags = ",".join(r.get("tags", [])) or "(no tags)"
            lines.append(f"    {r['filename']}  [{tags}]")
    return "\n".join(lines)
