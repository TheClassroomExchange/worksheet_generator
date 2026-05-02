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

def compose_pattern_parade_image(image_id: str, output_path: Path,
                                 grade: str | None = None) -> Path:
    """Compose the named image and write it as PNG. Returns the output path.

    Some image IDs (e.g., WS01_P2_PARADE) are reused across grades with
    different content per grade. When `grade` is provided, grade-specific
    overrides are tried FIRST before the generic dispatcher. This lets G2
    show stacked-animal growing parades while K still shows missing-element
    repeating parades — same image_id, different recipe per grade.
    """
    image: Image.Image | None = None

    # ── Grade-specific overrides (try first; fall through if no match) ──
    if grade and image_id is not None:
        image = _compose_grade_override(image_id, grade)
        if image is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path, "PNG")
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
    elif image_id.startswith("M1_") and image_id.endswith("_CARD"):
        # M1_BEA_CARD, M1_FINN_CARD, etc. — single animal card
        animal = image_id.split("_")[1].lower()
        image = render_svg(asset(animal), width=240)
    elif image_id == "M2_PARADE_STRIP":
        image = render_svg(asset("parade_strip"), width=600)
    elif image_id.startswith("M3_"):
        # M3_CLAP, M3_STOMP, etc. — single icon card
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

    if image is None:
        # Fallback: a labelled placeholder rectangle
        image = _placeholder(image_id, width=400, height=120)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, "PNG")
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

    # Read the blueprint's grade so grade-specific overrides fire correctly.
    grade: str | None = None
    bp_path = unit_dir / "0_blueprint.json"
    if bp_path.exists():
        try:
            grade = json.loads(bp_path.read_text(encoding="utf-8")).get("grade")
        except Exception:
            grade = None

    image_ids = sorted(set(_collect_image_ids(unit_dir)))
    print(f"Composing {len(image_ids)} images for {unit_dir.name} "
          f"(grade={grade!r})...")
    for image_id in image_ids:
        try:
            output_path = out_dir / f"{image_id}.png"
            compose_pattern_parade_image(image_id, output_path, grade=grade)
            manifest[image_id] = str(output_path)
        except Exception as e:
            print(f"  ! {image_id} failed: {e}")
            manifest[image_id] = None
    print(f"  ✓ {sum(1 for v in manifest.values() if v)} succeeded, {sum(1 for v in manifest.values() if not v)} failed")
    return manifest
