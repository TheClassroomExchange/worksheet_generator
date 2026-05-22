"""Bespoke composers for the three Real-Life Modelling units (g1/g2/g3).

Theme: real-world data modelling (sort, tally, predict, refine, reflect).
Per-grade theming:
  g1 — Sugar Bush (Maple, taps, syrup buckets, daily count)
  g2 — Town (Coach Cara/Sport Sam, town map, bus routes)
  g3 — Community (Coach Cara/Sport Sam, rink, community events)

Shared workflow IDs use a single composer; theme-specific IDs branch by
grade.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    # g1 sugar bush
    "M1_TREE_TOKEN", "M2_BUCKET_TOKEN", "M9_SYRUP_JAR", "M10_BUSH_POSTER",
    "WS01_P1_BUSH_BOX", "WS01_P2_QUESTIONS", "WS01_P3_MY_DAY",
    "WS02_P1_BUSH_COUNT", "WS02_P2_DATA_QUESTIONS", "WS02_P3_MY_COUNT",
    "WS03_P1_RULE1", "WS03_P2_RULE2", "WS03_P3_MY_RULE",
    "WS04_P3_MY_REFINE", "FORM_Q1_PICTURE",
    # g2 town
    "M1_TOWN_MAP", "M9_MAYOR_CHART", "M10_TOWN_POSTER",
    "WS03_P1_BUS", "WS03_P2_TOWN", "FORM_Q1_TOWN",
    # g3 community
    "M1_COMM_MAP", "M9_COACH_CHART", "M10_COMM_POSTER",
    "WS03_P1_RINK", "WS03_P2_COM", "FORM_Q1_COMM",
    # Shared (g2 + g3 use these, sometimes g1 too)
    "M3_CYCLE_CHART", "M4_DATA_TABLE", "M4_SITUATION_CARD",
    "M5_PREDICT_CHART", "M7_COUNTER_SHEET", "M7_SITUATION_CARD",
    "M8_COUNTER_SHEET", "M8_NUMBER_LINE", "M2_DATA_CHART",
    "WS01_P1_DESC", "WS01_P2_Q", "WS01_P3_SORT",
    "WS02_P1_TALLY", "WS02_P2_USE", "WS02_P3_REAL",
    "WS04_P1_COMPARE", "WS04_P2_REFINE", "WS04_P3_MY",
    "WS05_P1_TOPIC", "WS05_P2_Q", "WS05_P2_QUESTION",
    "WS05_P3_DATA", "WS05_P4_PREDICTION", "WS05_P5_REFLECT",
    "FORM_Q2_DATA", "FORM_Q3_PREDICT",
}


def _new_canvas(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _icon_tree(d: ImageDraw.ImageDraw, cx: int, cy: int, sz: int) -> None:
    h = sz // 2
    # crown
    d.ellipse((cx - h, cy - h, cx + h, cy + h * 0.5),
              outline=(20, 20, 20), width=3)
    # trunk
    d.rectangle((cx - h * 0.2, cy + h * 0.5, cx + h * 0.2, cy + h),
                outline=(20, 20, 20), width=3)


def _icon_bucket(d: ImageDraw.ImageDraw, cx: int, cy: int, sz: int,
                 label: str = "") -> None:
    h = sz // 2
    # trapezoid bucket
    pts = [(cx - h * 0.7, cy - h * 0.6),
           (cx + h * 0.7, cy - h * 0.6),
           (cx + h * 0.55, cy + h * 0.6),
           (cx - h * 0.55, cy + h * 0.6)]
    d.polygon(pts, outline=(20, 20, 20))
    for i in range(len(pts)):
        d.line([pts[i], pts[(i + 1) % len(pts)]], fill=(20, 20, 20), width=3)
    # handle
    d.arc((cx - h * 0.7, cy - h * 0.95, cx + h * 0.7, cy - h * 0.4),
          start=180, end=360, fill=(20, 20, 20), width=2)
    if label:
        TC._text_centered(d, (cx, cy + h * 0.05), label, TC._font(20, bold=True))


def _icon_jar(d: ImageDraw.ImageDraw, cx: int, cy: int, sz: int,
              fill_pct: float = 0.6, label: str = "") -> None:
    h = sz // 2
    # jar body (rectangle with rounded top)
    body_l, body_r = cx - h * 0.55, cx + h * 0.55
    body_t, body_b = cy - h * 0.5, cy + h * 0.95
    d.rectangle((body_l, body_t, body_r, body_b),
                outline=(20, 20, 20), width=3)
    # neck
    d.rectangle((body_l + 12, cy - h * 0.85, body_r - 12, body_t),
                outline=(20, 20, 20), width=3)
    # lid
    d.rectangle((body_l + 6, cy - h * 1.0, body_r - 6, cy - h * 0.85),
                fill=(60, 60, 60), outline=(20, 20, 20), width=2)
    # syrup fill
    fill_top = body_b - (body_b - body_t) * max(0, min(1, fill_pct))
    d.rectangle((body_l + 4, fill_top, body_r - 4, body_b - 4),
                fill=(140, 90, 40), outline=None)
    if label:
        TC._text_centered(d, (cx, body_b + 28), label,
                          TC._font(22, bold=True))


def _draw_token_grid(d: ImageDraw.ImageDraw, canvas: Image.Image,
                     icon_drawer, label_template: str = "{i}",
                     count: int = 12, cols: int = 4) -> None:
    """Generic helper to render a grid of cuttable token cards."""
    import math
    rows = math.ceil(count / cols)
    margin = 60
    cell_w = (1024 - 2 * margin) // cols
    cell_h = (768 - 2 * margin) // rows
    for i in range(count):
        r, c = divmod(i, cols)
        x0 = margin + c * cell_w
        y0 = margin + r * cell_h
        d.rectangle((x0 + 6, y0 + 6, x0 + cell_w - 6, y0 + cell_h - 6),
                    outline=(180, 180, 180), width=1)
        cx, cy = x0 + cell_w // 2, y0 + cell_h // 2 - 8
        sz = min(cell_w, cell_h) - 60
        icon_drawer(d, cx, cy, sz, label_template.format(i=i + 1))


def _compose_tree_tokens() -> Image.Image:
    canvas, draw = _new_canvas("Maple Tree Tokens")
    _draw_token_grid(draw, canvas,
                     lambda d, cx, cy, sz, lbl: (_icon_tree(d, cx, cy, sz),
                                                 TC._text_centered(d, (cx, cy + sz // 2 + 18),
                                                                   lbl, TC._font(18, bold=True))),
                     label_template="Tree {i}", count=12, cols=4)
    return canvas


def _compose_bucket_tokens() -> Image.Image:
    canvas, draw = _new_canvas("Syrup Bucket Tokens")
    _draw_token_grid(draw, canvas,
                     lambda d, cx, cy, sz, lbl: _icon_bucket(d, cx, cy, sz, lbl),
                     label_template="{i} L", count=12, cols=4)
    return canvas


def _compose_syrup_jar() -> Image.Image:
    canvas, draw = _new_canvas("Syrup Jar — Daily Count")
    # 3 jars at increasing fill levels
    levels = [0.25, 0.5, 0.85]
    for i, fl in enumerate(levels):
        cx = 256 + i * 256
        _icon_jar(draw, cx, 380, sz=280, fill_pct=fl,
                  label=f"Day {i + 1}: {int(fl * 100)} L")
    return canvas


def _compose_data_chart(rows: int = 5, cols: tuple = ("Day", "Taps", "Buckets")) -> Image.Image:
    canvas, draw = _new_canvas("Data Chart")
    n_cols = len(cols)
    cell_w = (1024 - 80) // n_cols
    top = 130
    cell_h = 80
    # header
    for j, ch in enumerate(cols):
        x0 = 40 + j * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          ch, TC._font(24, bold=True))
    # rows
    for r in range(rows):
        y0 = top + cell_h * (r + 1)
        for j in range(n_cols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    return canvas


def _compose_cycle_chart(steps: list[str], title: str = "Cycle") -> Image.Image:
    canvas, draw = _new_canvas(title)
    # 4 boxes in a rectangular cycle with arrows
    n = len(steps)
    if n != 4:
        steps = (steps + ["?"] * 4)[:4]
    positions = [(280, 200), (744, 200), (744, 540), (280, 540)]
    for (x, y), step in zip(positions, steps):
        draw.rectangle((x - 130, y - 60, x + 130, y + 60),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x, y), step, TC._font(22, bold=True))
    # arrows top, right, bottom, left
    arrow_specs = [
        ((410, 200), (614, 200)),
        ((744, 260), (744, 480)),
        ((614, 540), (410, 540)),
        ((280, 480), (280, 260)),
    ]
    for (x0, y0), (x1, y1) in arrow_specs:
        draw.line([(x0, y0), (x1, y1)], fill=(20, 20, 20), width=4)
        # arrowhead
        if x0 == x1:  # vertical
            ay = y1
            sign = 1 if y1 > y0 else -1
            draw.polygon([(x1 - 8, ay - 12 * sign),
                          (x1 + 8, ay - 12 * sign),
                          (x1, ay)], fill=(20, 20, 20))
        else:
            ax = x1
            sign = 1 if x1 > x0 else -1
            draw.polygon([(ax - 12 * sign, y1 - 8),
                          (ax - 12 * sign, y1 + 8),
                          (ax, y1)], fill=(20, 20, 20))
    return canvas


def _compose_predict_chart() -> Image.Image:
    canvas, draw = _new_canvas("Predict vs. Actual")
    headers = ["Day", "Predicted", "Actual", "Difference"]
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
    for r in range(6):
        y0 = top + cell_h * (r + 1)
        for j in range(n_cols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    return canvas


def _compose_situation_card(prompts: list[str] | None = None) -> Image.Image:
    canvas, draw = _new_canvas("Situation Cards")
    prompts = prompts or [
        "Counted 12 trees on Day 1.",
        "Tapped 8 trees on Day 2.",
        "Filled 5 buckets on Day 3.",
        "Took 3 days to fill the jar.",
        "Friend says the syrup tastes sweetest at the end.",
        "Predict: how many buckets next week?",
    ]
    cols = 2
    rows = (len(prompts) + 1) // cols
    margin = 40
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, p in enumerate(prompts):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        # wrap text
        words = p.split()
        font = TC._font(20)
        line, ly = "", y0 + 30
        for w in words:
            test = (line + " " + w).strip()
            tb = draw.textbbox((0, 0), test, font=font)
            if tb[2] - tb[0] > cw - 40:
                draw.text((x0 + 24, ly), line, font=font, fill=(20, 20, 20))
                ly += 26
                line = w
            else:
                line = test
        if line:
            draw.text((x0 + 24, ly), line, font=font, fill=(20, 20, 20))
    return canvas


def _compose_counter_sheet() -> Image.Image:
    canvas, draw = _new_canvas("Counter Sheet")
    # 5x4 number grid for tracking
    margin = 60
    cell_w = (1024 - 2 * margin) // 5
    cell_h = (768 - 130 - margin) // 4
    for r in range(4):
        for c in range(5):
            x0 = margin + c * cell_w
            y0 = 130 + r * cell_h
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
            n = r * 5 + c + 1
            TC._text_centered(draw, (x0 + cell_w // 2, y0 + cell_h // 2),
                              str(n), TC._font(40, bold=True))
    return canvas


def _compose_number_line(start: int = 0, end: int = 30,
                         step: int = 5) -> Image.Image:
    canvas, draw = _new_canvas("Number Line")
    margin = 80
    y = 384
    draw.line([(margin, y), (1024 - margin, y)], fill=(20, 20, 20), width=4)
    n_ticks = (end - start) // step + 1
    span = 1024 - 2 * margin
    for i in range(n_ticks):
        x = margin + (span * i // (n_ticks - 1))
        draw.line([(x, y - 14), (x, y + 14)], fill=(20, 20, 20), width=3)
        v = start + i * step
        TC._text_centered(draw, (x, y + 40),
                          str(v), TC._font(24, bold=True))
    # arrow caps
    draw.polygon([(margin - 16, y - 10), (margin - 16, y + 10),
                  (margin - 32, y)], fill=(20, 20, 20))
    draw.polygon([(1024 - margin + 16, y - 10), (1024 - margin + 16, y + 10),
                  (1024 - margin + 32, y)], fill=(20, 20, 20))
    return canvas


def _compose_map(title: str, places: list[tuple[str, tuple[int, int]]]) -> Image.Image:
    canvas, draw = _new_canvas(title)
    # frame
    draw.rectangle((60, 110, 964, 720), outline=(20, 20, 20), width=4)
    # paths between places
    if len(places) > 1:
        for i in range(len(places) - 1):
            (_, p0), (_, p1) = places[i], places[i + 1]
            draw.line([p0, p1], fill=(120, 120, 120), width=3)
    # places
    for name, (x, y) in places:
        draw.ellipse((x - 12, y - 12, x + 12, y + 12),
                     fill=(20, 20, 20))
        draw.text((x + 18, y - 14), name,
                  font=TC._font(20, bold=True), fill=(20, 20, 20))
    return canvas


def _compose_workspace(prompt: str, title: str | None = None,
                       box_h: int = 380) -> Image.Image:
    canvas, draw = _new_canvas(title)
    if prompt:
        TC._text_centered(draw, (512, 130), prompt, TC._font(26))
    box_y0 = 180
    draw.rectangle((80, box_y0, 944, box_y0 + box_h),
                   outline=(20, 20, 20), width=4)
    for gy in range(box_y0 + 50, box_y0 + box_h, 50):
        draw.line([(100, gy), (924, gy)],
                  fill=(220, 220, 220), width=1)
    return canvas


def _compose_compare_two() -> Image.Image:
    canvas, draw = _new_canvas("Compare Two Days")
    for i, day in enumerate(("Day A", "Day B")):
        x0 = 40 + i * 500
        x1 = x0 + 460
        draw.rectangle((x0, 130, x1, 700),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, ((x0 + x1) // 2, 165),
                          day, TC._font(28, bold=True))
        # mini number line
        ly = 280
        draw.line([(x0 + 40, ly), (x1 - 40, ly)],
                  fill=(20, 20, 20), width=3)
        for k in range(6):
            tx = x0 + 40 + (x1 - x0 - 80) * k // 5
            draw.line([(tx, ly - 10), (tx, ly + 10)],
                      fill=(20, 20, 20), width=2)
            TC._text_centered(draw, (tx, ly + 28), str(k * 5),
                              TC._font(18))
        # workspace
        draw.rectangle((x0 + 30, 380, x1 - 30, 660),
                       outline=(20, 20, 20), width=2)
    return canvas


def _compose_predict_refine() -> Image.Image:
    canvas, draw = _new_canvas("Refine Your Prediction")
    rows = ["Original prediction:", "What I noticed:", "New prediction:"]
    y = 140
    for r in rows:
        draw.text((80, y), r, font=TC._font(24, bold=True), fill=(20, 20, 20))
        draw.rectangle((80, y + 36, 944, y + 156),
                       outline=(20, 20, 20), width=2)
        y += 180
    return canvas


def _compose_anchor_poster(title: str, headline: str,
                           rows: list[str]) -> Image.Image:
    canvas, draw = _new_canvas()
    draw.rectangle((40, 40, 984, 140), outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 90), headline, TC._font(46, bold=True))
    draw.rectangle((40, 160, 984, 720), outline=(20, 20, 20), width=3)
    n = len(rows)
    spacing = (720 - 180) // n
    for i, r in enumerate(rows):
        y = 180 + i * spacing
        draw.text((80, y), f"• {r}", font=TC._font(28),
                  fill=(20, 20, 20))
    return canvas


# ── Per-image-id dispatcher ───────────────────────────────────────────────

def compose_real_life_image(image_id: str, grade: str | None = None,
                            unit_id: str | None = None) -> Image.Image | None:
    is_g1 = (grade == "Grade 1")
    is_g2 = (grade == "Grade 2")
    is_g3 = (grade == "Grade 3")

    # ─── g1 sugar bush ───
    if image_id == "M1_TREE_TOKEN":
        return _compose_tree_tokens()
    if image_id == "M2_BUCKET_TOKEN":
        return _compose_bucket_tokens()
    if image_id == "M9_SYRUP_JAR":
        return _compose_syrup_jar()
    if image_id == "M10_BUSH_POSTER":
        return _compose_anchor_poster(
            "Sugar Bush", "Maple Sugar Bush",
            ["1. ASK a question.",
             "2. COUNT taps and trees.",
             "3. TALLY each day.",
             "4. PREDICT the next day.",
             "5. REFINE your guess."])
    if image_id == "WS01_P1_BUSH_BOX":
        return _compose_workspace(
            "Draw what you see in the sugar bush:",
            title="The Bush", box_h=440)
    if image_id == "WS01_P2_QUESTIONS":
        return _compose_workspace("List 3 questions about the sugar bush:",
                                  title="My Questions", box_h=400)
    if image_id == "WS01_P3_MY_DAY":
        return _compose_workspace("Tell about a day in the sugar bush:",
                                  title="My Day", box_h=440)
    if image_id == "WS02_P1_BUSH_COUNT":
        return _compose_data_chart(rows=5, cols=("Day", "Trees Tapped", "Buckets"))
    if image_id == "WS02_P2_DATA_QUESTIONS":
        return _compose_workspace("Use the chart to answer 3 questions:",
                                  title="Ask the Data", box_h=440)
    if image_id == "WS02_P3_MY_COUNT":
        return _compose_data_chart(rows=5, cols=("Day", "My Count", "Note"))
    if image_id == "WS03_P1_RULE1":
        return _compose_workspace("Make a rule from the data:",
                                  title="Rule 1", box_h=440)
    if image_id == "WS03_P2_RULE2":
        return _compose_workspace("Make a second rule:",
                                  title="Rule 2", box_h=440)
    if image_id == "WS03_P3_MY_RULE":
        return _compose_workspace("Write your own rule and explain:",
                                  title="My Rule", box_h=440)
    if image_id == "WS04_P3_MY_REFINE":
        return _compose_workspace("Refine your prediction:",
                                  title="My Refined Prediction", box_h=440)
    if image_id == "FORM_Q1_PICTURE":
        return _compose_workspace(
            "Draw what you see and label one thing.",
            title="Picture Prompt", box_h=440)

    # ─── g2 town ───
    if image_id == "M1_TOWN_MAP":
        return _compose_map("Town Map", [
            ("Library", (220, 250)),
            ("School",  (520, 200)),
            ("Park",    (820, 300)),
            ("Rink",    (240, 540)),
            ("Store",   (560, 600)),
            ("Bus Stop", (820, 580)),
        ])
    if image_id == "M9_MAYOR_CHART":
        return _compose_anchor_poster(
            "Town Mayor", "Mayor's Question Chart",
            ["What does the town need?",
             "How many people use this?",
             "When is it busiest?",
             "Who would benefit?"])
    if image_id == "M10_TOWN_POSTER":
        return _compose_anchor_poster(
            "Town", "Math in My Town",
            ["Buses, stores, parks count!",
             "Sort by category.",
             "Tally + total.",
             "Show on a graph.",
             "Tell the town story."])
    if image_id == "WS03_P1_BUS":
        return _compose_data_chart(rows=5, cols=("Bus #", "Riders", "Time"))
    if image_id == "WS03_P2_TOWN":
        return _compose_data_chart(rows=5, cols=("Place", "Visits", "Day"))
    if image_id == "FORM_Q1_TOWN":
        return _compose_workspace(
            "Draw one place in the town and label it.",
            title="Town Prompt", box_h=440)

    # ─── g3 community ───
    if image_id == "M1_COMM_MAP":
        return _compose_map("Community Map", [
            ("Rink",     (220, 250)),
            ("Field",    (520, 200)),
            ("Pool",     (820, 300)),
            ("Court",    (240, 540)),
            ("Gym",      (560, 600)),
            ("Track",    (820, 580)),
        ])
    if image_id == "M9_COACH_CHART":
        return _compose_anchor_poster(
            "Coach", "Coach Cara's Stat Chart",
            ["Goals scored",
             "Saves made",
             "Team practice days",
             "Equipment shared"])
    if image_id == "M10_COMM_POSTER":
        return _compose_anchor_poster(
            "Community", "Math in My Community",
            ["Track stats. Plan events.",
             "Sort by category.",
             "Tally + total.",
             "Show on a graph.",
             "Improve your community."])
    if image_id == "WS03_P1_RINK":
        return _compose_data_chart(rows=5, cols=("Game", "Goals", "Saves"))
    if image_id == "WS03_P2_COM":
        return _compose_data_chart(rows=5, cols=("Event", "People", "Notes"))
    if image_id == "FORM_Q1_COMM":
        return _compose_workspace(
            "Draw a community event and label it.",
            title="Community Prompt", box_h=440)

    # ─── shared (all three real_life units) ───
    if image_id == "M3_CYCLE_CHART":
        return _compose_cycle_chart(["ASK", "COLLECT", "SHOW", "REFLECT"],
                                    title="Modelling Cycle")
    if image_id == "M4_DATA_TABLE":
        return _compose_data_chart(rows=6, cols=("Item", "Count", "Total"))
    if image_id == "M2_DATA_CHART":
        return _compose_data_chart(rows=6, cols=("Day", "Count", "Notes"))
    if image_id in ("M4_SITUATION_CARD", "M7_SITUATION_CARD"):
        return _compose_situation_card()
    if image_id == "M5_PREDICT_CHART":
        return _compose_predict_chart()
    if image_id in ("M7_COUNTER_SHEET", "M8_COUNTER_SHEET"):
        return _compose_counter_sheet()
    if image_id == "M8_NUMBER_LINE":
        return _compose_number_line(start=0, end=30, step=5)

    if image_id == "WS01_P1_DESC":
        return _compose_workspace("Describe what you see:",
                                  title="Describe", box_h=440)
    if image_id == "WS01_P2_Q":
        return _compose_workspace("List 3 questions to investigate:",
                                  title="My Questions", box_h=440)
    if image_id == "WS01_P3_SORT":
        return _compose_data_chart(rows=5, cols=("Category", "Tally", "Total"))
    if image_id == "WS02_P1_TALLY":
        return _compose_data_chart(rows=5, cols=("Item", "Tally", "Total"))
    if image_id == "WS02_P2_USE":
        return _compose_workspace("Use the data to answer 3 questions:",
                                  title="Use the Data", box_h=440)
    if image_id == "WS02_P3_REAL":
        return _compose_data_chart(rows=5, cols=("Day", "Data", "Notes"))
    if image_id == "WS04_P1_COMPARE":
        return _compose_compare_two()
    if image_id == "WS04_P2_REFINE":
        return _compose_predict_refine()
    if image_id == "WS04_P3_MY":
        return _compose_workspace("Refine and explain your model:",
                                  title="My Refined Model", box_h=440)

    # WS05 capstone (shared)
    if image_id == "WS05_P1_TOPIC":
        return _compose_workspace("Pick a real-life topic:",
                                  title="My Topic", box_h=200)
    if image_id in ("WS05_P2_Q", "WS05_P2_QUESTION"):
        return _compose_workspace("Write your investigation question:",
                                  title="My Question", box_h=200)
    if image_id == "WS05_P3_DATA":
        return _compose_data_chart(rows=6, cols=("Item", "Count", "Total"))
    if image_id == "WS05_P4_PREDICTION":
        return _compose_predict_refine()
    if image_id == "WS05_P5_REFLECT":
        return _compose_workspace("Reflect on what you learned:",
                                  title="My Reflection", box_h=440)

    if image_id == "FORM_Q2_DATA":
        return _compose_data_chart(rows=4, cols=("Item", "Count"))
    if image_id == "FORM_Q3_PREDICT":
        return _compose_workspace("Make a prediction. Show your reasoning.",
                                  title="Predict", box_h=400)

    return None
