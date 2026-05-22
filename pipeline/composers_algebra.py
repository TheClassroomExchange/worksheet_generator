"""Bespoke composers for the four algebra units (g2/g3).

  whats_missing       — variables, balance mats, addition/subtraction
  if_then_detectives  — condition+action cards, truth tables
  balanced_equations  — balance scales, equation puzzles
  bug_busters         — code cards, grid mat, bug cards, debugging
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    # whats_missing (g2)
    "M1_VAR_CARD", "M2_BALANCE_MAT", "M3_ADD_CARD", "M4_SUB_CARD",
    "M5_COUNTER_SHEET", "M6_TARGET_CARD", "M7_CAPSTONE_TEMPLATE",
    "M9_VAR_CHART",
    "WS01_P1_FIND", "WS01_P2_MATCH", "WS01_P3_OWN",
    "WS02_P1_ADD50", "WS02_P2_ADD100", "WS02_P3_OWN",
    "WS03_P1_MS", "WS03_P2_MM", "WS03_P3_OWN",
    "WS04_P1_M50", "WS04_P2_M100", "WS04_P3_PICK",
    "WS05_P1_CASE", "WS05_P2_EQN", "WS05_P3_SOLVE", "WS05_P4_EQUIV",
    "FORM_Q1_VAR", "FORM_Q2_ADD", "FORM_Q3_SUB",
    # if_then_detectives (g2)
    "M1_IFTHEN_CARD", "M2_CONDITION_CARD", "M3_ACTION_CARD",
    "M4_INPUT_CARD", "M5_ALTER_CARD", "M7_SORT_MAT", "M9_TRUTH_CHART",
    "M10_IFTHEN_POSTER",
    "WS01_P2_TF", "WS02_P1_MATCH", "WS02_P2_TWO",
    "WS03_P1_TRACE", "WS03_P2_INPUTS", "WS03_P3_VERIFY",
    "WS04_P1_COND", "WS04_P2_ACTION", "WS04_P3_SWAP",
    "WS05_P1_CODE", "WS05_P2_TRACE", "WS05_P3_ALTER", "WS05_P4_REFLECT",
    "FORM_Q1_FIND", "FORM_Q2_TRACE", "FORM_Q3_WRITE",
    # balanced_equations (g3)
    "M1_VAR_CHART", "M4_MULT_CARD", "M5_TARGET_CARD", "M9_EQUATION_CHART",
    "M10_ENGINEER_POSTER",
    "WS01_P2_SORT",
    "WS02_P1_PAIRS", "WS02_P2_PARTNER",
    "WS03_P1_PAIRS", "WS03_P2_PARTNER", "WS03_P3_OWN",
    "WS04_P1_M100", "WS04_P2_M500", "WS04_P3_TARGET",
    "WS05_P1_PUZZLE", "WS05_P2_SOLVE", "WS05_P3_EQUIV",
    "FORM_Q3_DIV",
    # bug_busters (g3)
    "M1_GRID_MAT", "M2_CODE_CARD", "M3_BUG_CARD", "M4_ROBOT_TOKEN",
    "M5_CONCURRENT_CHART", "M7_LOOP_CARD", "M8_ALTER_CARD", "M9_BUG_CHART",
    "M10_BUSTER_POSTER",
    "WS01_P1_SORT", "WS01_P2_TRACE",
    "WS02_P1_SYNC", "WS02_P2_LOOP", "WS02_P3_MY",
    "WS03_P1_BUGS", "WS03_P2_TRACE",
    "WS04_P1_FIX", "WS04_P2_MIXED", "WS04_P3_PARTNER",
    "WS05_P2_BUG", "WS05_P3_PARTNER",
    "FORM_Q1_CS", "FORM_Q2_WRITE", "FORM_Q3_BUG",
    # Shared between if_then and bug_busters (and others):
    "WS05_P4_REFLECT",  # already listed above
    # ---- g1 balance_stories ----
    "M1_BALANCE_INSTRUCTIONS", "M3_SORT_CARD", "M4_EXPRESSION_CARD",
    "M5_LABEL", "M6_MYSTERY_CARD", "M8_STORY_TEMPLATE", "M9_EQUAL_CHART",
    "M7_TARGET_CARD",
    "WS01_P1_TWELVE_CARDS", "WS01_P2_TWO_COLUMNS", "WS01_P3_WHY_BOX",
    "WS02_P1_SIX_PAIRS", "WS02_P2_FOUR_BALANCES", "WS02_P3_MY_OWN",
    "WS03_P1_EIGHT_ADDS", "WS03_P2_SIX_SUBS", "WS03_P3_THREE_BALANCES",
    "WS04_P1_EIGHT_SLOTS", "WS04_P2_SIX_SLOTS", "WS04_P3_MY_TARGET",
    "WS05_P1_STORY_BOX", "WS05_P2_BALANCE_BOX",
    "WS05_P3_EQUATION", "WS05_P4_EQUIVALENT",
    "FORM_Q1_PAIRS", "FORM_Q2_MISSING",
    # ---- g1 loop_the_loop ----
    "M3_SAMPLE_CARD", "M5_LOOP_CARD", "M6_TEMPLATE",
    "M7_PREDICT_CHART", "M9_CAPSTONE_TEMPLATE",
    "WS01_P1_FIVE_STEPS", "WS01_P2_FOUR_GRIDS", "WS01_P3_TASK_BOX",
    "WS02_P1_FOUR_CONVERSIONS", "WS02_P2_THREE_SHAPES", "WS02_P3_MY_LOOP",
    "WS03_P1_SIX_GRIDS", "WS03_P2_FOUR_SHAPES", "WS03_P3_LOOP_PREDICT",
    "WS04_P1_SIX_ALTERS", "WS04_P2_FOUR_STEPS", "WS04_P3_INVARIANT",
    "WS05_P1_PROJECT_BOX", "WS05_P2_CODE_AREA",
    "WS05_P3_PREDICTION", "WS05_P4_VERIFY",
    "FORM_Q1_LOOP", "FORM_Q2_PREDICT_GRID",
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _equation_text(left: str, right: str = "") -> Image.Image:
    canvas, draw = _new()
    txt = f"{left}  =  {right}" if right else left
    TC._text_centered(draw, (512, 384), txt, TC._font(72, bold=True))
    return canvas


def _card_grid(items: list[str], cols: int = 4, title: str | None = None,
               box_label_font: int = 24) -> Image.Image:
    """Grid of N text cards."""
    import math
    canvas, draw = _new(title)
    rows = max(1, math.ceil(len(items) / cols))
    margin = 50
    top = 110 if title else 60
    cell_w = (1024 - 2 * margin) // cols
    cell_h = (768 - top - margin) // rows
    for i, item in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cell_w
        y0 = top + r * cell_h
        draw.rectangle((x0 + 8, y0 + 8, x0 + cell_w - 8, y0 + cell_h - 8),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cell_w // 2, y0 + cell_h // 2),
                          item, TC._font(box_label_font, bold=True))
    return canvas


def _balance_mat() -> Image.Image:
    canvas, draw = _new("Balance Mat")
    # base + post
    draw.line([(220, 600), (804, 600)], fill=(20, 20, 20), width=4)
    draw.line([(512, 200), (512, 600)], fill=(20, 20, 20), width=4)
    # cross beam
    draw.line([(220, 250), (804, 250)], fill=(20, 20, 20), width=5)
    # pans
    for cx in (300, 724):
        draw.line([(cx, 250), (cx - 60, 320)], fill=(20, 20, 20), width=2)
        draw.line([(cx, 250), (cx + 60, 320)], fill=(20, 20, 20), width=2)
        draw.arc((cx - 80, 300, cx + 80, 360),
                 start=0, end=180, fill=(20, 20, 20), width=3)
        # workspace below pans
        draw.rectangle((cx - 100, 380, cx + 100, 540),
                       outline=(20, 20, 20), width=2)
    # equation arrow / label
    TC._text_centered(draw, (512, 670), "= ?", TC._font(40, bold=True))
    return canvas


def _truth_chart() -> Image.Image:
    canvas, draw = _new("Truth Chart")
    headers = ["Condition", "TRUE", "FALSE"]
    rows = [["Number > 5", "?", "?"],
            ["Even number", "?", "?"],
            ["Has wheels", "?", "?"],
            ["Is red", "?", "?"]]
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
    for r, row in enumerate(rows):
        y0 = top + cell_h * (r + 1)
        for j, val in enumerate(row):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
            if j > 0:
                draw.ellipse((x0 + cell_w // 2 - 24, y0 + cell_h // 2 - 24,
                              x0 + cell_w // 2 + 24, y0 + cell_h // 2 + 24),
                             outline=(20, 20, 20), width=2)
            else:
                TC._text_centered(draw,
                                  (x0 + cell_w // 2, y0 + cell_h // 2),
                                  val, TC._font(20))
    return canvas


def _grid_mat(cols: int = 8, rows: int = 6) -> Image.Image:
    canvas, draw = _new("Robot Grid Mat")
    margin = 80
    top = 130
    bottom = 700
    cell = min((1024 - 2 * margin) // cols, (bottom - top) // rows)
    grid_w = cell * cols
    grid_h = cell * rows
    x0 = (1024 - grid_w) // 2
    y0 = top
    for r in range(rows + 1):
        draw.line([(x0, y0 + r * cell), (x0 + grid_w, y0 + r * cell)],
                  fill=(20, 20, 20), width=2)
    for c in range(cols + 1):
        draw.line([(x0 + c * cell, y0), (x0 + c * cell, y0 + grid_h)],
                  fill=(20, 20, 20), width=2)
    # axis labels
    for c in range(cols):
        TC._text_centered(draw, (x0 + c * cell + cell // 2, y0 - 20),
                          str(c), TC._font(18))
    for r in range(rows):
        TC._text_centered(draw, (x0 - 20, y0 + r * cell + cell // 2),
                          str(r), TC._font(18))
    return canvas


def _arrow_card(symbol: str, label: str) -> Image.Image:
    canvas, draw = _new()
    # large arrow inside box
    draw.rectangle((100, 100, 924, 668), outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 320), symbol, TC._font(180, bold=True))
    TC._text_centered(draw, (512, 560), label, TC._font(34, bold=True))
    return canvas


def _writing_workspace(prompt: str, title: str | None = None,
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


def _equation_table(rows: int = 5,
                    headers: tuple = ("Equation", "Variable", "Solution")) -> Image.Image:
    canvas, draw = _new("Equation Table")
    n_cols = len(headers)
    cell_w = (1024 - 80) // n_cols
    top = 130
    cell_h = 80
    for j, h in enumerate(headers):
        x0 = 40 + j * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          h, TC._font(22, bold=True))
    for r in range(rows):
        y0 = top + cell_h * (r + 1)
        for j in range(n_cols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    return canvas


def _capstone_template(steps: list[str]) -> Image.Image:
    canvas, draw = _new()
    y = 30
    available = 768 - 60
    sec_h = available // len(steps)
    for s in steps:
        draw.rectangle((30, y, 994, y + sec_h - 8),
                       outline=(20, 20, 20), width=2)
        draw.text((50, y + 10), s, font=TC._font(20, bold=True),
                  fill=(20, 20, 20))
        for gy in range(y + 50, y + sec_h - 16, 36):
            draw.line([(60, gy), (970, gy)], fill=(220, 220, 220), width=1)
        y += sec_h
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


def _bug_card(label: str = "BUG") -> Image.Image:
    canvas, draw = _new()
    cx, cy = 512, 384
    # body
    draw.ellipse((cx - 200, cy - 130, cx + 200, cy + 130),
                 outline=(20, 20, 20), width=4)
    draw.line([(cx, cy - 130), (cx, cy + 130)],
              fill=(20, 20, 20), width=3)
    # spots
    for sx, sy in [(cx - 100, cy - 50), (cx + 100, cy - 50),
                   (cx - 100, cy + 50), (cx + 100, cy + 50)]:
        draw.ellipse((sx - 16, sy - 16, sx + 16, sy + 16),
                     outline=(20, 20, 20), width=2)
    # antennae
    for sign in (-1, 1):
        draw.line([(cx + sign * 50, cy - 130), (cx + sign * 80, cy - 200)],
                  fill=(20, 20, 20), width=3)
        draw.ellipse((cx + sign * 80 - 8, cy - 208,
                      cx + sign * 80 + 8, cy - 192),
                     outline=(20, 20, 20), width=2)
    TC._text_centered(draw, (cx, cy + 200), label,
                      TC._font(36, bold=True))
    return canvas


def compose_algebra_image(image_id: str, grade: str | None = None,
                          unit_id: str | None = None) -> Image.Image | None:
    # ─────────── whats_missing (g2) ───────────
    if image_id == "M1_VAR_CARD":
        return _card_grid(["?", "x", "□", "△", "y", "○", "◇", "▢"],
                          cols=4, title="Variable Cards", box_label_font=72)
    if image_id == "M2_BALANCE_MAT":
        return _balance_mat()
    if image_id == "M3_ADD_CARD":
        return _card_grid(["? + 3 = 8", "5 + ? = 9", "? + 4 = 12",
                           "10 = 6 + ?", "? + 7 = 15", "11 = ? + 4",
                           "? + 6 = 14", "9 + ? = 13"],
                          cols=2, title="Addition Cards")
    if image_id == "M4_SUB_CARD":
        return _card_grid(["10 - ? = 4", "? - 5 = 6", "12 - ? = 7",
                           "? - 3 = 8", "9 - ? = 2", "15 - ? = 9",
                           "? - 6 = 5", "8 - ? = 4"],
                          cols=2, title="Subtraction Cards")
    if image_id == "M5_COUNTER_SHEET":
        return _equation_table(rows=8,
                               headers=("Counters", "Total", "Note"))
    if image_id in ("M6_TARGET_CARD", "M5_TARGET_CARD", "M7_TARGET_CARD"):
        return _card_grid(["10", "20", "50", "100", "5", "25", "75", "200"],
                          cols=4, title="Target Cards", box_label_font=64)
    if image_id == "M7_CAPSTONE_TEMPLATE":
        return _capstone_template([
            "1. The CASE:",
            "2. The EQUATION:",
            "3. SOLVE the variable:",
            "4. Equivalent expressions:",
        ])
    if image_id in ("M9_VAR_CHART", "M1_VAR_CHART"):
        return _equation_table(rows=6,
                               headers=("Variable", "Stands for", "Value"))
    if image_id == "WS01_P1_FIND":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS01_P2_MATCH":
        return _card_grid(
            ["? + 5 = 10  →  ? = ", "12 - ? = 7  →  ? = ",
             "? + 8 = 14  →  ? = ", "20 - ? = 12  →  ? = "],
            cols=2, title="Match the Variable", box_label_font=22)
    if image_id == "WS01_P3_OWN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P1_ADD50":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P2_ADD100":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P3_OWN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P1_MS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P2_MM":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P3_OWN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P1_M50":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_M100":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_PICK":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P1_CASE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_EQN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P3_SOLVE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P4_EQUIV":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "FORM_Q1_VAR":
        return _writing_workspace("Find the variable.",
                                  title="Variable Check", box_h=440)
    if image_id == "FORM_Q2_ADD":
        return _writing_workspace("Add to find the missing.",
                                  title="Addition Check", box_h=440)
    if image_id == "FORM_Q3_SUB":
        return _writing_workspace("Subtract to find the missing.",
                                  title="Subtraction Check", box_h=440)
    if image_id == "FORM_Q3_DIV":
        return _writing_workspace("Divide to find the missing.",
                                  title="Division Check", box_h=440)

    # ─────────── if_then_detectives (g2) ───────────
    if image_id == "M1_IFTHEN_CARD":
        return _card_grid(
            ["IF it rains\nTHEN open umbrella",
             "IF dark\nTHEN turn on light",
             "IF cold\nTHEN wear coat",
             "IF tired\nTHEN sleep",
             "IF hungry\nTHEN eat",
             "IF thirsty\nTHEN drink",
             "IF dirty\nTHEN wash",
             "IF late\nTHEN run"],
            cols=2, title="IF-THEN Cards", box_label_font=20)
    if image_id == "M2_CONDITION_CARD":
        return _card_grid(
            ["it rains", "it's dark", "you're cold",
             "you're tired", "you're hungry", "it's late",
             "you're thirsty", "the door is locked"],
            cols=4, title="Condition Cards", box_label_font=18)
    if image_id == "M3_ACTION_CARD":
        return _card_grid(
            ["open umbrella", "turn on light", "wear coat",
             "go to bed", "eat lunch", "run faster",
             "drink water", "use the key"],
            cols=4, title="Action Cards", box_label_font=18)
    if image_id == "M4_INPUT_CARD":
        return _card_grid(
            ["7", "12", "even", "odd", "red", "blue",
             "BIG", "small", "yes", "no", "5+5", "3-1"],
            cols=4, title="Input Cards", box_label_font=24)
    if image_id == "M5_ALTER_CARD":
        return _card_grid(
            ["change condition", "swap action",
             "add an ELSE", "remove a step",
             "add a check", "use AND", "use OR", "wrap in loop"],
            cols=2, title="Alteration Cards", box_label_font=22)
    if image_id == "M7_SORT_MAT":
        canvas, draw = _new("Sort Mat: Conditions vs Actions")
        for i, label in enumerate(("CONDITIONS (IF…)", "ACTIONS (THEN…)")):
            x0 = 40 + i * 500
            x1 = x0 + 460
            draw.rectangle((x0, 130, x1, 720),
                           outline=(20, 20, 20), width=4)
            TC._text_centered(draw, ((x0 + x1) // 2, 165),
                              label, TC._font(28, bold=True))
        return canvas
    if image_id == "M9_TRUTH_CHART":
        return _truth_chart()
    if image_id == "M8_COUNTER_SHEET":
        # 20 blank counters in a 4×5 grid (top-half halves shaded vs bottom for
        # two-colour counters used in true/false games).
        canvas, draw = _new("Two-Colour Counters (cut & flip)")
        cols, rows = 5, 4
        margin_x = 80
        margin_y = 130
        gap = 30
        cell_w = (1024 - 2 * margin_x - (cols - 1) * gap) // cols
        cell_h = (768 - margin_y - 80 - (rows - 1) * gap) // rows
        r = min(cell_w, cell_h) // 2 - 8
        for row in range(rows):
            for col in range(cols):
                cx = margin_x + col * (cell_w + gap) + cell_w // 2
                cy = margin_y + row * (cell_h + gap) + cell_h // 2
                # full circle outline
                draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                             outline=(20, 20, 20), width=3)
                # top semicircle shaded (light fill = "flipped" half)
                draw.chord((cx - r, cy - r, cx + r, cy + r),
                           start=180, end=360, fill=(220, 220, 220),
                           outline=(20, 20, 20), width=2)
                # midline divider
                draw.line([(cx - r, cy), (cx + r, cy)],
                          fill=(20, 20, 20), width=2)
        TC._text_centered(draw, (512, 720),
                          "TRUE = light side up    FALSE = dark side up",
                          TC._font(20))
        return canvas
    if image_id == "M10_IFTHEN_POSTER":
        # Defer to smart_fallback POSTER path so it can embed Inspector If +
        # Action Dog character SVGs into anchor poster zones rather than
        # rendering a plain text poster.
        return None
    if image_id == "WS01_P2_TF":
        return _truth_chart()
    if image_id == "WS02_P1_MATCH":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P2_TWO":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P3_OWN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P1_TRACE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P2_INPUTS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P3_VERIFY":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P1_COND":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_ACTION":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_SWAP":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P1_CODE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_TRACE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P3_ALTER":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P4_REFLECT":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "FORM_Q1_FIND":
        return _writing_workspace("Find the rule.",
                                  title="Find the Rule", box_h=440)
    if image_id == "FORM_Q2_TRACE":
        return _writing_workspace("Trace the input.",
                                  title="Trace Check", box_h=440)
    if image_id == "FORM_Q3_WRITE":
        return _writing_workspace("Write your own IF-THEN rule.",
                                  title="Write a Rule", box_h=440)

    # ─────────── balanced_equations (g3) ───────────
    if image_id == "M4_MULT_CARD":
        return _card_grid(["? × 3 = 12", "4 × ? = 20", "? × 5 = 25",
                           "6 × ? = 24", "? × 8 = 32", "? × 7 = 21",
                           "9 × ? = 36", "? × 4 = 28"],
                          cols=2, title="Multiplication Cards")
    if image_id == "M9_EQUATION_CHART":
        return _equation_table(
            rows=6,
            headers=("Equation", "Variable", "Solution"))
    if image_id == "M10_ENGINEER_POSTER":
        return _poster("Engineer's Equations", [
            "Both sides must BALANCE.",
            "What you do to one side, do to the other.",
            "Variables stand for numbers.",
            "Solve = isolate the variable.",
            "Check by substituting back.",
        ])
    if image_id == "WS01_P2_SORT":
        return None  # defer to smart_fallback WS hero composer
    if image_id in ("WS02_P1_PAIRS", "WS03_P1_PAIRS"):
        return _writing_workspace("Find equation pairs that balance:",
                                  title="Equation Pairs", box_h=480)
    if image_id in ("WS02_P2_PARTNER", "WS03_P2_PARTNER"):
        return _writing_workspace("Trade with a partner. Solve theirs.",
                                  title="Partner Solve", box_h=480)
    if image_id == "WS04_P1_M100":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_M500":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_TARGET":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P1_PUZZLE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_SOLVE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P3_EQUIV":
        return None  # defer to smart_fallback WS hero composer

    # ─────────── bug_busters (g3) ───────────
    if image_id == "M1_GRID_MAT":
        return _grid_mat(cols=8, rows=6)
    if image_id == "M2_CODE_CARD":
        return _card_grid(
            ["MOVE 1 RIGHT", "MOVE 1 LEFT",
             "MOVE 1 UP", "MOVE 1 DOWN",
             "TURN LEFT", "TURN RIGHT",
             "REPEAT 3", "STOP"],
            cols=4, title="Code Cards", box_label_font=20)
    if image_id == "M3_BUG_CARD":
        return _card_grid(
            ["wrong direction", "skipped step",
             "wrong number", "missing repeat",
             "extra step", "swapped pair",
             "wrong start", "wrong end"],
            cols=4, title="Bug Cards", box_label_font=18)
    if image_id == "M4_ROBOT_TOKEN":
        canvas, draw = _new("Robot Tokens")
        # 6 robots in a row
        for i in range(6):
            cx = 100 + i * 150
            cy = 384
            # head
            draw.rectangle((cx - 50, cy - 80, cx + 50, cy - 10),
                           outline=(20, 20, 20), width=3)
            # body
            draw.rectangle((cx - 60, cy + 10, cx + 60, cy + 90),
                           outline=(20, 20, 20), width=3)
            # eyes
            draw.ellipse((cx - 26, cy - 60, cx - 14, cy - 48),
                         fill=(20, 20, 20))
            draw.ellipse((cx + 14, cy - 60, cx + 26, cy - 48),
                         fill=(20, 20, 20))
            # arms
            draw.line([(cx - 60, cy + 30), (cx - 90, cy + 50)],
                      fill=(20, 20, 20), width=3)
            draw.line([(cx + 60, cy + 30), (cx + 90, cy + 50)],
                      fill=(20, 20, 20), width=3)
            TC._text_centered(draw, (cx, cy + 130),
                              f"R{i + 1}", TC._font(22, bold=True))
        return canvas
    if image_id == "M5_CONCURRENT_CHART":
        return _equation_table(
            rows=6,
            headers=("Step", "Robot A", "Robot B"))
    if image_id == "M7_LOOP_CARD":
        return _card_grid(
            ["REPEAT 3 [STEP]",
             "REPEAT 5 [STEP]",
             "REPEAT 2 [TURN, STEP]",
             "REPEAT 4 [STEP, STEP]",
             "WHILE NOT END",
             "REPEAT UNTIL FOUND"],
            cols=2, title="Loop Cards", box_label_font=20)
    if image_id == "M8_ALTER_CARD":
        return _card_grid(
            ["swap two steps", "add a STOP",
             "remove a step", "add a TURN",
             "double the loop", "halve the loop"],
            cols=2, title="Alter Cards", box_label_font=22)
    if image_id == "M9_BUG_CHART":
        return _equation_table(
            rows=5,
            headers=("Code", "Bug", "Fix"))
    if image_id == "M10_BUSTER_POSTER":
        return _poster("Bug Busters", [
            "READ the code carefully.",
            "TRACE step by step.",
            "FIND the first bug.",
            "FIX one thing at a time.",
            "TEST the fix.",
        ])
    if image_id == "WS01_P1_SORT":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS01_P2_TRACE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P1_SYNC":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P2_LOOP":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P3_MY":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P1_BUGS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P2_TRACE":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P1_FIX":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_MIXED":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_PARTNER":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_BUG":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P3_PARTNER":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "FORM_Q1_CS":
        return _writing_workspace("Spot the bug in this code.",
                                  title="Spot the Bug", box_h=440)
    if image_id == "FORM_Q2_WRITE":
        return _writing_workspace("Write a 4-step code.",
                                  title="Write Code", box_h=440)
    if image_id == "FORM_Q3_BUG":
        return _writing_workspace("Trace and find the bug.",
                                  title="Trace and Find", box_h=440)

    # ─────────── g1 balance_stories ───────────
    if image_id == "M1_BALANCE_INSTRUCTIONS":
        return _balance_mat()
    if image_id == "M3_SORT_CARD":
        # g1 balance_stories M3 is "Change vs Stay-the-Same" sort cards —
        # NOT addition expressions. Render category headers with example
        # scenarios as labels (no math expressions).
        return _card_grid(["GIVE 2 more",
                           "TAKE 1 away",
                           "Same group",
                           "ADD 3 more",
                           "MOVE to other side",
                           "Same total",
                           "REMOVE 4",
                           "Same balance"],
                          cols=4, title="Change vs Stay-the-Same",
                          box_label_font=20)
    if image_id == "M4_EXPRESSION_CARD":
        return _card_grid(["3 + 5", "8 - 2", "4 + 4", "10 - 4",
                           "5 + 3", "9 - 1", "2 + 6", "7 + 1"],
                          cols=4, title="Expression Cards",
                          box_label_font=22)
    if image_id == "M5_LABEL":
        return _balance_mat()
    if image_id == "M6_MYSTERY_CARD":
        return _card_grid(["? + 4 = 9", "? + 5 = 10",
                           "? + 6 = 12", "? + 7 = 14"],
                          cols=2, title="Mystery Cards",
                          box_label_font=24)
    if image_id == "M8_STORY_TEMPLATE":
        return _writing_workspace("Write your math story:",
                                  title="Story Template", box_h=480)
    if image_id == "M9_EQUAL_CHART":
        return _equation_table(rows=6,
                               headers=("Left", "=", "Right"))
    if image_id == "WS01_P1_TWELVE_CARDS":
        return _card_grid(
            ["3+4", "5+2", "6+1", "4+3",
             "2+5", "1+6", "7+0", "0+7",
             "8-1", "9-2", "10-3", "11-4"],
            cols=4, title="Twelve Cards", box_label_font=22)
    if image_id == "WS01_P2_TWO_COLUMNS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS01_P3_WHY_BOX":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P1_SIX_PAIRS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P2_FOUR_BALANCES":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P3_MY_OWN":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P1_EIGHT_ADDS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P2_SIX_SUBS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P3_THREE_BALANCES":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P1_EIGHT_SLOTS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_SIX_SLOTS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_MY_TARGET":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P1_STORY_BOX":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_BALANCE_BOX":
        return _balance_mat()
    if image_id == "WS05_P3_EQUATION":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P4_EQUIVALENT":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "FORM_Q1_PAIRS":
        return _writing_workspace("Match equal pairs.",
                                  title="Pairs Check", box_h=440)
    if image_id == "FORM_Q2_MISSING":
        return _writing_workspace("Find the missing number.",
                                  title="Missing Check", box_h=440)

    # ─────────── g1 loop_the_loop ───────────
    if image_id == "M3_SAMPLE_CARD":
        return _card_grid(["MOVE 3", "TURN", "REPEAT 2",
                           "STOP", "MOVE 5", "TURN LEFT"],
                          cols=3, title="Sample Cards",
                          box_label_font=22)
    if image_id == "M5_LOOP_CARD":
        return _card_grid(["REPEAT 3", "REPEAT 5",
                           "REPEAT 2", "REPEAT 4"],
                          cols=2, title="Loop Cards",
                          box_label_font=24)
    if image_id == "M6_TEMPLATE":
        return _writing_workspace("Code template — write your code:",
                                  title="Template", box_h=480)
    if image_id == "M7_PREDICT_CHART":
        return _equation_table(
            rows=6, headers=("Step", "Predict", "Actual"))
    if image_id == "M9_CAPSTONE_TEMPLATE":
        return _capstone_template([
            "1. The PROJECT:",
            "2. The CODE:",
            "3. The LOOP:",
            "4. The OUTCOME:",
        ])
    if image_id == "WS01_P1_FIVE_STEPS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS01_P2_FOUR_GRIDS":
        canvas, draw = _new("Four Grids")
        # 4 small grids
        for i in range(4):
            x = 60 + (i % 2) * 480
            y = 130 + (i // 2) * 280
            draw.rectangle((x, y, x + 440, y + 240),
                           outline=(20, 20, 20), width=3)
            for k in range(7):
                draw.line([(x + 60 * (k + 1), y), (x + 60 * (k + 1), y + 240)],
                          fill=(180, 180, 180), width=1)
            for k in range(4):
                draw.line([(x, y + 60 * (k + 1)), (x + 440, y + 60 * (k + 1))],
                          fill=(180, 180, 180), width=1)
        return canvas
    if image_id == "WS01_P3_TASK_BOX":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P1_FOUR_CONVERSIONS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P2_THREE_SHAPES":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS02_P3_MY_LOOP":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P1_SIX_GRIDS":
        return _grid_mat(cols=8, rows=6)
    if image_id == "WS03_P2_FOUR_SHAPES":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS03_P3_LOOP_PREDICT":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P1_SIX_ALTERS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P2_FOUR_STEPS":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS04_P3_INVARIANT":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P1_PROJECT_BOX":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P2_CODE_AREA":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P3_PREDICTION":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "WS05_P4_VERIFY":
        return None  # defer to smart_fallback WS hero composer
    if image_id == "FORM_Q1_LOOP":
        return _writing_workspace("Trace the loop.",
                                  title="Loop Check", box_h=440)
    if image_id == "FORM_Q2_PREDICT_GRID":
        return _grid_mat(cols=8, rows=6)

    return None
