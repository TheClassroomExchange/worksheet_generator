"""
Composition module — combines SVG primitives into final worksheet/manipulative images.

Strategy:
  - Render each SVG primitive to a PIL Image at a target size via `rsvg-convert`.
  - Composite them onto a transparent canvas using PIL.
  - Save the result to a PNG file in `composed/` for the Slides pipeline to upload.

Primitives live in `sample_assets/`. Composed outputs go in
`generated_units/<batch>/<unit>/composed/`.

The main entry points are:
  - render_svg(svg_path, width, height) -> PIL.Image
  - compose_parade_strip(cells, ...) -> PIL.Image
  - compose_animal_key(animals, ...) -> PIL.Image
  - compose_for_unit(unit_dir) -> dict[image_id -> Path]
      Walks every image_placeholder in the unit's stage JSONs and produces a
      composed PNG for each. Returns a manifest mapping image IDs to paths.
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "sample_assets"


# ── Primitive rendering ───────────────────────────────────────────────────

def render_svg(svg_path: Path, width: int = None, height: int = None) -> Image.Image:
    """Render an SVG file to a PIL Image using rsvg-convert."""
    cmd = ["rsvg-convert", str(svg_path), "-f", "png"]
    if width:
        cmd += ["-w", str(width)]
    if height:
        cmd += ["-h", str(height)]
    result = subprocess.run(cmd, capture_output=True, check=True)
    from io import BytesIO
    return Image.open(BytesIO(result.stdout)).convert("RGBA")


def asset(name: str) -> Path:
    """Resolve a primitive name to its SVG path."""
    p = ASSETS_DIR / f"{name}.svg"
    if not p.exists():
        raise FileNotFoundError(f"Asset not found: {p}")
    return p


# ── Parade strip composition ──────────────────────────────────────────────

# Standard cell dimensions. Must match the parade_strip.svg layout.
CELL_SIZE = 90
CELL_GAP = 5
CELL_TOP = 10
STRIP_HEIGHT = 130

ANIMAL_NAMES = {"bea", "finn", "bibi", "moss"}


def compose_parade_strip(
    cells: list,
    cell_count: int = None,
    show_missing_as_question: bool = True,
    box_indices: list[int] = None,  # which cells to draw a thick box around (e.g., for "core" highlight)
    extending_arrows: bool = False,  # add "before the start" / "after the end" arrows
) -> Image.Image:
    """
    Compose a parade strip with characters in cells.

    Args:
      cells: list of strings, one per cell. Each is either:
             - "bea" / "finn" / "bibi" / "moss"  (animal name)
             - "?"  (missing — render M4 missing-card icon)
             - None (empty cell with dashed outline)
      cell_count: total cells to draw (defaults to len(cells)).
      box_indices: if given, draw a thicker rectangle around these cells
                   (used to indicate "the core is here").
      extending_arrows: add small directional arrow labels outside cells 0
                        and N-1 ("before the start" / "after the end").

    Returns a PIL RGBA Image.
    """
    if cell_count is None:
        cell_count = len(cells)
    while len(cells) < cell_count:
        cells.append(None)

    width = CELL_GAP + cell_count * (CELL_SIZE + CELL_GAP)
    canvas = Image.new("RGBA", (width, STRIP_HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # Render the base strip layout (cells + footprints) — but we want
    # different cell styling depending on filled vs empty vs missing.
    # So we build cell-by-cell instead of starting from parade_strip.svg.

    for i in range(cell_count):
        x = CELL_GAP + i * (CELL_SIZE + CELL_GAP)
        cell_box = (x, CELL_TOP, x + CELL_SIZE, CELL_TOP + CELL_SIZE)
        content = cells[i] if i < len(cells) else None

        # Cell background + border
        if content is None:
            # Empty cell — dashed outline
            _draw_dashed_rect(draw, cell_box, dash_len=6, gap=4, width=2)
        else:
            # Solid cell
            draw.rectangle(cell_box, fill="white", outline="black", width=2)

        # Cell content
        if content == "?":
            # Render the missing-card SVG into this cell
            mc = render_svg(asset("missing_card"), width=CELL_SIZE - 8, height=CELL_SIZE - 8)
            canvas.paste(mc, (x + 4, CELL_TOP + 4), mc)
        elif content in ANIMAL_NAMES:
            ani = render_svg(asset(content), width=CELL_SIZE - 8, height=int((CELL_SIZE - 8) * 1.1))
            canvas.paste(ani, (x + 4, CELL_TOP + 2), ani)

        # Box highlight (thicker border)
        if box_indices and i in box_indices:
            draw.rectangle(cell_box, outline="black", width=4)

    # Footprints below cells
    fp_y = CELL_TOP + CELL_SIZE + 8
    for i in range(cell_count):
        x = CELL_GAP + i * (CELL_SIZE + CELL_GAP) + CELL_SIZE // 2
        for offset in (-15, 0, 15):
            cx = x + offset
            cy = fp_y + (3 if offset == 0 else 0)
            draw.ellipse((cx - 6, cy - 4, cx + 6, cy + 4), fill=(136, 136, 136, 140))

    # Extending arrows
    if extending_arrows:
        # Left arrow
        draw.line((CELL_GAP - 2, CELL_TOP + CELL_SIZE // 2,
                   CELL_GAP - 2 - 8, CELL_TOP + CELL_SIZE // 2), fill="black", width=2)
        # No room outside the canvas — caller should pad if they want labels visible.

    return canvas


def _draw_dashed_rect(draw, box, dash_len, gap, width):
    x0, y0, x1, y1 = box
    # Top
    _draw_dashed_line(draw, (x0, y0), (x1, y0), dash_len, gap, width)
    # Bottom
    _draw_dashed_line(draw, (x0, y1), (x1, y1), dash_len, gap, width)
    # Left
    _draw_dashed_line(draw, (x0, y0), (x0, y1), dash_len, gap, width)
    # Right
    _draw_dashed_line(draw, (x1, y0), (x1, y1), dash_len, gap, width)


def _draw_dashed_line(draw, p0, p1, dash_len, gap, width):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0
    while pos < length:
        seg_end = min(pos + dash_len, length)
        sx, sy = x0 + ux * pos, y0 + uy * pos
        ex, ey = x0 + ux * seg_end, y0 + uy * seg_end
        draw.line((sx, sy, ex, ey), fill="black", width=width)
        pos += dash_len + gap


# ── Animal key composition ────────────────────────────────────────────────

def compose_animal_key(animals: list[str], icon_size: int = 80, label_height: int = 20) -> Image.Image:
    """A horizontal row of animals with names labelled below — used as a worksheet legend."""
    n = len(animals)
    cell_w = icon_size + 16
    width = n * cell_w + 8
    height = icon_size + label_height + 16
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    for i, ani in enumerate(animals):
        x = 8 + i * cell_w
        img = render_svg(asset(ani), width=icon_size, height=int(icon_size * 1.1))
        canvas.paste(img, (x, 4), img)
    # Names
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    for i, ani in enumerate(animals):
        x = 8 + i * cell_w + cell_w // 2
        y = icon_size + 4
        draw.text((x, y), ani.capitalize(), fill="black", font=font, anchor="mt")
    return canvas


# ── Icon-row composition (for sound/body icons) ───────────────────────────

def compose_icon_row(icons: list[str], icon_size: int = 80, label_height: int = 24) -> Image.Image:
    """A horizontal row of icon cards (like clap, stomp, tall, small) for a worksheet legend."""
    n = len(icons)
    cell_w = icon_size + 16
    width = n * cell_w + 8
    height = icon_size + label_height + 8
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    for i, ic in enumerate(icons):
        x = 8 + i * cell_w
        img = render_svg(asset(f"icon_{ic}"), width=icon_size, height=icon_size)
        canvas.paste(img, (x, 4), img)
    return canvas


# ── Per-image-id composition for Unit 1 (Pattern Parade) ──────────────────

# Map every WSxx_/M_/CHAR_/FORM_/REF_/AS_ image_id from Unit 1's JSONs to a
# specific composition recipe. Centralised here so we have a single source of
# truth that's easy to audit against the JSON specs.

# Per-theme dispatcher gating: each composer only fires when the unit_id
# substring-matches at least one of its theme keywords. Prevents
# cross-theme collisions on shared image IDs like M10_POSTER (claimed by
# data_detectives) being rendered for an algebra-balance unit. When unit_id
# is None (legacy callers), gating is skipped — preserves existing behaviour.
_COMPOSER_THEMES: dict[str, tuple[str, ...]] = {
    "phonics":         ("language", "phonics", "cvc_decoders"),  # Language
    "data_detectives": ("data_detectives",),
    "real_life":       ("real_life_modelling", "sugar_bush", "town_planner",
                        "community_helpers"),
    "algebra":         ("balance_stories", "loop_the_loop", "if_then_detectives",
                        "balanced_equations", "bug_busters", "whats_missing"),
    "probability":     ("likelihood", "what_could_happen", "likely_unlikely",
                        "data_likelihood"),
    "financial":       ("classroom_market", "tap_to_pay", "plan_your_party",
                        "coin_counters"),
    "measurement":     ("how_long", "how_heavy", "fencing", "bigger_smaller",
                        "measurement"),
    "spatial_coding":  ("mapping", "mirror_mirror", "shape_safari",
                        "map_it_move", "coding", "little_programmers",
                        "spatial"),
    "number":          ("adding_machine", "number_friends", "groups_of",
                        "place_value", "fraction_street", "times_table",
                        "counting_crew", "number_"),
}


def _theme_matches(unit_id: str | None, theme: str) -> bool:
    """Return True if the unit_id substring-matches any keyword for this
    composer theme. None unit_id allows all (legacy)."""
    if unit_id is None:
        return True
    keys = _COMPOSER_THEMES.get(theme, ())
    return any(k in unit_id for k in keys)


def compose_pattern_parade_image(image_id: str, output_path: Path,
                                 grade: str | None = None,
                                 subject: str | None = None,
                                 unit_id: str | None = None) -> Path:
    """Compose the named image and write it as PNG. Returns the output path.

    Some image IDs (e.g., WS01_P2_PARADE) are reused across grades with
    different content per grade. When `grade` is provided, grade-specific
    overrides are tried FIRST before the generic dispatcher. This lets G2
    show stacked-animal growing parades while K still shows missing-element
    repeating parades — same image_id, different recipe per grade.

    ``subject`` (e.g. "Mathematics" or "Language") gates the phonics
    dispatcher: phonics composers share several image_ids with math
    composers (WS01_P2_BOXES, AS_*_TRACKER, …) so we only let phonics
    claim them when the unit IS a Language unit.

    ``unit_id`` (e.g. "g1_algebra_balance_stories") gates per-theme
    dispatchers: each composer only fires when the unit_id substring-
    matches at least one of its theme keywords. Prevents cross-theme
    collisions on shared image IDs like M10_POSTER. None preserves legacy
    behaviour.
    """
    image: Image.Image | None = None

    # ── Per-theme dispatchers (try first; fall through if not handled) ──
    # Phonics composers share several IDs with math composers
    # (WS01_P2_BOXES, AS_DIAG_TRACKER, AS_FORM_TRACKER_L2..L4, WS02_P2_BUILD).
    # Gate strictly on subject AND unit_id so a math unit never resolves to
    # phonics' Sound Boxes recipe.
    if (image is None
        and (subject is None or subject == "Language")
        and _theme_matches(unit_id, "phonics")):
        try:
            from . import composers_phonics as _ph
            image = _ph.compose_phonics_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! phonics dispatcher errored on {image_id}: {e}")

    # Data Detectives (k/g1/g2/g3): tally, pictograph, sorting, anchor charts.
    if image is None and _theme_matches(unit_id, "data_detectives"):
        try:
            from . import composers_data_detectives as _dd
            image = _dd.compose_data_detectives_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! data_detectives dispatcher errored on {image_id}: {e}")

    # Real-Life Modelling (g1 sugar bush / g2 town / g3 community)
    if image is None and _theme_matches(unit_id, "real_life"):
        try:
            from . import composers_real_life as _rl
            image = _rl.compose_real_life_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! real_life dispatcher errored on {image_id}: {e}")

    # Algebra units: whats_missing, if_then_detectives, balanced_equations,
    # bug_busters, balance_stories, loop_the_loop
    if image is None and _theme_matches(unit_id, "algebra"):
        try:
            from . import composers_algebra as _alg
            image = _alg.compose_algebra_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! algebra dispatcher errored on {image_id}: {e}")

    # Probability units (g1 likelihood, g2 what could happen, g3 likely-unlikely)
    if image is None and _theme_matches(unit_id, "probability"):
        try:
            from . import composers_probability as _pr
            image = _pr.compose_probability_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! probability dispatcher errored on {image_id}: {e}")

    # Financial units (g1 classroom_market, g2 tap_to_pay, g3 plan_your_party)
    if image is None and _theme_matches(unit_id, "financial"):
        try:
            from . import composers_financial as _fin
            image = _fin.compose_financial_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! financial dispatcher errored on {image_id}: {e}")

    # Measurement units (k bigger_smaller, g1 how_long, g2 how_heavy, g3 fencing)
    if image is None and _theme_matches(unit_id, "measurement"):
        try:
            from . import composers_measurement as _ms
            image = _ms.compose_measurement_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! measurement dispatcher errored on {image_id}: {e}")

    # Spatial + coding units (k shape_safari, g1 mapping, g2 mirror, g3 map_it_move,
    # k_coding_little_programmers)
    if image is None and _theme_matches(unit_id, "spatial_coding"):
        try:
            from . import composers_spatial_coding as _sc
            image = _sc.compose_spatial_coding_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! spatial_coding dispatcher errored on {image_id}: {e}")

    # Number-sense units (g1-g3 friends, adding, groups, place value, fractions, times)
    if image is None and _theme_matches(unit_id, "number"):
        try:
            from . import composers_number as _nu
            image = _nu.compose_number_image(image_id, grade=grade, unit_id=unit_id)
        except Exception as e:
            print(f"  ! number dispatcher errored on {image_id}: {e}")

    # Pattern Parade single-asset cards: M1_<ANIMAL>_CARD, M3_<ACTION>,
    # M6_WORD_<WORD>. Each renders an existing SVG primitive on a hero canvas.
    if image is None:
        single_asset_map = {
            "M1_BEA_CARD":      "bea",
            "M1_FINN_CARD":     "finn",
            "M1_BIBI_CARD":     "bibi",
            "M1_MOSS_CARD":     "moss",
            "M3_CLAP":          "icon_clap",
            "M3_STOMP":         "icon_stomp",
            "M3_HUM":           "icon_hum",
            "M3_TAP":           "icon_tap",
            "M3_WAVE":          "icon_wave",
            "M3_JUMP":          "icon_jump",
            "M3_FREEZE":        "icon_freeze",
            "M3_SPIN":          "icon_spin",
            "M6_WORD_PATTERN":  "word_pattern",
            "M6_WORD_CORE":     "word_core",
            "M6_WORD_EXTEND":   "word_extend",
            "M6_WORD_MISSING":  "word_missing",
        }
        if image_id in single_asset_map:
            try:
                svg = ASSETS_DIR / f"{single_asset_map[image_id]}.svg"
                if svg.exists():
                    rendered = render_svg(svg, width=520, height=520).convert("RGBA")
                    canvas = Image.new("RGB", (1024, 768), "white")
                    px = (1024 - rendered.width) // 2
                    py = (768 - rendered.height) // 2
                    canvas.paste(rendered, (px, py), rendered)
                    image = canvas
            except Exception as e:
                print(f"  ! single-asset dispatcher errored on {image_id}: {e}")

    # Pattern Parade themed worksheet strips: WS01_P3_HOCKEY/MELT/PAPERFOLD
    # use the standard parade-strip composer with thematic placeholders so the
    # slide shows real content matching the page topic.
    if image is None and image_id in ("WS01_P3_HOCKEY", "WS01_P3_MELT",
                                       "WS01_P3_PAPERFOLD", "WS01_P1_STRIP_D",
                                       "WS03_P1_TOP", "WS03_P3_RULES"):
        # 6 empty parade cells — themed by id, pattern is for student to fill.
        image = compose_parade_strip([None] * 6)

    # Pattern Parade formative parades
    if image is None and image_id in ("FORM_Q1_PARADE_A", "FORM_Q1_PARADE_B",
                                       "FORM_Q1_PARADE_C"):
        # Each variant shows a small AB-pattern parade
        if image_id == "FORM_Q1_PARADE_A":
            image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea"])
        elif image_id == "FORM_Q1_PARADE_B":
            image = compose_parade_strip(["bea", "finn", "finn", "bea", "finn", "finn"])
        else:
            image = compose_parade_strip(["bea", "bea", "finn", "bea", "bea", "finn"])

    # Pattern Parade animal-key images (used as legend on multiple worksheets)
    if image is None and image_id in ("WS01_P2_KEY", "WS05_P2_KEY", "WS05_P3_KEY"):
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])

    # Counting Crew dot/buddy reference cards (M3_DOTS_*, M3_BUDDY_REFERENCE).
    if image is None and image_id.startswith("M3_") and ("DOTS_" in image_id or
                                                          image_id == "M3_BUDDY_REFERENCE"):
        try:
            asset_name = image_id.lower().replace("m3_", "icon_")
            svg = ASSETS_DIR / f"{asset_name}.svg"
            if svg.exists():
                # Render at 480px square — fits the manipulative slide hero box.
                rendered = render_svg(svg, width=480, height=480).convert("RGBA")
                canvas = Image.new("RGB", (1024, 768), "white")
                paste_x = (1024 - rendered.width) // 2
                paste_y = (768 - rendered.height) // 2
                canvas.paste(rendered, (paste_x, paste_y), rendered)
                image = canvas
        except Exception as e:
            print(f"  ! dot-card dispatcher errored on {image_id}: {e}")

    # ── Grade-specific overrides (try first; fall through if no match) ──
    if image is None and grade and image_id is not None:
        image = _compose_grade_override(image_id, grade)
        if image is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path, "PNG")
            return output_path

    if image is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "PNG")
        compose_pattern_parade_image._last_was_placeholder = False  # type: ignore[attr-defined]
        return output_path

    # ── Worksheet 1: Coco's First Parade (Kindergarten defaults) ──
    if image_id == "WS01_P1_PARADE":
        image = compose_parade_strip(["bea", "finn", "bea", "finn", None])
    elif image_id == "WS01_P1_KEY":
        image = compose_animal_key(["bea", "finn"])
    elif image_id == "WS01_P2_PARADE":
        image = compose_parade_strip(["bea", "finn", "bea", None, "bea", "finn", None])
    elif image_id == "WS01_P3_PARADE":
        image = compose_parade_strip([None] * 5)
    elif image_id == "WS01_P3_KEY":
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])

    # ── Worksheet 2: Find the Beat ──
    elif image_id == "WS02_P1_PARADE_A":
        image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea", "finn"])
    elif image_id == "WS02_P1_PARADE_B":
        image = compose_parade_strip(["bea", "finn", "bibi", "bea", "finn", "bibi"])
    elif image_id == "WS02_P1_PARADE_C":
        image = compose_parade_strip(["bea", "finn", "finn", "bea", "finn", "finn"])
    elif image_id == "WS02_P2_PARADE":
        # AB pattern with first 2 cells boxed
        image = compose_parade_strip(["bea", "finn", None, None, None, None, None],
                                     box_indices=[0, 1])
    elif image_id == "WS02_P3_PARADE":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS02_P3_LOOP_REMINDER":
        image = render_svg(asset("core_loop"), width=120)
    elif image_id == "WS02_P3_KEY":
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])

    # ── Worksheet 3: Same Beat, Three Ways ──
    elif image_id == "WS03_P1_ANIMAL":
        image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea", "finn"])
    elif image_id == "WS03_P1_SOUND":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS03_P1_BODY":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS03_P1_REF":
        image = compose_icon_row(["clap", "stomp", "tall", "small"])
    elif image_id == "WS03_P2_ANIMAL":
        image = compose_parade_strip(["bea", "finn", "finn", "bea", "finn", "finn"])
    elif image_id == "WS03_P2_SOUND":
        # We don't have a "sounds in cells" composition; render placeholder labelled cells
        image = compose_parade_strip([None] * 6)  # placeholder
    elif image_id == "WS03_P2_BODY":
        image = compose_parade_strip([None] * 6)  # placeholder
    elif image_id == "WS03_P3_ANIMAL":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS03_P3_SOUND":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS03_P3_BODY":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS03_P3_REF":
        image = compose_icon_row(["clap", "stomp", "hum", "tap", "tall", "small", "jump", "freeze"], icon_size=70)

    # ── Worksheet 4: Help Coco Fix It ──
    elif image_id == "WS04_P1_ROW_A":
        image = compose_parade_strip(["bea", "finn", "?", "finn", "bea", "finn"])
    elif image_id == "WS04_P1_ROW_B":
        image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea", "?"])
    elif image_id == "WS04_P1_ROW_C":
        image = compose_parade_strip(["?", "finn", "bea", "finn", "bea", "finn"])
    elif image_id == "WS04_P2_PARADE":
        image = compose_parade_strip([None, None, "bea", "finn", "bea", "finn", None, None])
    elif image_id == "WS04_P3_PARADE":
        image = compose_parade_strip([None] * 6)
    elif image_id == "WS04_P3_ANSWER_BOX":
        image = _compose_answer_box()
    elif image_id == "WS04_P3_KEY":
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])

    # ── Worksheet 5: Lead Your Own Parade ──
    elif image_id == "WS05_P1_BOX":
        image = _compose_my_core_box()
    elif image_id == "WS05_P1_LOOP":
        image = render_svg(asset("core_loop"), width=120)
    elif image_id == "WS05_P1_KEY":
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])
    elif image_id == "WS05_P2_PARADE":
        image = compose_parade_strip([None] * 8)
    elif image_id == "WS05_P3_PARADE":
        image = compose_parade_strip([None] * 8)
    elif image_id == "WS05_P3_CAPTION":
        image = _compose_caption_box("My core was the same. I just used ___ instead of animals.")
    elif image_id == "WS05_P3_REF":
        image = compose_icon_row(["clap", "stomp", "hum", "tap", "tall", "small", "jump", "freeze"], icon_size=70)

    # ── Manipulatives — usually one icon each ──
    elif image_id in {"M1_BEA_CARD", "M1_FINN_CARD", "M1_BIBI_CARD",
                      "M1_MOSS_CARD", "M1_COCO_CARD"}:
        # Pattern Parade family: single animal card. (Restricted to known
        # animal IDs; other narratives' M1_*_CARD fall through to their own
        # composer or the smart fallback.)
        animal = image_id.split("_")[1].lower()
        image = render_svg(asset(animal), width=240)
    elif image_id == "M2_PARADE_STRIP":
        image = render_svg(asset("parade_strip"), width=600)
    elif image_id in {"M3_CLAP", "M3_STOMP", "M3_JUMP", "M3_FREEZE",
                      "M3_HUM", "M3_TAP", "M3_WAVE", "M3_SPIN",
                      "M3_TALL", "M3_SMALL"}:
        # Pattern Parade family: single icon card. (Restricted to known
        # icons; broader M3_* IDs from other narratives fall through to
        # narrative-specific composers or the smart fallback.)
        ic = image_id.split("_", 1)[1].lower()
        image = render_svg(asset(f"icon_{ic}"), width=240)
    elif image_id == "M4_MISSING_CARD":
        image = render_svg(asset("missing_card"), width=160)
    elif image_id == "M5_CORE_LOOP":
        image = render_svg(asset("core_loop"), width=320)
    elif image_id.startswith("M6_WORD_"):
        # M6_WORD_PATTERN, M6_WORD_CORE, etc.
        word = image_id.split("_", 2)[2].lower()
        image = render_svg(asset(f"word_{word}"), width=350)

    # ── Character watermarks / illustrations ──
    elif image_id == "CHAR_COCO_FRONT":
        # Try the kawaii SVG first (sample_assets/characters/COCO.svg).
        # Fall back to the legacy lowercase pattern-parade coco asset only
        # if the kawaii SVG is missing. Added 2026-05-10 — without this
        # check the math g1_spatial_mapping unit was rendering Compass Coco
        # as a phonics-themed clipart pair instead of the kawaii cat.
        kawaii = _character_svg_path("COCO")
        if kawaii is not None:
            image = _compose_custom_character_card(kawaii, "Compass Coco the Cat")
        else:
            image = render_svg(asset("coco"), width=400)

    # ── Formative & reflection ──
    elif image_id.startswith("FORM_Q1_PARADE_"):
        # FORM_Q1_PARADE_A, _B, _C
        suffix = image_id[-1]
        if suffix == "A":
            image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea", "finn"])
        elif suffix == "B":
            # Sound version — placeholder strip (sound-in-cells not yet supported)
            image = _compose_sound_strip(["clap", "stomp", "clap", "stomp", "clap", "stomp"])
        elif suffix == "C":
            image = compose_parade_strip(["bea", "finn", "finn", "bea", "finn", "finn"])
    elif image_id == "FORM_Q2_TOP":
        image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea", "finn"])
    elif image_id == "FORM_Q2_BLANK":
        image = compose_parade_strip([None] * 6)
    elif image_id == "FORM_Q2_KEY":
        image = compose_icon_row(["clap", "stomp", "tall", "small"])
    elif image_id == "FORM_Q3_FACES":
        image = _compose_face_rating()
    elif image_id == "REF_STARS":
        image = _compose_star_rating()
    elif image_id == "REF_YN_TABLE":
        image = _compose_yn_table([
            "I made my own parade.",
            "I found the core.",
            "I showed my core another way.",
            "I fixed a missing animal.",
        ])
    elif image_id in ("REF_FAV_BOX", "REF_TRICKY_BOX", "REF_NEXT_BOX"):
        prompts = {
            "REF_FAV_BOX": "My favourite part of the Pattern Parade was...",
            "REF_TRICKY_BOX": "The trickiest part for me was...",
            "REF_NEXT_BOX": "Next time, I want to try...",
        }
        image = _compose_reflection_box(prompts[image_id])

    # ── Grade 2 Pattern Parade worksheets (added 2026-04-29) ──
    # WS01: three-type sorter
    elif image_id == "WS01_P1_STRIP_A":
        # 5-cell repeating Bea-Finn-Bea-Finn-Bea
        image = compose_parade_strip(["bea", "finn", "bea", "finn", "bea"])
    elif image_id == "WS01_P1_STRIP_B":
        # 4-cell growing 1, 2, 3, 4 stacked Beas
        image = compose_growing_strip("bea", [1, 2, 3, 4])
    elif image_id == "WS01_P1_STRIP_C":
        # 4-cell shrinking 4, 3, 2, 1 Finns
        image = compose_growing_strip("finn", [4, 3, 2, 1])
    elif image_id == "WS01_P1_LABELS":
        image = compose_label_stack(["REPEATING", "GROWING", "SHRINKING"])
    elif image_id == "WS01_P2_PARADE":
        # Growing 2, 4, 6, 8 stacked Beas (rule +2)
        image = compose_growing_strip("bea", [2, 4, 6, 8])
    elif image_id == "WS01_P3_CALENDAR":
        image = compose_real_life_thumbnail("calendar")
    elif image_id == "WS01_P3_BRICKS":
        image = compose_real_life_thumbnail("bricks")
    elif image_id == "WS01_P3_HOPSCOTCH":
        image = compose_real_life_thumbnail("hopscotch")
    elif image_id == "WS01_P3_COOKIE":
        image = compose_real_life_thumbnail("cookie")

    # WS02: name the jump
    elif image_id == "WS02_P1_STRIP_A":
        # 1, 3, 5, 7 — +2 growing
        image = compose_growing_strip("bea", [1, 3, 5, 7])
    elif image_id == "WS02_P1_STRIP_B":
        # 10, 8, 6, 4 — -2 shrinking
        image = compose_growing_strip("bea", [10, 8, 6, 4])
    elif image_id == "WS02_P1_STRIP_C":
        # 1, 2, 3, 4 — +1 growing
        image = compose_growing_strip("bea", [1, 2, 3, 4])
    elif image_id == "WS02_P1_STRIP_D":
        # 8, 5, 2 with empty 4th cell
        image = compose_growing_strip("bea", [8, 5, 2, 0])
    elif image_id == "WS02_P2_KEY":
        # Single Bea reference icon — render a small parade strip with one cell
        image = render_svg(asset("bea"), width=120)

    # WS03: three faces of a rule (already partly handled above; add table & numbers)
    elif image_id == "WS03_P1_NUMBERS":
        image = compose_number_row([""] * 4)
    elif image_id == "WS03_P1_TABLE":
        # Headers TERM/VALUE, term column pre-filled 1-4, value blank
        image = compose_table_of_values(
            [("1", ""), ("2", ""), ("3", ""), ("4", "")]
        )
    elif image_id == "WS03_P2_TABLE":
        # Term: 1-4, Value: 5, 8, 11, blank
        image = compose_table_of_values(
            [("1", "5"), ("2", "8"), ("3", "11"), ("4", "")]
        )
    elif image_id == "WS03_P3_NUMBERS":
        image = compose_number_row([""] * 4)
    elif image_id == "WS03_P3_TABLE":
        image = compose_table_of_values(
            [("1", ""), ("2", ""), ("3", ""), ("4", "")]
        )

    # WS04: Detective Pro
    elif image_id == "WS04_P1_STRIP_A":
        # repeating 6-cell Bea-Finn-Finn-?-Finn-Finn (rule ABB)
        image = compose_parade_strip(["bea", "finn", "finn", "?", "finn", "finn"])
    elif image_id == "WS04_P1_STRIP_B":
        # growing 4, 8, ?, 16 (rule +4)
        image = compose_growing_strip("bea", [4, 8, 0, 16])  # 0 marks gap
    elif image_id == "WS04_P1_STRIP_C":
        # shrinking ?, 9, 6, 3 (rule -3)
        image = compose_growing_strip("bea", [0, 9, 6, 3])
    elif image_id == "WS04_P2_TABLE":
        # term 1-5, value 5, 8, 11, blank, blank
        image = compose_table_of_values(
            [("1", "5"), ("2", "8"), ("3", "11"), ("4", ""), ("5", "")]
        )
    elif image_id == "WS04_P3_TABLE":
        # term 1-8, only term 5 = 30 pre-filled, highlighted
        image = compose_table_of_values(
            [(str(i), "30" if i == 5 else "") for i in range(1, 9)],
            highlight_row=5,
        )

    # WS05: summative — Lead the Number Parade to 100
    elif image_id == "WS05_P1_HEADER":
        # Composite header: leave a labelled stub for now (rendering 3 boxes
        # plus an animal legend plus a hundred chart in one composite is
        # heavy; the slide already places these via the layout engine).
        image = _compose_caption_box("My Rule | Pattern Type | My Core or First 2 Terms")
    elif image_id == "WS05_P2_PARADE":
        image = compose_parade_strip([None] * 8)
    elif image_id == "WS05_P2_NUMBERS":
        image = compose_number_row([""] * 8)
    elif image_id == "WS05_P3_TABLE":
        image = compose_table_of_values(
            [(str(i), "") for i in range(1, 9)]
        )
    elif image_id == "WS05_P3_HUNDRED":
        image = compose_hundred_chart(max_value=100)

    # ── Grade 1 worksheet stragglers (added 2026-04-29) ──
    # WS02 G1 image IDs that previously fell through:
    elif image_id == "WS02_P1_RULES":
        # AB / ABB / AAB / ABC label stack for matching
        image = compose_label_stack(["AB", "ABB", "AAB", "ABC"])
    elif image_id == "WS02_P3_RULES":
        # rule-bank reminder card
        image = compose_label_stack(["AB", "ABB", "AAB", "ABC"])
    elif image_id == "WS04_P3_KEY":
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])
    elif image_id in ("WS05_P3_KEY", "WS04_P3_KEY"):
        image = compose_animal_key(["bea", "finn", "bibi", "moss"])

    # ── G2 formative + reflection ──
    elif image_id == "FORM_Q1_STRIP_A":
        # 4-cell repeating Bea-Finn-Bea-Finn (rule AB)
        image = compose_parade_strip(["bea", "finn", "bea", "finn"])
    elif image_id == "FORM_Q1_STRIP_B":
        image = compose_growing_strip("bea", [1, 4, 7, 10])
    elif image_id == "FORM_Q1_STRIP_C":
        image = compose_growing_strip("bea", [12, 9, 6, 3])
    elif image_id == "FORM_Q2_PARADE":
        image = compose_growing_strip("bea", [3, 6, 9, 12])
    elif image_id == "FORM_Q2_TABLE":
        image = compose_table_of_values(
            [("1", ""), ("2", ""), ("3", ""), ("4", "")]
        )

    # ── Assessment suite ──
    elif image_id == "AS_DIAG_TRACKER" or image_id.startswith("AS_FORM_TRACKER_"):
        # Trackers are tables — render natively in Slides; here just stub
        image = _compose_tracker_stub(image_id)
    elif image_id == "AS_RUBRIC":
        # Rubric is a table — render natively in Slides; stub here
        image = _compose_rubric_stub()
    elif image_id == "AS_CERT_BORDER":
        image = render_svg(asset("certificate_border"), width=850)
    elif image_id == "AS_CERT_COCO":
        image = render_svg(asset("coco"), width=180)

    # ── Counting Crew narrative composers (added 2026-05-03) ──
    # These dispatch entries call the generic procedural composers in
    # pipeline/template_composers.py to fill in hero artwork for the K
    # Number Counting Crew unit's 29 image_ids. The composers are
    # narrative-agnostic — future units (Coin Counters, Number Friends,
    # etc.) can reuse them by adding a similar dispatch block, or by
    # parameterising the same recipes through the blueprint stage.
    if image is None:
        from . import template_composers as TC
        # Character puppets (chef pair sticker for Mae/Theo, dog for Buddy)
        if image_id == "CHAR_MAE_FRONT":
            svg = _character_svg_path("MAE")
            image = (_compose_custom_character_card(svg, "Mae the Counting Crew Chef")
                     if svg is not None else
                     TC.compose_character_card(
                         "Mae the Chef",
                         "Lead Counter — counts forward and backward",
                         clipart_file="slide01_people_01.png"))
        elif image_id == "CHAR_THEO_FRONT":
            svg = _character_svg_path("THEO")
            image = (_compose_custom_character_card(svg, "Theo the Counting Crew Chef")
                     if svg is not None else
                     TC.compose_character_card(
                         "Theo the Chef",
                         "Cooking Partner — composing/decomposing",
                         clipart_file="slide01_people_01.png"))
        elif image_id == "CHAR_BUDDY_FRONT":
            svg = _character_svg_path("BUDDY")
            image = (_compose_custom_character_card(svg, "Buddy the Puppy")
                     if svg is not None else
                     TC.compose_character_card(
                         "Buddy the Puppy",
                         "Counting Companion — paw prints and bones",
                         clipart_file="slide02_random_04.png"))
        elif image_id == "AS_CERT_CHEFS":
            image = TC.compose_certificate_scene(
                clipart_file="slide01_people_01.png",
                caption="Junior Counting Crew")
        # Manipulative templates
        elif image_id == "M1_CUBE_SORTING_MAT":
            image = TC.compose_sorting_mat(
                zones=["COUNT HERE", "GROUP A", "GROUP B"],
                title="Cube Sorting Mat")
        elif image_id == "M2_TEN_FRAME_GRID":
            image = TC.compose_ten_frame_grid(
                rows=2, cols=5, label="Ten-Frame Mat")
        elif image_id == "M4_MYSTERY_CARD":
            image = TC.compose_number_card("?", label="Mystery Card")
        elif image_id == "M4_NUMERAL_CARD_SAMPLE":
            image = TC.compose_number_card(7, label="Number Card",
                                           with_quantity_dots=True)
        elif image_id == "M5_OBJECT_TRAY":
            image = TC.compose_sorting_mat(
                zones=["APPLES", "BOTTLES", "BOOKS", "BLOCKS", "BEARS"],
                title="Object Sorting Tray")
        elif image_id == "M6_COMPARE_STRIP":
            image = TC.compose_compare_strip(
                left_label="GROUP A", right_label="GROUP B",
                options=["MORE", "LESS", "EQUAL"])
        elif image_id == "M7_PATH_TILE_SAMPLE":
            image = TC.compose_number_path(start=0, end=20,
                                           arrow_label="FORWARD")
        # Worksheet 1 — Where Did You See a Number?
        elif image_id == "WS01_P1_QUADRANT_GRID":
            image = TC.compose_quadrant_grid(
                quadrants=[
                    ("COUNTING", "slide09_food_03.png"),
                    ("LABELS", "slide02_random_03.png"),
                    ("MEASURE", None),
                    ("TIME", None),
                ],
                title="Where Did You See a Number?")
        elif image_id == "WS01_P2_SORT_BOXES":
            image = TC.compose_sorting_boxes(
                boxes=["COUNTING", "LABELS", "MEASURE", "TIME"],
                title="Sort the cards")
        elif image_id == "WS01_P2_SORT_CARDS_CLOCK_PAGE_RULER_BUS":
            image = TC.compose_object_montage(
                objects=[
                    ("Clock", None),
                    ("Page #", "slide02_random_03.png"),
                    ("Ruler", None),
                    ("Bus", "slide07_vehicles_06.png" if (_clipart_path := __import__('pipeline.clipart', fromlist=['absolute_path']).absolute_path('slide07_vehicles_06.png')) and _clipart_path.exists() else None),
                ],
                title="Sort cards")
        elif image_id == "WS01_P3_THEO_SPEECH_BUBBLE":
            image = TC.compose_speech_bubble(
                character_clipart="slide01_people_01.png",
                speech_text="My favourite number today is …",
                character_name="Theo")
        # Worksheet 2 — My Counting Path
        elif image_id == "WS02_P1_PATH_GREEN_ARROW":
            image = TC.compose_number_path(
                start=0, end=10,
                arrow_color=(60, 160, 60), arrow_label="FORWARD")
        elif image_id == "WS02_P2_PATH_RED_ARROW":
            image = TC.compose_number_path(
                start=10, end=0,
                arrow_color=(200, 60, 60), arrow_label="BACKWARD")
        elif image_id == "WS02_P3_MUFFIN_TRAY_BEFORE_AFTER":
            image = TC.compose_object_montage(
                objects=[("BEFORE: 5 muffins", "slide09_food_01.png"),
                         ("AFTER: 2 muffins", "slide09_food_01.png")],
                title="Mae's Muffin Tray")
        # Worksheet 3 — Match, Trace, Write Numbers
        elif image_id == "WS03_P1_NUMBER_QUANTITY_MATCH":
            image = TC.compose_match_grid(
                left_items=[3, 7, 1, 5, 9],
                right_items=[7, 5, 1, 3, 9],
                title="Match number to quantity")
        elif image_id == "WS03_P2_TRACING_GRID_0_10":
            image = TC.compose_tracing_grid(
                numbers=range(0, 11),
                title="Trace and Write 0–10")
        elif image_id == "WS03_P3_TEEN_TENSSTICK_DRAW_BOX":
            image = TC.compose_teen_tens_stick(target=15)
        # Worksheet 4 — Subitize
        elif image_id == "WS04_P1_DICE_PATTERN_DOT_CARDS":
            image = TC.compose_subitize_card_set(
                standard_counts=[1, 2, 3, 4, 5],
                random_counts=[1, 2, 3, 4, 5],
                title="Subitizing dot cards")
        elif image_id == "WS04_P2_SORT_MAT_SUBITIZE_COUNT":
            image = TC.compose_sorting_mat(
                zones=["I see it", "I count it"],
                title="Subitize or count?")
        elif image_id == "WS04_P3_PAW_PRINT_GROUPS_1_TO_8":
            image = TC.compose_paw_print_groups(
                group_sizes=[1, 2, 3, 4, 5, 6, 7, 8],
                title="Buddy's paw-print groups")
        # Worksheet 5 — Build 7 and Compare Plates
        elif image_id == "WS05_P1_TWO_TEN_FRAMES_TARGET_7":
            image = TC.compose_two_ten_frames(
                target=7, decomp_a=(4, 3), decomp_b=(5, 2),
                label="Two ways to build 7")
        elif image_id == "WS05_P2_PLATE_A_VS_PLATE_B_COOKIES":
            image = TC.compose_compare_strip(
                left_label="Plate A: 6 cookies",
                right_label="Plate B: 4 cookies",
                options=["MORE", "LESS", "EQUAL"])
        elif image_id == "WS05_P3_BLANK_PLATE_PAIR_FOR_DRAWING":
            image = TC.compose_blank_pair(
                title="Draw your own plates",
                left_label="Plate A", right_label="Plate B")
        # Formative
        elif image_id == "FORM_Q1_NUMBER_QUANTITY_MATCH":
            image = TC.compose_match_grid(
                left_items=[2, 5, 8, 11, 15, 18],
                right_items=[5, 11, 2, 8, 18, 15],
                title="Match number to quantity")
        elif image_id == "FORM_Q2_FILL_THE_NUMBER_LINE":
            image = TC.compose_number_line_blank(
                start=0, end=20, blanks=[3, 8, 13, 17],
                title="Fill in the missing numbers")
        # ── Coin Counters narrative composers (added 2026-05-04) ──
        # Character puppets — chef pair sticker for Penny + Nick + cert; dog clipart
        # for Quincy as a closest-fit (the library has no piggy-bank specifically).
        elif image_id == "CHAR_PENNY_FRONT":
            svg = _character_svg_path("PENNY")
            # Unit-aware label: g3_number_fraction_street uses Penny as
            # "Penny the Place Value Pal", not the literal 1¢ coin.
            if unit_id and "fraction_street" in unit_id:
                penny_label = "Penny the Place Value Pal"
            else:
                penny_label = "Penny the Penny"
            image = (_compose_custom_character_card(svg, penny_label)
                     if svg is not None else
                     TC.compose_character_card(
                         penny_label,
                         "Lead Counter — estimates and counts",
                         clipart_file="slide01_people_01.png"))
        elif image_id == "CHAR_NICK_FRONT":
            svg = _character_svg_path("NICK")
            image = (_compose_custom_character_card(svg, "Nick the Nickel")
                     if svg is not None else
                     TC.compose_character_card(
                         "Nick the Partner",
                         "Snack-shop partner — adds and subtracts",
                         clipart_file="slide01_people_01.png"))
        elif image_id == "CHAR_QUINCY_FRONT":
            svg = _character_svg_path("QUINCY")
            image = (_compose_custom_character_card(svg, "Quincy the Piggy Bank")
                     if svg is not None else
                     TC.compose_character_card(
                         "Quincy the Piggy Bank",
                         "Counting cheerleader — coins go in",
                         clipart_file="slide02_random_04.png"))
        # Coin cards (M1) — single number cards labelled by value
        elif image_id == "M1_PENNY_CARD":
            image = TC.compose_number_card("1¢", label="PENNY")
        elif image_id == "M1_NICKEL_CARD":
            image = TC.compose_number_card("5¢", label="NICKEL")
        elif image_id == "M1_DIME_CARD":
            image = TC.compose_number_card("10¢", label="DIME")
        elif image_id == "M1_QUARTER_CARD":
            image = TC.compose_number_card("25¢", label="QUARTER")
        # Estimation jar template
        elif image_id == "M2_JAR_TEMPLATE":
            image = TC.compose_blank_pair(
                title="Estimation Jar — fill with pennies",
                left_label="My GUESS", right_label="Actual COUNT")
        # Snap-cubes label
        elif image_id == "M3_CUBE_STORAGE_LABEL":
            image = TC.compose_number_card(
                "30", label="SNAP-CUBES per child", with_quantity_dots=False)
        # Ten-frame mat
        elif image_id == "M4_TEN_FRAME_MAT":
            image = TC.compose_ten_frame_grid(
                rows=2, cols=5, label="Ten-Frame Mat")
        # Snack shop price cards
        elif image_id == "M5_PIZZA_CARD":
            image = TC.compose_object_montage(
                objects=[("PIZZA  25¢", "slide09_food_01.png")],
                title="Pizza")
        elif image_id == "M5_POPCORN_CARD":
            image = TC.compose_object_montage(
                objects=[("POPCORN  10¢", "slide09_food_02.png")],
                title="Popcorn")
        elif image_id == "M5_LOLLIPOP_CARD":
            image = TC.compose_object_montage(
                objects=[("LOLLIPOP  5¢", "slide09_food_04.png")],
                title="Lollipop")
        # Paper plate template (M6)
        elif image_id == "M6_PAPER_PLATE_TEMPLATE":
            image = TC.compose_blank_pair(
                title="Sharing Paper Plates",
                left_label="Plate 1", right_label="Plate 2")
        # Sharing objects sheet (M7)
        elif image_id == "M7_OBJECTS_SHEET":
            image = TC.compose_object_montage(
                objects=[("Cookies", "slide09_food_03.png"),
                         ("Stars", None),
                         ("Grapes", None)],
                title="Sharing Objects Kit")
        # Worksheet 1 — penny jars + coin path
        elif image_id == "WS01_P1_PENNY_JAR_SMALL":
            image = TC.compose_blank_pair(
                title="My Smart Guess (small jar)",
                left_label="GUESS", right_label="COUNT")
        elif image_id == "WS01_P2_PENNY_JAR_LARGE":
            image = TC.compose_blank_pair(
                title="My Smart Guess (bigger jar)",
                left_label="GUESS", right_label="COUNT")
        elif image_id == "WS01_P3_COIN_PATH_STARTING_AT_14":
            image = TC.compose_number_path(
                start=14, end=19,
                arrow_color=(60, 160, 60), arrow_label="COUNT ON")
        # Worksheet 2 — partners of 5 + partner hunt
        elif image_id == "WS02_P1_SIX_TEN_FRAMES":
            image = TC.compose_two_ten_frames(
                target=5, decomp_a=(2, 3), decomp_b=(1, 4),
                label="Partners of 5")
        elif image_id == "WS02_P2_PARTNER_HUNT_SCENES":
            image = TC.compose_compare_strip(
                left_label="Showing", right_label="Hidden",
                options=["3 + 2", "4 + 1", "5 + 0"])
        elif image_id == "WS02_P3_TWO_EMPTY_TEN_FRAMES":
            image = TC.compose_ten_frame_grid(
                rows=2, cols=5, label="Build your partner")
        # Worksheet 3 — story problems
        elif image_id == "WS03_P1_THREE_STORY_SCENES":
            image = TC.compose_object_montage(
                objects=[("Add story", "slide09_food_03.png"),
                         ("Take-away", "slide09_food_01.png"),
                         ("Add story", "slide09_food_02.png")],
                title="Snack-shop stories")
        elif image_id == "WS03_P2_START_CHANGE_END_BOXES":
            image = TC.compose_sorting_mat(
                zones=["START", "CHANGE", "END"],
                title="Story modelling")
        elif image_id == "WS03_P3_STORY_BUILDER_BANNER":
            image = TC.compose_number_card("6 − 2 = 4", label="Story builder")
        # Worksheet 4 — sharing fairly
        elif image_id == "WS04_P1_THREE_SHARE_SCENES":
            image = TC.compose_sorting_mat(
                zones=["8 cookies, 2 plates",
                       "12 grapes, 3 plates",
                       "9 stickers, 3 plates"],
                title="Share fairly")
        elif image_id == "WS04_P2_TWO_LEFTOVER_SCENES":
            image = TC.compose_sorting_mat(
                zones=["7 cookies, 2 plates", "10 grapes, 3 plates"],
                title="Leftovers!")
        elif image_id == "WS04_P3_BLANK_SHARING_FRAME":
            image = TC.compose_blank_pair(
                title="My sharing story",
                left_label="Things shared",
                right_label="My share")
        # Worksheet 5 — coin match + snack pay
        elif image_id == "WS05_P1_COIN_MATCH_GRID":
            image = TC.compose_match_grid(
                left_items=["1¢", "5¢", "10¢", "25¢"],
                right_items=["PENNY", "NICKEL", "DIME", "QUARTER"],
                title="Match the coin")
        elif image_id == "WS05_P2_SNACK_PAY_SCENES":
            image = TC.compose_object_montage(
                objects=[("Popcorn 10¢", "slide09_food_02.png"),
                         ("Lollipop 5¢", "slide09_food_04.png"),
                         ("Pizza 25¢", "slide09_food_01.png")],
                title="Pay the price")
        elif image_id == "WS05_P3_PAY_TEN_CENTS_BOXES":
            image = TC.compose_sorting_mat(
                zones=["WAY 1", "WAY 2", "WAY 3"],
                title="Pay 10¢ three ways")
        # Formative — partner hunt scene + number line
        elif image_id == "FORM_Q1_NUMBER_QUANTITY_MATCH" and grade == "Kindergarten" and "coin_counters" in str(output_path):
            # Coin Counters override — partner-hunt scenes (otherwise Counting Crew match grid)
            image = TC.compose_compare_strip(
                left_label="Showing", right_label="Hidden",
                options=["2 + 3", "4 + 1", "0 + 5"])
        # Reflection sheet visuals
        elif image_id == "REF_YN_TABLE":
            image = TC.compose_match_grid(
                left_items=["I guessed", "I built 5", "I shared", "I named coins"],
                right_items=["YES", "YES", "YES", "YES"],
                title="Did you do these things?")
        elif image_id == "REF_FAV_BOX":
            image = TC.compose_object_montage(
                objects=[("PENNY 1¢", None), ("NICKEL 5¢", None),
                         ("DIME 10¢", None), ("QUARTER 25¢", None)],
                title="Favourite coin?")
        elif image_id == "REF_TRICKY_BOX":
            image = TC.compose_sorting_mat(
                zones=["Hidden cubes", "Leftover cookies", "Dime vs nickel"],
                title="Trickiest part?")
        elif image_id == "REF_NEXT_BOX":
            image = TC.compose_sorting_mat(
                zones=["Loonie ($1)", "Bigger prices", "Add to 20"],
                title="What next?")

    used_placeholder = False
    if image is None:
        # Smart fallback: real procedural composite using template_composers +
        # stock clipart (character map for CHAR_*, generic templated composites
        # for M_/WS_/FORM_/REF_/AS_). Added 2026-05-04 to drop the placeholder
        # count to ~0 for the 8 new narratives shipped this session — units now
        # route out of _drafts/ on the strength of "real images, even if generic"
        # instead of waiting on bespoke SVG art for every character.
        # Pass unit_dir so smart_fallback can read 3_manipulatives.json for
        # unit-specific labels (added 2026-05-10 after visual_inspector flagged
        # 86 missing_asset issues from generic empty-rectangle composites).
        unit_dir = output_path.parent.parent if output_path.parent.name == "composed" else None
        image = _smart_fallback(image_id, unit_dir=unit_dir)
    if image is None:
        # Last-resort fallback: labelled gray rectangle (only when smart
        # fallback also returns None — should be rare).
        image = _placeholder(image_id, width=400, height=120)
        used_placeholder = True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, "PNG")
    # Track placeholder use for the visual-quality gate. compose_for_unit reads
    # this attribute to flag every image_id that fell back to the labelled
    # rectangle so build_unit_deck can refuse to publish a unit with missing
    # artwork. Added 2026-05-03 after Counting Crew shipped with placeholder
    # hero images on every worksheet and manipulative slide.
    compose_pattern_parade_image._last_was_placeholder = used_placeholder  # type: ignore[attr-defined]
    return output_path


# ── Helpers for special compositions ──────────────────────────────────────

def _compose_sound_strip(sounds: list) -> Image.Image:
    """Like a parade strip but each cell holds a sound icon."""
    n = len(sounds)
    width = CELL_GAP + n * (CELL_SIZE + CELL_GAP)
    canvas = Image.new("RGBA", (width, STRIP_HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)
    for i, snd in enumerate(sounds):
        x = CELL_GAP + i * (CELL_SIZE + CELL_GAP)
        cell_box = (x, CELL_TOP, x + CELL_SIZE, CELL_TOP + CELL_SIZE)
        if snd is None:
            _draw_dashed_rect(draw, cell_box, 6, 4, 2)
        else:
            draw.rectangle(cell_box, fill="white", outline="black", width=2)
            ic = render_svg(asset(f"icon_{snd}"), width=CELL_SIZE - 12, height=CELL_SIZE - 12)
            canvas.paste(ic, (x + 6, CELL_TOP + 6), ic)
    return canvas


def _compose_my_core_box() -> Image.Image:
    img = Image.new("RGBA", (520, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((4, 4, 516, 196), outline="black", width=3)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 14), "My Core", fill="black", font=font)
    return img


def _compose_caption_box(text: str) -> Image.Image:
    img = Image.new("RGBA", (640, 90), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((4, 4, 636, 86), outline="black", width=2)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 30), text, fill="black", font=font)
    return img


def _compose_answer_box() -> Image.Image:
    img = Image.new("RGBA", (380, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((4, 4, 376, 196), outline="black", width=3)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 14), "My Answer", fill="black", font=font)
    draw.text((30, 70), "1.", fill="black", font=font)
    draw.line((60, 95, 350, 95), fill="black", width=1)
    draw.text((30, 130), "2.", fill="black", font=font)
    draw.line((60, 155, 350, 155), fill="black", width=1)
    return img


def _compose_face_rating() -> Image.Image:
    img = Image.new("RGBA", (600, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    centers = [120, 300, 480]
    labels = ["I got it!", "Almost!", "Need help!"]
    moods = ["happy", "neutral", "sad"]
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for cx, lab, mood in zip(centers, labels, moods):
        # Face circle
        draw.ellipse((cx - 50, 20, cx + 50, 120), outline="black", width=3, fill="white")
        # Eyes
        draw.ellipse((cx - 22, 50, cx - 12, 60), fill="black")
        draw.ellipse((cx + 12, 50, cx + 22, 60), fill="black")
        # Mouth
        if mood == "happy":
            draw.arc((cx - 25, 70, cx + 25, 100), start=0, end=180, fill="black", width=3)
        elif mood == "neutral":
            draw.line((cx - 20, 90, cx + 20, 90), fill="black", width=3)
        else:  # sad
            draw.arc((cx - 25, 90, cx + 25, 120), start=180, end=360, fill="black", width=3)
        # Label
        draw.text((cx, 145), lab, fill="black", font=font, anchor="mt")
    return img


def _compose_star_rating() -> Image.Image:
    img = Image.new("RGBA", (700, 220), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    options = [(1, "Just starting"), (2, "Mostly got it"), (3, "I am a Conductor!")]
    cell_w = 220
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for i, (n, label) in enumerate(options):
        cx = i * cell_w + cell_w // 2 + 10
        # Oval
        draw.ellipse((cx - 90, 20, cx + 90, 140), outline="black", width=3, fill="white")
        # Stars
        star_img = render_svg(asset("star"), width=44)
        for k in range(n):
            sx = cx - (n - 1) * 25 + k * 50 - 22
            img.paste(star_img, (int(sx), 50), star_img)
        # Label
        draw.text((cx, 165), label, fill="black", font=font, anchor="mt")
    return img


def _compose_yn_table(questions: list[str]) -> Image.Image:
    n = len(questions)
    row_h = 50
    width, height = 600, n * row_h + 8
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
        font_b = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
    except OSError:
        font = font_b = ImageFont.load_default()
    draw.rectangle((4, 4, width - 4, height - 4), outline="black", width=2)
    for i, q in enumerate(questions):
        y = 4 + i * row_h
        if i > 0:
            draw.line((4, y, width - 4, y), fill="#888", width=1)
        draw.text((20, y + row_h // 2), q, fill="black", font=font, anchor="lm")
        # YES/NO bubbles on the right
        bubble_y = y + row_h // 2
        for j, label in enumerate(("YES", "NO")):
            bx = width - 130 + j * 60
            draw.ellipse((bx - 22, bubble_y - 16, bx + 22, bubble_y + 16),
                         outline="black", width=2, fill="white")
            draw.text((bx, bubble_y), label, fill="black", font=font_b, anchor="mm")
    return img


def _compose_reflection_box(prompt: str) -> Image.Image:
    img = Image.new("RGBA", (600, 240), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    draw.text((10, 6), prompt, fill="black", font=font)
    draw.rectangle((4, 36, 596, 236), outline="black", width=2)
    return img


def _compose_grade_override(image_id: str, grade: str) -> Image.Image | None:
    """
    Grade-specific override for image IDs that are reused across grades but
    mean different things per grade. Return None if no grade-specific recipe
    applies — caller falls through to the generic dispatcher.

    Add new (grade, image_id) entries here when an existing K image_id needs
    a different recipe at a higher grade.
    """
    if grade == "Grade 2":
        # G2 worksheet 1: three-type sorter
        if image_id == "WS01_P1_STRIP_A":
            return compose_parade_strip(["bea", "finn", "bea", "finn", "bea"])
        if image_id == "WS01_P1_STRIP_B":
            return compose_growing_strip("bea", [1, 2, 3, 4])
        if image_id == "WS01_P1_STRIP_C":
            return compose_growing_strip("finn", [4, 3, 2, 1])
        if image_id == "WS01_P1_LABELS":
            return compose_label_stack(["REPEATING", "GROWING", "SHRINKING"])
        if image_id == "WS01_P2_PARADE":
            # G2: growing 2,4,6,8 stacked Beas — DIFFERENT from K's missing-cell strip
            return compose_growing_strip("bea", [2, 4, 6, 8])
        if image_id == "WS01_P3_CALENDAR":
            return compose_real_life_thumbnail("calendar")
        if image_id == "WS01_P3_BRICKS":
            return compose_real_life_thumbnail("bricks")
        if image_id == "WS01_P3_HOPSCOTCH":
            return compose_real_life_thumbnail("hopscotch")
        if image_id == "WS01_P3_COOKIE":
            return compose_real_life_thumbnail("cookie")

        # G2 worksheet 2: name the jump
        if image_id == "WS02_P1_STRIP_A":
            return compose_growing_strip("bea", [1, 3, 5, 7])
        if image_id == "WS02_P1_STRIP_B":
            return compose_growing_strip("bea", [10, 8, 6, 4])
        if image_id == "WS02_P1_STRIP_C":
            return compose_growing_strip("bea", [1, 2, 3, 4])
        if image_id == "WS02_P1_STRIP_D":
            return compose_growing_strip("bea", [8, 5, 2, 0])
        if image_id == "WS02_P2_PARADE":
            # Empty 4-cell strip for student-built growing parade
            return compose_parade_strip([None] * 4)
        if image_id == "WS02_P3_PARADE":
            return compose_parade_strip([None] * 4)
        if image_id == "WS02_P2_KEY":
            return render_svg(asset("bea"), width=120)

        # G2 worksheet 3: three faces of a rule
        if image_id == "WS03_P1_PARADE":
            return compose_growing_strip("bea", [2, 4, 6, 8])
        if image_id == "WS03_P1_NUMBERS":
            return compose_number_row([""] * 4)
        if image_id == "WS03_P1_TABLE":
            return compose_table_of_values(
                [("1", ""), ("2", ""), ("3", ""), ("4", "")])
        if image_id == "WS03_P2_TABLE":
            return compose_table_of_values(
                [("1", "5"), ("2", "8"), ("3", "11"), ("4", "")])
        if image_id == "WS03_P3_NUMBERS":
            return compose_number_row([""] * 4)
        if image_id == "WS03_P3_TABLE":
            return compose_table_of_values(
                [("1", ""), ("2", ""), ("3", ""), ("4", "")])
        if image_id == "WS03_P3_PARADE":
            # Empty 4-cell parade for student-built rule
            return compose_parade_strip([None] * 4)

        # G2 worksheet 4: Detective Pro
        if image_id == "WS04_P1_STRIP_A":
            return compose_parade_strip(["bea", "finn", "finn", "?", "finn", "finn"])
        if image_id == "WS04_P1_STRIP_B":
            return compose_growing_strip("bea", [4, 8, 0, 16])
        if image_id == "WS04_P1_STRIP_C":
            return compose_growing_strip("bea", [0, 9, 6, 3])
        if image_id == "WS04_P2_TABLE":
            return compose_table_of_values(
                [("1", "5"), ("2", "8"), ("3", "11"), ("4", ""), ("5", "")])
        if image_id == "WS04_P3_TABLE":
            return compose_table_of_values(
                [(str(i), "30" if i == 5 else "") for i in range(1, 9)],
                highlight_row=5)
        if image_id == "WS04_P2_PARADE":
            # G2: empty 8-cell strip with anchor cells filled at term 3-6 — keep
            # K's recipe behavior since the Detective Pro flow is similar; G2
            # uses the table for prediction. Leave None to fall through.
            return None

        # G2 worksheet 5: summative
        if image_id == "WS05_P1_HEADER":
            return _compose_caption_box(
                "My Rule | Pattern Type | My Core or First 2 Terms")
        if image_id == "WS05_P2_PARADE":
            return compose_parade_strip([None] * 8)
        if image_id == "WS05_P2_NUMBERS":
            return compose_number_row([""] * 8)
        if image_id == "WS05_P3_TABLE":
            return compose_table_of_values([(str(i), "") for i in range(1, 9)])
        if image_id == "WS05_P3_HUNDRED":
            return compose_hundred_chart(max_value=100)

        # G2 formative + reflection
        if image_id == "FORM_Q1_STRIP_A":
            return compose_parade_strip(["bea", "finn", "bea", "finn"])
        if image_id == "FORM_Q1_STRIP_B":
            return compose_growing_strip("bea", [1, 4, 7, 10])
        if image_id == "FORM_Q1_STRIP_C":
            return compose_growing_strip("bea", [12, 9, 6, 3])
        if image_id == "FORM_Q2_PARADE":
            return compose_growing_strip("bea", [3, 6, 9, 12])
        if image_id == "FORM_Q2_TABLE":
            return compose_table_of_values(
                [("1", ""), ("2", ""), ("3", ""), ("4", "")])

    # Grade 1 stragglers (apply across grade-1 only — K and G2 are unaffected)
    if grade == "Grade 1":
        if image_id == "WS02_P1_RULES":
            return compose_label_stack(["AB", "ABB", "AAB", "ABC"])
        if image_id == "WS02_P3_RULES":
            return compose_label_stack(["AB", "ABB", "AAB", "ABC"])

    return None


# ── Grade 2 compose recipes (added 2026-04-29) ───────────────────────────
#
# These render the new Grade 2 imagery (growing/shrinking parades, table of
# values, real-life-pattern thumbnails, hundred chart, number rows, label
# stacks) so worksheets show actual artwork instead of placeholder rectangles.


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    """Pick a system font, falling back gracefully."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def compose_growing_strip(animal: str, counts: list[int],
                          show_footprints: bool = True) -> Image.Image:
    """
    Render a growing/shrinking parade strip where each cell shows `count`
    stacked copies of `animal`. e.g. counts=[1,2,3,4] for a +1 growing
    pattern with `animal="bea"`.

    Uses a slightly taller cell so 4-deep stacks are legible.
    """
    if animal not in ANIMAL_NAMES:
        # Allow callers to pass "bea"/"finn"/etc. directly; ignore unknowns.
        animal = "bea"
    n = len(counts)
    cell_w = CELL_SIZE + 10
    cell_h = max(int(CELL_SIZE * 1.3), max(counts, default=1) * 28 + 20)
    width = CELL_GAP + n * (cell_w + CELL_GAP)
    height = cell_h + (24 if show_footprints else 8)
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # Render the animal once at small size; paste it `count` times per cell.
    icon_w = cell_w - 16
    icon_h = int(icon_w * 0.95)
    icon = render_svg(asset(animal), width=icon_w, height=icon_h)

    for i, count in enumerate(counts):
        x = CELL_GAP + i * (cell_w + CELL_GAP)
        cell_box = (x, 4, x + cell_w, 4 + cell_h)
        draw.rectangle(cell_box, outline="black", width=2)

        # Stack `count` icons vertically inside the cell, scaled down so they
        # all fit. Use a smaller icon size for high counts.
        if count <= 0:
            continue
        per_h = min(icon_h, max(20, (cell_h - 16) // max(1, count)))
        per_w = int(per_h * (icon_w / icon_h)) if icon_h else icon_w
        small = render_svg(asset(animal), width=per_w, height=per_h)
        total_h = per_h * count
        y0 = 4 + (cell_h - total_h) // 2
        cx = x + (cell_w - per_w) // 2
        for k in range(count):
            canvas.paste(small, (cx, y0 + k * per_h), small)

    if show_footprints:
        fy = height - 12
        for i in range(n):
            cx = CELL_GAP + i * (cell_w + CELL_GAP) + cell_w // 2
            draw.ellipse((cx - 6, fy - 4, cx + 6, fy + 4), fill="#ccc")
    return canvas


def compose_table_of_values(
    rows: list[tuple[str, str]],
    headers: tuple[str, str] = ("TERM", "VALUE"),
    *,
    pre_filled_terms: bool = True,
    highlight_row: int | None = None,
) -> Image.Image:
    """
    Render a 2-column table-of-values image.

    Args:
        rows: list of (term_label, value_label) pairs. Use empty string ""
            for cells the student fills in.
        headers: column headers (default ("TERM", "VALUE")).
        pre_filled_terms: cosmetic — controls whether the term column gets
            a slightly lighter-grey background to signal it's pre-filled.
        highlight_row: 1-indexed row to draw with a light-grey fill (e.g. an
            anchor value the student is given).

    The output is sized to roughly fit a worksheet hero slot (~520 wide).
    """
    n = len(rows)
    col_w = 240
    row_h = 44
    header_h = 50
    total_w = 2 * col_w + 4
    total_h = header_h + n * row_h + 4

    img = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    h_font = _font(20, bold=True)
    body_font = _font(20)

    # Outer border
    draw.rectangle((0, 0, total_w - 1, total_h - 1), outline="black", width=2)

    # Header row
    draw.rectangle((0, 0, col_w, header_h), fill=(240, 240, 240), outline="black", width=2)
    draw.rectangle((col_w, 0, total_w, header_h), fill=(240, 240, 240), outline="black", width=2)
    draw.text((col_w // 2, header_h // 2), headers[0], fill="black",
              font=h_font, anchor="mm")
    draw.text((col_w + col_w // 2, header_h // 2), headers[1], fill="black",
              font=h_font, anchor="mm")

    # Data rows
    for r, (term, value) in enumerate(rows):
        y0 = header_h + r * row_h
        y1 = y0 + row_h
        # Highlight (1-indexed)
        if highlight_row is not None and r + 1 == highlight_row:
            draw.rectangle((0, y0, total_w, y1), fill=(255, 240, 200))
        elif pre_filled_terms and term:
            draw.rectangle((0, y0, col_w, y1), fill=(250, 250, 250))
        # Cell borders
        draw.line((col_w, y0, col_w, y1), fill="black", width=1)
        draw.line((0, y1, total_w, y1), fill="#bbb", width=1)
        if term:
            draw.text((col_w // 2, y0 + row_h // 2), term, fill="black",
                      font=body_font, anchor="mm")
        if value:
            draw.text((col_w + col_w // 2, y0 + row_h // 2), value, fill="black",
                      font=body_font, anchor="mm")

    return img


def compose_real_life_thumbnail(kind: str) -> Image.Image:
    """
    Tiny recognizable thumbnail of a real-life pattern context.

    kind in {"calendar", "bricks", "hopscotch", "cookie"}.
    """
    width, height = 280, 220
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((2, 2, width - 2, height - 2), outline="black", width=2)

    if kind == "calendar":
        title_font = _font(14, bold=True)
        cell_font = _font(18, bold=True)
        # Header row of 7 day labels
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        cw = (width - 16) // 7
        y_hdr = 14
        for i, d in enumerate(days):
            cx = 8 + i * cw + cw // 2
            draw.text((cx, y_hdr), d, fill="#666", font=title_font, anchor="mm")
        # Numbers row 1..7
        y_num = 70
        for i in range(7):
            cx = 8 + i * cw + cw // 2
            draw.rectangle((8 + i * cw + 4, y_num - 24, 8 + i * cw + cw - 4, y_num + 24),
                           outline="black", width=1)
            draw.text((cx, y_num), str(i + 1), fill="black", font=cell_font, anchor="mm")
        draw.text((width // 2, height - 24), "+1 each day",
                  fill="#444", font=title_font, anchor="mm")

    elif kind == "bricks":
        # Three rows of offset bricks
        bw = 60
        bh = 30
        for row in range(3):
            y = 30 + row * (bh + 6)
            offset = (bw // 2) if row % 2 == 1 else 0
            x = 10 + offset
            while x < width - 10:
                draw.rectangle((x, y, min(x + bw, width - 10), y + bh),
                               outline="black", width=2, fill="#f5f5f5")
                x += bw + 4
        draw.text((width // 2, height - 16), "Repeating offset",
                  fill="#444", font=_font(13, bold=True), anchor="mm")

    elif kind == "hopscotch":
        # Vertical hopscotch grid: 1, 2, [3,4 side-by-side], 5, [6,7]
        sq = 50
        cell_font = _font(20, bold=True)
        cx = width // 2
        # 1, 2 (single squares)
        for i, n in enumerate([1, 2]):
            y = 12 + i * (sq + 4)
            draw.rectangle((cx - sq // 2, y, cx + sq // 2, y + sq),
                           outline="black", width=2)
            draw.text((cx, y + sq // 2), str(n), fill="black", font=cell_font, anchor="mm")
        # 3, 4 (paired)
        y = 12 + 2 * (sq + 4)
        draw.rectangle((cx - sq, y, cx, y + sq), outline="black", width=2)
        draw.rectangle((cx, y, cx + sq, y + sq), outline="black", width=2)
        draw.text((cx - sq // 2, y + sq // 2), "3", fill="black", font=cell_font, anchor="mm")
        draw.text((cx + sq // 2, y + sq // 2), "4", fill="black", font=cell_font, anchor="mm")

    elif kind == "cookie":
        # Four frames showing decreasing cookie size
        frame_w = (width - 20) // 4
        for i in range(4):
            x0 = 10 + i * frame_w
            cx = x0 + frame_w // 2
            cy = height // 2
            radius = max(8, 32 - i * 7)
            # Outline of full cookie position
            draw.ellipse((cx - 32, cy - 32, cx + 32, cy + 32),
                         outline="#ccc", width=1)
            # Actual cookie (shrinks)
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         outline="black", width=2, fill="#fff8dd")
            # A few chocolate-chip dots
            for dx, dy in [(-radius // 3, -radius // 3),
                           (radius // 3, -radius // 4),
                           (-radius // 4, radius // 3)]:
                if abs(dx) < radius - 4 and abs(dy) < radius - 4:
                    draw.ellipse((cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3),
                                 fill="#5a3a1a")
        draw.text((width // 2, height - 16), "Shrinking",
                  fill="#444", font=_font(13, bold=True), anchor="mm")

    else:
        return _placeholder(f"real-life:{kind}", width, height)
    return img


def compose_number_row(values: list[str], cell_w: int = 70,
                       cell_h: int = 70) -> Image.Image:
    """
    Render an empty (or partly filled) row of N boxes for a number sequence.
    `values` may contain "" for empty / fillable cells.
    """
    n = len(values)
    width = CELL_GAP + n * (cell_w + CELL_GAP)
    height = cell_h + 10
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    body_font = _font(22, bold=True)
    for i, v in enumerate(values):
        x = CELL_GAP + i * (cell_w + CELL_GAP)
        draw.rectangle((x, 4, x + cell_w, 4 + cell_h), outline="black", width=2)
        if v:
            draw.text((x + cell_w // 2, 4 + cell_h // 2), v, fill="black",
                      font=body_font, anchor="mm")
    return img


def compose_hundred_chart(max_value: int = 100,
                          cell_size: int = 22,
                          start_at_zero: bool = True) -> Image.Image:
    """
    Small 0–100 (or 0–50) chart in a 5- or 10-column grid. Used as a number
    reference in Grade 2 worksheets.
    """
    cols = 10
    n = max_value + (1 if start_at_zero else 0)
    rows = (n + cols - 1) // cols
    width = cols * cell_size + 4
    height = rows * cell_size + 24
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    body_font = _font(11)
    title_font = _font(11, bold=True)
    draw.text((width // 2, 8), f"0–{max_value} chart",
              fill="black", font=title_font, anchor="mm")
    base_y = 18
    for k in range(n):
        col = k % cols
        row = k // cols
        x = 2 + col * cell_size
        y = base_y + row * cell_size
        draw.rectangle((x, y, x + cell_size, y + cell_size),
                       outline="#aaa", width=1)
        n_text = str(k if start_at_zero else k + 1)
        draw.text((x + cell_size // 2, y + cell_size // 2),
                  n_text, fill="black", font=body_font, anchor="mm")
    return img


def compose_label_stack(labels: list[str]) -> Image.Image:
    """
    Vertical stack of labelled boxes, e.g. for "REPEATING / GROWING /
    SHRINKING" sort targets in Grade 2 worksheet 1.
    """
    box_w = 220
    box_h = 60
    gap = 12
    width = box_w + 4
    height = len(labels) * (box_h + gap) - gap + 4
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    label_font = _font(20, bold=True)
    for i, lbl in enumerate(labels):
        y0 = 2 + i * (box_h + gap)
        draw.rectangle((2, y0, 2 + box_w, y0 + box_h),
                       outline="black", width=2)
        draw.text((2 + box_w // 2, y0 + box_h // 2),
                  lbl, fill="black", font=label_font, anchor="mm")
    return img


def _compose_tracker_stub(image_id: str) -> Image.Image:
    """Tracker tables are best rendered natively in Slides — stub here."""
    return _placeholder(f"{image_id}\n(rendered as a Slides table)", width=600, height=300)


def _compose_rubric_stub() -> Image.Image:
    return _placeholder("AS_RUBRIC\n(rendered as a Slides table)", width=700, height=350)


def _placeholder(label: str, width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), (245, 245, 245, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((2, 2, width - 2, height - 2), outline="#999", width=2)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    draw.text((width // 2, height // 2), label, fill="#666", font=font, anchor="mm", align="center")
    return img


# ── Smart fallback: real composites for unmatched image_ids ───────────────
#
# When a unit ships a brand-new narrative (Maple/Sap Sam, Detective Dee, etc.)
# its CHAR_/M_/WS_/FORM_/AS_ image_ids have no bespoke composer. Before
# 2026-05-04 the fallback was _placeholder() (gray box), and every such ID
# tripped the placeholder-artwork gate, routing the unit to _drafts/.
#
# This section provides a procedurally-real composite for any unmatched ID:
# - Character portraits: stock-clipart approximation via compose_character_card
# - Manipulatives/worksheets: generic templated composites from
#   template_composers (sorting mats, montages, etc.) using the ID itself
#   as a label so the slide is meaningful even without bespoke art.
#
# These composites mark _last_was_placeholder = False so units route out of
# _drafts/ on the strength of "real images, even if generic."

# Character key (between CHAR_ and _FRONT) → (display name, stock clipart filename).
# Add new characters here as units are created.
CHARACTERS_DIR = ASSETS_DIR / "characters"


def _compose_custom_character_card(svg_path: Path, name: str) -> "Image.Image":
    """Hero image using a hand-drawn character SVG instead of stock clipart.

    Same 1024×768 layout as TC.compose_character_card: art at top, name
    banner at bottom. The art is rendered from the SVG via rsvg-convert
    and pasted preserving aspect ratio inside (160, 60, 864, 560).
    """
    from . import template_composers as TC

    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)

    box_x0, box_y0, box_x1, box_y1 = 160, 60, 864, 560
    box_w, box_h = box_x1 - box_x0, box_y1 - box_y0

    art = render_svg(svg_path, width=box_w, height=box_h).convert("RGBA")
    paste_x = box_x0 + (box_w - art.width) // 2
    paste_y = box_y0 + (box_h - art.height) // 2
    canvas.paste(art, (paste_x, paste_y), art)

    # Name banner
    draw.rectangle((140, 580, 884, 670), fill=(245, 245, 245),
                   outline=(80, 80, 80), width=3)
    TC._text_centered(draw, (512, 625), name, TC._font(54, bold=True))
    return canvas


def _character_svg_path(key: str) -> "Path | None":
    """Return the custom SVG path for a character key if one exists."""
    p = CHARACTERS_DIR / f"{key}.svg"
    return p if p.exists() else None


def _extract_character_clipart_from_description(desc: str) -> list[str | None]:
    """Scan a manipulative description for character names referenced after
    'Centre-left:' / 'Centre-right:' / 'Centre:' anchor markers, and return
    paths to their kawaii SVGs (or None if no SVG exists for a name).

    Used by the smart_fallback POSTER path to embed characters into M10
    anchor posters where the description names them explicitly, e.g.
    "Centre-left: Bot the Robot. Centre-right: Buggy the Beetle." → returns
    [BOT.svg, BUGGY.svg].
    """
    import re
    if not desc:
        return []
    paths: list[str | None] = []
    seen: set[str] = set()
    # Walk all "Centre[-left|-right]:" markers and pull capitalised-word
    # clusters (Bot, Inspector If, Then the Action Dog, etc.) from each,
    # then try each cluster word as a possible character SVG key.
    for m in re.finditer(
        r"Cent(?:re|er)(?:-left|-right)?\s*:\s*([^.]{4,160})",
        desc, flags=re.IGNORECASE,
    ):
        phrase = m.group(1).strip()
        # Try each capitalised word; "Inspector If and Then the Action Dog"
        # should yield IF + THEN; "Bot the Robot and Buggy the Beetle"
        # yields BOT + BUGGY.
        for word in re.findall(r"\b([A-Z][a-zA-Z]+)\b", phrase):
            key = word.upper()
            if key in seen:
                continue
            # Skip common stop-words / titles that aren't character names
            if key in {"THE", "A", "AN", "OF", "AND", "OR", "MR", "MS",
                       "MRS", "INSPECTOR", "DETECTIVE", "OFFICER", "DOCTOR",
                       "DR", "PROFESSOR", "COACH", "CAPTAIN", "HEADER",
                       "TITLE", "AROUND", "THEM", "CENTRE", "CENTER",
                       "BUBBLE", "LETTERS", "LEFT", "RIGHT", "ANCHOR",
                       "POSTER", "MAP", "IT", "MOVE", "BUILD", "MATCH",
                       "LOCATE", "BIG", "SMALL", "SAME", "SHAPE"}:
                continue
            svg = _character_svg_path(key)
            if svg is not None:
                seen.add(key)
                paths.append(str(svg))
                if len(paths) >= 4:
                    return paths
    return paths


_CHARACTER_CLIPART = {
    # g1 Real-Life Math (Sugar Bush) — Maple, Sap Sam
    "MAPLE":   ("Maple the Maple Tree", "slide05_plants_01.png"),
    "SAP_SAM": ("Sap Sam the Collector", "slide01_people_01.png"),
    # g2 What's Missing — Detective Dee, Mystery Mo
    "DEE":     ("Detective Dee", "slide02_random_05.png"),
    "MO":      ("Mystery Mo", "slide09_food_04.png"),
    # g2 If-Then Detectives — Inspector If, Then the Action Dog
    "IF":      ("Inspector If the Cat", "slide06_animals_02.png"),
    "THEN":    ("Then the Action Dog", "slide02_random_04.png"),
    # g2 Math in My Town — Coach Cara, Sport Sam
    "CARA":    ("Coach Cara", "slide03_sports_03.png"),
    "SAM":     ("Sport Sam", "slide03_sports_02.png"),
    # g3 Balanced Equations — Eddy the Engineer, Vex the Vet
    "EDDY":    ("Eddy the Engineer", "slide02_random_01.png"),
    "VEX":     ("Vex the Variable Vet", "slide08_places_04.png"),
    # g3 Bug Busters — Buzz the Beetle, Patch the Repair Pup
    "BUZZ":    ("Buzz the Bug-Buster Beetle", "slide06_animals_03.png"),
    "PATCH":   ("Patch the Repair Pup", "slide02_random_04.png"),
    # g3 Math in My Community (re-uses CARA/SAM)
    # k Data Detectives — Detective Dot, Tally
    "DOT":     ("Detective Dot the Squirrel", "slide05_plants_02.png"),
    "TALLY":   ("Tally the Tally Cat", "slide06_animals_01.png"),
    # k Shape Safari — Sammy the Sloth, Mira the Monkey
    "SAMMY":   ("Sammy the Safari Sloth", "slide06_animals_04.png"),
    "MIRA":    ("Mira the Map Monkey", "slide02_random_09.png"),
    # k Measurement Bigger Smaller — Max the Moose, Tess the Mouse
    "MAX":     ("Max the Measure Moose", "slide06_animals_01.png"),
    "TESS":    ("Tess the Tiny Mouse", "slide06_animals_02.png"),
    # g1 Data Likelihood — Lucky the Loon, Maybe Mae the Mouse
    "LUCKY":   ("Lucky Lou the Loon", "slide04_planets_01.png"),
    "MAYBE":   ("Maybe Mae the Cat", "slide04_planets_02.png"),
    # g1 Spatial Mapping — Trekker Tig the Tiger, Compass Coco the Cat
    "TIG":     ("Trekker Tig the Tiger Cub", "slide06_animals_03.png"),
    "COCO":    ("Compass Coco the Cat", "slide06_animals_01.png"),
    # g1 Measurement How Long — Roo the Rabbit, Cal the Calendar Cat
    "ROO":     ("Roo the Ruler Rabbit", "slide05_plants_01.png"),
    "CAL":     ("Cal the Calendar Cat", "slide04_planets_02.png"),
    # g2 Spatial Mirror Mirror — Symmy the Symmetry Squirrel, Flippy the Frog
    "SYMMY":   ("Symmy the Symmetry Squirrel", "slide06_animals_03.png"),
    "FLIPPY":  ("Flippy the Folding Frog", "slide09_food_01.png"),
    # k Coding Little Programmers — Bot the Robot, Buggy the Beetle
    "BOT":     ("Bot the Robot Programmer", "slide02_random_01.png"),
    "BUGGY":   ("Buggy the Debug Beetle", "slide06_animals_03.png"),
    # g1 Financial Classroom Market — Penny Penguin, Coin Cassie
    "PENNY":   ("Penny the Penguin Shopkeeper", "slide06_animals_02.png"),
    "COIN":    ("Coin Cassie the Cashier", "slide01_people_01.png"),
    # g2 Financial Tap to Pay — Tappy Toonie, Loonie Lou
    "TAPPY":   ("Tappy the Toonie Frog", "slide09_food_01.png"),
    "LOONIE":  ("Loonie Lou the Mouse", "slide06_animals_02.png"),
    # g3 Financial Plan Your Party — Pat the Party Planner, Budget Bea
    "PAT":     ("Pat the Party Planner Pup", "slide02_random_04.png"),
    "BUDGET":  ("Budget Bea the Bear", "slide06_animals_04.png"),
    # g2 Real-Life Math town — Tom the Town Helper (secondary character)
    "TOM":     ("Tom the Town Helper", "slide01_people_01.png"),
    # g1 Spatial Mapping — Compass (Coco variant), Trekker (Tig variant)
    "COMPASS": ("Compass Coco the Cat", "slide06_animals_01.png"),
    "TREKKER": ("Trekker Tig the Tiger Cub", "slide06_animals_03.png"),
    # === LANGUAGE PROGRAMME (2023 SoR) ===
    # g1 CVC Decoders — Sounder Sam the Owl, Blendy the Bear
    "SOUNDER": ("Sounder Sam the Owl", "slide06_animals_05.png"),
    "BLENDY":  ("Blendy the Bear", "slide06_animals_04.png"),
    # Number-unit secondary characters (use stock clipart fallback)
    "DAN":     ("Dan the Divider", "slide01_people_01.png"),
    "DOUBLES": ("Doubles the Robot", "slide01_people_01.png"),
    "FRANKIE": ("Frankie the Fraction Friend", "slide06_animals_01.png"),
    "HUGO":    ("Detective Hugo Hundreds", "slide01_people_01.png"),
    "LILA":    ("Lila", "slide01_people_01.png"),
    "MAYA":    ("Maya the Multiplication Maven", "slide01_people_01.png"),
    "MINNIE":  ("Minnie the Minus Mouse", "slide01_people_01.png"),
    "ONA":     ("Detective Ona Ones", "slide01_people_01.png"),
    "OTTO":    ("Otto", "slide01_people_01.png"),
    "PIXEL":   ("Pixel the Practice Pal", "slide02_random_01.png"),
    "PLUS":    ("Plus the Adding Pup", "slide01_people_01.png"),
    "SCOOT":   ("Scoot", "slide01_people_01.png"),
    "TINA":    ("Detective Tina Tens", "slide01_people_01.png"),
    "TONY":    ("Tony the Toolkit Master", "slide01_people_01.png"),
    "NICK":    ("Nick the Nickel", "slide01_people_01.png"),
    "QUINCY":  ("Quincy the Piggy Bank", "slide01_people_01.png"),
    # k Number Counting Crew + k Coding + g3 Number Times Table
    "MAE":     ("Mae the Multiplier", "slide01_people_01.png"),
    "THEO":    ("Theo the Counting Crew Chef", "slide01_people_01.png"),
    "BUDDY":   ("Buddy the Workshop Helper", "slide06_animals_03.png"),
    # k Number Coin Counters secondary character (renamed from COIN)
    "CASSIE":  ("Coin Cassie the Cashier", "slide01_people_01.png"),
    # g3 Number Place-Value detectives
    "TOM":     ("Town Tom the Town Helper", "slide01_people_01.png"),
    # g1 Algebra characters
    "BELLA":   ("Bella the Balance Beam Scientist", "slide01_people_01.png"),
    "BOBBY":   ("Bobby the Balance Beam Buddy", "slide01_people_01.png"),
    "CODA":    ("Coda the Coding Robot", "slide06_animals_01.png"),
    "LOOPER":  ("Looper the Loop Helper", "slide02_random_01.png"),
    # g2 spatial Symmetry Squirrel + Folding Frog already mapped above
    # g2 Number Place-Value Detectives — Detective Hugo, Tina, Ona — mapped above
    # g2 Number Groups Of — Mae, Buddy mapped above
    # k Spatial Shape Safari already maps SAMMY/MIRA above
}


def _lookup_manipulative(unit_dir: "Path | None", image_id: str) -> dict | None:
    """Look up a manipulative entry in <unit_dir>/3_manipulatives.json.

    Matches by `asset_id` (case-insensitive) OR by image_placeholder.id == image_id.
    Returns the asset dict or None.
    """
    if unit_dir is None:
        return None
    p = unit_dir / "3_manipulatives.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    iid_upper = image_id.upper()
    for asset in data.get("assets", []):
        aid = (asset.get("asset_id") or "").upper()
        # Match by asset_id OR by image_placeholder id; in both cases attach
        # the placeholder dict so _zones_from_manipulative can read keywords
        # and description from it.
        for ph in asset.get("image_placeholders", []) or []:
            phid = (ph.get("id") or "").upper()
            if phid == iid_upper:
                merged = dict(asset)
                merged["_placeholder"] = ph
                return merged
        if aid == iid_upper:
            merged = dict(asset)
            phs = asset.get("image_placeholders") or []
            if phs:
                merged["_placeholder"] = phs[0]
            return merged
    return None


def _zones_from_manipulative(asset: dict) -> list[str]:
    """Extract 4-8 short zone labels from a manipulative asset's
    image_placeholder description for richer POSTER/CHART/TEMPLATE composites.

    Revised 2026-05-10 (R16): the real placeholder descriptions are rich and
    structured (e.g. "4 sections: MOVE (arrows), POSITION (above/below/...),
    RECORD (code strip), TEST (bug check)", or "Centre-left: Bot the Robot.
    Centre-right: Buggy the Beetle. Around them: arrows, mat, code strip
    icons."). Earlier versions short-circuited on a tiny keywords list like
    ['floor','mat'] and ignored the description entirely. This pass prefers
    description-extracted zones and uses keywords only as padding.
    """
    import re

    ph = asset.get("_placeholder") or {}
    desc = ph.get("description") or asset.get("purpose", "") or ""
    keywords = ph.get("keywords") or []
    name = asset.get("name", "")

    NOISE = {"line", "art", "b&w", "bw", "grid", "letter", "portrait",
             "landscape", "page", "manipulative", "classroom", "icon",
             "icons", "border", "borders", "cut", "lines", "cell", "cells",
             "with thin", "rows", "row", "section", "sections", "column",
             "columns", "header", "title", "size", "sizes", "thin", "solid",
             "dashed", "across", "stacked", "row)", "rows)", "in long", "long)",
             "top row", "middle row", "bottom row", "left", "right", "top", "bottom",
             "centre", "center", "small icon", "small icons", "with a small icon"}
    NOISE_SUBSTRINGS = ("line art", "b&w", "thin solid", "cut-line",
                        "cut lines", "cut line", "in long", "in tall",
                        "in across", "in wide", "fold line", "fold lines",
                        "each ~", "~1.5in", "~2in", "~1in", "~3in",
                        "varies in size", "varied lengths", "vary in size",
                        "no fill", "no content", "thin underline",
                        "thin underlines", "thin border", "thin borders",
                        "blank picture", "picture frame", "response slot",
                        "response slots", "vertical plan", "slot vertical",
                        "horizontal plan", "stacked vertically",
                        "stacked horizontally")

    def _clean_token(s: str) -> str:
        s = re.sub(r"\s*\([^)]*\)\s*", " ", s).strip().rstrip(".:;,'\"")
        s = s.lstrip("'\"").rstrip("'\"")
        s = re.sub(r"^(a|an|the)\s+", "", s, flags=re.IGNORECASE).strip()
        s = re.sub(r"^\d+\s+", "", s)            # strip leading count "5 forward"
        # NOTE: removed the prior overly-greedy `^\d+\s*[¢$]?\s*` because it
        # ate leading digits before hyphens ("2-LANE CODE" → "-LANE CODE").
        # "5¢" labels keep their digit (which IS the content).
        s = re.sub(r"\s+[¢$]\d+\.?\d*\s*$", "", s)  # trailing $X
        s = re.sub(r"\s+~?\d[\d.\sx×]*(?:in|cm|mm|tall|wide|long|across).*$",
                   "", s, flags=re.IGNORECASE)  # trailing size measurement
        # Strip meta-art prefixes/suffixes that leak from "Around them: small
        # icons of X" / "Header: 'X'" / "Long X trailing across…" patterns.
        s = re.sub(r"^(?:small\s+)?icons?\s+(?:of|for)\s+\d*\s*",
                    "", s, flags=re.IGNORECASE)
        s = re.sub(r"^small\s+icons?\s+", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+icons?$", "", s, flags=re.IGNORECASE)  # trailing "icons"
        s = re.sub(r"^Header\s*[:\-]\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"^Long\s+\w+\s+trailing\s+across.*$",
                    "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+—.*$", "", s)            # trailing em-dash + comment
        s = re.sub(r"\s+\d+\s+unit\s+themes?$",
                    "", s, flags=re.IGNORECASE)
        # Strip "Row N: ..." / "Section N: ..." prefixes if they slipped through
        s = re.sub(r"^(?:Row|Section|Column|Station)\s+\d+\s*:\s*",
                    "", s, flags=re.IGNORECASE)
        # Strip leading/trailing stray quote chars that survived parenthetical
        # removal (e.g. Header: 'Bigger left 'Bigger).
        s = s.strip(" '\"")
        # Filter labels that are essentially layout directives, not content
        if re.search(r"\bicon\s+(?:on|at|in)\s+the\b", s, re.IGNORECASE):
            return ""
        if re.search(r"\bin\s+bold\b|\bin\s+italic\b", s, re.IGNORECASE):
            return ""
        return s.strip()

    def _ok(s: str) -> bool:
        if not (2 <= len(s) <= 38):
            return False
        sl = s.lower()
        if sl in NOISE:
            return False
        if any(w in sl for w in NOISE_SUBSTRINGS):
            return False
        # Filter out fragments containing only descriptive words
        if sl.endswith(")") and "(" not in sl:
            return False  # leftover close-paren fragment
        # Real labels don't contain colons or semicolons; presence of one
        # indicates a meta-text fragment leaked through ("Section headings:
        # COIN", "single line for WEATHER;")
        if ":" in s or ";" in s:
            return False
        # Real labels don't span hyphens/slashes if they look like meta
        # (e.g. "COIN/DICE/MARBLES" while individually fine, when whole desc
        # was a fragment).
        if "/" in s and s.count("/") >= 2:
            return False
        return True

    candidates: list[str] = []
    seen: set[str] = set()

    def _push(tok: str) -> None:
        tok = _clean_token(tok)
        if _ok(tok) and tok.lower() not in seen:
            seen.add(tok.lower())
            # Keep full label (up to 40 chars); the renderer (e.g.
            # _compose_anchor_poster_rich) auto-fits via textbbox by
            # shrinking the font or wrapping to 2 lines.
            candidates.append(tok.title()[:40] if tok.isupper() or tok.islower()
                              else tok[:40])

    if desc:
        # PATTERN PRE — "Section N (LABEL...)", "Section N: <NOUN>",
        # "Row N: <a/the> <NOUN>", or quoted labels like "label 'X'" /
        # "labelled 'X'" — these catch capstone-template style descriptions
        # where each row/section has its real name inside parens or quotes.
        for m in re.finditer(
            r"(?:Section|Row|Column|Station|Block|Panel|Quadrant)\s+\d+\s*"
            r"\(([A-Z][^)]{2,30})\)",
            desc, flags=re.IGNORECASE,
        ):
            label = m.group(1).strip()
            # Drop any trailing descriptor after the first comma or space-
            # ditch words ("carnival", "section", etc.)
            label = re.split(
                r"[,;]|\s+(?:carnival|section|station|panel|page|area)\b",
                label, flags=re.IGNORECASE, maxsplit=1,
            )[0].strip()
            _push(label)
        for m in re.finditer(
            r"(?:Section|Row|Column|Station)\s+\d+\s*:\s*[^.]{0,60}?"
            r"(?:icon|label|frame|with)?\s*'([^']{2,30})'",
            desc, flags=re.IGNORECASE,
        ):
            _push(m.group(1).strip())
        # "label 'X'" / "labelled 'X'" — common in anchor-chart descriptions
        for m in re.finditer(
            r"(?:labels?|labelled|labeled|named|called)\s+'([^']{2,30})'",
            desc, flags=re.IGNORECASE,
        ):
            _push(m.group(1).strip())

        # PATTERN A — colon-introduced list: "N rows: A, B, C" /
        # "Sections: A, B, C" / "Cards: A, B, C" / "Objects: A, B, C"
        for m in re.finditer(
            r"(?:\d+\s+)?(?:rows?|sections?|columns?|stations?|groups?|"
            r"cards?|tokens?|tiles?|pieces?|spinners?|nets?|categor(?:y|ies)|"
            r"objects?|items?|examples?|words?|terms?|features?|shapes?|"
            r"animals?|coins?|bills?|stickers?|stations?)"
            r"(?:\s+(?:stacked|listed|shown|labelled?|labeled|named|arranged))?"
            r"\s*:\s*([^.]{8,300})",
            desc, flags=re.IGNORECASE,
        ):
            # Strip parentheticals first so slashes inside parens aren't split
            tail = re.sub(r"\([^)]*\)", "", m.group(1))
            parts = re.split(r",\s*|\s+and\s+|\s*\|\s*", tail)
            for p in parts:
                _push(p)
                if len(candidates) >= 8:
                    break
            if len(candidates) >= 6:
                break

        # PATTERN B — comma list after a trigger preposition
        if len(candidates) < 4:
            for m in re.finditer(
                r"(?:with|showing|listing|shows|including|covering|named|"
                r"labelled?|displayed|contains?|labels|labeled|featuring|"
                r"depict(?:s|ing)?|consists? of|made up of|holds?|"
                r"around them|around the centre)\s*:?\s+([^.]{10,300})",
                desc, flags=re.IGNORECASE,
            ):
                tail = re.sub(r"\([^)]*\)", "", m.group(1))
                parts = re.split(r",\s*|\s+and\s+", tail)
                for p in parts:
                    _push(p)
                    if len(candidates) >= 8:
                        break
                if len(candidates) >= 6:
                    break

        # PATTERN C — "Mix of X, Y, Z, W"
        if len(candidates) < 4:
            m = re.search(r"Mix of\s+([^.]{10,200})", desc, flags=re.IGNORECASE)
            if m:
                tail = re.sub(r"\([^)]*\)", "", m.group(1))
                for p in re.split(r",\s*|\s+and\s+", tail):
                    _push(p)

        # PATTERN D — POSTER / scene: extract characters after "Centre-left:"
        # / "Centre-right:" / "Centre:". Run UNCONDITIONALLY so character
        # names don't get crowded out by "Around them" or "with X" matches
        # that fill the candidate list with non-character zones first. The
        # character names then prepend so they land in the leading poster
        # slots that get clipart_files.
        char_candidates: list[str] = []
        for m in re.finditer(
            r"Cent(?:re|er)(?:-left|-right)?\s*:\s*([^.]{4,160})",
            desc, flags=re.IGNORECASE,
        ):
            phrase = m.group(1).strip()
            # Strip parentheticals FIRST so "(cat with deerstalker)" doesn't
            # eat the rest of the sentence when we split on "with".
            phrase = re.sub(r"\s*\([^)]*\)\s*", " ", phrase).strip()
            # Split first on " and " to capture both X and Y in one clause,
            # THEN trim each at descriptive prepositions.
            for sub in re.split(r"\s+and\s+", phrase, flags=re.IGNORECASE):
                sub = re.split(
                    r"\s+(?:holding|in\s+(?:a\s+)?safari|with\s+(?:a\s+)?|"
                    r"wearing|carrying|on\s+a|by\s+a)",
                    sub, flags=re.IGNORECASE, maxsplit=1,
                )[0].strip().rstrip(".,;")
                if sub:
                    char_candidates.append(sub)
        # Prepend character candidates so they get the leading clipart slots
        if char_candidates:
            existing_lower = set(seen)
            new_front: list[str] = []
            for c in char_candidates:
                cl = _clean_token(c)
                if _ok(cl) and cl.lower() not in existing_lower:
                    existing_lower.add(cl.lower())
                    new_front.append(cl[:40])
            if new_front:
                # Rebuild list: characters first, then prior candidates
                # (deduped against the new chars).
                merged = list(new_front)
                for c in candidates:
                    if c.lower() not in {x.lower() for x in new_front}:
                        merged.append(c)
                candidates = merged[:8]
                seen = {c.lower() for c in candidates}

        # PATTERN E — money/coin/bill values list:
        # "nickel (5¢), dime (10¢), quarter (25¢)..."
        if len(candidates) < 4:
            for m in re.finditer(
                r"\b(nickel|dime|quarter|loonie|toonie|penny|pennies|"
                r"\$\d+|cents?|coin|bill|dollar)\b[^,.]{0,30}",
                desc, flags=re.IGNORECASE,
            ):
                _push(m.group(0))
                if len(candidates) >= 6:
                    break

        # PATTERN F — final fallback: any sentence with ≥2 commas,
        # treated as a list (skip "thin solid" line-art noise)
        if len(candidates) < 4:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", desc)
                         if s.strip()]
            for sentence in sentences:
                if sentence.count(",") >= 2 and len(sentence) < 250:
                    for p in re.split(r",\s*|\s+and\s+", sentence.rstrip(".")):
                        _push(p)
                    if len(candidates) >= 4:
                        break

    # Pad with keywords from placeholder if still short
    if len(candidates) < 4:
        for kw in keywords:
            _push(str(kw))
            if len(candidates) >= 4:
                break

    # Final pad with generic if still short
    if len(candidates) < 4:
        name_clean = (name.replace("Anchor Chart", "")
                          .replace("Anchor Poster", "")
                          .replace("Poster", "").strip())
        for g in [name_clean, "Example", "Vocabulary", "Try It"]:
            _push(g)
            if len(candidates) >= 4:
                break

    return candidates[:8] or ["Concept", "Example", "Vocabulary", "Try It"]


def _compose_anchor_poster_rich(title: str, zones: list[str],
                                clipart_files: list[str | None] | None = None) -> "Image.Image":
    """Anchor poster: title across the top + 4-6 labeled zones in a 2-3 col grid.

    Each zone is a labeled box; if a clipart_file is provided for the slot,
    paste it as a small thumbnail above the label.
    """
    from . import template_composers as TC
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)

    # Title bar
    draw.rectangle((40, 30, 984, 110), outline=(40, 40, 40), width=4,
                   fill=(252, 248, 230))
    TC._text_centered(draw, (512, 70), title, TC._font(34, bold=True))

    # Decorative banner stripe under the title
    draw.line([(40, 120), (984, 120)], fill=(60, 60, 60), width=2)

    # Zones grid: 2 columns × 2-3 rows
    n = max(4, min(len(zones), 6))
    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols
    grid_top = 150
    grid_bot = 730
    grid_h = grid_bot - grid_top
    cell_h = (grid_h - 24 * (rows - 1)) // rows
    cell_w = (1024 - 80 - 24 * (cols - 1)) // cols

    clipart_files = clipart_files or [None] * n
    for i in range(n):
        r = i // cols
        c = i % cols
        x0 = 40 + c * (cell_w + 24)
        y0 = grid_top + r * (cell_h + 24)
        x1 = x0 + cell_w
        y1 = y0 + cell_h
        draw.rounded_rectangle((x0, y0, x1, y1), radius=14,
                               outline=(60, 60, 60), width=3,
                               fill=(255, 255, 255))
        clip = clipart_files[i] if i < len(clipart_files) else None
        if clip:
            inner_box = (x0 + 30, y0 + 24, x1 - 30, y1 - 80)
            clip_str = str(clip)
            try:
                if clip_str.lower().endswith(".svg"):
                    # Render SVG to PIL.Image and paste, preserving aspect ratio
                    box_w = inner_box[2] - inner_box[0]
                    box_h = inner_box[3] - inner_box[1]
                    img = render_svg(Path(clip_str), width=box_w,
                                      height=box_h)
                    img.thumbnail((box_w, box_h), Image.LANCZOS)
                    paste_x = inner_box[0] + (box_w - img.width) // 2
                    paste_y = inner_box[1] + (box_h - img.height) // 2
                    if img.mode == "RGBA":
                        canvas.paste(img, (paste_x, paste_y), img)
                    else:
                        canvas.paste(img, (paste_x, paste_y))
                else:
                    TC._paste_clipart(canvas, clip_str, inner_box)
            except Exception:
                pass
        label = zones[i] if i < len(zones) else ""
        # Auto-fit label using textbbox measurement so it always renders
        # within the cell width without mid-word clipping. Drop font size
        # progressively, then split into 2 lines, then truncate-with-ellipsis
        # only as last resort.
        avail_w = cell_w - 28
        line1, line2 = label, ""
        font_size = 22
        for size in (22, 20, 18, 16, 14, 13, 12):
            font = TC._font(size, bold=True)
            try:
                bbox = draw.textbbox((0, 0), label, font=font)
                w = bbox[2] - bbox[0]
            except Exception:
                w = len(label) * (size * 0.6)
            if w <= avail_w:
                font_size = size
                line1, line2 = label, ""
                break
        else:
            # Single line at 12pt is still too wide; try 2-line wrap at 16pt
            font_size = 16
            font = TC._font(font_size, bold=True)
            # Split at the natural midpoint (space closest to middle of string)
            mid = len(label) // 2
            best_split = mid
            best_diff = mid
            for i_, ch in enumerate(label):
                if ch == " ":
                    diff = abs(i_ - mid)
                    if diff < best_diff:
                        best_diff = diff
                        best_split = i_
            line1 = label[:best_split].strip()
            line2 = label[best_split:].strip()
            # If lines are still too wide at 16pt, drop both to 13pt
            try:
                w1 = (draw.textbbox((0, 0), line1, font=font))[2]
                w2 = (draw.textbbox((0, 0), line2, font=font))[2]
            except Exception:
                w1 = w2 = avail_w + 1
            if w1 > avail_w or w2 > avail_w:
                font_size = 13
        font = TC._font(font_size, bold=True)
        if line2:
            cy = y1 - 50
            TC._text_centered(draw, ((x0 + x1) // 2, cy),
                              line1, font)
            TC._text_centered(draw, ((x0 + x1) // 2, cy + font_size + 4),
                              line2, font)
        else:
            TC._text_centered(draw, ((x0 + x1) // 2, y1 - 35),
                              line1, font)
    return canvas


def _compose_anchor_chart_rich(title: str, columns: list[tuple[str, list[str]]]) -> "Image.Image":
    """Anchor chart: title on top + 2-3 columns each with a header + 3-5 bullet items."""
    from . import template_composers as TC
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)

    # Title bar
    draw.rectangle((40, 30, 984, 110), outline=(40, 40, 40), width=4,
                   fill=(248, 240, 245))
    TC._text_centered(draw, (512, 70), title, TC._font(34, bold=True))

    # Columns
    n = max(2, min(len(columns), 3))
    cols_top = 140
    cols_bot = 730
    col_w = (1024 - 80 - 24 * (n - 1)) // n
    for i in range(n):
        header, bullets = columns[i] if i < len(columns) else ("", [])
        x0 = 40 + i * (col_w + 24)
        x1 = x0 + col_w
        # Header
        draw.rectangle((x0, cols_top, x1, cols_top + 60),
                       outline=(40, 40, 40), width=3, fill=(255, 245, 220))
        TC._text_centered(draw, ((x0 + x1) // 2, cols_top + 30),
                          header, TC._font(26, bold=True))
        # Body
        draw.rectangle((x0, cols_top + 60, x1, cols_bot),
                       outline=(40, 40, 40), width=3, fill=(255, 255, 255))
        # Bullets
        y = cols_top + 90
        for b in bullets[:5]:
            draw.ellipse((x0 + 18, y + 5, x0 + 30, y + 17), fill=(40, 40, 40))
            try:
                font = TC._font(20)
                draw.text((x0 + 42, y), str(b)[:32], fill=(20, 20, 20),
                          font=font)
            except Exception:
                pass
            y += 36
    return canvas


def _compose_grid_paper(title: str, rows: int, cols: int,
                         row_labels: list[str] | None = None,
                         col_labels: list[str] | None = None,
                         cell_label_pattern: str | None = None) -> "Image.Image":
    """Render an actual N×M grid (for floor mats, cards-in-grid, etc.).

    `cell_label_pattern`: if given, each cell shows the pattern with {r}/{c}
    placeholders (e.g. "{c}{r}" for "A1", "B2"; "→" for all-arrows).
    """
    from . import template_composers as TC
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)

    # Title
    TC._text_centered(draw, (512, 50), title, TC._font(30, bold=True))

    # Grid bounds — leave room for title and optional axis labels
    pad_left = 80 if row_labels else 60
    pad_top = 110 if col_labels else 90
    pad_right = 40
    pad_bottom = 40
    grid_x0 = pad_left
    grid_y0 = pad_top
    grid_x1 = 1024 - pad_right
    grid_y1 = 768 - pad_bottom
    cell_w = (grid_x1 - grid_x0) // cols
    cell_h = (grid_y1 - grid_y0) // rows

    # Column labels (top)
    if col_labels:
        for c in range(cols):
            cx = grid_x0 + c * cell_w + cell_w // 2
            TC._text_centered(draw, (cx, pad_top - 28),
                              str(col_labels[c] if c < len(col_labels) else ""),
                              TC._font(24, bold=True))
    # Row labels (left)
    if row_labels:
        for r in range(rows):
            cy = grid_y0 + r * cell_h + cell_h // 2
            TC._text_centered(draw, (pad_left - 32, cy),
                              str(row_labels[r] if r < len(row_labels) else ""),
                              TC._font(24, bold=True))

    # Grid cells
    for r in range(rows):
        for c in range(cols):
            x0 = grid_x0 + c * cell_w
            y0 = grid_y0 + r * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            draw.rectangle((x0, y0, x1, y1),
                           outline=(40, 40, 40), width=2,
                           fill=(255, 255, 255))
            if cell_label_pattern:
                col_lab = col_labels[c] if (col_labels and c < len(col_labels)) else chr(ord("A") + c)
                row_lab = row_labels[r] if (row_labels and r < len(row_labels)) else str(r + 1)
                txt = (cell_label_pattern
                       .replace("{c}", str(col_lab))
                       .replace("{r}", str(row_lab)))
                TC._text_centered(draw, ((x0 + x1) // 2, (y0 + y1) // 2),
                                  txt, TC._font(22, bold=True))
    return canvas


def _compose_template_rich(title: str, sections: list[str]) -> "Image.Image":
    """Capstone template: title + N labeled sections in a strip layout."""
    from . import template_composers as TC
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)

    # Title
    draw.rectangle((40, 30, 984, 110), outline=(40, 40, 40), width=4,
                   fill=(240, 250, 240))
    TC._text_centered(draw, (512, 70), title, TC._font(34, bold=True))

    # Sections
    n = max(2, min(len(sections), 4))
    s_top = 140
    s_bot = 730
    s_h = (s_bot - s_top - 18 * (n - 1)) // n
    for i in range(n):
        y0 = s_top + i * (s_h + 18)
        y1 = y0 + s_h
        # Number circle
        draw.ellipse((50, y0 + s_h // 2 - 30, 110, y0 + s_h // 2 + 30),
                     outline=(40, 40, 40), width=4, fill=(255, 240, 200))
        TC._text_centered(draw, (80, y0 + s_h // 2),
                          str(i + 1), TC._font(28, bold=True))
        # Section box
        draw.rectangle((130, y0, 980, y1),
                       outline=(40, 40, 40), width=3, fill=(255, 255, 255))
        # Section label
        try:
            font = TC._font(24, bold=True)
            draw.text((150, y0 + 18),
                      sections[i] if i < len(sections) else "",
                      fill=(20, 20, 20), font=font)
        except Exception:
            pass
        # Drawing/writing space below the label
        draw.line([(150, y0 + 60), (960, y0 + 60)], fill=(180, 180, 180), width=1)
    return canvas


def _smart_fallback(image_id: str, unit_dir: "Path | None" = None) -> "Image.Image | None":
    """Produce a real composite for image_ids without a bespoke composer.

    Returns a PIL Image (caller marks used_placeholder=False) or None if
    the ID is too generic for a sensible composite (caller falls back to
    _placeholder gray box).

    When ``unit_dir`` is provided, looks up matching manipulative entries
    in 3_manipulatives.json for richer, unit-specific zone labels and
    keywords (added 2026-05-10 to address 86 visual_inspector missing_asset
    flags from over-generic compose_object_montage rectangles).
    """
    from . import template_composers as TC

    # ── Character portraits: CHAR_<KEY>_FRONT ──
    if image_id.startswith("CHAR_") and image_id.endswith("_FRONT"):
        key = image_id[5:-6]
        # ALWAYS prefer the hand-drawn SVG if it exists, regardless of whether
        # the key is in _CHARACTER_CLIPART. The CLIPART map only carries the
        # display name + stock-clipart fallback. Keys NOT in the map but WITH
        # an SVG used to fall through to a stock person card — fixed 2026-05-10
        # after visual_inspector flagged Mae, Theo, Buddy and others rendering
        # as identical generic line-art chefs.
        svg = _character_svg_path(key)
        if key in _CHARACTER_CLIPART:
            name, clip = _CHARACTER_CLIPART[key]
            if svg is not None:
                return _compose_custom_character_card(svg, name)
            return TC.compose_character_card(name=name, clipart_file=clip)
        # Unknown to the map: still try the SVG before falling back.
        if svg is not None:
            return _compose_custom_character_card(
                svg, key.replace("_", " ").title()
            )
        return TC.compose_character_card(
            name=key.replace("_", " ").title(),
            clipart_file="slide01_people_01.png",
        )

    # ── Reflection sheet (REF_*) ──
    if image_id == "REF_STARS":
        return _compose_star_rating()
    if image_id == "REF_YN_TABLE":
        return TC.compose_match_grid(
            left_items=["Q1", "Q2", "Q3", "Q4"],
            right_items=["YES / NO"] * 4,
            title="Reflection: did you do these things?",
        )
    if image_id in ("REF_FAV_BOX", "REF_TRICKY_BOX", "REF_NEXT_BOX"):
        prompts = {
            "REF_FAV_BOX": "My favourite part was...",
            "REF_TRICKY_BOX": "The trickiest part was...",
            "REF_NEXT_BOX": "Next I want to try...",
        }
        return _compose_reflection_box(prompts[image_id])

    # ── Formative check-in (FORM_*) ──
    if image_id.endswith("_FACES"):
        return _compose_face_rating()
    if image_id.startswith("FORM_"):
        return TC.compose_object_montage(
            objects=[(image_id.replace("_", " "), None)],
            title="Check-in prompt",
        )

    # ── Assessment suite (AS_*) ──
    if image_id == "AS_RUBRIC":
        return _compose_rubric_stub()
    if image_id.startswith("AS_FORM_TRACKER") or image_id == "AS_DIAG_TRACKER":
        return _compose_tracker_stub(image_id)
    if image_id.startswith("AS_CERT_BORDER") or image_id == "AS_CERT_FRIENDS":
        return TC.compose_certificate_scene(caption="Certificate of Achievement")
    if image_id.startswith("AS_CERT_"):
        # AS_CERT_<NAME> → reuse the unit's anchor character via _CHARACTER_CLIPART
        key = image_id[len("AS_CERT_"):]
        if key in _CHARACTER_CLIPART:
            name, clip = _CHARACTER_CLIPART[key]
            svg = _character_svg_path(key)
            if svg is not None:
                return _compose_custom_character_card(svg, name)
            return TC.compose_character_card(name=name, clipart_file=clip)
        return TC.compose_certificate_scene(caption="Certificate of Achievement")

    # ── Manipulatives (M*) by hint in the ID ──
    if image_id.startswith("M") and "_" in image_id:
        upper = image_id.upper()
        # Look up unit-specific manipulative metadata when available; this
        # populates real vocab/zones into the templates instead of generic
        # "Group A / B / C" placeholders.
        m_asset = _lookup_manipulative(unit_dir, image_id)
        m_name = (m_asset or {}).get("name", "") if m_asset else ""
        m_title = m_name or image_id.replace("_", " ").title()
        m_zones = _zones_from_manipulative(m_asset) if m_asset else []
        m_desc = ""
        if m_asset:
            m_desc = (m_asset.get("_placeholder") or {}).get("description", "") or ""

        # GRID detector: when description specifies an NxM grid AND the asset
        # is a "mat" / "grid" / "table" / "card grid" (no rich semantic zones
        # to render in 4 sections), draw an actual NxM grid instead of falling
        # to the labelled-template fallback.
        import re as _re
        grid_m = _re.search(r"(\d+)\s*[xX×]\s*(\d+)\s*grid", m_desc)
        if grid_m and any(k in upper for k in ("MAT", "FLOOR", "STRIP",
                                                "CODE_STRIPS", "STRIPS")):
            try:
                rows = int(grid_m.group(1))
                cols = int(grid_m.group(2))
                # Cap to a sensible visible grid (deck slide constraints)
                rows = min(max(rows, 2), 6)
                cols = min(max(cols, 2), 6)
                col_labels = None
                row_labels = None
                # Heuristic: "Letters A-D across columns" or numbers 1-N down rows
                if _re.search(r"Letters?\s+([A-Z])-([A-Z])\s+(?:across\s+)?columns",
                              m_desc, _re.IGNORECASE):
                    am = _re.search(r"Letters?\s+([A-Z])-([A-Z])\s+(?:across\s+)?columns",
                                     m_desc, _re.IGNORECASE)
                    a = am.group(1).upper()
                    b = am.group(2).upper()
                    col_labels = [chr(ord(a) + i)
                                  for i in range(min(cols, ord(b) - ord(a) + 1))]
                if _re.search(r"(\d+)-(\d+)\s+down\s+rows", m_desc):
                    rm = _re.search(r"(\d+)-(\d+)\s+down\s+rows", m_desc)
                    a = int(rm.group(1))
                    b = int(rm.group(2))
                    row_labels = [str(a + i) for i in range(min(rows, b - a + 1))]
                # For floor mats / blank strips, leave cells blank (just grid)
                pattern = None
                # For arrow-card grids: fill cells with the arrow direction
                if "arrow" in m_desc.lower() and (
                    "5 forward" in m_desc.lower() or
                    "5 back" in m_desc.lower() or
                    "5 left" in m_desc.lower()
                ):
                    # Use existing arrow-cards composer dispatch — leave None,
                    # let the smart_fallback fall through to the card path below.
                    grid_m = None  # Disable grid path; arrows handled elsewhere
                if grid_m:
                    return _compose_grid_paper(m_title, rows, cols,
                                                row_labels=row_labels,
                                                col_labels=col_labels,
                                                cell_label_pattern=pattern)
            except (ValueError, IndexError):
                pass

        if any(k in upper for k in ("POSTER", "ANCHOR")):
            # Always supply ≥4 zones so the rich poster has no empty
            # quadrants (visual_inspector flagged "labelled-but-empty
            # quadrants" when only 2-3 keywords were present).
            zones = list(m_zones or [])
            defaults = ["Vocabulary", "Examples", "Steps", "Key Idea"]
            for d in defaults:
                if len(zones) >= 4:
                    break
                if d not in zones:
                    zones.append(d)
            # Extract character SVGs from the description so M10 posters can
            # embed kawaii character art in their character zones (rather than
            # rendering an empty quadrant under the character's label).
            placeholder_desc = ""
            if m_asset:
                placeholder_desc = (m_asset.get("_placeholder") or {}).get(
                    "description", "") or ""
            char_paths = _extract_character_clipart_from_description(
                placeholder_desc)
            # Order the zones so that character names come first (so their
            # SVGs land in the leading slots), then non-character zones.
            char_zones: list[str] = []
            other_zones: list[str] = []
            for z in zones:
                z_upper_words = {w.upper() for w in z.split()
                                  if w and w[0].isalpha()}
                if any(_character_svg_path(w) is not None
                       for w in z_upper_words):
                    char_zones.append(z)
                else:
                    other_zones.append(z)
            ordered_zones = char_zones + other_zones
            ordered_zones = ordered_zones[:6]
            # Pad clipart_files: first N from char_paths, rest None
            clipart = list(char_paths)[:len(char_zones)]
            while len(clipart) < len(ordered_zones):
                clipart.append(None)
            return _compose_anchor_poster_rich(m_title, ordered_zones,
                                                clipart)
        if any(k in upper for k in ("CHART", "VOCAB")):
            # Always populate ≥6 entries to give 2 columns × 3 rows of real
            # content. Pad with educational defaults if the manipulative's
            # keywords/description yielded fewer.
            zones = list(m_zones or [])
            defaults = ["Definition", "Example", "Counter-example",
                        "Vocabulary", "Try It", "Key Idea"]
            for d in defaults:
                if len(zones) >= 6:
                    break
                if d not in zones:
                    zones.append(d)
            mid = max(2, len(zones) // 2)
            cols = [
                (zones[0] if zones else "Categories",
                 zones[1:mid] if mid > 1 else ["—"]),
                (zones[mid] if len(zones) > mid else "Examples",
                 zones[mid + 1:] if len(zones) > mid + 1 else ["—"]),
            ]
            return _compose_anchor_chart_rich(m_title, cols)
        if "MAT" in upper:
            zones = m_zones or ["Group A", "Group B", "Group C"]
            return TC.compose_sorting_mat(
                zones=zones[:4],
                title=m_title,
            )
        if any(k in upper for k in ("CARD", "TOKEN", "OUTCOME", "COUNTER",
                                      "STRIP", "STICKER", "PUPPET",
                                      "PIECE", "TILE", "BILL")):
            cards = list(m_zones or [])
            defaults = ["Card 1", "Card 2", "Card 3", "Card 4"]
            for d in defaults:
                if len(cards) >= 4:
                    break
                if d not in cards:
                    cards.append(d)
            objects = [(c[:18], None) for c in cards[:4]]
            return TC.compose_object_montage(
                objects=objects,
                title=m_title,
            )
        if any(k in upper for k in ("TEMPLATE", "CAPSTONE", "TRACKER",
                                      "WORKSHEET")):
            sections = list(m_zones or [])
            defaults = ["Section 1", "Section 2", "Section 3", "Section 4",
                        "Section 5"]
            for d in defaults:
                if len(sections) >= 4:
                    break
                if d not in sections:
                    sections.append(d)
            return _compose_template_rich(m_title, sections[:4])
        # Catch-all for any other M_ id (sheets, jars, decks, props, etc.)
        # — use the rich template composer with padded sections rather than
        # a single empty-bordered rectangle (visual_inspector flagged 30+
        # M_ slides as empty-watermark across rounds 4-5).
        cards = list(m_zones or [])
        defaults = ["Section 1", "Section 2", "Section 3", "Section 4"]
        for d in defaults:
            if len(cards) >= 4:
                break
            if d not in cards:
                cards.append(d)
        return _compose_template_rich(m_title, cards[:4])

    # ── Worksheets (WS*) ──
    if image_id.startswith("WS"):
        # Look up unit-specific worksheet metadata and render a proper
        # worksheet HERO: title + prompt sentence + blank grid workspace.
        # R21 caught the prior _compose_template_rich path leaking
        # "Read prompt / Try it / Show your work" debug stubs into student-
        # facing slides because the sentence-length filter rejected most
        # real instructions (30-100 chars) for being "too long".
        ws_title = ""
        ws_prompt = ""
        if unit_dir is not None:
            try:
                import re
                m = re.match(r"WS(\d+)_P(\d+)", image_id.upper())
                if m:
                    lesson_n, part_n = int(m.group(1)), int(m.group(2))
                    ws_path = unit_dir / f"2_worksheet_{lesson_n:02d}.json"
                    if ws_path.exists():
                        wsdata = json.loads(ws_path.read_text(encoding="utf-8"))
                        for page in wsdata.get("pages", []) or []:
                            for part in page.get("parts", []) or []:
                                if part.get("part_number") == part_n:
                                    ws_title = str(part.get("part_title") or "").strip()
                                    ws_prompt = str(part.get("student_instructions") or "").strip()
                                    break
                            if ws_title:
                                break
            except Exception:
                pass

        # Render: title bar + centered prompt + ruled workspace area
        from . import template_composers as TC
        canvas = TC._new(1024, 768)
        draw = ImageDraw.Draw(canvas)
        if not ws_title:
            ws_title = image_id.replace("_", " ").title()
        # Title bar (top)
        draw.rectangle((40, 30, 984, 110), outline=(40, 40, 40), width=4,
                       fill=(252, 248, 230))
        # Auto-fit title via textbbox so it doesn't clip
        title_pt = 30
        for pt in (30, 26, 22, 20, 18):
            try:
                bb = draw.textbbox((0, 0), ws_title, font=TC._font(pt, bold=True))
                if (bb[2] - bb[0]) <= 900:
                    title_pt = pt
                    break
            except Exception:
                pass
        TC._text_centered(draw, (512, 70), ws_title,
                          TC._font(title_pt, bold=True))
        # Prompt (centered just below title)
        if ws_prompt:
            # Wrap manually so prompt fits in 2 lines max
            words = ws_prompt.split()
            line = ""
            lines = []
            for w in words:
                test = (line + " " + w).strip()
                if len(test) <= 60:
                    line = test
                else:
                    lines.append(line)
                    line = w
                    if len(lines) >= 2:
                        break
            if line and len(lines) < 2:
                lines.append(line)
            for i, ln in enumerate(lines[:2]):
                TC._text_centered(draw, (512, 150 + i * 32), ln,
                                  TC._font(20))
        # Workspace area: ruled rectangle
        ws_top = 220 if ws_prompt else 150
        ws_bot = 730
        draw.rectangle((60, ws_top, 964, ws_bot),
                       outline=(40, 40, 40), width=4,
                       fill=(255, 255, 255))
        # Ruled lines for student writing/drawing
        for gy in range(ws_top + 50, ws_bot, 50):
            draw.line([(80, gy), (944, gy)],
                      fill=(225, 225, 225), width=1)
        return canvas

    # No sensible smart composite — caller uses _placeholder.
    return None


# ── Walk a unit and compose every image ───────────────────────────────────

def _collect_image_ids(unit_dir: Path) -> Iterable[str]:
    """Yield every image_id referenced anywhere in the unit's stage JSONs."""
    for path in sorted(unit_dir.glob("*.json")):
        if path.name in ("manifest.json", "input_row.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        yield from _walk_for_image_ids(data)


def _walk_for_image_ids(node) -> Iterable[str]:
    if isinstance(node, dict):
        if "image_placeholders" in node and isinstance(node["image_placeholders"], list):
            for ph in node["image_placeholders"]:
                if isinstance(ph, dict) and "id" in ph:
                    yield ph["id"]
        for v in node.values():
            yield from _walk_for_image_ids(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_for_image_ids(v)


def compose_for_unit(unit_dir: Path) -> dict:
    """
    Compose every image referenced in a unit's JSONs.
    Writes PNGs to <unit_dir>/composed/<image_id>.png.
    Returns a manifest mapping image_id -> path.

    Reads the unit's grade from `0_blueprint.json` and passes it to
    `compose_pattern_parade_image()` so grade-specific overrides fire for
    image IDs that are reused across grades with different content (e.g.,
    WS01_P2_PARADE = missing-cells in K, growing 2/4/6/8 in G2).
    """
    out_dir = unit_dir / "composed"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}

    # Read the blueprint's grade + subject + unit_id so grade-specific
    # overrides fire correctly, the phonics dispatcher is gated on
    # Language-only, and per-theme dispatchers gate on unit_id substring
    # match.
    grade: str | None = None
    subject: str | None = None
    unit_id: str | None = None
    bp_path = unit_dir / "0_blueprint.json"
    if bp_path.exists():
        try:
            bp = json.loads(bp_path.read_text(encoding="utf-8"))
            grade = bp.get("grade")
            subject = bp.get("subject")
            unit_id = bp.get("unit_id")
        except Exception:
            pass

    image_ids = sorted(set(_collect_image_ids(unit_dir)))
    placeholder_ids: list[str] = []
    print(f"Composing {len(image_ids)} images for {unit_dir.name} "
          f"(grade={grade!r}, subject={subject!r}, unit_id={unit_id!r})...")
    for image_id in image_ids:
        try:
            output_path = out_dir / f"{image_id}.png"
            compose_pattern_parade_image(image_id, output_path, grade=grade,
                                         subject=subject, unit_id=unit_id)
            manifest[image_id] = str(output_path)
            if getattr(compose_pattern_parade_image, "_last_was_placeholder", False):
                placeholder_ids.append(image_id)
        except Exception as e:
            print(f"  ! {image_id} failed: {e}")
            manifest[image_id] = None
    succeeded = sum(1 for v in manifest.values() if v)
    failed = sum(1 for v in manifest.values() if not v)
    print(f"  ✓ {succeeded} succeeded, {failed} failed, {len(placeholder_ids)} placeholders")
    # Persist a sidecar manifest so the visual-quality gate downstream
    # (validate_unit_for_slides + build_unit_deck) can detect placeholder
    # artwork and refuse to publish. Added 2026-05-03 — Counting Crew
    # shipped to Drive with every hero image as a labelled gray box because
    # the new narrative had no real composites; the gate now blocks this.
    from datetime import datetime, timezone
    sidecar = out_dir / ".composed_manifest.json"
    sidecar.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "succeeded": succeeded,
        "failed": failed,
        "placeholder_image_ids": sorted(placeholder_ids),
        "placeholder_count": len(placeholder_ids),
    }, indent=2) + "\n", encoding="utf-8")
    return manifest
