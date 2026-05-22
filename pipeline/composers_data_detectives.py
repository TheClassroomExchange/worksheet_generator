"""Bespoke composers for the four Data Detectives units (k/g1/g2/g3).

Theme: data sorting → tally → pictograph → bar graph → ordering →
interpretation. Vocabulary across the four grades shares M1-M10 and
WS01-WS05 image_ids, so a single dispatcher covers all four with light
grade-aware variation.

Pattern follows pattern_parade composer.py:
  1. Tiny library of icon primitives (PIL-drawn small shapes).
  2. Composer functions that arrange primitives on a 1024x768 canvas.
  3. Per-image-id branches in `compose_data_detectives_image()` mapping
     each WS_/M_/AS_/FORM_/REF_/CHAR_ id to a recipe.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from . import template_composers as TC

# ── Primitive icons (PIL-drawn) ──────────────────────────────────────────

LINE_W = 3
LINE_W_THIN = 2

# Object primitives are drawn as B&W line art into a square box. Size is
# the pixel side of the bounding square.


def _icon_square(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
                 solid: bool = False) -> None:
    h = size // 2
    box = (cx - h, cy - h, cx + h, cy + h)
    if solid:
        draw.rectangle(box, fill=(20, 20, 20), outline=(20, 20, 20), width=LINE_W)
    else:
        draw.rectangle(box, fill=None, outline=(20, 20, 20), width=LINE_W)


def _icon_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
                 solid: bool = False) -> None:
    h = size // 2
    box = (cx - h, cy - h, cx + h, cy + h)
    if solid:
        draw.ellipse(box, fill=(20, 20, 20), outline=(20, 20, 20), width=LINE_W)
    else:
        draw.ellipse(box, fill=None, outline=(20, 20, 20), width=LINE_W)


def _icon_triangle(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
                   solid: bool = False) -> None:
    h = size // 2
    pts = [(cx, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    if solid:
        draw.polygon(pts, fill=(20, 20, 20), outline=(20, 20, 20))
    else:
        draw.polygon(pts, fill=None, outline=(20, 20, 20))
        # PIL polygon outline=1; reinforce
        draw.line(pts + [pts[0]], fill=(20, 20, 20), width=LINE_W)


def _icon_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
               solid: bool = False) -> None:
    R = size // 2
    r = R * 0.45
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    if solid:
        draw.polygon(pts, fill=(20, 20, 20), outline=(20, 20, 20))
    else:
        draw.polygon(pts, fill=None)
        draw.line(pts + [pts[0]], fill=(20, 20, 20), width=LINE_W_THIN)


def _icon_apple(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    body = (cx - h * 0.85, cy - h * 0.7, cx + h * 0.85, cy + h * 0.85)
    draw.ellipse(body, outline=(20, 20, 20), width=LINE_W)
    # stem
    draw.line([(cx, cy - h * 0.7), (cx + h * 0.2, cy - h * 1.0)],
              fill=(20, 20, 20), width=LINE_W_THIN)
    # leaf
    draw.polygon([(cx + h * 0.2, cy - h * 1.0),
                  (cx + h * 0.55, cy - h * 0.85),
                  (cx + h * 0.3, cy - h * 0.65)],
                 outline=(20, 20, 20))


def _icon_banana(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    # crescent banana approximated by two arcs
    box_outer = (cx - h, cy - h * 0.6, cx + h, cy + h * 0.9)
    draw.arc(box_outer, start=0, end=180, fill=(20, 20, 20), width=LINE_W)
    box_inner = (cx - h * 0.85, cy - h * 0.3, cx + h * 0.85, cy + h * 0.55)
    draw.arc(box_inner, start=0, end=180, fill=(20, 20, 20), width=LINE_W)
    # stem caps
    draw.line([(cx - h, cy + h * 0.15), (cx - h * 0.85, cy + h * 0.13)],
              fill=(20, 20, 20), width=LINE_W)
    draw.line([(cx + h, cy + h * 0.15), (cx + h * 0.85, cy + h * 0.13)],
              fill=(20, 20, 20), width=LINE_W)


def _icon_grape(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    # cluster of small circles
    h = size // 2
    r = h // 4
    coords = [
        (cx - r, cy - h * 0.5), (cx + r, cy - h * 0.5),
        (cx - 2 * r, cy - r * 0.2), (cx, cy - r * 0.2), (cx + 2 * r, cy - r * 0.2),
        (cx - r, cy + r * 0.6), (cx + r, cy + r * 0.6),
        (cx, cy + h * 0.7),
    ]
    for x, y in coords:
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(20, 20, 20), width=LINE_W_THIN)
    # stem
    draw.line([(cx, cy - h * 0.5), (cx, cy - h)], fill=(20, 20, 20), width=LINE_W_THIN)


def _icon_dog(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    # head
    draw.ellipse((cx - h * 0.7, cy - h * 0.6, cx + h * 0.7, cy + h * 0.5),
                 outline=(20, 20, 20), width=LINE_W)
    # ears
    draw.polygon([(cx - h * 0.7, cy - h * 0.4),
                  (cx - h * 0.95, cy - h * 0.0),
                  (cx - h * 0.5, cy - h * 0.1)],
                 outline=(20, 20, 20))
    draw.polygon([(cx + h * 0.7, cy - h * 0.4),
                  (cx + h * 0.95, cy - h * 0.0),
                  (cx + h * 0.5, cy - h * 0.1)],
                 outline=(20, 20, 20))
    # eyes
    draw.ellipse((cx - h * 0.32, cy - h * 0.2, cx - h * 0.18, cy - h * 0.05),
                 fill=(20, 20, 20))
    draw.ellipse((cx + h * 0.18, cy - h * 0.2, cx + h * 0.32, cy - h * 0.05),
                 fill=(20, 20, 20))
    # nose
    draw.ellipse((cx - h * 0.12, cy + h * 0.1, cx + h * 0.12, cy + h * 0.25),
                 fill=(20, 20, 20))
    # smile
    draw.arc((cx - h * 0.25, cy + h * 0.18, cx + h * 0.25, cy + h * 0.42),
             start=20, end=160, fill=(20, 20, 20), width=LINE_W_THIN)


def _icon_cat(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    # head
    draw.ellipse((cx - h * 0.7, cy - h * 0.55, cx + h * 0.7, cy + h * 0.55),
                 outline=(20, 20, 20), width=LINE_W)
    # pointy ears
    draw.polygon([(cx - h * 0.55, cy - h * 0.4),
                  (cx - h * 0.75, cy - h * 0.95),
                  (cx - h * 0.25, cy - h * 0.55)],
                 outline=(20, 20, 20))
    draw.polygon([(cx + h * 0.55, cy - h * 0.4),
                  (cx + h * 0.75, cy - h * 0.95),
                  (cx + h * 0.25, cy - h * 0.55)],
                 outline=(20, 20, 20))
    # eyes
    draw.ellipse((cx - h * 0.32, cy - h * 0.15, cx - h * 0.16, cy + h * 0.1),
                 outline=(20, 20, 20), width=LINE_W_THIN)
    draw.ellipse((cx + h * 0.16, cy - h * 0.15, cx + h * 0.32, cy + h * 0.1),
                 outline=(20, 20, 20), width=LINE_W_THIN)
    draw.ellipse((cx - h * 0.27, cy - h * 0.05, cx - h * 0.21, cy + h * 0.05),
                 fill=(20, 20, 20))
    draw.ellipse((cx + h * 0.21, cy - h * 0.05, cx + h * 0.27, cy + h * 0.05),
                 fill=(20, 20, 20))
    # nose triangle
    draw.polygon([(cx - h * 0.08, cy + h * 0.15),
                  (cx + h * 0.08, cy + h * 0.15),
                  (cx, cy + h * 0.25)], fill=(20, 20, 20))
    # whiskers
    for sign in (-1, 1):
        for dy in (-h * 0.05, h * 0.05):
            draw.line([(cx + sign * h * 0.1, cy + h * 0.22 + dy),
                       (cx + sign * h * 0.55, cy + h * 0.22 + dy)],
                      fill=(20, 20, 20), width=LINE_W_THIN)


def _icon_fish(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    # body
    draw.ellipse((cx - h * 0.7, cy - h * 0.4, cx + h * 0.5, cy + h * 0.4),
                 outline=(20, 20, 20), width=LINE_W)
    # tail
    draw.polygon([(cx + h * 0.5, cy),
                  (cx + h, cy - h * 0.45),
                  (cx + h, cy + h * 0.45)], outline=(20, 20, 20))
    # eye
    draw.ellipse((cx - h * 0.55, cy - h * 0.18, cx - h * 0.4, cy - h * 0.03),
                 fill=(20, 20, 20))


def _icon_bird(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    h = size // 2
    # body
    draw.ellipse((cx - h * 0.6, cy - h * 0.3, cx + h * 0.55, cy + h * 0.5),
                 outline=(20, 20, 20), width=LINE_W)
    # head
    draw.ellipse((cx - h * 0.95, cy - h * 0.55, cx - h * 0.4, cy - h * 0.05),
                 outline=(20, 20, 20), width=LINE_W)
    # beak
    draw.polygon([(cx - h * 0.95, cy - h * 0.32),
                  (cx - h * 1.2, cy - h * 0.28),
                  (cx - h * 0.95, cy - h * 0.18)], fill=(20, 20, 20))
    # eye
    draw.ellipse((cx - h * 0.7, cy - h * 0.4, cx - h * 0.62, cy - h * 0.32),
                 fill=(20, 20, 20))
    # legs
    for x in (cx - h * 0.15, cx + h * 0.15):
        draw.line([(x, cy + h * 0.5), (x, cy + h * 0.85)],
                  fill=(20, 20, 20), width=LINE_W_THIN)


_ICON_DRAWERS = {
    "square_solid":  lambda d, cx, cy, sz: _icon_square(d, cx, cy, sz, solid=True),
    "square_hollow": lambda d, cx, cy, sz: _icon_square(d, cx, cy, sz, solid=False),
    "circle_solid":  lambda d, cx, cy, sz: _icon_circle(d, cx, cy, sz, solid=True),
    "circle_hollow": lambda d, cx, cy, sz: _icon_circle(d, cx, cy, sz, solid=False),
    "triangle":      lambda d, cx, cy, sz: _icon_triangle(d, cx, cy, sz, solid=False),
    "star":          lambda d, cx, cy, sz: _icon_star(d, cx, cy, sz, solid=False),
    "apple":   _icon_apple,
    "banana":  _icon_banana,
    "grape":   _icon_grape,
    "dog":     _icon_dog,
    "cat":     _icon_cat,
    "fish":    _icon_fish,
    "bird":    _icon_bird,
}


def draw_icon(canvas: Image.Image, kind: str, cx: int, cy: int, size: int = 60) -> None:
    drawer = _ICON_DRAWERS.get(kind)
    if drawer is None:
        return
    d = ImageDraw.Draw(canvas)
    drawer(d, cx, cy, size)


# ── Tally helpers ─────────────────────────────────────────────────────────

def _draw_tally(draw: ImageDraw.ImageDraw, x: int, y: int, count: int,
                bar_h: int = 28, bar_gap: int = 6, bundle_gap: int = 14) -> int:
    """Draw `count` tally marks starting at (x, y). Bundles of 5 = 4 verticals
    crossed by a diagonal. Returns the right edge x-coordinate."""
    cur_x = x
    full_bundles = count // 5
    rem = count % 5
    for _ in range(full_bundles):
        for i in range(4):
            draw.line([(cur_x + i * bar_gap, y),
                       (cur_x + i * bar_gap, y + bar_h)],
                      fill=(20, 20, 20), width=LINE_W)
        # diagonal
        draw.line([(cur_x - 4, y + bar_h - 4),
                   (cur_x + 3 * bar_gap + 4, y + 4)],
                  fill=(20, 20, 20), width=LINE_W)
        cur_x += 3 * bar_gap + bundle_gap
    for i in range(rem):
        draw.line([(cur_x, y), (cur_x, y + bar_h)],
                  fill=(20, 20, 20), width=LINE_W)
        cur_x += bar_gap
    return cur_x


# ── Composers ─────────────────────────────────────────────────────────────

def compose_object_pile(objects: list[str], title: str = "",
                        below_boxes: list[str] | None = None) -> Image.Image:
    """A scattered pile of object icons + optional labelled empty bins below."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
        top = 100
    else:
        top = 60
    # Pile area
    pile_y0, pile_y1 = top, top + 240
    pile_x0, pile_x1 = 110, 914
    rng = random.Random(len(objects))
    icon_size = 64
    for i, kind in enumerate(objects):
        # scatter loosely with some grid bias to avoid heavy overlap
        cols = max(1, int(math.sqrt(len(objects) * (pile_x1 - pile_x0) /
                                    (pile_y1 - pile_y0))))
        col = i % cols
        row = i // cols
        cell_w = (pile_x1 - pile_x0) / cols
        rows = max(1, math.ceil(len(objects) / cols))
        cell_h = (pile_y1 - pile_y0) / rows
        cx = int(pile_x0 + cell_w * (col + 0.5) + rng.randint(-22, 22))
        cy = int(pile_y0 + cell_h * (row + 0.5) + rng.randint(-18, 18))
        draw_icon(canvas, kind, cx, cy, size=icon_size)

    if below_boxes:
        # Two side-by-side empty bins, labelled
        n = len(below_boxes)
        gap = 30
        box_w = (1024 - 2 * 90 - gap * (n - 1)) // n
        bin_y0 = pile_y1 + 50
        bin_y1 = bin_y0 + 220
        for i, label in enumerate(below_boxes):
            x0 = 90 + i * (box_w + gap)
            x1 = x0 + box_w
            draw.rectangle((x0, bin_y0, x1, bin_y1),
                           outline=(20, 20, 20), width=4)
            TC._text_centered(draw, ((x0 + x1) // 2, bin_y0 - 22),
                              label, TC._font(28, bold=True))
    return canvas


def compose_sorting_bins(labels: list[str], title: str = "") -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 60), title, TC._font(38, bold=True))
        top = 130
    else:
        top = 90
    n = len(labels)
    gap = 30
    box_w = (1024 - 2 * 80 - gap * (n - 1)) // n
    box_h = 480
    for i, label in enumerate(labels):
        x0 = 80 + i * (box_w + gap)
        x1 = x0 + box_w
        TC._text_centered(draw, ((x0 + x1) // 2, top + 8),
                          label, TC._font(34, bold=True))
        draw.rectangle((x0, top + 50, x1, top + 50 + box_h),
                       outline=(20, 20, 20), width=4)
    return canvas


def compose_workspace_frame(prompt: str, title: str | None = None,
                            box_h: int = 360) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    y = 70
    if title:
        TC._text_centered(draw, (512, y), title, TC._font(38, bold=True))
        y += 60
    if prompt:
        TC._text_centered(draw, (512, y + 20), prompt, TC._font(28))
        y += 60
    # Bordered workspace
    box_y0 = y + 20
    box_y1 = box_y0 + box_h
    draw.rectangle((100, box_y0, 924, box_y1),
                   outline=(20, 20, 20), width=4)
    # Faint guide lines
    for gy in range(box_y0 + 60, box_y1, 60):
        draw.line([(120, gy), (904, gy)], fill=(200, 200, 200), width=1)
    return canvas


def compose_tally_chart(rows: list[tuple[str, int | None]], *,
                        title: str | None = None,
                        question_line: bool = False,
                        show_total: bool = True) -> Image.Image:
    """Multi-row tally chart: each row = (label, count_or_None).

    None count = blank tally area (template).
    """
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    y = 70
    if title:
        TC._text_centered(draw, (512, y), title, TC._font(38, bold=True))
        y += 60
    if question_line:
        draw.text((100, y), "Question:", font=TC._font(26, bold=True), fill=(20, 20, 20))
        draw.line([(260, y + 28), (920, y + 28)], fill=(20, 20, 20), width=2)
        y += 70
    # Header row
    label_x, tally_x, total_x = 110, 350, 800
    draw.text((label_x, y), "Item", font=TC._font(26, bold=True), fill=(20, 20, 20))
    draw.text((tally_x, y), "Tally", font=TC._font(26, bold=True), fill=(20, 20, 20))
    if show_total:
        draw.text((total_x, y), "Total", font=TC._font(26, bold=True), fill=(20, 20, 20))
    y += 38
    draw.line([(100, y), (924, y)], fill=(20, 20, 20), width=2)
    y += 16
    row_h = 80
    for label, count in rows:
        draw.text((label_x, y + 18), label or "", font=TC._font(26),
                  fill=(20, 20, 20))
        if count is not None:
            _draw_tally(draw, tally_x, y + 18, count)
            if show_total:
                draw.text((total_x + 12, y + 18), str(count),
                          font=TC._font(28, bold=True), fill=(20, 20, 20))
        else:
            # blank tally region — show light dots
            draw.rectangle((tally_x - 10, y + 6, tally_x + 380, y + row_h - 8),
                           outline=(180, 180, 180), width=1)
            if show_total:
                draw.rectangle((total_x - 6, y + 12, total_x + 80, y + row_h - 14),
                               outline=(180, 180, 180), width=1)
        # row separator
        draw.line([(100, y + row_h), (924, y + row_h)],
                  fill=(220, 220, 220), width=1)
        y += row_h
    return canvas


def compose_tally_inline_diagrams(counts: list[int],
                                  title: str | None = None) -> Image.Image:
    """N tally diagrams stacked vertically with their numeric value below."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    y = 60
    if title:
        TC._text_centered(draw, (512, y), title, TC._font(36, bold=True))
        y += 70
    spacing = (768 - y - 60) // max(1, len(counts))
    for i, count in enumerate(counts):
        cy = y + spacing * i + spacing // 2
        # tally drawn centered horizontally
        # rough width estimate
        bundles = count // 5
        rem = count % 5
        bar_gap = 12
        bundle_gap = 22
        width = bundles * (3 * bar_gap + bundle_gap) + rem * bar_gap
        x = (1024 - width) // 2
        _draw_tally(draw, x, cy - 25, count, bar_h=50, bar_gap=bar_gap,
                    bundle_gap=bundle_gap)
        # value label to the right
        TC._text_centered(draw, (x + width + 80, cy),
                          f"= {count}", TC._font(32, bold=True))
    return canvas


def compose_tally_progression() -> Image.Image:
    """Reference chart showing tally marks for 1, 2, 3, 4, 5."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 60), "Tally Marks Reference",
                      TC._font(40, bold=True))
    cells = 5
    cell_w = (1024 - 80) // cells
    for n in range(1, cells + 1):
        x0 = 40 + (n - 1) * cell_w
        x1 = x0 + cell_w
        # box
        draw.rectangle((x0, 150, x1, 600), outline=(20, 20, 20), width=3)
        # title
        TC._text_centered(draw, ((x0 + x1) // 2, 190),
                          f"{n}", TC._font(48, bold=True))
        # tally inside
        cx = (x0 + x1) // 2
        bar_gap = 14
        bundle_gap = 22
        bundles = n // 5
        rem = n % 5
        width = bundles * (3 * bar_gap + bundle_gap) + rem * bar_gap
        if bundles == 0 and rem == 0:
            continue
        sx = cx - width // 2 + (bar_gap // 2 if rem else 0)
        _draw_tally(draw, sx, 380, n, bar_h=70, bar_gap=bar_gap,
                    bundle_gap=bundle_gap)
        TC._text_centered(draw, ((x0 + x1) // 2, 540),
                          "marks", TC._font(22))
    return canvas


def compose_tally_addition_problems(problems: list[tuple[int, int, int]],
                                    title: str | None = None) -> Image.Image:
    """Each problem = (a, b, expected_total). Drawn as: tally(a) + tally(b) = ___"""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    y = 60
    if title:
        TC._text_centered(draw, (512, y), title, TC._font(36, bold=True))
        y += 70
    avail = 768 - y - 40
    spacing = avail // max(1, len(problems))
    for i, (a, b, total) in enumerate(problems):
        cy = y + spacing * i + spacing // 2
        # Layout: tally(a) [+] tally(b) [=] [____]
        x = 80
        bar_gap = 12
        bundle_gap = 18
        # tally a
        end_a = _draw_tally(draw, x, cy - 22, a, bar_h=44, bar_gap=bar_gap,
                            bundle_gap=bundle_gap)
        TC._text_centered(draw, (end_a + 30, cy),
                          "+", TC._font(36, bold=True))
        x = end_a + 60
        end_b = _draw_tally(draw, x, cy - 22, b, bar_h=44, bar_gap=bar_gap,
                            bundle_gap=bundle_gap)
        TC._text_centered(draw, (end_b + 30, cy),
                          "=", TC._font(36, bold=True))
        # answer line
        ax0, ax1 = end_b + 60, end_b + 200
        draw.line([(ax0, cy + 22), (ax1, cy + 22)],
                  fill=(20, 20, 20), width=3)
    return canvas


def compose_pictograph(rows: list[tuple[str, int | None, str | None]], *,
                       title: str | None = None,
                       icon_default: str = "apple",
                       blank_label: bool = False) -> Image.Image:
    """N rows. Each row = (label, count_or_None, icon_or_None).
    None count = empty grid cells (template). None icon = use default."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    y = 70
    if title:
        TC._text_centered(draw, (512, y), title, TC._font(36, bold=True))
        y += 70
    label_w = 200
    cells = 8
    cell_w = (1024 - 2 * 60 - label_w - 20) // cells
    cell_h = 60
    avail_h = 768 - y - 40
    spacing = max(cell_h + 30, avail_h // max(1, len(rows)))
    for i, (label, count, icon) in enumerate(rows):
        ry = y + spacing * i
        # label or label-line
        if label:
            draw.text((60, ry + cell_h // 2 - 12), label,
                      font=TC._font(24, bold=True), fill=(20, 20, 20))
        elif blank_label:
            draw.line([(60, ry + cell_h // 2 + 14),
                       (60 + label_w - 20, ry + cell_h // 2 + 14)],
                      fill=(20, 20, 20), width=2)
        # cells
        gx0 = 60 + label_w + 10
        for c in range(cells):
            x0 = gx0 + c * cell_w
            draw.rectangle((x0, ry, x0 + cell_w - 4, ry + cell_h),
                           outline=(180, 180, 180), width=1)
        if count is not None:
            for c in range(min(count, cells)):
                cx = gx0 + c * cell_w + cell_w // 2 - 2
                cy = ry + cell_h // 2
                draw_icon(canvas, icon or icon_default, cx, cy, size=44)
    return canvas


def compose_anchor_chart(header: str, rows: list[tuple[str, str]]) -> Image.Image:
    """Vocabulary/poster chart: header + N rows of (term, definition)."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    # Header
    draw.rectangle((40, 40, 984, 130), outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 85), header, TC._font(46, bold=True))
    y = 160
    row_h = (768 - y - 40) // max(1, len(rows))
    for term, defn in rows:
        draw.rectangle((40, y, 984, y + row_h),
                       outline=(20, 20, 20), width=2)
        draw.text((60, y + row_h // 2 - 16), term,
                  font=TC._font(28, bold=True), fill=(20, 20, 20))
        # definition - wrap
        wrap_w = 700
        words = defn.split()
        line = ""
        line_y = y + 14
        font = TC._font(20)
        for w in words:
            test = (line + " " + w).strip()
            try:
                tb = draw.textbbox((0, 0), test, font=font)
                tw = tb[2] - tb[0]
            except Exception:
                tw = len(test) * 10
            if tw > wrap_w:
                draw.text((280, line_y), line, font=font, fill=(20, 20, 20))
                line_y += 26
                line = w
            else:
                line = test
        if line:
            draw.text((280, line_y), line, font=font, fill=(20, 20, 20))
        y += row_h
    return canvas


def compose_attribute_cards(attrs: list[tuple[str, str]],
                            cols: int = 4) -> Image.Image:
    """Grid of N cards, each with a bold word + small icon below.

    Icon sizing rules (avoid border-crossing):
      - SAFE_PAD: minimum white-space margin between icon edge and card
        border, on every side.
      - TEXT_BAND: vertical space reserved for the title at the top.
      - The icon's bounding-box side equals min(card_w, card_h - TEXT_BAND)
        minus 2*SAFE_PAD, then further shrunk by ICON_FUDGE for icons whose
        rendering extends past their nominal box (bird: legs+beak, fish:
        tail). This keeps every shape comfortably inside the cell.
    """
    SAFE_PAD = 14            # inside-cell whitespace, all sides
    TEXT_BAND = 56           # space reserved for the title at the top
    # Some icons draw past `size`. Shrink them so the actual rendering fits.
    ICON_FUDGE = {
        "bird": 0.62,        # bird draws cx-1.2h to cx+0.55h horizontally
        "fish": 0.78,        # fish tail extends to cx+h
        "dog":  0.85, "cat": 0.85,  # ear tips extend slightly above box
        "apple": 0.90, "banana": 0.92, "grape": 0.95,
    }

    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    rows = math.ceil(len(attrs) / cols)
    margin = 40
    gap = 16
    card_w = (1024 - 2 * margin - gap * (cols - 1)) // cols
    card_h = (768 - 2 * margin - gap * (rows - 1)) // rows
    for i, (word, icon) in enumerate(attrs):
        r, c = divmod(i, cols)
        x0 = margin + c * (card_w + gap)
        y0 = margin + r * (card_h + gap)
        draw.rectangle((x0, y0, x0 + card_w, y0 + card_h),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + card_w // 2, y0 + 30),
                          word, TC._font(22, bold=True))
        if icon:
            # Bounding side that fits BOTH the cell width AND the cell
            # height below the text band, with SAFE_PAD on every side.
            usable = min(card_w, card_h - TEXT_BAND) - 2 * SAFE_PAD
            size = int(usable * ICON_FUDGE.get(icon, 1.0))
            # Centre the icon vertically in the region below the title.
            icon_cy = y0 + TEXT_BAND + (card_h - TEXT_BAND) // 2
            draw_icon(canvas, icon, x0 + card_w // 2, icon_cy, size=size)
    return canvas


def compose_question_cards(questions: list[str], cols: int = 3) -> Image.Image:
    """Grid of survey question cards, each with response slots."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    rows = math.ceil(len(questions) / cols)
    margin = 30
    gap = 14
    card_w = (1024 - 2 * margin - gap * (cols - 1)) // cols
    card_h = (768 - 2 * margin - gap * (rows - 1)) // rows
    for i, q in enumerate(questions):
        r, c = divmod(i, cols)
        x0 = margin + c * (card_w + gap)
        y0 = margin + r * (card_h + gap)
        draw.rectangle((x0, y0, x0 + card_w, y0 + card_h),
                       outline=(20, 20, 20), width=2)
        # wrap question text to ~3 lines
        words = q.split()
        font_q = TC._font(16, bold=True)
        line, line_y = "", y0 + 14
        wrap_w = card_w - 24
        for w in words:
            test = (line + " " + w).strip()
            tb = draw.textbbox((0, 0), test, font=font_q)
            if tb[2] - tb[0] > wrap_w:
                draw.text((x0 + 12, line_y), line, font=font_q, fill=(20, 20, 20))
                line_y += 22
                line = w
            else:
                line = test
        if line:
            draw.text((x0 + 12, line_y), line, font=font_q, fill=(20, 20, 20))
        # 3 response icons below
        icons = ["circle_hollow", "square_hollow", "triangle"]
        ny = y0 + card_h - 36
        for j, k in enumerate(icons):
            cx = x0 + card_w * (j + 1) // (len(icons) + 1)
            draw_icon(canvas, k, cx, ny, size=28)


    return canvas


def compose_capstone_template() -> Image.Image:
    """Detective case template — 5 stacked sections."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    sections = [
        "1. My QUESTION:",
        "2. My DATA (tally):",
        "3. My PICTOGRAPH:",
        "4. What I FOUND:",
        "5. My CONCLUSION:",
    ]
    y = 30
    available = 768 - 60
    sec_h = available // len(sections)
    for s in sections:
        draw.rectangle((30, y, 994, y + sec_h - 8),
                       outline=(20, 20, 20), width=2)
        draw.text((50, y + 10), s, font=TC._font(20, bold=True),
                  fill=(20, 20, 20))
        # interior guide lines
        for gy in range(y + 50, y + sec_h - 16, 36):
            draw.line([(60, gy), (970, gy)],
                      fill=(220, 220, 220), width=1)
        y += sec_h
    return canvas


def compose_class_tracker(title: str, expectation: str = "",
                          rows: int = 8) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), title, TC._font(34, bold=True))
    if expectation:
        TC._text_centered(draw, (512, 95), expectation, TC._font(20))
    # Table
    name_w = 380
    cols = 4
    rest_w = (1024 - 80 - name_w) // cols
    top = 140
    headers = ["Name"] + ["YES", "NO", "?", "Notes"][:cols]
    # Header row
    x = 40
    draw.rectangle((x, top, x + name_w, top + 40),
                   outline=(20, 20, 20), width=2)
    TC._text_centered(draw, (x + name_w // 2, top + 20),
                      "Name", TC._font(20, bold=True))
    for i, h in enumerate(headers[1:]):
        x0 = 40 + name_w + i * rest_w
        draw.rectangle((x0, top, x0 + rest_w, top + 40),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + rest_w // 2, top + 20),
                          h, TC._font(18, bold=True))
    # rows
    row_h = (768 - top - 80) // rows
    for r in range(rows):
        y = top + 40 + r * row_h
        draw.rectangle((40, y, 40 + name_w, y + row_h),
                       outline=(20, 20, 20), width=1)
        for i in range(cols):
            x0 = 40 + name_w + i * rest_w
            draw.rectangle((x0, y, x0 + rest_w, y + row_h),
                           outline=(20, 20, 20), width=1)
    return canvas


def compose_object_token_sheet(tokens: list[str], cols: int = 5) -> Image.Image:
    """Sheet of small object tokens (cuttable squares)."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    rows = math.ceil(len(tokens) / cols)
    margin = 40
    cell_w = (1024 - 2 * margin) // cols
    cell_h = (768 - 2 * margin) // rows
    for i, kind in enumerate(tokens):
        r, c = divmod(i, cols)
        x0 = margin + c * cell_w
        y0 = margin + r * cell_h
        # cut-line border (dashed)
        for px in range(x0, x0 + cell_w, 8):
            draw.line([(px, y0), (min(px + 4, x0 + cell_w), y0)],
                      fill=(180, 180, 180), width=1)
            draw.line([(px, y0 + cell_h),
                       (min(px + 4, x0 + cell_w), y0 + cell_h)],
                      fill=(180, 180, 180), width=1)
        for py in range(y0, y0 + cell_h, 8):
            draw.line([(x0, py), (x0, min(py + 4, y0 + cell_h))],
                      fill=(180, 180, 180), width=1)
            draw.line([(x0 + cell_w, py),
                       (x0 + cell_w, min(py + 4, y0 + cell_h))],
                      fill=(180, 180, 180), width=1)
        cx, cy = x0 + cell_w // 2, y0 + cell_h // 2
        draw_icon(canvas, kind, cx, cy, size=min(cell_w, cell_h) - 30)
    return canvas


def compose_data_unit_poster() -> Image.Image:
    """Anchor poster summarising the data-detectives flow."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 60), "Data Detectives!",
                      TC._font(54, bold=True))
    # Four stages with icons
    stages = [
        ("ASK",     "circle_hollow"),
        ("COLLECT", "square_hollow"),
        ("SHOW",    "triangle"),
        ("TELL",    "star"),
    ]
    n = len(stages)
    margin = 40
    gap = 20
    cell_w = (1024 - 2 * margin - gap * (n - 1)) // n
    top = 200
    cell_h = 380
    for i, (label, icon) in enumerate(stages):
        x0 = margin + i * (cell_w + gap)
        x1 = x0 + cell_w
        draw.rectangle((x0, top, x1, top + cell_h),
                       outline=(20, 20, 20), width=4)
        draw_icon(canvas, icon, (x0 + x1) // 2, top + 130, size=120)
        TC._text_centered(draw, ((x0 + x1) // 2, top + cell_h - 50),
                          label, TC._font(36, bold=True))
        # arrow to next
        if i < n - 1:
            ay = top + cell_h // 2
            draw.line([(x1 + 2, ay), (x1 + gap - 2, ay)],
                      fill=(20, 20, 20), width=4)
            draw.polygon([(x1 + gap - 2, ay - 8),
                          (x1 + gap - 2, ay + 8),
                          (x1 + gap + 8, ay)], fill=(20, 20, 20))
    TC._text_centered(draw, (512, 660),
                      "Ask. Collect. Show. Tell.",
                      TC._font(32, bold=True))
    return canvas


# ── Composers added for K, G2, G3 ─────────────────────────────────────────

def compose_big_sort_mat(zones: list[str], title: str | None = None) -> Image.Image:
    """Larger sorting mat for K (used as a printable manipulative mat)."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 60), title, TC._font(40, bold=True))
        top = 130
    else:
        top = 80
    n = len(zones)
    cell_w = (1024 - 80) // n
    for i, label in enumerate(zones):
        x0 = 40 + i * cell_w
        x1 = x0 + cell_w - 12
        draw.rectangle((x0, top + 60, x1, 720), outline=(20, 20, 20), width=4)
        TC._text_centered(draw, ((x0 + x1) // 2, top + 30),
                          label, TC._font(34, bold=True))
    return canvas


def compose_yes_no_question_card(prompt: str) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 80), "Question Card", TC._font(36, bold=True))
    # prompt box
    draw.rectangle((80, 160, 944, 360), outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 260), prompt, TC._font(34, bold=True))
    # YES / NO bubbles
    for i, label in enumerate(("YES", "NO")):
        cx = 320 + i * 384
        draw.ellipse((cx - 100, 460, cx + 100, 660),
                     outline=(20, 20, 20), width=4)
        TC._text_centered(draw, (cx, 560), label, TC._font(56, bold=True))
    return canvas


def compose_find_the_most_least(rows: list[tuple[str, int, str]]) -> Image.Image:
    """A pictograph + boxes asking for MOST/LEAST. Used for WS04_P1_FIND."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), "Which has the MOST?  The LEAST?",
                      TC._font(30, bold=True))
    # pictograph in top half
    pic = compose_pictograph(rows, title=None)
    pic.thumbnail((1024, 360), Image.LANCZOS)
    canvas.paste(pic, ((1024 - pic.width) // 2, 90))
    # MOST / LEAST answer slots
    y = 540
    for label in ("MOST:", "LEAST:"):
        draw.text((120, y), label, font=TC._font(28, bold=True), fill=(20, 20, 20))
        draw.line([(280, y + 32), (940, y + 32)], fill=(20, 20, 20), width=2)
        y += 80
    return canvas


def compose_compare_pictographs(left: tuple[str, list], right: tuple[str, list]) -> Image.Image:
    """Two side-by-side small pictographs for WS04_P2_COMPARE."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 40), "Compare the Two Graphs", TC._font(28, bold=True))
    for i, (label, rows) in enumerate((left, right)):
        x_off = i * 512
        TC._text_centered(draw, (x_off + 256, 90), label, TC._font(24, bold=True))
        sub = compose_pictograph(rows, title=None)
        sub.thumbnail((480, 600), Image.LANCZOS)
        canvas.paste(sub, (x_off + (512 - sub.width) // 2, 130))
    return canvas


def compose_venn_diagram(left_label: str, right_label: str,
                         left_items: list[str] = (),
                         right_items: list[str] = (),
                         both_items: list[str] = ()) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 60),
                      f"{left_label} / {right_label}",
                      TC._font(40, bold=True))
    # Two intersecting circles
    R = 240
    cx_l, cx_r, cy = 380, 644, 440
    draw.ellipse((cx_l - R, cy - R, cx_l + R, cy + R),
                 outline=(20, 20, 20), width=4)
    draw.ellipse((cx_r - R, cy - R, cx_r + R, cy + R),
                 outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (cx_l - 90, cy - R + 24),
                      left_label, TC._font(28, bold=True))
    TC._text_centered(draw, (cx_r + 90, cy - R + 24),
                      right_label, TC._font(28, bold=True))
    TC._text_centered(draw, ((cx_l + cx_r) // 2, cy - R + 24),
                      "BOTH", TC._font(24, bold=True))
    # Items
    def place(items, x, y_start):
        for i, it in enumerate(items[:6]):
            draw.text((x - 40, y_start + i * 28), f"• {it}",
                      font=TC._font(20), fill=(20, 20, 20))
    place(left_items, cx_l - 110, cy - 50)
    place(right_items, cx_r + 70, cy - 50)
    place(both_items, (cx_l + cx_r) // 2 - 30, cy - 30)
    return canvas


def compose_carroll_diagram(row_labels: tuple[str, str],
                            col_labels: tuple[str, str],
                            cells: list[list] | None = None) -> Image.Image:
    """2x2 Carroll diagram with labelled rows and cols."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), "Carroll Diagram", TC._font(36, bold=True))
    # Layout
    label_h = 60
    label_w = 200
    grid_x0, grid_y0 = 80 + label_w, 110 + label_h
    grid_w = 1024 - grid_x0 - 60
    grid_h = 768 - grid_y0 - 60
    cell_w, cell_h = grid_w // 2, grid_h // 2
    # Column labels
    for i, lab in enumerate(col_labels):
        x = grid_x0 + i * cell_w + cell_w // 2
        TC._text_centered(draw, (x, 110 + label_h // 2),
                          lab, TC._font(26, bold=True))
    # Row labels
    for i, lab in enumerate(row_labels):
        y = grid_y0 + i * cell_h + cell_h // 2
        TC._text_centered(draw, (80 + label_w // 2, y),
                          lab, TC._font(26, bold=True))
    # Grid cells
    for r in range(2):
        for c in range(2):
            x0 = grid_x0 + c * cell_w
            y0 = grid_y0 + r * cell_h
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=3)
            if cells:
                items = cells[r * 2 + c] if r * 2 + c < len(cells) else []
                for i, item in enumerate(items[:5]):
                    draw.text((x0 + 14, y0 + 14 + i * 28),
                              f"• {item}", font=TC._font(20),
                              fill=(20, 20, 20))
    return canvas


def compose_two_way_table(row_headers: list[str], col_headers: list[str],
                          values: list[list[int | None]] | None = None,
                          title: str | None = None,
                          totals: bool = False) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(34, bold=True))
        top = 110
    else:
        top = 70
    nrows = len(row_headers) + 1 + (1 if totals else 0)
    ncols = len(col_headers) + 1 + (1 if totals else 0)
    cell_w = (1024 - 80) // ncols
    cell_h = (768 - top - 60) // nrows
    # corner
    draw.rectangle((40, top, 40 + cell_w, top + cell_h),
                   outline=(20, 20, 20), width=2)
    # column headers
    for j, ch in enumerate(col_headers):
        x0 = 40 + cell_w * (j + 1)
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          ch, TC._font(22, bold=True))
    if totals:
        x0 = 40 + cell_w * (len(col_headers) + 1)
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          "Total", TC._font(22, bold=True))
    # rows
    for i, rh in enumerate(row_headers):
        y0 = top + cell_h * (i + 1)
        draw.rectangle((40, y0, 40 + cell_w, y0 + cell_h),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (40 + cell_w // 2, y0 + cell_h // 2),
                          rh, TC._font(22, bold=True))
        for j in range(len(col_headers)):
            x0 = 40 + cell_w * (j + 1)
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
            if values:
                v = values[i][j] if j < len(values[i]) else None
                if v is not None:
                    TC._text_centered(draw, (x0 + cell_w // 2, y0 + cell_h // 2),
                                      str(v), TC._font(26))
        if totals:
            x0 = 40 + cell_w * (len(col_headers) + 1)
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    if totals:
        y0 = top + cell_h * (len(row_headers) + 1)
        draw.rectangle((40, y0, 40 + cell_w, y0 + cell_h),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (40 + cell_w // 2, y0 + cell_h // 2),
                          "Total", TC._font(22, bold=True))
        for j in range(len(col_headers) + 1):
            x0 = 40 + cell_w * (j + 1)
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    return canvas


def compose_bar_graph(labels: list[str], values: list[int] | None = None,
                      title: str | None = None,
                      y_max: int = 10, scale: int = 1,
                      blank: bool = False) -> Image.Image:
    """Vertical bar graph with axes. If `blank`, draws axes + labels only."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(34, bold=True))
    # Plot region
    plot_x0, plot_y0 = 140, 110
    plot_x1, plot_y1 = 980, 640
    # Axes
    draw.line([(plot_x0, plot_y0), (plot_x0, plot_y1)],
              fill=(20, 20, 20), width=3)
    draw.line([(plot_x0, plot_y1), (plot_x1, plot_y1)],
              fill=(20, 20, 20), width=3)
    # y-axis ticks
    n_ticks = y_max // scale
    for k in range(0, n_ticks + 1):
        y = plot_y1 - (k * (plot_y1 - plot_y0) // n_ticks)
        draw.line([(plot_x0 - 10, y), (plot_x0, y)],
                  fill=(20, 20, 20), width=2)
        draw.text((plot_x0 - 60, y - 14), str(k * scale),
                  font=TC._font(20), fill=(20, 20, 20))
        # gridline
        draw.line([(plot_x0, y), (plot_x1, y)],
                  fill=(220, 220, 220), width=1)
    # bars
    n = len(labels)
    bar_w = (plot_x1 - plot_x0) // (n * 2)
    for i, lab in enumerate(labels):
        bx = plot_x0 + (2 * i + 1) * bar_w - bar_w // 2
        # x label
        TC._text_centered(draw, (bx + bar_w // 2, plot_y1 + 28),
                          lab, TC._font(20, bold=True))
        if not blank and values and i < len(values) and values[i] is not None:
            v = values[i]
            h = (v / y_max) * (plot_y1 - plot_y0)
            draw.rectangle((bx, plot_y1 - h, bx + bar_w, plot_y1),
                           fill=(80, 80, 80), outline=(20, 20, 20), width=2)
    return canvas


def compose_tree_diagram(root: str, branches: list[tuple[str, list[str]]]) -> Image.Image:
    """Simple tree: root → branches → leaves."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), "Tree Diagram", TC._font(36, bold=True))
    # root
    TC._text_centered(draw, (512, 130), root, TC._font(28, bold=True))
    draw.rectangle((400, 105, 624, 165), outline=(20, 20, 20), width=3)
    n = len(branches)
    if n == 0:
        return canvas
    branch_y = 280
    branch_w = (1024 - 80) // n
    for i, (b_label, leaves) in enumerate(branches):
        bx = 40 + i * branch_w + branch_w // 2
        TC._text_centered(draw, (bx, branch_y), b_label, TC._font(22, bold=True))
        draw.rectangle((bx - 80, branch_y - 24, bx + 80, branch_y + 24),
                       outline=(20, 20, 20), width=2)
        # connector to root
        draw.line([(512, 165), (bx, branch_y - 24)],
                  fill=(20, 20, 20), width=2)
        # leaves
        leaf_y = branch_y + 130
        if leaves:
            leaf_x_step = min(120, (branch_w - 20) // max(1, len(leaves)))
            start = bx - leaf_x_step * (len(leaves) - 1) // 2
            for j, leaf in enumerate(leaves):
                lx = start + j * leaf_x_step
                draw.line([(bx, branch_y + 24), (lx, leaf_y - 16)],
                          fill=(20, 20, 20), width=2)
                draw.rectangle((lx - 50, leaf_y - 16, lx + 50, leaf_y + 16),
                               outline=(20, 20, 20), width=2)
                TC._text_centered(draw, (lx, leaf_y),
                                  leaf, TC._font(18))
    return canvas


def compose_frequency_table(headers: list[str],
                            rows: list[list],
                            title: str | None = None) -> Image.Image:
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(34, bold=True))
        top = 110
    else:
        top = 70
    ncols = len(headers)
    nrows = len(rows) + 1
    cell_w = (1024 - 80) // ncols
    cell_h = (768 - top - 60) // nrows
    # header
    for j, h in enumerate(headers):
        x0 = 40 + j * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          h, TC._font(22, bold=True))
    # rows
    for i, row in enumerate(rows):
        y0 = top + cell_h * (i + 1)
        for j in range(ncols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
            v = row[j] if j < len(row) else None
            if v is not None:
                TC._text_centered(draw, (x0 + cell_w // 2, y0 + cell_h // 2),
                                  str(v), TC._font(22))
    return canvas


def compose_mean_problems(problems: list[tuple[str, list[int]]]) -> Image.Image:
    """N mean-calculation problems shown as: [data] → mean = ___"""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50),
                      "Find the MEAN (average)", TC._font(34, bold=True))
    y = 130
    spacing = (768 - y - 60) // max(1, len(problems))
    for label, data in problems:
        draw.text((80, y + 10), f"{label}:", font=TC._font(22, bold=True),
                  fill=(20, 20, 20))
        # data inline
        data_str = " + ".join(str(d) for d in data)
        draw.text((220, y + 10), data_str, font=TC._font(22),
                  fill=(20, 20, 20))
        # mean = ___
        draw.text((80, y + 50), f"Mean = {data_str} / {len(data)} = ",
                  font=TC._font(22), fill=(20, 20, 20))
        # answer line
        draw.line([(680, y + 70), (920, y + 70)],
                  fill=(20, 20, 20), width=2)
        y += spacing
    return canvas


def compose_blank_workspace_grid() -> Image.Image:
    """Generic workspace area for student-built representations (graphs, tables)."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), "Make Your Own", TC._font(34, bold=True))
    draw.rectangle((60, 110, 964, 720), outline=(20, 20, 20), width=4)
    # light grid
    for x in range(80, 964, 40):
        draw.line([(x, 110), (x, 720)], fill=(230, 230, 230), width=1)
    for y in range(130, 720, 40):
        draw.line([(60, y), (964, y)], fill=(230, 230, 230), width=1)
    return canvas


def compose_data_displays_overview() -> Image.Image:
    """Anchor chart showing the 3 main data displays for G2."""
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    TC._text_centered(draw, (512, 50), "Three Ways to Show Data",
                      TC._font(34, bold=True))
    items = [
        ("TALLY",      "|||| |||| ||"),
        ("PICTOGRAPH", "🍎🍎🍎🍌🍌"),
        ("BAR GRAPH",  "▮▮▮▮▮"),
    ]
    cell_w = (1024 - 60) // 3
    for i, (name, ex) in enumerate(items):
        x0 = 30 + i * cell_w
        x1 = x0 + cell_w - 10
        draw.rectangle((x0, 130, x1, 700),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, ((x0 + x1) // 2, 175),
                          name, TC._font(28, bold=True))
        TC._text_centered(draw, ((x0 + x1) // 2, 400),
                          ex, TC._font(36))
        TC._text_centered(draw, ((x0 + x1) // 2, 660),
                          "Use when…", TC._font(20))
    return canvas


# ── Per-image-id dispatcher ───────────────────────────────────────────────

# IDs explicitly handled. Used by the driver's has_real_composite() check
# so a survey knows which IDs are now backed by a bespoke composer.
HANDLED_IDS = {
    # ---- g1_data_detectives ----
    # M_ manipulatives
    "M1_OBJECTS", "M2_TALLY_CHART", "M3_GRID", "M4_TOKENS", "M5_QUESTIONS",
    "M6_CAPSTONE", "M7_VOCAB", "M8_TALLY_REF", "M9_ATTRIBUTES", "M10_POSTER",
    # WS_ worksheets
    "WS01_P1_PILE", "WS01_P2_BOXES", "WS01_P3_FRAME",
    "WS02_P1_TALLIES", "WS02_P2_CHART", "WS02_P3_TOTALS",
    "WS03_P1_PICTOGRAPH", "WS03_P2_TALLY_AND_GRID", "WS03_P3_BLANK_GRID",
    "WS04_P1_PICTOGRAPHS", "WS04_P2_TALLY", "WS04_P3_GRID",
    "WS05_P1_TALLY", "WS05_P2_GRID", "WS05_P3_CONCLUSION",
    # FORM_ formative
    "FORM_Q1_TALLIES", "FORM_Q2_GRID",
    # AS_ assessment
    "AS_FORM_TRACKER_L2", "AS_FORM_TRACKER_L3", "AS_FORM_TRACKER_L4",
    "AS_DIAG_TRACKER",
    # ---- k_data_detectives ----
    "M1_SORT_MAT", "M2_BUTTON_TOKEN", "M3_TALLY_CHART", "M4_PICTOGRAPH",
    "M5_QUESTION_CARD", "M6_CAPSTONE_TEMPLATE", "M7_OBJECT_TOKEN",
    "M8_CLASS_CHART", "M9_DATA_CHART", "M10_DETECTIVE_POSTER",
    "WS01_P1_COLOUR", "WS01_P2_SIZE", "WS01_P3_MY",
    "WS02_P1_COUNT", "WS02_P2_CLASS", "WS02_P3_SURVEY",
    "WS03_P1_BUILD", "WS03_P2_SURVEY", "WS03_P3_MY",
    "WS04_P1_FIND", "WS04_P2_COMPARE", "WS04_P3_CLASS",
    "WS05_P1_QUESTION", "WS05_P2_SURVEY", "WS05_P3_GRAPH", "WS05_P4_DESC",
    "FORM_Q1_SORT", "FORM_Q2_TALLY", "FORM_Q3_GRAPH", "FORM_Q4_FACES",
    # ---- g2_data_detectives ----
    "M1_VENN", "M2_CARROLL", "M3_TWO_WAY", "M4_BAR_GRID", "M5_DATA_CARDS",
    "M8_MODE", "M9_QUESTIONS",
    "WS01_P1_VENN", "WS01_P2_CARROLL", "WS01_P3_BLANK",
    "WS02_P1_TABLE", "WS02_P2_BLANK", "WS02_P3_HOME",
    "WS03_P1_BAR", "WS03_P2_BUILD", "WS03_P3_BLANK",
    "WS04_P1_DISPLAYS", "WS04_P2_SPECIAL", "WS04_P3_LINES",
    "WS05_P2_BAR",
    "FORM_Q1_TABLE", "FORM_Q2_BUILD",
    # ---- g3_data_detectives ----
    "M1_TREE", "M2_FREQ", "M4_MEAN", "M5_DATA", "M8_SCALE", "M9_CALCS",
    "WS01_P1_TREE", "WS01_P2_READ",
    "WS02_P1_SORT", "WS02_P3_SURVEY",
    "WS03_P1_GRAPH", "WS03_P3_PICK",
    "WS04_P1_MEAN", "WS04_P2_MODE", "WS04_P3_BOTH",
    "WS05_P1_TABLE", "WS05_P2_GRAPH",
    "FORM_Q2_SCALE",
    # Shared between g2 and g3 (dispatcher branches by grade):
    "WS01_P3_BLANK", "WS02_P2_BUILD", "WS03_P2_BUILD", "WS03_P3_BLANK",
    "FORM_Q1_TABLE",
}


def compose_data_detectives_image(image_id: str,
                                  grade: str | None = None,
                                  unit_id: str | None = None
                                  ) -> Image.Image | None:
    """Return a composed image for a Data-Detectives image_id, or None if
    this dispatcher does not handle it (caller falls through to other
    composers)."""

    # ─── M_ manipulatives ───
    if image_id == "M1_OBJECTS":
        # Sortable shape tokens — shapes by colour (solid = red, hollow = blue)
        tokens = (["square_solid"] * 4 + ["square_hollow"] * 4 +
                  ["circle_solid"] * 4 + ["circle_hollow"] * 4 +
                  ["triangle"] * 4 + ["star"] * 4 + ["apple", "banana", "grape"])[:30]
        return compose_object_token_sheet(tokens, cols=5)

    if image_id == "M2_TALLY_CHART":
        return compose_tally_chart(
            [(None, None)] * 5,
            title="My Tally Chart",
            question_line=True,
            show_total=True,
        )

    if image_id == "M3_GRID":
        return compose_pictograph(
            [(None, None, None)] * 4,
            title="My Pictograph",
            blank_label=True,
        )

    if image_id == "M4_TOKENS":
        # Picture tokens — pets and fruits to glue onto pictograph
        tokens = (["apple"] * 6 + ["banana"] * 6 + ["grape"] * 6 +
                  ["dog"] * 6 + ["cat"] * 6)[:30]
        return compose_object_token_sheet(tokens, cols=6)

    if image_id == "M5_QUESTIONS":
        questions = [
            "Do you have a pet?", "Favourite fruit?", "Favourite colour?",
            "Cats or dogs?", "Do you walk to school?", "Favourite season?",
            "Favourite drink?", "Favourite snack?", "Do you read at night?",
            "Favourite sport?", "Best subject?", "Hot or cold drink?",
        ]
        return compose_question_cards(questions, cols=3)

    if image_id == "M6_CAPSTONE":
        return compose_capstone_template()

    if image_id == "M7_VOCAB":
        return compose_anchor_chart(
            header="Data Words",
            rows=[
                ("DATA",      "Information we collect to answer a question."),
                ("TALLY",     "Marks we use to count. Five marks = a bundle."),
                ("PICTOGRAPH", "A graph that uses pictures to show data."),
                ("CATEGORY",  "A group that things belong to."),
                ("MOST",      "The category with the largest number."),
                ("LEAST",     "The category with the smallest number."),
            ],
        )

    if image_id == "M8_TALLY_REF":
        return compose_tally_progression()

    if image_id == "M9_ATTRIBUTES":
        return compose_attribute_cards([
            ("RED",      "circle_solid"),
            ("BLUE",     "circle_hollow"),
            ("BIG",      "square_solid"),
            ("SMALL",    "square_hollow"),
            ("ROUND",    "circle_hollow"),
            ("STRAIGHT", "triangle"),
            ("FRUIT",    "apple"),
            ("PET",      "dog"),
            ("FAST",     "bird"),
            ("SLOW",     "fish"),
            ("YUMMY",    "banana"),
            ("BUNCH",    "grape"),
        ], cols=4)

    if image_id == "M10_POSTER":
        return compose_data_unit_poster()

    # ─── WS_ worksheets ───
    if image_id == "WS01_P1_PILE":
        return compose_object_pile(
            objects=["square_solid", "square_solid",
                     "circle_solid", "circle_solid",
                     "square_hollow", "square_hollow",
                     "circle_hollow", "circle_hollow"],
            title="The Pile",
            below_boxes=["RED PILE", "BLUE PILE"],
        )

    if image_id == "WS01_P2_BOXES":
        return compose_sorting_bins(["SQUARES", "CIRCLES"],
                                    title="Sort by SHAPE")

    if image_id == "WS01_P3_FRAME":
        return compose_workspace_frame(
            prompt="Draw your sort and write the rule:",
            title="My RULE: ___",
            box_h=420,
        )

    if image_id == "WS02_P1_TALLIES":
        return compose_tally_inline_diagrams(
            [3, 4, 5, 7, 9],
            title="Read the Tally Marks",
        )

    if image_id == "WS02_P2_CHART":
        return compose_tally_chart(
            [("Apples", None), ("Bananas", None), ("Grapes", None)],
            title="My Tally Chart",
            question_line=True,
        )

    if image_id == "WS02_P3_TOTALS":
        return compose_tally_addition_problems(
            [(5, 4, 9), (5, 5, 10), (3, 5, 8)],
            title="Add the Tallies",
        )

    if image_id == "WS03_P1_PICTOGRAPH":
        return compose_pictograph(
            [("Apples",  3, "apple"),
             ("Bananas", 5, "banana"),
             ("Grapes",  2, "grape")],
            title="Class Snack Pictograph",
        )

    if image_id == "WS03_P2_TALLY_AND_GRID":
        # combined: tally chart on top half + blank pictograph on bottom half
        canvas = TC._new(1024, 768)
        # render two sub-images and paste
        top_img = compose_tally_chart(
            [("Dogs", 4), ("Cats", 6), ("Fish", 3), ("Birds", 2)],
            title="My Pets Tally")
        bot_img = compose_pictograph(
            [("Dogs", None, "dog"), ("Cats", None, "cat"),
             ("Fish", None, "fish"), ("Birds", None, "bird")],
            title="Now make the pictograph")
        # downscale both to half height
        top_img.thumbnail((1024, 384), Image.LANCZOS)
        bot_img.thumbnail((1024, 384), Image.LANCZOS)
        canvas.paste(top_img, ((1024 - top_img.width) // 2, 0))
        canvas.paste(bot_img, ((1024 - bot_img.width) // 2, 384))
        return canvas

    if image_id == "WS03_P3_BLANK_GRID":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="Make Your Own Pictograph",
            blank_label=True,
        )

    if image_id == "WS04_P1_PICTOGRAPHS":
        # 3 small pictographs stacked
        canvas = TC._new(1024, 768)
        img_a = compose_pictograph([("Pizza", 5, "circle_solid"),
                                    ("Tacos", 3, "triangle"),
                                    ("Pasta", 2, "square_solid")],
                                   title="Favourite Lunch")
        img_b = compose_pictograph([("Sun", 4, "star"),
                                    ("Rain", 2, "circle_hollow"),
                                    ("Snow", 6, "square_hollow")],
                                   title="Today's Weather")
        img_c = compose_pictograph([("Walk", 5, "circle_hollow"),
                                    ("Bus",  4, "square_solid"),
                                    ("Car",  3, "circle_solid")],
                                   title="How I Got to School")
        for i, im in enumerate((img_a, img_b, img_c)):
            im.thumbnail((1024, 256), Image.LANCZOS)
            canvas.paste(im, ((1024 - im.width) // 2, i * 256))
        return canvas

    if image_id == "WS04_P2_TALLY":
        return compose_tally_chart(
            [("Dog", 7), ("Cat", 5), ("Fish", 3), ("Bird", 2)],
            title="Favourite Animal",
        )

    if image_id == "WS04_P3_GRID":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="Now Make a Pictograph",
            blank_label=True,
        )

    if image_id == "WS05_P1_TALLY":
        return compose_tally_chart(
            [(None, None)] * 4,
            title="My Capstone Tally",
            question_line=True,
        )

    if image_id == "WS05_P2_GRID":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="My Capstone Pictograph",
            blank_label=True,
        )

    if image_id == "WS05_P3_CONCLUSION":
        return compose_workspace_frame(
            prompt="Write your conclusion:",
            title="My Conclusion",
            box_h=320,
        )

    # ─── FORM_ formative ───
    if image_id == "FORM_Q1_TALLIES":
        return compose_tally_inline_diagrams([3, 7, 11],
                                             title="Read the tally")

    if image_id == "FORM_Q2_GRID":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="Build a pictograph",
            blank_label=True,
        )

    # ─── AS_ assessment ───
    if image_id.startswith("AS_FORM_TRACKER"):
        # AS_FORM_TRACKER_L2 / L3 / L4 — class checklist
        suffix_to_title = {
            "AS_FORM_TRACKER_L2": "Lesson 2 Formative Tracker (Tally)",
            "AS_FORM_TRACKER_L3": "Lesson 3 Formative Tracker (Pictograph)",
            "AS_FORM_TRACKER_L4": "Lesson 4 Formative Tracker (Ordering)",
        }
        return compose_class_tracker(
            title=f"Data Detectives — {suffix_to_title.get(image_id, image_id)}",
            expectation="Expectation: D1.1 — sort, tally, pictograph, interpret.",
            rows=8,
        )

    if image_id == "AS_DIAG_TRACKER":
        return compose_class_tracker(
            title="Data Detectives — Day 1 Diagnostic Checklist",
            expectation="Expectation: D1.1 — sort by one rule.",
            rows=10,
        )

    # ───────────────────────────── K branches ─────────────────────────────
    if image_id == "M1_SORT_MAT":
        return compose_big_sort_mat(["GROUP A", "GROUP B"],
                                    title="My Sorting Mat")
    if image_id == "M2_BUTTON_TOKEN":
        return compose_object_token_sheet(
            ["circle_solid", "circle_hollow", "square_solid",
             "square_hollow", "star", "triangle"] * 5, cols=5)
    if image_id == "M3_TALLY_CHART":
        return compose_tally_chart([(None, None)] * 4,
                                   title="Class Tally", question_line=True)
    if image_id == "M4_PICTOGRAPH":
        return compose_pictograph([(None, None, None)] * 4,
                                  title="Class Pictograph", blank_label=True)
    if image_id == "M5_QUESTION_CARD":
        return compose_yes_no_question_card("Do you like apples?")
    if image_id == "M6_CAPSTONE_TEMPLATE":
        return compose_capstone_template()
    if image_id == "M7_OBJECT_TOKEN":
        return compose_object_token_sheet(
            ["apple", "banana", "grape", "dog", "cat", "fish"] * 5, cols=5)
    if image_id == "M8_CLASS_CHART":
        return compose_class_tracker(
            title="Class Chart",
            expectation="Use to record class data.",
            rows=10,
        )
    if image_id == "M9_DATA_CHART":
        return compose_anchor_chart(
            header="Data Chart",
            rows=[("ASK", "Pick a question."),
                  ("SORT", "Group your data."),
                  ("COUNT", "How many in each?"),
                  ("SHOW", "Make a graph."),
                  ("TELL", "What does it mean?")],
        )
    if image_id == "M10_DETECTIVE_POSTER":
        return compose_data_unit_poster()

    if image_id == "WS01_P1_COLOUR":
        return compose_object_pile(
            ["circle_solid"] * 4 + ["circle_hollow"] * 4,
            title="Sort by COLOUR",
            below_boxes=["DARK", "LIGHT"],
        )
    if image_id == "WS01_P2_SIZE":
        return compose_sorting_bins(["BIG", "SMALL"], title="Sort by SIZE")
    if image_id == "WS01_P3_MY":
        return compose_workspace_frame("Sort and tell your rule:",
                                       title="My Rule: ___")
    if image_id == "WS02_P1_COUNT":
        return compose_tally_inline_diagrams([3, 5, 7],
                                             title="Count the marks")
    if image_id == "WS02_P2_CLASS":
        return compose_tally_chart(
            [("Apples", None), ("Bananas", None), ("Grapes", None)],
            title="Class Snack Tally", question_line=True,
        )
    if image_id == "WS02_P3_SURVEY":
        return compose_workspace_frame("Survey 3 friends. Tally their answers.",
                                       title="My Survey")
    if image_id == "WS03_P1_BUILD":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="Build a Pictograph", blank_label=True)
    if image_id == "WS03_P2_SURVEY":
        return compose_pictograph(
            [("Dogs", 4, "dog"), ("Cats", 3, "cat"), ("Fish", 2, "fish")],
            title="Sample Pictograph")
    if image_id == "WS03_P3_MY":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="My Own Pictograph", blank_label=True)
    if image_id == "WS04_P1_FIND":
        return compose_find_the_most_least(
            [("Pizza", 5, "circle_solid"),
             ("Tacos", 2, "triangle"),
             ("Pasta", 4, "square_solid")])
    if image_id == "WS04_P2_COMPARE":
        return compose_compare_pictographs(
            ("Class A", [("Dogs", 5, "dog"), ("Cats", 3, "cat")]),
            ("Class B", [("Dogs", 2, "dog"), ("Cats", 6, "cat")]),
        )
    if image_id == "WS04_P3_CLASS":
        return compose_workspace_frame("Show class data here:",
                                       title="Our Class Data")
    if image_id == "WS05_P1_QUESTION":
        return compose_workspace_frame("Pick a question for your survey:",
                                       title="My Question")
    if image_id == "WS05_P2_SURVEY":
        return compose_tally_chart(
            [(None, None)] * 4,
            title="My Survey Tally", question_line=True)
    if image_id == "WS05_P3_GRAPH":
        return compose_pictograph(
            [(None, None, None)] * 3,
            title="My Pictograph", blank_label=True)
    if image_id == "WS05_P4_DESC":
        return compose_workspace_frame("Tell what your data shows:",
                                       title="My Story")

    if image_id == "FORM_Q1_SORT":
        return compose_object_pile(
            ["circle_solid", "circle_hollow", "square_solid", "square_hollow"],
            title="Sort these objects",
            below_boxes=["DARK", "LIGHT"])
    if image_id == "FORM_Q2_TALLY":
        return compose_tally_inline_diagrams([4, 6],
                                             title="Read the tally")
    if image_id == "FORM_Q3_GRAPH":
        return compose_pictograph(
            [("Sun", 3, "star"), ("Rain", 2, "circle_hollow")],
            title="Read the graph")
    if image_id == "FORM_Q4_FACES":
        # reuse the existing _compose_face_rating? It's in compose.py.
        # We approximate here so we don't depend on private helpers.
        canvas = TC._new(1024, 768)
        draw = ImageDraw.Draw(canvas)
        TC._text_centered(draw, (512, 60),
                          "How did the lesson go?",
                          TC._font(36, bold=True))
        for i, mood in enumerate(("smile", "neutral", "frown")):
            cx = 256 + i * 256
            cy = 380
            r = 100
            draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                         outline=(20, 20, 20), width=4)
            # eyes
            draw.ellipse((cx - 38, cy - 20, cx - 22, cy - 4),
                         fill=(20, 20, 20))
            draw.ellipse((cx + 22, cy - 20, cx + 38, cy - 4),
                         fill=(20, 20, 20))
            # mouth
            if mood == "smile":
                draw.arc((cx - 40, cy + 10, cx + 40, cy + 60),
                         start=0, end=180, fill=(20, 20, 20), width=4)
            elif mood == "neutral":
                draw.line([(cx - 40, cy + 35), (cx + 40, cy + 35)],
                          fill=(20, 20, 20), width=4)
            else:
                draw.arc((cx - 40, cy + 30, cx + 40, cy + 80),
                         start=180, end=360, fill=(20, 20, 20), width=4)
        return canvas

    # ───────────────────────────── G2 branches ────────────────────────────
    is_g2 = (grade == "Grade 2")
    is_g3 = (grade == "Grade 3")

    if image_id == "M1_VENN":
        return compose_venn_diagram("Likes Pizza", "Likes Pasta",
                                    left_items=["Avi", "Sam"],
                                    right_items=["Lin", "Mia"],
                                    both_items=["Theo", "Eli"])
    if image_id == "M2_CARROLL":
        return compose_carroll_diagram(
            row_labels=("Pet", "No Pet"),
            col_labels=("Walks to school", "Doesn't walk"),
            cells=[["Sam", "Lin"], ["Avi"], ["Theo"], ["Mia", "Eli"]],
        )
    if image_id == "M3_TWO_WAY":
        return compose_two_way_table(
            row_headers=["Boys", "Girls"],
            col_headers=["Walk", "Bus", "Car"],
            values=[[5, 3, 2], [4, 4, 2]],
            title="Two-Way Frequency Table",
            totals=True,
        )
    if image_id == "M4_BAR_GRID":
        return compose_bar_graph(
            ["Mon", "Tue", "Wed", "Thu", "Fri"],
            blank=True, title="Bar Grid", y_max=10)
    if image_id == "M5_DATA_CARDS":
        return compose_object_token_sheet(
            ["apple", "banana", "grape", "dog", "cat", "fish",
             "bird", "star", "circle_solid", "square_solid"] * 3, cols=5)
    if image_id == "M8_MODE":
        return compose_anchor_chart(
            header="MODE",
            rows=[("MODE", "The most common value in a data set."),
                  ("Find it", "Look for the value that appears most often."),
                  ("Example", "1, 2, 2, 3, 4 → mode = 2"),
                  ("Tip", "There can be more than one mode.")],
        )
    if image_id == "M9_QUESTIONS":
        return compose_question_cards([
            "Pizza or pasta?", "Walk or bus?", "Cat or dog?",
            "Sun or rain?", "Apple or banana?", "Math or art?",
            "Read or play?", "Snow or sand?", "Day or night?",
        ], cols=3)

    if image_id == "WS01_P1_VENN":
        return compose_venn_diagram("Has wheels", "Has wings",
                                    left_items=["car", "bus", "bike"],
                                    right_items=["bird", "plane"],
                                    both_items=["airplane (taxiing)"])
    if image_id == "WS01_P2_CARROLL":
        return compose_carroll_diagram(
            ("Round", "Not round"),
            ("Red", "Not red"),
            cells=[["apple"], ["circle"], ["strawberry"], ["square"]],
        )
    if image_id == "WS01_P3_BLANK" and is_g2:
        return compose_workspace_frame("Make your own Venn or Carroll:",
                                       title="My Sort")
    if image_id == "WS02_P1_TABLE":
        return compose_two_way_table(
            row_headers=["Boys", "Girls"],
            col_headers=["Pizza", "Pasta"],
            values=[[6, 3], [4, 5]], totals=True,
            title="Lunch Choice")
    if image_id == "WS02_P2_BLANK" and is_g2:
        return compose_two_way_table(
            row_headers=["Row A", "Row B"],
            col_headers=["Col 1", "Col 2"],
            title="Make Your Own Table", totals=True)
    if image_id == "WS02_P3_HOME":
        return compose_workspace_frame("Survey at home — record results:",
                                       title="Home Survey")
    if image_id == "WS03_P1_BAR":
        return compose_bar_graph(
            ["Walk", "Bus", "Car", "Bike"],
            values=[6, 4, 3, 2], y_max=8,
            title="How students get to school")
    if image_id == "WS03_P2_BUILD" and is_g2:
        return compose_bar_graph(
            ["A", "B", "C", "D"], blank=True,
            title="Build a Bar Graph", y_max=10)
    if image_id == "WS03_P3_BLANK" and is_g2:
        return compose_bar_graph(
            ["?", "?", "?", "?"], blank=True,
            title="My Bar Graph", y_max=10)
    if image_id == "WS04_P1_DISPLAYS":
        return compose_data_displays_overview()
    if image_id == "WS04_P2_SPECIAL":
        return compose_anchor_chart(
            header="Special Categories",
            rows=[("MODE",   "The most common."),
                  ("RANGE",  "Highest minus lowest."),
                  ("OUTLIER", "A value far from the rest.")],
        )
    if image_id == "WS04_P3_LINES":
        return compose_workspace_frame("Make 3 statements about the data:",
                                       title="What I Notice", box_h=420)
    if image_id == "WS05_P2_BAR":
        return compose_bar_graph(
            ["Mon", "Tue", "Wed", "Thu"], blank=True,
            title="Capstone Bar Graph", y_max=10)
    if image_id == "FORM_Q1_TABLE" and is_g2:
        return compose_two_way_table(
            row_headers=["A", "B"],
            col_headers=["X", "Y"],
            values=[[3, 5], [4, 2]],
            title="Read the table")
    if image_id == "FORM_Q2_BUILD":
        return compose_bar_graph(
            ["Cats", "Dogs", "Fish"], values=[5, 7, 3],
            y_max=8, title="Build the bar")

    # ───────────────────────────── G3 branches ────────────────────────────
    if image_id == "M1_TREE":
        return compose_tree_diagram(
            "Animals",
            [("Mammals", ["Dog", "Cat", "Cow"]),
             ("Birds",   ["Robin", "Owl"]),
             ("Fish",    ["Salmon", "Trout"])],
        )
    if image_id == "M2_FREQ":
        return compose_frequency_table(
            ["Category", "Tally", "Frequency"],
            [["Pizza", "|||| |||", 8],
             ["Pasta", "|||| |", 6],
             ["Salad", "||||", 4]],
            title="Frequency Table")
    if image_id == "M4_MEAN":
        return compose_mean_problems([
            ("Set A", [4, 6, 8]),
            ("Set B", [3, 5, 5, 7]),
            ("Set C", [10, 12, 14, 16]),
        ])
    if image_id == "M5_DATA":
        return compose_object_token_sheet(
            ["apple", "banana", "grape", "dog", "cat", "fish", "bird"] * 4,
            cols=5)
    if image_id == "M8_SCALE":
        return compose_anchor_chart(
            header="SCALE",
            rows=[("SCALE", "How much each unit on the axis represents."),
                  ("Why", "Lets us show big data on a small graph."),
                  ("Example", "Scale of 5 → each square = 5 students."),
                  ("Tip", "Pick a scale that fits the largest value.")],
        )
    if image_id == "M9_CALCS":
        return compose_anchor_chart(
            header="MEAN, MEDIAN, MODE, RANGE",
            rows=[("MEAN",   "Add all, divide by how many."),
                  ("MEDIAN", "The middle value (in order)."),
                  ("MODE",   "The value that appears most often."),
                  ("RANGE",  "Highest minus lowest.")],
        )

    if image_id == "WS01_P1_TREE":
        return compose_tree_diagram(
            "School Things",
            [("Tools",   ["Pencil", "Eraser"]),
             ("Books",   ["Math", "Reader"]),
             ("Snacks",  ["Apple", "Granola"])],
        )
    if image_id == "WS01_P2_READ":
        return compose_frequency_table(
            ["Snack", "Tally", "Frequency"],
            [["Apples",  "|||| ||",  7],
             ["Bananas", "||||",     5],
             ["Grapes",  "|||",      3]],
            title="Read the Frequency Table")
    if image_id == "WS01_P3_BLANK" and is_g3:
        return compose_frequency_table(
            ["Item", "Tally", "Frequency"],
            [[None] * 3] * 4,
            title="Make Your Own Frequency Table")
    if image_id == "WS02_P1_SORT":
        return compose_workspace_frame(
            "Sort the data and write the categories:",
            title="Sort and Categorise")
    if image_id == "WS02_P2_BUILD" and is_g3:
        return compose_frequency_table(
            ["Item", "Tally", "Frequency"],
            [[None] * 3] * 5,
            title="Build a Frequency Table")
    if image_id == "WS02_P3_SURVEY":
        return compose_workspace_frame("Survey 10 friends — tally the results:",
                                       title="My Survey")
    if image_id == "WS03_P1_GRAPH":
        return compose_bar_graph(
            ["Mon", "Tue", "Wed", "Thu", "Fri"],
            values=[10, 15, 20, 5, 25], y_max=30, scale=5,
            title="Read the Scaled Bar Graph")
    if image_id == "WS03_P2_BUILD" and is_g3:
        return compose_bar_graph(
            ["A", "B", "C", "D"], blank=True, y_max=30, scale=5,
            title="Build a Scaled Bar Graph")
    if image_id == "WS03_P3_PICK":
        return compose_anchor_chart(
            header="Pick the right SCALE",
            rows=[("Small data (≤10)",  "scale = 1"),
                  ("Medium (10–50)",   "scale = 5"),
                  ("Large (50+)",      "scale = 10 or 20"),
                  ("Tip", "Make the tallest bar fit on the page.")],
        )
    if image_id == "WS04_P1_MEAN":
        return compose_mean_problems([
            ("Goals scored", [2, 3, 4, 5, 6]),
            ("Pages read",   [10, 12, 15, 18]),
            ("Hours slept",  [8, 9, 7, 8]),
        ])
    if image_id == "WS04_P2_MODE":
        return compose_workspace_frame(
            "List 5 numbers. Circle the MODE:",
            title="Find the Mode")
    if image_id == "WS04_P3_BOTH":
        return compose_workspace_frame(
            "Calculate the MEAN and find the MODE:",
            title="Mean and Mode", box_h=380)
    if image_id == "WS05_P1_TABLE":
        return compose_frequency_table(
            ["Item", "Tally", "Frequency"],
            [[None] * 3] * 5,
            title="Capstone Frequency Table")
    if image_id == "WS05_P2_GRAPH":
        return compose_bar_graph(
            ["?", "?", "?", "?"], blank=True, y_max=30, scale=5,
            title="Capstone Bar Graph")
    if image_id == "FORM_Q1_TABLE" and is_g3:
        return compose_frequency_table(
            ["Item", "Tally", "Frequency"],
            [["A", "||||",  4],
             ["B", "|||| ||", 7],
             ["C", "|||",   3]],
            title="Read the table")
    if image_id == "FORM_Q2_SCALE":
        return compose_bar_graph(
            ["P", "Q", "R"], values=[10, 25, 15], y_max=30, scale=5,
            title="Use the scale")

    return None
