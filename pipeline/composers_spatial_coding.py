"""Spatial + coding composers (5 units).

  k_spatial_shape_safari       — 2D/3D shape exploration
  g1_spatial_mapping           — directions and maps
  g2_spatial_mirror_mirror     — symmetry
  g3_spatial_map_it_move_it    — coordinates and translations
  k_coding_little_programmers  — robot/code blocks
"""
from __future__ import annotations

import math
from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    "M1_2D_SHAPES", "M1_MAT", "M1_SHAPES", "M1_SOLIDS",
    "M2_3D_NETS", "M2_ARROWS", "M2_ATTRS", "M2_BLOCKS",
    "M3_CONGRUENT", "M3_POS", "M3_SAFARI_SCENE",
    "M3_STRUCTURES", "M3_SYMMETRY",
    "M4_CONGRUENT", "M4_MAP", "M4_MAP_GRID", "M4_OBJ",
    "M4_POSITION_CARDS",
    "M5_MAP", "M5_PATTERN_BLOCKS", "M5_STRIPS", "M5_SYMBOLS", "M5_TOKENS",
    "M7_ANCHOR", "M7_ATTRIBUTES",
    "M8_AREA", "M8_BUGS", "M8_POSITIONS", "M8_TURNS",
    "M9_ANIMALS", "M9_DIRECTIONS", "M9_ROBOTS", "M9_STICK",
    "WS01_P1_MATCH", "WS01_P1_NAMES", "WS01_P1_SHAPES",
    "WS01_P2_COUNTS", "WS01_P2_GRID", "WS01_P2_PATH", "WS01_P2_SYM",
    "WS01_P3_BOXES", "WS01_P3_DRAW", "WS01_P3_SORT",
    "WS02_P1_DECOMP", "WS02_P1_MATCH", "WS02_P1_SHAPES",
    "WS02_P1_STRUCTURES", "WS02_P1_TILES",
    "WS02_P2_CIRCLE", "WS02_P2_COMP", "WS02_P2_GRID",
    "WS02_P2_HEX", "WS02_P2_TOWER",
    "WS02_P3_BOXES", "WS02_P3_DRAW", "WS02_P3_FREE",
    "WS02_P3_INSIDE", "WS02_P3_REARRANGE",
    "WS03_P1_MATCH", "WS03_P1_PAIRS", "WS03_P1_PANELS",
    "WS03_P1_PICK", "WS03_P1_SHAPES",
    "WS03_P2_DRAW", "WS03_P2_FIND", "WS03_P2_LINES",
    "WS03_P2_MAP", "WS03_P2_YN",
    "WS03_P3_DRAW", "WS03_P3_FRAME", "WS03_P3_ORDER", "WS03_P3_WHY",
    "WS04_P1_GRID", "WS04_P1_MAP", "WS04_P1_MAPS",
    "WS04_P1_TARGETS", "WS04_P1_TEST",
    "WS04_P2_BLANK", "WS04_P2_FIX", "WS04_P2_MAP",
    "WS04_P2_SHAPES", "WS04_P2_TURNS",
    "WS04_P3_BLANK", "WS04_P3_FRAME", "WS04_P3_FRAMES", "WS04_P3_WRITE",
    "WS05_P1_MATCH", "WS05_P1_REFERENCE", "WS05_P1_SHAPES", "WS05_P1_SORT",
    "WS05_P2_BUILD", "WS05_P2_CONGRUENT", "WS05_P2_FRAME",
    "WS05_P2_POS", "WS05_P2_SYMMETRY",
    "WS05_P3_CODE", "WS05_P3_FRAMES", "WS05_P3_MAP",
    "WS05_P3_MAZE", "WS05_P3_TRAIL",
    "FORM_Q1_DIR", "FORM_Q1_SHAPES", "FORM_Q1_SOLIDS",
    "FORM_Q1_STRUCTURE", "FORM_Q1_SYM",
    "FORM_Q2_AREA", "FORM_Q2_CONGRUENT", "FORM_Q2_PANELS",
    "FORM_Q2_POS", "FORM_Q2_SHAPES",
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _2d_shapes_grid() -> Image.Image:
    canvas, draw = _new("2D Shapes")
    shapes = ["square", "circle", "triangle", "rectangle",
              "pentagon", "hexagon", "trapezoid", "rhombus"]
    cols = 4
    rows = 2
    margin = 60
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, name in enumerate(shapes):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        cx, cy = x0 + cw // 2, y0 + ch // 2 - 14
        size = min(cw, ch) // 3
        if name == "circle":
            draw.ellipse((cx - size, cy - size, cx + size, cy + size),
                         outline=(20, 20, 20), width=3)
        elif name == "square":
            draw.rectangle((cx - size, cy - size, cx + size, cy + size),
                           outline=(20, 20, 20), width=3)
        elif name == "rectangle":
            draw.rectangle((cx - size * 1.3, cy - size * 0.7,
                            cx + size * 1.3, cy + size * 0.7),
                           outline=(20, 20, 20), width=3)
        elif name == "triangle":
            pts = [(cx, cy - size), (cx + size, cy + size),
                   (cx - size, cy + size)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif name == "rhombus":
            pts = [(cx, cy - size), (cx + size, cy),
                   (cx, cy + size), (cx - size, cy)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif name == "trapezoid":
            pts = [(cx - size * 0.6, cy - size * 0.6),
                   (cx + size * 0.6, cy - size * 0.6),
                   (cx + size, cy + size * 0.6),
                   (cx - size, cy + size * 0.6)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        else:  # regular polygon
            sides = {"pentagon": 5, "hexagon": 6}.get(name, 6)
            pts = []
            for k in range(sides):
                ang = -math.pi / 2 + 2 * math.pi * k / sides
                pts.append((cx + size * math.cos(ang),
                            cy + size * math.sin(ang)))
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch - 24),
                          name, TC._font(20, bold=True))
    return canvas


def _3d_solids() -> Image.Image:
    canvas, draw = _new("3D Solids")
    solids = ["cube", "sphere", "cylinder", "cone",
              "rect prism", "pyramid"]
    cols = 3
    rows = 2
    margin = 60
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, name in enumerate(solids):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        cx, cy = x0 + cw // 2, y0 + ch // 2 - 14
        s = min(cw, ch) // 3
        if name == "cube":
            # front
            draw.rectangle((cx - s * 0.6, cy - s * 0.5,
                            cx + s * 0.6, cy + s * 0.7),
                           outline=(20, 20, 20), width=3)
            # back top edge
            draw.polygon([(cx - s * 0.6, cy - s * 0.5),
                          (cx - s * 0.4, cy - s * 0.8),
                          (cx + s * 0.8, cy - s * 0.8),
                          (cx + s * 0.6, cy - s * 0.5)],
                         outline=(20, 20, 20))
            draw.line([(cx + s * 0.6, cy - s * 0.5),
                       (cx + s * 0.8, cy - s * 0.8)], fill=(20, 20, 20), width=2)
            draw.line([(cx + s * 0.6, cy + s * 0.7),
                       (cx + s * 0.8, cy + s * 0.4)], fill=(20, 20, 20), width=2)
            draw.line([(cx + s * 0.8, cy - s * 0.8),
                       (cx + s * 0.8, cy + s * 0.4)], fill=(20, 20, 20), width=2)
        elif name == "sphere":
            draw.ellipse((cx - s, cy - s, cx + s, cy + s),
                         outline=(20, 20, 20), width=3)
            draw.arc((cx - s, cy - s * 0.4, cx + s, cy + s * 0.4),
                     start=0, end=180, fill=(20, 20, 20), width=2)
        elif name == "cylinder":
            draw.rectangle((cx - s * 0.5, cy - s * 0.7,
                            cx + s * 0.5, cy + s * 0.7),
                           outline=(20, 20, 20), width=3)
            draw.ellipse((cx - s * 0.5, cy - s * 0.85,
                          cx + s * 0.5, cy - s * 0.55),
                         outline=(20, 20, 20), width=2)
            draw.ellipse((cx - s * 0.5, cy + s * 0.55,
                          cx + s * 0.5, cy + s * 0.85),
                         outline=(20, 20, 20), width=2)
        elif name == "cone":
            pts = [(cx, cy - s), (cx + s * 0.7, cy + s * 0.7),
                   (cx - s * 0.7, cy + s * 0.7)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
            draw.ellipse((cx - s * 0.7, cy + s * 0.55,
                          cx + s * 0.7, cy + s * 0.85),
                         outline=(20, 20, 20), width=2)
        elif name == "rect prism":
            draw.rectangle((cx - s * 0.9, cy - s * 0.4,
                            cx + s * 0.9, cy + s * 0.6),
                           outline=(20, 20, 20), width=3)
            draw.polygon([(cx - s * 0.9, cy - s * 0.4),
                          (cx - s * 0.7, cy - s * 0.65),
                          (cx + s * 1.1, cy - s * 0.65),
                          (cx + s * 0.9, cy - s * 0.4)],
                         outline=(20, 20, 20))
            draw.line([(cx + s * 0.9, cy - s * 0.4),
                       (cx + s * 1.1, cy - s * 0.65)], fill=(20, 20, 20), width=2)
            draw.line([(cx + s * 0.9, cy + s * 0.6),
                       (cx + s * 1.1, cy + s * 0.35)], fill=(20, 20, 20), width=2)
            draw.line([(cx + s * 1.1, cy - s * 0.65),
                       (cx + s * 1.1, cy + s * 0.35)], fill=(20, 20, 20), width=2)
        elif name == "pyramid":
            # base square (perspective)
            base = [(cx - s * 0.7, cy + s * 0.6),
                    (cx + s * 0.7, cy + s * 0.6),
                    (cx + s * 0.5, cy + s * 0.4),
                    (cx - s * 0.5, cy + s * 0.4)]
            draw.polygon(base, outline=(20, 20, 20))
            draw.line(base + [base[0]], fill=(20, 20, 20), width=3)
            apex = (cx, cy - s * 0.7)
            for b in base:
                draw.line([apex, b], fill=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch - 24),
                          name, TC._font(20, bold=True))
    return canvas


def _compass_arrows() -> Image.Image:
    canvas, draw = _new("Direction Arrows")
    cx, cy = 512, 384
    R = 220
    draw.ellipse((cx - R, cy - R, cx + R, cy + R),
                 outline=(20, 20, 20), width=4)
    # arrows
    for label, ang_deg in [("N", -90), ("E", 0), ("S", 90), ("W", 180)]:
        ang = math.radians(ang_deg)
        x_t = cx + (R - 50) * math.cos(ang)
        y_t = cy + (R - 50) * math.sin(ang)
        draw.line([(cx, cy), (x_t, y_t)], fill=(20, 20, 20), width=4)
        TC._text_centered(draw, (cx + (R + 30) * math.cos(ang),
                                  cy + (R + 30) * math.sin(ang)),
                          label, TC._font(40, bold=True))
    return canvas


def _symmetry_panels() -> Image.Image:
    canvas, draw = _new("Symmetry — Mirror Lines")
    # 6 panels with shape and dashed mirror line
    items = ["square", "rectangle", "circle", "triangle", "heart", "leaf"]
    cols = 3
    rows = 2
    margin = 40
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, name in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        cx, cy = x0 + cw // 2, y0 + ch // 2
        s = min(cw, ch) // 3
        # shape
        if name == "circle":
            draw.ellipse((cx - s, cy - s, cx + s, cy + s),
                         outline=(20, 20, 20), width=3)
        elif name == "square":
            draw.rectangle((cx - s, cy - s, cx + s, cy + s),
                           outline=(20, 20, 20), width=3)
        elif name == "rectangle":
            draw.rectangle((cx - s * 1.4, cy - s * 0.7,
                            cx + s * 1.4, cy + s * 0.7),
                           outline=(20, 20, 20), width=3)
        elif name == "triangle":
            pts = [(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif name == "heart":
            # two arcs + triangle
            draw.arc((cx - s, cy - s, cx, cy),
                     start=180, end=360, fill=(20, 20, 20), width=3)
            draw.arc((cx, cy - s, cx + s, cy),
                     start=180, end=360, fill=(20, 20, 20), width=3)
            draw.line([(cx - s, cy - s // 4),
                       (cx, cy + s)], fill=(20, 20, 20), width=3)
            draw.line([(cx + s, cy - s // 4),
                       (cx, cy + s)], fill=(20, 20, 20), width=3)
        elif name == "leaf":
            draw.ellipse((cx - s, cy - s * 0.7, cx + s, cy + s * 0.7),
                         outline=(20, 20, 20), width=3)
            draw.line([(cx - s, cy), (cx + s, cy)],
                      fill=(20, 20, 20), width=2)
        # dashed mirror line (vertical for most, horizontal for leaf)
        line_axis = "h" if name == "leaf" else "v"
        if line_axis == "v":
            for py in range(int(cy - s) - 10, int(cy + s) + 10, 12):
                draw.line([(cx, py), (cx, py + 6)],
                          fill=(180, 180, 180), width=2)
        else:
            for px in range(int(cx - s) - 10, int(cx + s) + 10, 12):
                draw.line([(px, cy), (px + 6, cy)],
                          fill=(180, 180, 180), width=2)
    return canvas


def _coordinate_grid(cols: int = 8, rows: int = 6,
                     points: list[tuple[int, int, str]] = None) -> Image.Image:
    canvas, draw = _new(f"Coordinate Grid ({cols} × {rows})")
    margin = 80
    cell = min((1024 - 2 * margin) // cols, (768 - 130 - 60) // rows)
    grid_w = cell * cols
    grid_h = cell * rows
    x0 = (1024 - grid_w) // 2
    y0 = 130
    for r in range(rows + 1):
        draw.line([(x0, y0 + r * cell), (x0 + grid_w, y0 + r * cell)],
                  fill=(20, 20, 20), width=2)
    for c in range(cols + 1):
        draw.line([(x0 + c * cell, y0), (x0 + c * cell, y0 + grid_h)],
                  fill=(20, 20, 20), width=2)
    # axis labels
    for c in range(cols):
        TC._text_centered(draw, (x0 + c * cell + cell // 2, y0 - 18),
                          str(c), TC._font(16))
    for r in range(rows):
        TC._text_centered(draw, (x0 - 18,
                                  y0 + (rows - 1 - r) * cell + cell // 2),
                          str(r), TC._font(16))
    if points:
        for c, r, label in points:
            cx = x0 + c * cell + cell // 2
            cy = y0 + (rows - 1 - r) * cell + cell // 2
            draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10),
                         fill=(20, 20, 20))
            TC._text_centered(draw, (cx + 24, cy - 14),
                              label, TC._font(20, bold=True))
    return canvas


def _safari_scene() -> Image.Image:
    canvas, draw = _new("Shape Safari")
    # background hill
    draw.arc((100, 350, 924, 750),
             start=180, end=360, fill=(20, 20, 20), width=3)
    # sun
    cx, cy = 800, 200
    draw.ellipse((cx - 60, cy - 60, cx + 60, cy + 60),
                 outline=(20, 20, 20), width=3)
    # a few shapes representing animals' bodies
    shapes = [("circle", (200, 500), 50),  # head
              ("square", (350, 540), 60),  # body
              ("triangle", (520, 540), 60),  # tent
              ("rectangle", (700, 540), 80)]  # cabin
    for name, (cx2, cy2), s in shapes:
        if name == "circle":
            draw.ellipse((cx2 - s, cy2 - s, cx2 + s, cy2 + s),
                         outline=(20, 20, 20), width=3)
        elif name == "square":
            draw.rectangle((cx2 - s, cy2 - s, cx2 + s, cy2 + s),
                           outline=(20, 20, 20), width=3)
        elif name == "triangle":
            pts = [(cx2, cy2 - s), (cx2 + s, cy2 + s), (cx2 - s, cy2 + s)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif name == "rectangle":
            draw.rectangle((cx2 - s, cy2 - s * 0.7,
                            cx2 + s, cy2 + s * 0.7),
                           outline=(20, 20, 20), width=3)
    return canvas


def _position_cards() -> Image.Image:
    positions = ["LEFT", "RIGHT", "UP", "DOWN", "ABOVE", "BELOW",
                 "INSIDE", "OUTSIDE"]
    canvas, draw = _new("Position Words")
    cols = 4
    rows = 2
    margin = 60
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, w in enumerate(positions):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch // 2),
                          w, TC._font(36, bold=True))
    return canvas


def _pattern_blocks() -> Image.Image:
    canvas, draw = _new("Pattern Blocks")
    # 6 pattern blocks: hexagon, trapezoid, rhombus, square, triangle, parallelogram
    items = [("hexagon", 6),
             ("trapezoid", "trap"),
             ("rhombus", "rhom"),
             ("square", 4),
             ("triangle", 3),
             ("parallel", "par")]
    cols = 3
    rows = 2
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, (name, sides) in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        cx, cy = x0 + cw // 2, y0 + ch // 2 - 14
        s = min(cw, ch) // 3
        if isinstance(sides, int):
            if name == "square":
                draw.rectangle((cx - s, cy - s, cx + s, cy + s),
                               outline=(20, 20, 20), width=3)
            else:
                pts = []
                for k in range(sides):
                    ang = -math.pi / 2 + 2 * math.pi * k / sides
                    pts.append((cx + s * math.cos(ang),
                                cy + s * math.sin(ang)))
                draw.polygon(pts, outline=(20, 20, 20))
                draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif sides == "trap":
            pts = [(cx - s * 0.6, cy - s * 0.6),
                   (cx + s * 0.6, cy - s * 0.6),
                   (cx + s, cy + s * 0.6),
                   (cx - s, cy + s * 0.6)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif sides == "rhom":
            pts = [(cx, cy - s), (cx + s, cy),
                   (cx, cy + s), (cx - s, cy)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        elif sides == "par":
            pts = [(cx - s * 0.4, cy - s * 0.6),
                   (cx + s, cy - s * 0.6),
                   (cx + s * 0.4, cy + s * 0.6),
                   (cx - s, cy + s * 0.6)]
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch - 24),
                          name, TC._font(20, bold=True))
    return canvas


def _workspace(prompt: str, title: str | None = None,
               box_h: int = 460) -> Image.Image:
    canvas, draw = _new(title)
    if prompt:
        TC._text_centered(draw, (512, 130), prompt, TC._font(26))
    box_y0 = 180
    draw.rectangle((80, box_y0, 944, box_y0 + box_h),
                   outline=(20, 20, 20), width=4)
    for gy in range(box_y0 + 50, box_y0 + box_h, 50):
        draw.line([(100, gy), (924, gy)],
                  fill=(220, 220, 220), width=1)
    return canvas


def _poster(headline: str, points: list[str]) -> Image.Image:
    canvas, draw = _new()
    draw.rectangle((40, 40, 984, 140), outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 90), headline, TC._font(46, bold=True))
    draw.rectangle((40, 160, 984, 720), outline=(20, 20, 20), width=3)
    spacing = (720 - 200) // max(1, len(points))
    for i, p in enumerate(points):
        y = 180 + i * spacing
        draw.text((80, y), f"• {p}", font=TC._font(26),
                  fill=(20, 20, 20))
    return canvas


def compose_spatial_coding_image(image_id: str, grade: str | None = None,
                                 unit_id: str | None = None) -> Image.Image | None:
    # ── Manipulatives ──
    if image_id in ("M1_2D_SHAPES", "M1_SHAPES", "M2_ATTRS"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _2d_shapes_grid()
    if image_id == "M1_SOLIDS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _3d_solids()
    if image_id == "M2_3D_NETS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _3d_solids()
    if image_id in ("M2_ARROWS", "M9_DIRECTIONS"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        # g1_spatial_mapping uses M9 for direction cards (arrows + step counts)
        # and M2 for paper 3D blocks — compass rose is wrong. Defer.
        if unit_id and "mapping" in unit_id:
            return None
        return _compass_arrows()
    if image_id in ("M2_BLOCKS", "M5_PATTERN_BLOCKS"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        # g1_spatial_mapping's M2 is paper 3D blocks; pattern_blocks (2D) is wrong.
        if unit_id and "mapping" in unit_id:
            return None
        return _pattern_blocks()
    if image_id in ("M3_CONGRUENT", "M4_CONGRUENT"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _2d_shapes_grid()
    if image_id in ("M3_POS", "M4_POSITION_CARDS", "M8_POSITIONS"):
        return _position_cards()
    if image_id == "M3_SAFARI_SCENE":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _safari_scene()
    if image_id == "M3_STRUCTURES":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _3d_solids()
    if image_id == "M3_SYMMETRY":
        return _symmetry_panels()
    if image_id in ("M4_MAP", "M4_MAP_GRID", "M5_MAP"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=10, rows=6, points=[
            (2, 4, "A"), (5, 2, "B"), (8, 5, "C"),
        ])
    if image_id in ("M4_OBJ", "M5_TOKENS", "M5_SYMBOLS"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        # g1_spatial_mapping's M5_TOKENS is treasure tokens; 2D shapes wrong.
        if unit_id and "mapping" in unit_id:
            return None
        return _2d_shapes_grid()
    if image_id == "M5_STRIPS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=10, rows=4)
    if image_id in ("M7_ANCHOR", "M7_ATTRIBUTES"):
        return _poster("Shape Attributes", [
            "Sides — straight or curved?",
            "Corners — how many?",
            "Equal sides?",
            "Right angles?",
            "Symmetry — does it match?",
        ])
    if image_id == "M8_AREA":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=8, rows=6)
    if image_id in ("M8_BUGS", "M9_ROBOTS", "M9_STICK"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=8, rows=6)
    if image_id == "M8_TURNS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _compass_arrows()
    if image_id == "M9_ANIMALS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _safari_scene()
    if image_id == "M1_MAT":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=10, rows=8)

    # ── Worksheets — most workspaces ──
    spatial_ws = {
        "WS01_P1_MATCH":    ("Match shape names.", "Match Shapes"),
        "WS01_P1_NAMES":    ("Name each shape.", "Name Shapes"),
        "WS01_P1_SHAPES":   ("Draw the shapes.", "Draw Shapes"),
        "WS01_P2_COUNTS":   ("Count sides and corners.", "Counts"),
        "WS01_P2_PATH":     ("Trace a path.", "Path"),
        "WS01_P2_SYM":      ("Draw the line of symmetry.", "Symmetry"),
        "WS01_P3_BOXES":    ("Match box shapes.", "Boxes"),
        "WS01_P3_DRAW":     ("Draw a structure.", "Build & Draw"),
        "WS01_P3_SORT":     ("Sort the shapes.", "Sort"),
        "WS02_P1_DECOMP":   ("Decompose into shapes.", "Decompose"),
        "WS02_P1_MATCH":    ("Match nets to solids.", "Match Nets"),
        "WS02_P1_SHAPES":   ("Identify the shape.", "Identify"),
        "WS02_P1_STRUCTURES":("Sketch a structure.", "Sketch"),
        "WS02_P1_TILES":    ("Tile the area.", "Tile"),
        "WS02_P2_CIRCLE":   ("Circle congruent shapes.", "Congruent"),
        "WS02_P2_COMP":     ("Compare two shapes.", "Compare"),
        "WS02_P2_HEX":      ("Hexagon work.", "Hexagons"),
        "WS02_P2_TOWER":    ("Build a tower.", "Tower"),
        "WS02_P3_BOXES":    ("Sort 3D solids.", "Sort 3D"),
        "WS02_P3_DRAW":     ("Draw the solid.", "Draw 3D"),
        "WS02_P3_FREE":     ("Free design.", "Design"),
        "WS02_P3_INSIDE":   ("Find shapes INSIDE.", "Inside"),
        "WS02_P3_REARRANGE":("Rearrange the parts.", "Rearrange"),
        "WS03_P1_MATCH":    ("Match symmetry pairs.", "Sym Match"),
        "WS03_P1_PAIRS":    ("Pair the symmetric shapes.", "Pairs"),
        "WS03_P1_PANELS":   ("Complete the symmetry panel.", "Panels"),
        "WS03_P1_PICK":     ("Pick the symmetric shape.", "Pick Sym"),
        "WS03_P1_SHAPES":   ("Symmetric shapes.", "Sym Shapes"),
        "WS03_P2_DRAW":     ("Draw the mirror image.", "Mirror Draw"),
        "WS03_P2_FIND":     ("Find symmetry lines.", "Find Lines"),
        "WS03_P2_LINES":    ("Mark the lines.", "Mark Lines"),
        "WS03_P2_YN":       ("Symmetric? Yes/No.", "Sym Y/N"),
        "WS03_P3_DRAW":     ("Draw your own symmetric design.", "My Sym"),
        "WS03_P3_FRAME":    ("Frame the symmetric image.", "Frame"),
        "WS03_P3_ORDER":    ("Order by symmetry count.", "Order"),
        "WS03_P3_WHY":      ("Why is it symmetric?", "Why"),
        "WS04_P1_MAP":      ("Map work.", "Map"),
        "WS04_P1_MAPS":     ("Compare maps.", "Compare Maps"),
        "WS04_P1_TARGETS":  ("Hit the coordinates.", "Targets"),
        "WS04_P1_TEST":     ("Test the route.", "Test"),
        "WS04_P2_BLANK":    ("Make a blank map.", "Blank Map"),
        "WS04_P2_FIX":      ("Fix the map errors.", "Fix Map"),
        "WS04_P2_MAP":      ("Add to the map.", "Add to Map"),
        "WS04_P2_SHAPES":   ("Plot shapes.", "Plot"),
        "WS04_P2_TURNS":    ("Plan the turns.", "Turns"),
        "WS04_P3_BLANK":    ("Blank canvas.", "Blank"),
        "WS04_P3_FRAME":    ("Frame your design.", "Frame"),
        "WS04_P3_FRAMES":   ("Multiple frames.", "Frames"),
        "WS04_P3_WRITE":    ("Write your code.", "Write Code"),
        "WS05_P1_MATCH":    ("Capstone match.", "Capstone Match"),
        "WS05_P1_REFERENCE":("Reference page.", "Reference"),
        "WS05_P1_SHAPES":   ("Capstone shapes.", "Capstone Shapes"),
        "WS05_P1_SORT":     ("Capstone sort.", "Capstone Sort"),
        "WS05_P2_BUILD":    ("Build a structure.", "Capstone Build"),
        "WS05_P2_CONGRUENT":("Capstone congruent.", "Capstone Congruent"),
        "WS05_P2_FRAME":    ("Capstone frame.", "Capstone Frame"),
        "WS05_P2_POS":      ("Capstone positions.", "Capstone Positions"),
        "WS05_P2_SYMMETRY": ("Capstone symmetry.", "Capstone Symmetry"),
        "WS05_P3_CODE":     ("Capstone: write code.", "Capstone Code"),
        "WS05_P3_FRAMES":   ("Capstone frames.", "Capstone Frames"),
        "WS05_P3_MAZE":     ("Solve the maze.", "Maze"),
        "WS05_P3_TRAIL":    ("Plan the trail.", "Trail"),
    }
    if image_id in spatial_ws:
        # Defer to smart_fallback's WS hero composer for real part labels
        # (added 2026-05-10).
        return None

    if image_id in ("WS01_P2_GRID", "WS02_P2_GRID", "WS03_P2_MAP",
                     "WS04_P1_GRID", "WS05_P3_MAP"):
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=8, rows=6)

    # ── Formative ──
    if image_id == "FORM_Q1_DIR":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _compass_arrows()
    if image_id == "FORM_Q1_SHAPES":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _2d_shapes_grid()
    if image_id == "FORM_Q1_SOLIDS":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _3d_solids()
    if image_id == "FORM_Q1_STRUCTURE":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _3d_solids()
    if image_id == "FORM_Q1_SYM":
        return _symmetry_panels()
    if image_id == "FORM_Q2_AREA":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _coordinate_grid(cols=6, rows=4)
    if image_id == "FORM_Q2_CONGRUENT":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _2d_shapes_grid()
    if image_id == "FORM_Q2_PANELS":
        return _symmetry_panels()
    if image_id == "FORM_Q2_POS":
        return _position_cards()
    if image_id == "FORM_Q2_SHAPES":
        if grade == "Kindergarten" and unit_id and "coding" in unit_id:

            return None  # K-coding defer
        return _2d_shapes_grid()

    return None
