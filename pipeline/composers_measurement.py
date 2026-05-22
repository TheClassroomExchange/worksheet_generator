"""Measurement composers (k/g1/g2/g3): length, mass, capacity, time, area."""
from __future__ import annotations

import math
from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    "M1_ATTRIBUTES", "M1_POLY", "M1_STRIPS", "M1_UNITS",
    "M2_BALANCE", "M2_CM_STRIPS", "M2_STRIPS", "M2_UNITS",
    "M3_METRE", "M3_OBJECTS", "M3_TILES",
    "M4_BAL", "M4_BALANCE", "M4_CUPS", "M4_RULERS",
    "M5_CLOCKS", "M5_CUBES", "M5_CUPS", "M5_TIME",
    "M6_CALENDAR", "M6_CARNIVAL",
    "M7_ANCHOR", "M7_BENCHMARK", "M7_CHART",
    "M8_CALENDAR_REF", "M8_CAPS", "M8_UNITS", "M8_ZERO",
    "M9_ANIMALS", "M9_CAPSTONE", "M9_EVENTS", "M9_GRID",
    "WS01_P1_MATCH", "WS01_P1_PAIRS", "WS01_P1_PERIM",
    "WS01_P2_LINES", "WS01_P2_STRIPS", "WS01_P2_TWO", "WS01_P2_UNITS",
    "WS01_P3_BOXES", "WS01_P3_BUILD", "WS01_P3_HOME", "WS01_P3_ROWS",
    "WS02_P1_EST", "WS02_P1_PAIRS", "WS02_P1_STRIPS",
    "WS02_P2_BALANCES", "WS02_P2_COMP", "WS02_P2_CONVERT",
    "WS02_P2_TILES",
    "WS02_P3_BOXES", "WS02_P3_ROWS", "WS02_P3_SAME",
    "WS03_P1_GRID", "WS03_P1_MASS", "WS03_P1_MEASURE", "WS03_P1_PAIRS",
    "WS03_P2_CUPS", "WS03_P2_DRAW", "WS03_P2_PICK",
    "WS03_P3_BOXES", "WS03_P3_CIRCLE", "WS03_P3_ERROR", "WS03_P3_ROWS",
    "WS04_P1_CALENDAR", "WS04_P1_CAP", "WS04_P1_CUBES", "WS04_P1_EVENTS",
    "WS04_P2_BAL", "WS04_P2_CONVERT", "WS04_P2_COUNT", "WS04_P2_MATCH",
    "WS04_P3_CONV", "WS04_P3_HOLIDAYS", "WS04_P3_HOME",
    "WS05_P1_OBJECTS", "WS05_P1_PA", "WS05_P1_STRIPS", "WS05_P1_UNITS",
    "WS05_P2_BALANCES", "WS05_P2_CM", "WS05_P2_ORDER", "WS05_P2_RULER",
    "WS05_P3_CALENDAR", "WS05_P3_CLOCKS", "WS05_P3_CUPS", "WS05_P3_TIME",
    "FORM_Q1_LENGTH", "FORM_Q1_LINE", "FORM_Q1_OBJECTS", "FORM_Q1_PERIM",
    "FORM_Q2_AREA", "FORM_Q2_CONVERT", "FORM_Q2_MASS", "FORM_Q2_STRIPS",
    "FORM_Q3_CAPACITY",
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _ruler(length_cm: int = 30) -> Image.Image:
    canvas, draw = _new(f"Ruler — {length_cm} cm")
    margin = 60
    y = 380
    span_w = 1024 - 2 * margin
    # body
    draw.rectangle((margin, y - 40, 1024 - margin, y + 40),
                   outline=(20, 20, 20), width=3)
    # tick marks every cm
    for i in range(length_cm + 1):
        x = margin + span_w * i // length_cm
        long_tick = (i % 5 == 0)
        h = 28 if long_tick else 14
        draw.line([(x, y - 40), (x, y - 40 + h)],
                  fill=(20, 20, 20), width=2 if long_tick else 1)
        if long_tick:
            TC._text_centered(draw, (x, y + 56), str(i),
                              TC._font(20, bold=True))
    return canvas


def _cm_strips() -> Image.Image:
    canvas, draw = _new("Centimetre Strips")
    # 5 strips of varying length
    margin = 80
    strip_h = 50
    for i, n_cm in enumerate((4, 7, 10, 6, 12)):
        y0 = 130 + i * 110
        # subdivisions
        cell_w = 30
        for k in range(n_cm):
            draw.rectangle((margin + k * cell_w, y0,
                            margin + (k + 1) * cell_w, y0 + strip_h),
                           outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (margin + n_cm * cell_w + 60,
                                  y0 + strip_h // 2),
                          f"{n_cm} cm", TC._font(24, bold=True))
    return canvas


def _balance_scale() -> Image.Image:
    canvas, draw = _new("Balance Scale")
    # base
    draw.line([(220, 600), (804, 600)], fill=(20, 20, 20), width=4)
    draw.line([(512, 250), (512, 600)], fill=(20, 20, 20), width=4)
    # cross beam
    draw.line([(240, 280), (784, 280)], fill=(20, 20, 20), width=5)
    # pans
    for cx in (300, 724):
        draw.line([(cx, 280), (cx - 60, 350)], fill=(20, 20, 20), width=2)
        draw.line([(cx, 280), (cx + 60, 350)], fill=(20, 20, 20), width=2)
        draw.arc((cx - 80, 330, cx + 80, 390),
                 start=0, end=180, fill=(20, 20, 20), width=3)
    # labels
    TC._text_centered(draw, (300, 660), "A", TC._font(32, bold=True))
    TC._text_centered(draw, (724, 660), "B", TC._font(32, bold=True))
    return canvas


def _cups_capacity() -> Image.Image:
    canvas, draw = _new("Cups & Capacity")
    # 4 cups of varying fill
    n = 4
    margin = 100
    spacing = (1024 - 2 * margin) // n
    levels = [0.25, 0.5, 0.75, 1.0]
    for i, fl in enumerate(levels):
        cx = margin + spacing // 2 + i * spacing
        cy = 400
        # cup outline
        draw.polygon([(cx - 80, cy - 120),
                      (cx + 80, cy - 120),
                      (cx + 60, cy + 120),
                      (cx - 60, cy + 120)],
                     outline=(20, 20, 20), width=4)
        # fill level (water)
        fill_top = cy + 120 - 240 * fl
        # interpolate cup width at fill_top
        ratio = (240 - 240 * fl) / 240
        wx = 80 - (80 - 60) * (1 - fl)
        draw.rectangle((cx - wx + 4, fill_top, cx + wx - 4, cy + 120 - 4),
                       fill=(140, 200, 240))
        # label
        TC._text_centered(draw, (cx, cy + 160),
                          f"{int(fl * 100)}%", TC._font(22, bold=True))
    return canvas


def _clock(hour: int = 3, minute: int = 0) -> Image.Image:
    canvas, draw = _new(f"Clock — {hour:02d}:{minute:02d}")
    cx, cy = 512, 400
    R = 220
    draw.ellipse((cx - R, cy - R, cx + R, cy + R),
                 outline=(20, 20, 20), width=5)
    # hour marks
    for h in range(12):
        ang = -math.pi / 2 + 2 * math.pi * h / 12
        x0 = cx + (R - 18) * math.cos(ang)
        y0 = cy + (R - 18) * math.sin(ang)
        x1 = cx + R * math.cos(ang)
        y1 = cy + R * math.sin(ang)
        draw.line([(x0, y0), (x1, y1)], fill=(20, 20, 20), width=4)
        # number
        nx = cx + (R - 50) * math.cos(ang)
        ny = cy + (R - 50) * math.sin(ang)
        label = str(h if h != 0 else 12)
        TC._text_centered(draw, (int(nx), int(ny)), label,
                          TC._font(28, bold=True))
    # hour hand
    h_ang = -math.pi / 2 + 2 * math.pi * (hour % 12 + minute / 60) / 12
    h_len = R * 0.55
    draw.line([(cx, cy),
               (cx + h_len * math.cos(h_ang),
                cy + h_len * math.sin(h_ang))],
              fill=(20, 20, 20), width=8)
    # minute hand
    m_ang = -math.pi / 2 + 2 * math.pi * minute / 60
    m_len = R * 0.85
    draw.line([(cx, cy),
               (cx + m_len * math.cos(m_ang),
                cy + m_len * math.sin(m_ang))],
              fill=(20, 20, 20), width=5)
    # center dot
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10),
                 fill=(20, 20, 20))
    return canvas


def _calendar(month: str = "April") -> Image.Image:
    canvas, draw = _new(f"Calendar — {month}")
    margin = 40
    top = 130
    cell_w = (1024 - 2 * margin) // 7
    cell_h = 80
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, d in enumerate(days):
        x0 = margin + i * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + 40),
                       outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cell_w // 2, top + 20),
                          d, TC._font(18, bold=True))
    # 5 weeks
    day_num = 1
    for w in range(5):
        for c in range(7):
            x0 = margin + c * cell_w
            y0 = top + 40 + w * cell_h
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
            if 1 <= day_num <= 30:
                draw.text((x0 + 8, y0 + 8), str(day_num),
                          font=TC._font(20, bold=True),
                          fill=(20, 20, 20))
            day_num += 1
    return canvas


def _area_grid(rows: int = 6, cols: int = 8) -> Image.Image:
    canvas, draw = _new(f"Area Grid — {cols} × {rows}")
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
    return canvas


def _polygon_cards() -> Image.Image:
    canvas, draw = _new("Polygon Cards")
    polys = [
        ("triangle",  3),
        ("square",    4),
        ("pentagon",  5),
        ("hexagon",   6),
        ("rectangle", 4),
        ("octagon",   8),
    ]
    cols = 3
    rows = 2
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, (name, sides) in enumerate(polys):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        cx, cy = x0 + cw // 2, y0 + ch // 2 - 14
        radius = min(cw, ch) // 3
        if name == "rectangle":
            draw.rectangle((cx - radius, cy - radius // 2,
                            cx + radius, cy + radius // 2),
                           outline=(20, 20, 20), width=3)
        else:
            pts = []
            for k in range(sides):
                ang = -math.pi / 2 + 2 * math.pi * k / sides
                pts.append((cx + radius * math.cos(ang),
                            cy + radius * math.sin(ang)))
            draw.polygon(pts, outline=(20, 20, 20))
            draw.line(pts + [pts[0]], fill=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch - 30),
                          name, TC._font(22, bold=True))
    return canvas


def _benchmark_chart() -> Image.Image:
    canvas, draw = _new("Benchmarks")
    items = [
        ("1 cm", "fingernail"),
        ("10 cm", "thumb to pinky"),
        ("1 m", "long step"),
        ("1 g", "paper clip"),
        ("100 g", "stick of butter"),
        ("1 kg", "1 L of water"),
        ("1 mL", "drop"),
        ("1 L", "milk carton"),
    ]
    cols = 2
    rows = math.ceil(len(items) / cols)
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, (m, ex) in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 4, y0 + ch // 2),
                          m, TC._font(28, bold=True))
        TC._text_centered(draw, (x0 + 3 * cw // 4, y0 + ch // 2),
                          ex, TC._font(20))
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


def compose_measurement_image(image_id: str, grade: str | None = None,
                              unit_id: str | None = None) -> Image.Image | None:
    # ── Manipulatives ──
    if image_id == "M1_POLY":
        if grade == "Kindergarten":
            return None  # K uses non-standard objects, not metric polygons
        return _polygon_cards()
    if image_id in ("M1_STRIPS", "M2_STRIPS", "M2_CM_STRIPS"):
        return _cm_strips()
    if image_id in ("M1_UNITS", "M2_UNITS", "M8_UNITS"):
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id == "M1_ATTRIBUTES":
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id in ("M2_BALANCE", "M4_BAL", "M4_BALANCE"):
        return _balance_scale()
    if image_id == "M3_METRE":
        return _ruler(length_cm=100)
    if image_id == "M3_OBJECTS":
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id in ("M3_TILES", "M9_GRID"):
        return _area_grid(rows=6, cols=8)
    if image_id == "M4_RULERS":
        return _ruler(length_cm=30)
    if image_id in ("M4_CUPS", "M5_CUPS", "M8_CAPS"):
        return _cups_capacity()
    if image_id == "M5_CLOCKS":
        return _clock(hour=3, minute=0)
    if image_id == "M5_CUBES":
        return _area_grid(rows=4, cols=4)
    if image_id == "M5_TIME":
        return _clock(hour=10, minute=15)
    if image_id in ("M6_CALENDAR", "M8_CALENDAR_REF"):
        return _calendar()
    if image_id == "M6_CARNIVAL":
        if grade == "Kindergarten":
            return None  # K uses non-standard objects, not metric polygons
        return _polygon_cards()
    if image_id in ("M7_ANCHOR", "M7_BENCHMARK", "M7_CHART"):
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id == "M8_ZERO":
        return _ruler(length_cm=20)
    if image_id == "M9_ANIMALS":
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id == "M9_CAPSTONE":
        return _workspace("Capstone canvas — measure 5 things.",
                          title="Capstone", box_h=500)
    if image_id == "M9_EVENTS":
        return _calendar(month="June")

    # ── Worksheets — most are workspaces ──
    measurement_workspaces = {
        "WS01_P1_MATCH":     ("Match attribute to unit.", "Match Attributes"),
        "WS01_P1_PAIRS":     ("Compare pairs by length.", "Pairs"),
        "WS01_P1_PERIM":     ("Find the perimeter.", "Perimeter"),
        "WS01_P2_LINES":     ("Measure each line.", "Lines"),
        "WS01_P2_TWO":       ("Compare two lengths.", "Two Lengths"),
        "WS01_P2_UNITS":     ("Pick the right unit.", "Pick Unit"),
        "WS01_P3_BOXES":     ("Estimate box sizes.", "Box Estimates"),
        "WS01_P3_BUILD":     ("Build something with cubes.", "Build"),
        "WS01_P3_HOME":      ("Measure 3 things at home.", "Home Measure"),
        "WS01_P3_ROWS":      ("Make rows of cubes.", "Cube Rows"),
        "WS02_P1_EST":       ("Estimate first, then measure.", "Estimate"),
        "WS02_P1_PAIRS":     ("Mass: pair compare.", "Mass Pairs"),
        "WS02_P2_BALANCES":  ("Balance these objects.", "Balance"),
        "WS02_P2_COMP":      ("Compare with the balance.", "Balance Compare"),
        "WS02_P2_CONVERT":   ("Convert between units.", "Convert"),
        "WS02_P2_TILES":     ("Cover with tiles.", "Tile Cover"),
        "WS02_P3_BOXES":     ("Box estimate vs actual.", "Box Compare"),
        "WS02_P3_ROWS":      ("Row math.", "Row Math"),
        "WS02_P3_SAME":      ("Find the SAME mass.", "Same Mass"),
        "WS03_P1_GRID":      ("Grid: count squares.", "Count Squares"),
        "WS03_P1_MASS":      ("Mass measurement.", "Mass"),
        "WS03_P1_MEASURE":   ("Measure 5 things.", "Measure 5"),
        "WS03_P1_PAIRS":     ("Capacity pairs.", "Capacity Pairs"),
        "WS03_P2_CUPS":      ("Pour and compare cups.", "Cups"),
        "WS03_P2_DRAW":      ("Draw a 3-cup container.", "Draw 3"),
        "WS03_P2_PICK":      ("Pick the right cup.", "Pick Cup"),
        "WS03_P3_BOXES":     ("Box capacity.", "Box Capacity"),
        "WS03_P3_CIRCLE":    ("Circle the unit.", "Circle Unit"),
        "WS03_P3_ERROR":     ("Find the measuring error.", "Find Error"),
        "WS03_P3_ROWS":      ("Row volume.", "Volume Rows"),
        "WS04_P1_CALENDAR":  ("Calendar math.", "Calendar"),
        "WS04_P1_CAP":       ("Capacity check.", "Capacity"),
        "WS04_P1_CUBES":     ("Volume with cubes.", "Cube Volume"),
        "WS04_P1_EVENTS":    ("Time events.", "Events"),
        "WS04_P2_BAL":       ("Balance practice.", "Balance Practice"),
        "WS04_P2_CONVERT":   ("Unit conversions.", "Convert Practice"),
        "WS04_P2_COUNT":     ("Count tiles.", "Tile Count"),
        "WS04_P2_MATCH":     ("Match unit to object.", "Match Units"),
        "WS04_P3_CONV":      ("Mixed conversions.", "Mixed Convert"),
        "WS04_P3_HOLIDAYS":  ("Holidays on calendar.", "Holidays"),
        "WS04_P3_HOME":      ("Home measurement.", "Home"),
        "WS05_P1_OBJECTS":   ("Capstone: pick 5 objects.", "Capstone Objects"),
        "WS05_P1_PA":        ("Perimeter and area.", "P&A"),
        "WS05_P1_STRIPS":    ("Strip measurements.", "Strips"),
        "WS05_P1_UNITS":     ("Capstone units.", "Capstone Units"),
        "WS05_P2_BALANCES":  ("Capstone balance.", "Capstone Balance"),
        "WS05_P2_CM":        ("Capstone cm.", "Capstone cm"),
        "WS05_P2_ORDER":     ("Order by length.", "Order"),
        "WS05_P2_RULER":     ("Capstone ruler.", "Capstone Ruler"),
        "WS05_P3_CALENDAR":  ("Capstone calendar.", "Capstone Calendar"),
        "WS05_P3_CLOCKS":    ("Capstone clocks.", "Capstone Clocks"),
        "WS05_P3_CUPS":      ("Capstone cups.", "Capstone Cups"),
        "WS05_P3_TIME":      ("Capstone time.", "Capstone Time"),
    }
    if image_id in measurement_workspaces:
        # Defer to smart_fallback's WS hero composer which reads
        # 2_worksheet_NN.json for real part labels (added 2026-05-10).
        return None

    if image_id == "WS01_P2_STRIPS":
        return _cm_strips()

    # ── Formative ──
    if image_id == "FORM_Q1_LENGTH":
        return _ruler(length_cm=20)
    if image_id == "FORM_Q1_LINE":
        return _workspace("Measure the line.", title="Length Check",
                          box_h=440)
    if image_id == "FORM_Q1_OBJECTS":
        if grade == "Kindergarten":
            return None  # K uses non-standard units (cubes/hands), not metric benchmarks
        return _benchmark_chart()
    if image_id == "FORM_Q1_PERIM":
        if grade == "Kindergarten":
            return None  # K uses non-standard objects, not metric polygons
        return _polygon_cards()
    if image_id == "FORM_Q2_AREA":
        return _area_grid(rows=4, cols=4)
    if image_id == "FORM_Q2_CONVERT":
        return _workspace("Convert.", title="Convert Check", box_h=440)
    if image_id == "FORM_Q2_MASS":
        return _balance_scale()
    if image_id == "FORM_Q2_STRIPS":
        return _cm_strips()
    if image_id == "FORM_Q3_CAPACITY":
        return _cups_capacity()

    return None
