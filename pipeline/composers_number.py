"""Number-sense composers across 6 units (g1-g3).

  g1_number_friends, g1_number_adding_machine
  g2_number_groups_of, g2_number_place_value_detectives
  g3_number_fraction_street, g3_number_times_table_toolkit
"""
from __future__ import annotations

import math
from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    # M_ — large set
    "M10_MACHINE_POSTER", "M10_PLATES_LABEL", "M10_STREET_POSTER",
    "M10_WORKSHOP_POSTER",
    "M1_BASE_TEN_LABEL", "M1_BUTTON_CARD", "M1_DOUBLE_TEN_FRAME",
    "M1_LABEL", "M1_PLUS_PUPPET_TEMPLATE",
    "M2_COUNTERS_LABEL", "M2_JAR_LABEL", "M2_MINNIE_PUPPET_TEMPLATE",
    "M2_PLACE_VALUE_MAT", "M2_PV_MAT_TH", "M2_TEN_FRAME",
    "M3_BASE_TEN_LABEL", "M3_CHART", "M3_DOUBLE_TEN_FRAME",
    "M3_KITTEN_TOKEN", "M3_NUMBER_LINE_PAGE", "M3_STREET_PAGE",
    "M4_ARRAY", "M4_BASKETS_TEMPLATE", "M4_COMPARE_CARD",
    "M4_COUNTERS_LABEL", "M4_DECOMP_CARD", "M4_NUMBER_LINE_PAGE",
    "M5_COMPARE_CARD", "M5_LABEL", "M5_PIZZA_FRACTIONS",
    "M5_ROUNDING_CARD", "M5_STORY_CARD", "M5_TRIANGLE_CARD",
    "M6_ARRAY_GRID", "M6_CUBES_LABEL", "M6_DICE_LABEL",
    "M6_PLATE_TEMPLATE", "M6_TREAT_TOKEN", "M6_TRIANGLE",
    "M7_COOKIE_TOKEN", "M7_FRACTION_STRIPS", "M7_HUNDREDS_CHART",
    "M7_MATCH_CARD", "M7_STORY_CARD", "M7_STRIPS",
    "M8_COOKIE_CARD", "M8_JARS_LABEL", "M8_PLATES_LABEL",
    "M8_RATIO_TABLE",
    "M9_PIZZA_CARD", "M9_PLATES_LABEL", "M9_STORY", "M9_TRIANGLE_CARD",
    # WS_ — large set; we'll handle them all as workspaces or specialized
    "WS01_P1_FACTS_TABLE", "WS01_P1_FOUR_CHUNKS",
    "WS01_P1_SIX_BUILDS", "WS01_P1_SIX_TRIANGLES",
    "WS01_P1_TWO_BUTTON_JARS",
    "WS01_P2_FOUR_ALGORITHMS", "WS01_P2_FOUR_TEN_FRAMES",
    "WS01_P2_SIX_NUMBERS", "WS01_P2_THREE_NUMBER_LINES",
    "WS01_P3_BLANK_REAL_LIFE_BOX", "WS01_P3_BLANK_STRATEGY_BOX",
    # FORM_
    "FORM_Q1_FLUENCY", "FORM_Q1_FOUR_BASKETS", "FORM_Q1_SIX_STRATEGY_BOXES",
    "FORM_Q1_THREE_ROWS", "FORM_Q1_TWO_DECOMP_BOXES",
    "FORM_Q2_ARRAY", "FORM_Q2_FILL_NUMBER_LINE", "FORM_Q2_ORDER",
    "FORM_Q2_ORDER_FIVE", "FORM_Q2_THREE_ARRAYS", "FORM_Q2_THREE_TRIANGLES",
    # Number catch-all (workspace-style WS_/M_ ids)
    "WS01_P3_PLUS_TWO_PAWS", "WS02_P1_DOUBLES_TABLE", "WS02_P2_NEAR_DOUBLES",
    "WS02_P3_FOUR_MAKE_TENS", "WS02_P4_STRATEGY_CHOICE",
    "WS03_P1_SIX_TRIANGLES", "WS03_P2_FOUR_CUPS", "WS03_P3_TWO_COLUMNS",
    "WS04_P1_TWO_CHANGE_ADD", "WS04_P2_TWO_CHANGE_TAKE",
    "WS04_P3_TWO_PART_WHOLE", "WS04_P4_BLANK_STORY_BOX",
    "WS05_P1_TWO_EVEN_SHARES", "WS05_P2_TWO_HALF_SHARES",
    "WS05_P3_WHY_HALF_BOX",
    "WS02_P1_MATCH_GRID", "WS02_P2_NUMERAL_WORD_MATCH",
    "WS02_P3_FIVE_WAYS_BOXES", "WS03_P1_DECOMP_GRID",
    "WS03_P2_COMPOSE_TASKS", "WS03_P3_OPEN_DECOMP",
    "WS04_P1_SIX_COMPARES", "WS04_P2_ORDER_TASKS", "WS04_P3_MY_NUMBERS",
    "WS05_P1_TWO_SHARE_SCENES", "WS05_P2_TWO_PIZZAS",
    "WS05_P3_FOUR_FRACTIONS",
    "WS01_P3_FOUR_CHUNKS", "WS01_P4_STRATEGY_CHOICE",
    "WS02_P1_TWO_CHANGE_ADD", "WS02_P2_TWO_CHANGE_TAKE",
    "WS02_P3_TWO_PART_WHOLE", "WS02_P4_BLANK_STORY",
    "WS03_P1_SIX_BASKETS", "WS03_P2_FOUR_ARRAYS", "WS03_P3_THREE_BUILDS",
    "WS03_P4_REAL_LIFE_BOX", "WS04_P1_FOUR_HALVES", "WS04_P2_FOUR_FOURTHS",
    "WS04_P3_THREE_BUILDS", "WS04_P4_REAL_LIFE_BOX",
    "WS05_P1_THREE_SHARES", "WS05_P2_THREE_TRIANGLES",
    "WS05_P3_SIX_STORIES", "WS05_P4_WAYS_BOX",
    "WS02_P1_THREE_TARGETS", "WS02_P2_SIX_COMPARES", "WS02_P3_ORDER",
    "WS03_P1_SIX_PAIRUPS", "WS03_P2_TWELVE_NUMBERS", "WS03_P3_SKIP_LINES",
    "WS04_P1_THREE_JARS", "WS04_P2_SKIP_LINES", "WS04_P3_HOCKEY_BOX",
    "WS05_P2_TWO_FRACTIONAL", "WS05_P3_TWO_PIZZAS", "WS05_P4_WHY_EQUAL_BOX",
    "WS01_P3_REAL_LIFE_BOX", "WS02_P2_THREE_LINES",
    "WS03_P1_NEAREST_10", "WS03_P2_NEAREST_100", "WS03_P3_FOUR_SCENARIOS",
    "WS04_P1_FOUR_EVEN", "WS04_P2_FOUR_MIXED", "WS04_P3_CHOICE_BOX",
    "WS05_P1_THREE_CHAINS", "WS05_P2_THREE_PIZZAS",
    "WS05_P3_SIX_CLAIMS", "WS05_P4_WHY_BOX",
    "WS02_P1_SIX_COMPARES",
    "WS01_P3_THREE_STORIES", "WS02_P1_FLUENCY_TABLE",
    "WS02_P2_SIX_TRIANGLES", "WS02_P3_SIX_PAIRS",
    "WS03_P1_SIX_TRICKY", "WS03_P2_HINTS", "WS03_P3_CHART",
    "WS04_P1_DECOMP", "WS04_P2_FRAC_MULT", "WS04_P3_THREE_WAYS_BOX",
    "WS05_P1_THREE_TABLES", "WS05_P2_SIX_SCENARIOS", "WS05_P3_MY_RATIO_BOX",
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _ten_frame(filled: int = 0) -> Image.Image:
    canvas, draw = _new("Ten Frame")
    rows, cols = 2, 5
    cell = 100
    grid_w = cell * cols
    grid_h = cell * rows
    x0 = (1024 - grid_w) // 2
    y0 = 250
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * cell
            y = y0 + r * cell
            draw.rectangle((x, y, x + cell, y + cell),
                           outline=(20, 20, 20), width=4)
            idx = r * cols + c
            if idx < filled:
                draw.ellipse((x + 18, y + 18, x + cell - 18, y + cell - 18),
                             fill=(20, 20, 20))
    return canvas


def _double_ten_frame() -> Image.Image:
    canvas, draw = _new("Double Ten Frame")
    rows, cols = 2, 5
    cell = 80
    margin = 80
    for blk in range(2):
        x_off = margin + blk * (cols * cell + 60)
        y0 = 280
        for r in range(rows):
            for c in range(cols):
                x = x_off + c * cell
                y = y0 + r * cell
                draw.rectangle((x, y, x + cell, y + cell),
                               outline=(20, 20, 20), width=3)
    return canvas


def _hundreds_chart() -> Image.Image:
    canvas, draw = _new("Hundreds Chart")
    rows, cols = 10, 10
    cell = 56
    grid_w = cell * cols
    grid_h = cell * rows
    x0 = (1024 - grid_w) // 2
    y0 = 130
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * cell
            y = y0 + r * cell
            draw.rectangle((x, y, x + cell, y + cell),
                           outline=(20, 20, 20), width=1)
            n = r * 10 + c + 1
            TC._text_centered(draw, (x + cell // 2, y + cell // 2),
                              str(n), TC._font(18, bold=True))
    return canvas


def _number_line(start: int = 0, end: int = 20, step: int = 1) -> Image.Image:
    canvas, draw = _new(f"Number Line {start}-{end}")
    margin = 60
    y = 384
    draw.line([(margin, y), (1024 - margin, y)], fill=(20, 20, 20), width=4)
    n = (end - start) // step + 1
    for i in range(n):
        x = margin + (1024 - 2 * margin) * i // (n - 1)
        h = 14 if i % 5 != 0 else 24
        draw.line([(x, y - h), (x, y + h)], fill=(20, 20, 20), width=2)
        if i % 5 == 0:
            v = start + i * step
            TC._text_centered(draw, (x, y + 50), str(v),
                              TC._font(22, bold=True))
    # arrow caps
    draw.polygon([(margin - 18, y - 12), (margin - 18, y + 12),
                  (margin - 32, y)], fill=(20, 20, 20))
    draw.polygon([(1024 - margin + 18, y - 12), (1024 - margin + 18, y + 12),
                  (1024 - margin + 32, y)], fill=(20, 20, 20))
    return canvas


def _place_value_mat(places: list[str] = None) -> Image.Image:
    places = places or ["Hundreds", "Tens", "Ones"]
    canvas, draw = _new("Place Value Mat")
    n = len(places)
    margin = 60
    cw = (1024 - 2 * margin) // n
    for i, p in enumerate(places):
        x0 = margin + i * cw
        x1 = x0 + cw - 14
        draw.rectangle((x0, 130, x1, 160),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, ((x0 + x1) // 2, 145),
                          p, TC._font(24, bold=True))
        draw.rectangle((x0, 170, x1, 720),
                       outline=(20, 20, 20), width=3)
    return canvas


def _array_grid(rows: int = 4, cols: int = 5) -> Image.Image:
    canvas, draw = _new(f"Array — {rows} × {cols}")
    margin = 80
    cell = min(60, (1024 - 2 * margin) // cols)
    grid_w = cell * cols
    grid_h = cell * rows
    x0 = (1024 - grid_w) // 2
    y0 = (768 - grid_h) // 2
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * cell
            y = y0 + r * cell
            draw.ellipse((x + 6, y + 6, x + cell - 6, y + cell - 6),
                         fill=(20, 20, 20))
    return canvas


def _fraction_strips() -> Image.Image:
    canvas, draw = _new("Fraction Strips")
    margin = 60
    strip_h = 50
    fractions = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 6), (1, 8)]
    for i, (num, den) in enumerate(fractions):
        y0 = 130 + i * 90
        strip_w = 1024 - 2 * margin
        # divisions
        for k in range(den):
            x0 = margin + strip_w * k // den
            x1 = margin + strip_w * (k + 1) // den
            draw.rectangle((x0, y0, x1, y0 + strip_h),
                           outline=(20, 20, 20), width=3)
            TC._text_centered(draw, ((x0 + x1) // 2, y0 + strip_h // 2),
                              f"1/{den}" if den > 1 else "1",
                              TC._font(20, bold=True))
    return canvas


def _pizza_fractions() -> Image.Image:
    canvas, draw = _new("Pizza Fractions")
    items = [(2, "1/2"), (4, "1/4"), (3, "1/3"), (6, "1/6"), (8, "1/8")]
    cols = 3
    rows = 2
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, (slices, lab) in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        cx, cy = x0 + cw // 2, y0 + ch // 2 - 14
        R = min(cw, ch) // 3
        draw.ellipse((cx - R, cy - R, cx + R, cy + R),
                     outline=(20, 20, 20), width=3)
        for k in range(slices):
            ang = -math.pi / 2 + 2 * math.pi * k / slices
            draw.line([(cx, cy),
                       (cx + R * math.cos(ang),
                        cy + R * math.sin(ang))],
                      fill=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch - 24),
                          lab, TC._font(22, bold=True))
    return canvas


def _ratio_table() -> Image.Image:
    canvas, draw = _new("Ratio Table")
    headers = ["× 1", "× 2", "× 3", "× 4", "× 5"]
    n_cols = len(headers)
    cell_w = (1024 - 80) // n_cols
    top = 130
    cell_h = 80
    for j, h in enumerate(headers):
        x0 = 40 + j * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          h, TC._font(24, bold=True))
    for r in range(6):
        y0 = top + cell_h * (r + 1)
        for j in range(n_cols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
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


def compose_number_image(image_id: str, grade: str | None = None,
                         unit_id: str | None = None) -> Image.Image | None:
    # ── Manipulatives ──
    if image_id in ("M1_DOUBLE_TEN_FRAME", "M3_DOUBLE_TEN_FRAME"):
        return _double_ten_frame()
    if image_id == "M2_TEN_FRAME":
        return _ten_frame()
    if image_id in ("M1_BUTTON_CARD", "M1_LABEL", "M2_COUNTERS_LABEL",
                     "M2_JAR_LABEL", "M3_BASE_TEN_LABEL", "M4_COUNTERS_LABEL",
                     "M5_LABEL", "M1_BASE_TEN_LABEL", "M6_CUBES_LABEL",
                     "M6_DICE_LABEL", "M8_JARS_LABEL", "M8_PLATES_LABEL",
                     "M9_PLATES_LABEL", "M10_PLATES_LABEL"):
        return _ten_frame(filled=5)
    if image_id in ("M2_PLACE_VALUE_MAT", "M2_PV_MAT_TH"):
        return _place_value_mat(["Thousands", "Hundreds", "Tens", "Ones"])
    if image_id in ("M3_NUMBER_LINE_PAGE", "M4_NUMBER_LINE_PAGE"):
        return _number_line(0, 20)
    if image_id == "M3_STREET_PAGE":
        return _number_line(0, 100, step=10)
    if image_id == "M3_CHART":
        return _hundreds_chart()
    if image_id in ("M4_ARRAY", "M6_ARRAY_GRID"):
        return _array_grid(4, 6)
    if image_id == "M4_BASKETS_TEMPLATE":
        return _workspace("Sort into 4 baskets.", title="Baskets",
                          box_h=460)
    if image_id in ("M4_COMPARE_CARD", "M5_COMPARE_CARD"):
        return _workspace("Compare numbers <, =, >.",
                          title="Compare", box_h=460)
    if image_id == "M4_DECOMP_CARD":
        return _workspace("Decompose: split a number two ways.",
                          title="Decompose", box_h=460)
    if image_id == "M5_PIZZA_FRACTIONS":
        return _pizza_fractions()
    if image_id == "M5_ROUNDING_CARD":
        return _number_line(0, 100, step=10)
    if image_id in ("M5_STORY_CARD", "M7_STORY_CARD", "M9_STORY"):
        return _workspace("Read the story. Show your math.",
                          title="Story Card", box_h=460)
    if image_id in ("M5_TRIANGLE_CARD", "M6_TRIANGLE", "M9_TRIANGLE_CARD"):
        return _array_grid(3, 3)
    if image_id == "M6_PLATE_TEMPLATE":
        return _array_grid(3, 3)
    if image_id in ("M6_TREAT_TOKEN", "M3_KITTEN_TOKEN", "M7_COOKIE_TOKEN",
                     "M8_COOKIE_CARD", "M7_MATCH_CARD"):
        return _array_grid(4, 5)
    if image_id == "M7_FRACTION_STRIPS":
        return _fraction_strips()
    if image_id == "M7_HUNDREDS_CHART":
        return _hundreds_chart()
    if image_id == "M7_STRIPS":
        return _fraction_strips()
    if image_id == "M8_RATIO_TABLE":
        return _ratio_table()
    if image_id == "M9_PIZZA_CARD":
        return _pizza_fractions()
    if image_id == "M1_PLUS_PUPPET_TEMPLATE":
        # Render the kawaii Plus SVG as the puppet template hero so the
        # manipulative slide actually shows the character (visual_inspector
        # round-6 flagged this as empty placeholder).
        from .compose import _character_svg_path, _compose_custom_character_card
        svg = _character_svg_path("PLUS")
        if svg is not None:
            return _compose_custom_character_card(svg, "Plus the Adding Pup")
        return _workspace("Plus the Adder puppet template.",
                          title="Plus Puppet", box_h=480)
    if image_id == "M2_MINNIE_PUPPET_TEMPLATE":
        from .compose import _character_svg_path, _compose_custom_character_card
        svg = _character_svg_path("MINNIE")
        if svg is not None:
            return _compose_custom_character_card(svg, "Minnie the Minus Mouse")
        return _workspace("Minnie the Minus puppet template.",
                          title="Minnie Puppet", box_h=480)
    if image_id == "M10_MACHINE_POSTER":
        return _poster("Adding Machine", [
            "Take TWO numbers.",
            "Add them with strategies.",
            "Check on the ten frame.",
            "Show your work.",
        ])
    if image_id == "M10_STREET_POSTER":
        return _poster("Fraction Street", [
            "Pizzas, pies, and bars!",
            "Equal parts = equal shares.",
            "Compare fractions.",
            "Add and subtract halves.",
        ])
    if image_id == "M10_WORKSHOP_POSTER":
        return _poster("Times Table Workshop", [
            "Skip count to multiply.",
            "Build arrays.",
            "Use fact families.",
            "Memorize × 1 to × 10.",
        ])

    # ── Worksheets — workspaces and specialized ──
    if image_id == "WS01_P1_FACTS_TABLE":
        return _ratio_table()
    if image_id in ("WS01_P1_FOUR_CHUNKS", "WS01_P1_SIX_BUILDS"):
        return _workspace("Build with chunks.", title="Build It",
                          box_h=480)
    if image_id == "WS01_P1_SIX_TRIANGLES":
        return _workspace("Six fact-family triangles.",
                          title="Triangles", box_h=480)
    if image_id == "WS01_P1_TWO_BUTTON_JARS":
        return _workspace("Two button jars — count and compare.",
                          title="Button Jars", box_h=480)
    if image_id == "WS01_P2_FOUR_ALGORITHMS":
        return _workspace("Show four algorithms.",
                          title="Algorithms", box_h=480)
    if image_id == "WS01_P2_FOUR_TEN_FRAMES":
        return _double_ten_frame()
    if image_id == "WS01_P2_SIX_NUMBERS":
        return _workspace("Order six numbers.",
                          title="Order Numbers", box_h=480)
    if image_id == "WS01_P2_THREE_NUMBER_LINES":
        return _number_line(0, 30)
    if image_id in ("WS01_P3_BLANK_REAL_LIFE_BOX",
                     "WS01_P3_BLANK_STRATEGY_BOX"):
        return _workspace("Show a real-life problem.",
                          title="Real-Life Box", box_h=480)

    # ── Formative ──
    if image_id == "FORM_Q1_FLUENCY":
        return _ten_frame(filled=5)
    if image_id == "FORM_Q1_FOUR_BASKETS":
        return _workspace("Sort into 4 baskets.", title="Baskets")
    if image_id == "FORM_Q1_SIX_STRATEGY_BOXES":
        return _workspace("Show 6 strategies.", title="Strategy Boxes",
                          box_h=480)
    if image_id == "FORM_Q1_THREE_ROWS":
        return _array_grid(3, 5)
    if image_id == "FORM_Q1_TWO_DECOMP_BOXES":
        return _workspace("Two decomposition boxes.",
                          title="Decompose")
    if image_id == "FORM_Q2_ARRAY":
        return _array_grid(4, 5)
    if image_id == "FORM_Q2_FILL_NUMBER_LINE":
        return _number_line(0, 20)
    if image_id == "FORM_Q2_ORDER":
        return _workspace("Order numbers.", title="Order")
    if image_id == "FORM_Q2_ORDER_FIVE":
        return _workspace("Order 5 numbers.", title="Order Five")
    if image_id == "FORM_Q2_THREE_ARRAYS":
        return _array_grid(3, 4)
    if image_id == "FORM_Q2_THREE_TRIANGLES":
        return _workspace("Three fact triangles.",
                          title="Triangles")

    # ── Catch-all for number-unit WS_/M_ ids: workspace with derived title ──
    # Triggered for any number-themed id we haven't given a bespoke composer.
    # Title comes from the id (humanised); prompt is a generic "Show your work".
    NUMBER_CATCHALL = {
        "WS01_P3_PLUS_TWO_PAWS", "WS02_P1_DOUBLES_TABLE", "WS02_P2_NEAR_DOUBLES",
        "WS02_P3_FOUR_MAKE_TENS", "WS02_P4_STRATEGY_CHOICE",
        "WS03_P1_SIX_TRIANGLES", "WS03_P2_FOUR_CUPS", "WS03_P3_TWO_COLUMNS",
        "WS04_P1_TWO_CHANGE_ADD", "WS04_P2_TWO_CHANGE_TAKE",
        "WS04_P3_TWO_PART_WHOLE", "WS04_P4_BLANK_STORY_BOX",
        "WS05_P1_TWO_EVEN_SHARES", "WS05_P2_TWO_HALF_SHARES",
        "WS05_P3_WHY_HALF_BOX",
        "WS02_P1_MATCH_GRID", "WS02_P2_NUMERAL_WORD_MATCH",
        "WS02_P3_FIVE_WAYS_BOXES", "WS03_P1_DECOMP_GRID",
        "WS03_P2_COMPOSE_TASKS", "WS03_P3_OPEN_DECOMP",
        "WS04_P1_SIX_COMPARES", "WS04_P2_ORDER_TASKS", "WS04_P3_MY_NUMBERS",
        "WS05_P1_TWO_SHARE_SCENES", "WS05_P2_TWO_PIZZAS",
        "WS05_P3_FOUR_FRACTIONS",
        "WS01_P3_FOUR_CHUNKS", "WS01_P4_STRATEGY_CHOICE",
        "WS02_P1_TWO_CHANGE_ADD", "WS02_P2_TWO_CHANGE_TAKE",
        "WS02_P3_TWO_PART_WHOLE", "WS02_P4_BLANK_STORY",
        "WS03_P1_SIX_BASKETS", "WS03_P2_FOUR_ARRAYS", "WS03_P3_THREE_BUILDS",
        "WS03_P4_REAL_LIFE_BOX", "WS04_P1_FOUR_HALVES", "WS04_P2_FOUR_FOURTHS",
        "WS04_P3_THREE_BUILDS", "WS04_P4_REAL_LIFE_BOX",
        "WS05_P1_THREE_SHARES", "WS05_P2_THREE_TRIANGLES",
        "WS05_P3_SIX_STORIES", "WS05_P4_WAYS_BOX",
        "WS02_P1_THREE_TARGETS", "WS02_P2_SIX_COMPARES", "WS02_P3_ORDER",
        "WS03_P1_SIX_PAIRUPS", "WS03_P2_TWELVE_NUMBERS", "WS03_P3_SKIP_LINES",
        "WS04_P1_THREE_JARS", "WS04_P2_SKIP_LINES", "WS04_P3_HOCKEY_BOX",
        "WS05_P2_TWO_FRACTIONAL", "WS05_P3_TWO_PIZZAS", "WS05_P4_WHY_EQUAL_BOX",
        "WS01_P3_REAL_LIFE_BOX", "WS02_P2_THREE_LINES",
        "WS03_P1_NEAREST_10", "WS03_P2_NEAREST_100", "WS03_P3_FOUR_SCENARIOS",
        "WS04_P1_FOUR_EVEN", "WS04_P2_FOUR_MIXED", "WS04_P3_CHOICE_BOX",
        "WS05_P1_THREE_CHAINS", "WS05_P2_THREE_PIZZAS",
        "WS05_P3_SIX_CLAIMS", "WS05_P4_WHY_BOX",
        "WS02_P1_SIX_COMPARES",
        "WS01_P3_THREE_STORIES", "WS02_P1_FLUENCY_TABLE",
        "WS02_P2_SIX_TRIANGLES", "WS02_P3_SIX_PAIRS",
        "WS03_P1_SIX_TRICKY", "WS03_P2_HINTS", "WS03_P3_CHART",
        "WS04_P1_DECOMP", "WS04_P2_FRAC_MULT", "WS04_P3_THREE_WAYS_BOX",
        "WS05_P1_THREE_TABLES", "WS05_P2_SIX_SCENARIOS", "WS05_P3_MY_RATIO_BOX",
    }
    if image_id in NUMBER_CATCHALL:
        # WS_ ids: defer to the smart_fallback WS hero composer in compose.py
        # which reads 2_worksheet_NN.json for real part labels (added 2026-05-10
        # to clear ~25 worksheet hero placeholders flagged by visual_inspector).
        if image_id.startswith("WS"):
            return None
        title = image_id.replace("_", " ").title()
        return _workspace("Show your work below.", title=title, box_h=480)

    return None
