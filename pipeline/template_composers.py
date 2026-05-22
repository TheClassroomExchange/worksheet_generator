"""Generic procedural composers for K-G3 worksheet/manipulative hero images.

Added 2026-05-03 to close the placeholder-artwork gap that shipped with the
Counting Crew unit. Before this module existed, units with new narratives
(non-Pattern-Parade) had no real composers in pipeline/compose.py and every
hero image fell back to `_placeholder()` (a labelled gray rectangle), which
made every worksheet/manipulative slide visually empty.

These composers are NARRATIVE-AGNOSTIC. They take parameters (numbers, labels,
clipart filenames) and produce a polished hero PNG. Any unit that needs a
ten-frame, sorting mat, number path, quadrant grid, comparison strip, etc.
calls the matching function instead of writing bespoke code.

Conventions:
- All functions return a PIL.Image.
- Default canvas 1024×768 (slide-friendly 4:3); strip variants use 1024×500.
- White background, dark grey strokes, kid-friendly Lexend-equivalent fonts
  with system fallback. Black-and-white default; colour suggestions optional.
- Clipart pulled via `pipeline.clipart.absolute_path(filename)`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from . import clipart as _clipart


# ── Font resolution ───────────────────────────────────────────────────────

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = _FONT_CANDIDATES if not bold else (
        ["/System/Library/Fonts/Supplemental/Arial Black.ttf"] + _FONT_CANDIDATES
    )
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ── Canvas helpers ────────────────────────────────────────────────────────

def _new(width: int = 1024, height: int = 768, bg=(255, 255, 255)) -> Image.Image:
    return Image.new("RGB", (width, height), bg)


def _text_centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                   font: ImageFont.ImageFont, fill=(20, 20, 20)) -> None:
    draw.text(xy, text, font=font, fill=fill, anchor="mm")


def _paste_clipart(canvas: Image.Image, filename: str, box: tuple[int, int, int, int]) -> bool:
    """Paste a clipart PNG into `box` (x0,y0,x1,y1), preserving aspect ratio.
    Returns True if the clipart loaded; False if the filename wasn't found
    (falls back to a labelled rectangle so the caller can still produce a
    composite — we do NOT silently leave an empty hole)."""
    p = _clipart.absolute_path(filename)
    x0, y0, x1, y1 = box
    box_w, box_h = x1 - x0, y1 - y0
    if not p or not p.exists():
        # Sentinel: draw a thin-bordered rectangle with the missing filename
        # so the issue is visible during validation.
        d = ImageDraw.Draw(canvas)
        d.rectangle(box, outline=(170, 170, 170), width=2)
        _text_centered(d, ((x0 + x1) // 2, (y0 + y1) // 2),
                       f"missing:{filename}", _font(16))
        return False
    try:
        img = Image.open(p).convert("RGBA")
    except Exception:
        d = ImageDraw.Draw(canvas)
        d.rectangle(box, outline=(170, 170, 170), width=2)
        return False
    img.thumbnail((box_w, box_h), Image.LANCZOS)
    paste_x = x0 + (box_w - img.width) // 2
    paste_y = y0 + (box_h - img.height) // 2
    if img.mode == "RGBA":
        canvas.paste(img, (paste_x, paste_y), img)
    else:
        canvas.paste(img, (paste_x, paste_y))
    return True


# ── Composers ─────────────────────────────────────────────────────────────


def compose_character_card(name: str, role_text: str = "",
                           clipart_file: str | None = None) -> Image.Image:
    """Hero image for a character puppet slide. Centered illustration + name."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if clipart_file:
        _paste_clipart(canvas, clipart_file, (160, 100, 864, 540))
    else:
        # Fallback: framed text box
        draw.rectangle((160, 100, 864, 540), outline=(120, 120, 120), width=4)
        _text_centered(draw, (512, 320), name, _font(64, bold=True))
    # Name banner
    draw.rectangle((140, 580, 884, 670), fill=(245, 245, 245),
                   outline=(80, 80, 80), width=3)
    _text_centered(draw, (512, 625), name, _font(54, bold=True))
    if role_text:
        # Wrap to ≤55 chars per line
        if len(role_text) > 55:
            role_text = role_text[:52] + "…"
        _text_centered(draw, (512, 720), role_text, _font(22))
    return canvas


def compose_certificate_scene(clipart_file: str | None = None,
                              caption: str = "Certificate of Achievement") -> Image.Image:
    """Hero scene for AS_CERT_*: chefs/dog/etc. inside a decorative frame."""
    canvas = _new(1024, 768, bg=(252, 250, 240))
    draw = ImageDraw.Draw(canvas)
    # Decorative double border
    draw.rectangle((30, 30, 994, 738), outline=(180, 140, 60), width=6)
    draw.rectangle((50, 50, 974, 718), outline=(220, 170, 80), width=2)
    if clipart_file:
        _paste_clipart(canvas, clipart_file, (180, 130, 844, 560))
    _text_centered(draw, (512, 645), caption, _font(38, bold=True), fill=(120, 80, 30))
    return canvas


def compose_ten_frame_grid(rows: int = 2, cols: int = 5,
                           filled: list[bool] | None = None,
                           label: str | None = None) -> Image.Image:
    """A ten-frame manipulative: 2×5 grid of cells, optionally pre-filled
    with a counter (filled[i] True = dot in cell i, reading L→R top→bottom)."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if label:
        _text_centered(draw, (512, 60), label, _font(40, bold=True))
        top = 130
    else:
        top = 100
    grid_w, grid_h = 800, 320
    cell_w = grid_w // cols
    cell_h = grid_h // rows
    left = (1024 - grid_w) // 2
    # Draw grid cells
    for r in range(rows):
        for c in range(cols):
            x0 = left + c * cell_w
            y0 = top + r * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4)
            if filled and (r * cols + c) < len(filled) and filled[r * cols + c]:
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                radius = min(cell_w, cell_h) // 3
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                             fill=(40, 40, 40))
    # Bottom note
    bottom_y = top + grid_h + 60
    _text_centered(draw, (512, bottom_y),
                   f"Ten-Frame: {rows} × {cols} cells", _font(26))
    return canvas


def compose_two_ten_frames(target: int, decomp_a: tuple[int, int],
                           decomp_b: tuple[int, int] | None = None,
                           label: str | None = None) -> Image.Image:
    """Two ten-frames side-by-side showing two compositions of `target`."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    title = label or f"Two ways to make {target}"
    _text_centered(draw, (512, 60), title, _font(40, bold=True))

    def draw_one_frame(left_x: int, top_y: int, decomp: tuple[int, int], lbl: str):
        a, b = decomp
        cols = 5
        cell_w = 70
        cell_h = 70
        # 2 rows × 5 cols
        for r in range(2):
            for c in range(cols):
                x0 = left_x + c * cell_w
                y0 = top_y + r * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h
                draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=3)
                idx = r * cols + c
                if idx < a:
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    radius = 22
                    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                                 fill=(200, 60, 60))
                elif idx < a + b:
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    radius = 22
                    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                                 fill=(220, 200, 50))
        _text_centered(draw, (left_x + (cols * cell_w) // 2, top_y - 30),
                       lbl, _font(28, bold=True))
        _text_centered(draw, (left_x + (cols * cell_w) // 2, top_y + 2 * cell_h + 30),
                       f"{a} red  +  {b} yellow  =  {a + b}", _font(24))

    draw_one_frame(80, 200, decomp_a, "Way 1")
    if decomp_b:
        draw_one_frame(580, 200, decomp_b, "Way 2")
    else:
        # Single frame variant — show centered
        pass
    return canvas


def compose_sorting_mat(zones: list[str],
                        zone_clipart: list[str | None] | None = None,
                        title: str = "Sorting Mat") -> Image.Image:
    """A labelled sorting mat with N zones across (default 3 or 4).
    Each zone gets a label and optional clipart icon."""
    n = len(zones)
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 60), title, _font(40, bold=True))
    margin = 40
    grid_top = 130
    grid_bottom = 700
    zone_w = (1024 - 2 * margin) // n
    for i, label in enumerate(zones):
        x0 = margin + i * zone_w
        x1 = x0 + zone_w - 8
        y0 = grid_top
        y1 = grid_bottom
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4)
        # Label banner
        draw.rectangle((x0, y0, x1, y0 + 70), fill=(240, 240, 240))
        _text_centered(draw, ((x0 + x1) // 2, y0 + 35),
                       label, _font(26, bold=True))
        # Optional zone icon
        if zone_clipart and i < len(zone_clipart) and zone_clipart[i]:
            icon_box = (x0 + 30, y0 + 100, x1 - 30, y0 + 350)
            _paste_clipart(canvas, zone_clipart[i], icon_box)
    return canvas


def compose_quadrant_grid(quadrants: list[tuple[str, str | None]],
                          title: str = "") -> Image.Image:
    """Four-quadrant grid with labels; each quadrant is (label, clipart_file).
    Shape: 2×2."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        _text_centered(draw, (512, 50), title, _font(38, bold=True))
        top = 110
    else:
        top = 50
    bottom = 730
    margin_x = 40
    grid_w = 1024 - 2 * margin_x
    half_w = grid_w // 2
    half_h = (bottom - top) // 2
    for i in range(4):
        col = i % 2
        row = i // 2
        x0 = margin_x + col * half_w
        y0 = top + row * half_h
        x1 = x0 + half_w - 8
        y1 = y0 + half_h - 8
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4)
        # Banner
        draw.rectangle((x0, y0, x1, y0 + 60), fill=(240, 240, 240))
        label, clip = quadrants[i] if i < len(quadrants) else ("", None)
        _text_centered(draw, ((x0 + x1) // 2, y0 + 30),
                       label, _font(24, bold=True))
        if clip:
            _paste_clipart(canvas, clip, (x0 + 25, y0 + 80, x1 - 25, y1 - 25))
    return canvas


def compose_compare_strip(left_label: str = "GROUP A",
                          right_label: str = "GROUP B",
                          options: list[str] | None = None) -> Image.Image:
    """Comparison strip: two labelled cells on top, MORE/LESS/EQUAL chooser below."""
    if options is None:
        options = ["MORE", "LESS", "EQUAL"]
    canvas = _new(1024, 500)
    draw = ImageDraw.Draw(canvas)
    # Top row: two cells
    cell_w = 460
    cell_h = 220
    margin = 40
    for i, lbl in enumerate([left_label, right_label]):
        x0 = margin + i * (cell_w + 24)
        x1 = x0 + cell_w
        y0 = 30
        y1 = y0 + cell_h
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4)
        # Banner
        draw.rectangle((x0, y0, x1, y0 + 50), fill=(240, 240, 240))
        _text_centered(draw, ((x0 + x1) // 2, y0 + 25),
                       lbl, _font(28, bold=True))
    # Bottom row: option pills
    opt_w = 280
    opt_h = 110
    opt_top = 320
    spacing = (1024 - len(options) * opt_w) // (len(options) + 1)
    for i, opt in enumerate(options):
        x0 = spacing + i * (opt_w + spacing)
        x1 = x0 + opt_w
        y0 = opt_top
        y1 = y0 + opt_h
        draw.rounded_rectangle((x0, y0, x1, y1),
                               radius=40, outline=(40, 40, 40), width=4,
                               fill=(252, 248, 220))
        _text_centered(draw, ((x0 + x1) // 2, (y0 + y1) // 2),
                       opt, _font(36, bold=True))
    return canvas


def compose_number_path(start: int = 0, end: int = 20,
                        arrow_color: tuple[int, int, int] = (60, 160, 60),
                        arrow_label: str = "FORWARD",
                        with_footprints: bool = True) -> Image.Image:
    """Number path tile strip: numerals 0…20 with directional arrow."""
    canvas = _new(1024, 500)
    draw = ImageDraw.Draw(canvas)
    # Arrow banner at top
    draw.rectangle((40, 30, 984, 100), outline=arrow_color, width=4,
                   fill=tuple(min(255, c + 180) for c in arrow_color))
    # Arrow head pointing right (or left for backward — caller chooses by passing reversed start/end)
    if start <= end:
        # Right-pointing arrow head
        draw.polygon([(940, 65), (980, 65), (970, 50)], fill=arrow_color)
        draw.polygon([(940, 65), (980, 65), (970, 80)], fill=arrow_color)
    else:
        draw.polygon([(70, 65), (40, 65), (50, 50)], fill=arrow_color)
        draw.polygon([(70, 65), (40, 65), (50, 80)], fill=arrow_color)
    _text_centered(draw, (512, 65), arrow_label, _font(28, bold=True), fill=arrow_color)
    # Number tiles
    nums = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
    n = len(nums)
    tile_w = 920 // n
    tile_h = 140
    tile_top = 160
    for i, num in enumerate(nums):
        x0 = 50 + i * tile_w
        x1 = x0 + tile_w - 4
        y0 = tile_top
        y1 = y0 + tile_h
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=3)
        _text_centered(draw, ((x0 + x1) // 2, (y0 + y1) // 2),
                       str(num), _font(34, bold=True))
        if with_footprints:
            fy = y1 + 20
            draw.ellipse(((x0 + x1) // 2 - 14, fy, (x0 + x1) // 2 + 14, fy + 26),
                         fill=(180, 140, 90))
    # Tag
    _text_centered(draw, (512, 460),
                   f"Counting {arrow_label.lower()} from {start} to {end}",
                   _font(22))
    return canvas


def compose_number_card(number: int | str, label: str | None = None,
                        with_quantity_dots: bool = False) -> Image.Image:
    """A single number card. Optionally shows the matching dot quantity."""
    canvas = _new(700, 700)
    draw = ImageDraw.Draw(canvas)
    # Card border
    draw.rounded_rectangle((40, 40, 660, 660), radius=24,
                           outline=(40, 40, 40), width=6,
                           fill=(252, 252, 245))
    if label:
        _text_centered(draw, (350, 110), label, _font(28, bold=True))
        num_y = 350
    else:
        num_y = 300
    _text_centered(draw, (350, num_y), str(number), _font(220, bold=True))
    if with_quantity_dots and isinstance(number, int) and 0 < number <= 10:
        # Render `number` dots in a row at bottom
        dot_y = 530
        spacing = 480 // max(number, 1)
        for i in range(number):
            cx = 350 - (number - 1) * spacing // 2 + i * spacing
            draw.ellipse((cx - 18, dot_y - 18, cx + 18, dot_y + 18),
                         fill=(40, 40, 40))
    return canvas


def compose_match_grid(left_items: list[str | int],
                       right_items: list[str | int],
                       title: str = "Match the pairs") -> Image.Image:
    """Match-the-pairs grid: left column of labels, right column of labels,
    children draw lines between matching pairs."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 50), title, _font(36, bold=True))
    n = max(len(left_items), len(right_items))
    row_h = 580 // n
    item_top = 110
    for i in range(n):
        cy = item_top + i * row_h + row_h // 2
        # Left item (number)
        if i < len(left_items):
            x0 = 110
            x1 = 320
            y0 = cy - 50
            y1 = cy + 50
            draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4,
                           fill=(252, 250, 240))
            _text_centered(draw, ((x0 + x1) // 2, cy),
                           str(left_items[i]), _font(60, bold=True))
        # Right item (quantity dots or label)
        if i < len(right_items):
            x0 = 700
            x1 = 910
            y0 = cy - 50
            y1 = cy + 50
            draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=4,
                           fill=(255, 252, 230))
            r = right_items[i]
            if isinstance(r, int) and 0 < r <= 10:
                # Render r dots
                spacing = min(28, 180 // max(r, 1))
                start_x = (x0 + x1) // 2 - (r - 1) * spacing // 2
                for k in range(r):
                    dx = start_x + k * spacing
                    draw.ellipse((dx - 10, cy - 10, dx + 10, cy + 10),
                                 fill=(40, 40, 40))
            else:
                _text_centered(draw, ((x0 + x1) // 2, cy),
                               str(r), _font(36, bold=True))
        # Connector dots in between
        draw.ellipse((325, cy - 8, 341, cy + 8), fill=(120, 120, 120))
        draw.ellipse((683, cy - 8, 699, cy + 8), fill=(120, 120, 120))
    return canvas


def compose_tracing_grid(numbers: Iterable[int] = range(0, 11),
                         title: str = "Trace and Write") -> Image.Image:
    """Tracing grid: rows of numerals + blank tracing lanes."""
    nums = list(numbers)
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 50), title, _font(36, bold=True))
    rows = len(nums)
    if rows == 0:
        return canvas
    row_h = 580 // max(rows, 1)
    top = 110
    for i, n in enumerate(nums):
        y = top + i * row_h
        # Numeral on left
        draw.rectangle((40, y + 8, 140, y + row_h - 8),
                       outline=(40, 40, 40), width=3, fill=(248, 248, 248))
        _text_centered(draw, (90, y + row_h // 2), str(n), _font(48, bold=True))
        # Tracing lanes (3 ghost numerals + 1 blank)
        for k in range(4):
            x0 = 170 + k * 200
            x1 = x0 + 180
            draw.rectangle((x0, y + 8, x1, y + row_h - 8),
                           outline=(180, 180, 180), width=2)
            if k < 3:
                _text_centered(draw, ((x0 + x1) // 2, y + row_h // 2),
                               str(n), _font(48, bold=True), fill=(200, 200, 200))
    return canvas


def compose_object_montage(objects: list[str | tuple[str, str | None]],
                           title: str = "") -> Image.Image:
    """Montage of objects/clipart in a row — for 'sort cards' / 'plates' /
    'muffin tray' type slides. Each object is either a label string OR a
    (label, clipart_file) tuple. Up to 6 objects per row."""
    canvas = _new(1024, 600)
    draw = ImageDraw.Draw(canvas)
    if title:
        _text_centered(draw, (512, 50), title, _font(36, bold=True))
        top = 110
    else:
        top = 60
    n = len(objects)
    if n == 0:
        return canvas
    cell_w = (1024 - 80) // n
    cell_h = 380
    for i, obj in enumerate(objects):
        x0 = 40 + i * cell_w
        x1 = x0 + cell_w - 12
        y0 = top
        y1 = y0 + cell_h
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=3,
                       fill=(252, 252, 248))
        if isinstance(obj, tuple):
            label, clip = obj
        else:
            label, clip = obj, None
        if clip:
            _paste_clipart(canvas, clip, (x0 + 20, y0 + 20, x1 - 20, y1 - 70))
        # Bottom label
        _text_centered(draw, ((x0 + x1) // 2, y1 - 30),
                       label, _font(22, bold=True))
    return canvas


def compose_speech_bubble(character_clipart: str | None, speech_text: str,
                          character_name: str = "") -> Image.Image:
    """Character with a speech bubble. Character left, bubble right."""
    canvas = _new(1024, 600)
    draw = ImageDraw.Draw(canvas)
    if character_clipart:
        _paste_clipart(canvas, character_clipart, (40, 80, 380, 520))
    else:
        draw.rectangle((40, 80, 380, 520), outline=(120, 120, 120), width=3)
        if character_name:
            _text_centered(draw, (210, 300), character_name, _font(36, bold=True))
    # Speech bubble
    bubble = (440, 100, 980, 460)
    draw.rounded_rectangle(bubble, radius=40,
                           outline=(40, 40, 40), width=4,
                           fill=(255, 252, 240))
    # Tail
    draw.polygon([(440, 280), (390, 320), (440, 350)],
                 outline=(40, 40, 40), fill=(255, 252, 240))
    draw.line([(440, 280), (390, 320), (440, 350)], fill=(40, 40, 40), width=4)
    # Wrap speech text into ~28-char lines
    words = speech_text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= 28:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # Render lines
    line_y = 160
    for ln in lines[:7]:
        _text_centered(draw, (710, line_y), ln, _font(28))
        line_y += 40
    return canvas


def compose_paw_print_groups(group_sizes: list[int],
                             title: str = "How many paw prints?") -> Image.Image:
    """Buddy-style: each row shows a group of N paw prints; child writes total."""
    canvas = _new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 50), title, _font(36, bold=True))
    rows = len(group_sizes)
    if rows == 0:
        return canvas
    row_h = 600 // rows
    top = 110
    for i, size in enumerate(group_sizes):
        y = top + i * row_h + row_h // 2
        # Render `size` paw prints
        spacing = min(60, 700 // max(size, 1))
        start_x = 80 + (700 - (size - 1) * spacing) // 2
        for k in range(size):
            cx = start_x + k * spacing
            # Paw shape
            draw.ellipse((cx - 16, y - 4, cx + 16, y + 22),
                         fill=(80, 50, 30))
            # toes
            for tx, ty in [(-12, -16), (-4, -22), (4, -22), (12, -16)]:
                draw.ellipse((cx + tx - 5, y + ty - 5, cx + tx + 5, y + ty + 5),
                             fill=(80, 50, 30))
        # Total box on right
        draw.rectangle((860, y - 32, 970, y + 32),
                       outline=(40, 40, 40), width=4)
        # We deliberately leave the total blank — the worksheet asks the
        # child to write it.
    return canvas


def compose_subitize_card_set(standard_counts: list[int] = (1, 2, 3, 4, 5),
                              random_counts: list[int] = (1, 2, 3, 4, 5),
                              title: str = "Subitizing dot cards") -> Image.Image:
    """Two rows of subitize dot cards: standard dice patterns + random patterns.
    Renders procedurally so the whole set fits on one slide."""
    canvas = _new(1024, 600)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 40), title, _font(32, bold=True))
    # Two rows of 5 cards
    DICE_POSITIONS = {
        1: [(0.5, 0.5)],
        2: [(0.3, 0.3), (0.7, 0.7)],
        3: [(0.3, 0.3), (0.5, 0.5), (0.7, 0.7)],
        4: [(0.3, 0.3), (0.7, 0.3), (0.3, 0.7), (0.7, 0.7)],
        5: [(0.3, 0.3), (0.7, 0.3), (0.5, 0.5), (0.3, 0.7), (0.7, 0.7)],
    }
    RANDOM_POSITIONS = {
        1: [(0.4, 0.6)],
        2: [(0.3, 0.4), (0.65, 0.35)],
        3: [(0.35, 0.35), (0.6, 0.45), (0.45, 0.7)],
        4: [(0.3, 0.3), (0.7, 0.4), (0.4, 0.7), (0.7, 0.75)],
        5: [(0.3, 0.3), (0.6, 0.35), (0.4, 0.55), (0.7, 0.65), (0.5, 0.85)],
    }
    card_w = 170
    card_h = 220
    gap = 12
    total_w = 5 * card_w + 4 * gap
    start_x = (1024 - total_w) // 2

    def draw_card(x: int, y: int, count: int, positions_map: dict, label: str):
        draw.rectangle((x, y, x + card_w, y + card_h),
                       outline=(40, 40, 40), width=4,
                       fill=(252, 252, 245))
        positions = positions_map[count]
        for px, py in positions:
            cx = x + int(card_w * px)
            cy = y + int(card_h * py * 0.85) + 10
            radius = 18
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         fill=(40, 40, 40))
        _text_centered(draw, (x + card_w // 2, y + card_h - 18),
                       label, _font(16))

    # Row 1: standard dice
    y_row1 = 90
    for i, c in enumerate(standard_counts):
        draw_card(start_x + i * (card_w + gap), y_row1, c, DICE_POSITIONS, f"DICE {c}")
    # Row 2: random
    y_row2 = y_row1 + card_h + 30
    for i, c in enumerate(random_counts):
        draw_card(start_x + i * (card_w + gap), y_row2, c, RANDOM_POSITIONS, f"RANDOM {c}")
    return canvas


def compose_sorting_boxes(boxes: list[str], title: str = "Sort the cards") -> Image.Image:
    """Simple labelled sorting boxes (like a 2-column or 3-column grid for
    sorting where things go)."""
    return compose_sorting_mat(zones=boxes, title=title)


def compose_blank_pair(title: str = "Draw your own",
                       left_label: str = "Plate A",
                       right_label: str = "Plate B") -> Image.Image:
    """Two large blank plates/circles for child to draw in."""
    canvas = _new(1024, 600)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 40), title, _font(36, bold=True))
    # Left plate
    draw.ellipse((90, 130, 470, 510), outline=(40, 40, 40), width=5,
                 fill=(255, 250, 240))
    _text_centered(draw, (280, 540), left_label, _font(28, bold=True))
    # Right plate
    draw.ellipse((554, 130, 934, 510), outline=(40, 40, 40), width=5,
                 fill=(240, 250, 255))
    _text_centered(draw, (744, 540), right_label, _font(28, bold=True))
    return canvas


def compose_teen_tens_stick(target: int = 15) -> Image.Image:
    """Tens-stick (10 cubes) + extras visualising a teen number."""
    canvas = _new(1024, 600)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 40), f"Teen visual: {target}", _font(36, bold=True))
    # Tens stick (10 stacked cubes vertically)
    cube_w = 80
    cube_h = 50
    stick_x = 200
    stick_top = 90
    for i in range(10):
        y0 = stick_top + i * cube_h
        draw.rectangle((stick_x, y0, stick_x + cube_w, y0 + cube_h),
                       outline=(40, 40, 40), width=3, fill=(220, 230, 250))
    _text_centered(draw, (stick_x + cube_w // 2, stick_top + 10 * cube_h + 25),
                   "TEN", _font(24, bold=True))
    # Extras (target - 10 cubes)
    extras = max(0, min(9, target - 10))
    extra_x = 460
    for i in range(extras):
        y0 = stick_top + i * cube_h
        draw.rectangle((extra_x, y0, extra_x + cube_w, y0 + cube_h),
                       outline=(40, 40, 40), width=3, fill=(255, 230, 200))
    _text_centered(draw, (extra_x + cube_w // 2, stick_top + max(extras, 1) * cube_h + 25),
                   f"+ {extras}", _font(24, bold=True))
    # Total
    _text_centered(draw, (820, 300), f"= {target}", _font(72, bold=True))
    return canvas


def compose_number_line_blank(start: int = 0, end: int = 20,
                              blanks: list[int] | None = None,
                              title: str = "Fill in the missing numbers") -> Image.Image:
    """A number line 0…20 with some cells empty for the child to fill in."""
    canvas = _new(1024, 400)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 40), title, _font(32, bold=True))
    nums = list(range(start, end + 1))
    n = len(nums)
    cell_w = 940 // n
    cell_h = 100
    top = 130
    blanks_set = set(blanks or [])
    for i, num in enumerate(nums):
        x0 = 42 + i * cell_w
        x1 = x0 + cell_w - 4
        y0 = top
        y1 = y0 + cell_h
        draw.rectangle((x0, y0, x1, y1), outline=(40, 40, 40), width=3)
        if num not in blanks_set:
            _text_centered(draw, ((x0 + x1) // 2, (y0 + y1) // 2),
                           str(num), _font(28, bold=True))
    _text_centered(draw, (512, 280),
                   f"Numbers from {start} to {end}", _font(22))
    return canvas


def compose_face_tracker_grid(title: str = "How did it go?") -> Image.Image:
    """3-face Likert tracker: happy / neutral / sad."""
    canvas = _new(1024, 500)
    draw = ImageDraw.Draw(canvas)
    _text_centered(draw, (512, 40), title, _font(36, bold=True))
    faces = ["GOT IT", "ALMOST", "TRY AGAIN"]
    colors = [(80, 180, 80), (220, 200, 60), (220, 100, 100)]
    spacing = 1024 // 4
    for i, (lbl, col) in enumerate(zip(faces, colors)):
        cx = spacing + i * spacing - spacing // 2 + spacing // 2  # evenly distributed
        cx = (i + 1) * (1024 // 4)
        cy = 240
        r = 80
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col,
                     outline=(40, 40, 40), width=4)
        # Eyes
        for ex in (-30, 30):
            draw.ellipse((cx + ex - 8, cy - 25, cx + ex + 8, cy - 9),
                         fill=(40, 40, 40))
        # Mouth varies by face
        if i == 0:  # happy
            draw.arc((cx - 35, cy - 10, cx + 35, cy + 40),
                     start=0, end=180, fill=(40, 40, 40), width=5)
        elif i == 1:  # neutral
            draw.line((cx - 30, cy + 22, cx + 30, cy + 22), fill=(40, 40, 40), width=5)
        else:  # sad
            draw.arc((cx - 35, cy + 10, cx + 35, cy + 60),
                     start=180, end=360, fill=(40, 40, 40), width=5)
        _text_centered(draw, (cx, cy + 130), lbl, _font(22, bold=True))
    return canvas
