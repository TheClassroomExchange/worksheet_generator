"""Probability/likelihood composers for the 3 probability units.

  g1_data_likelihood          — Lucky + Maybe Mae
  g2_data_what_could_happen   — Lucky + Maybe Mae (G2)
  g3_data_likely_unlikely     — Lucky + Maybe Mae (G3)
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    # M_
    "M1_EVENTS", "M1_LIKELIHOOD", "M1_SCALE",
    "M2_COMPLEMENTS", "M2_EVENTS", "M2_MAT",
    "M3_COINDICE", "M3_COINS", "M3_SPINNERS",
    "M4_DICE", "M4_POPCHART",
    "M5_MEANMODE", "M5_PRED_MAT",
    "M7_EVENT_CARDS", "M7_LIKELIHOOD",
    "M8_COMPLEMENTS", "M8_CYCLE", "M8_PRED",
    "M9_OUTCOMES",
    # WS_
    "WS01_P1_EVENTS", "WS01_P1_MATCH",
    "WS01_P2_BOX", "WS01_P2_SCALE", "WS01_P2_TABLE",
    "WS01_P3_LINES", "WS01_P3_WHY",
    "WS02_P1_COINDICE", "WS02_P1_EVENTS", "WS02_P1_MATCH",
    "WS02_P2_DECIDE", "WS02_P2_SORT", "WS02_P2_TABLE",
    "WS02_P3_LINES", "WS02_P3_REVISE", "WS02_P3_TRICKY",
    "WS03_P1_COINS", "WS03_P1_PREDICT", "WS03_P1_SPINNERS",
    "WS03_P2_BAG", "WS03_P2_DATA",
    "WS03_P3_CHECK", "WS03_P3_LINES",
    "WS04_P1_CLASSES", "WS04_P1_PREDICT", "WS04_P1_TALLY",
    "WS04_P2_CALC", "WS04_P3_BOX", "WS04_P3_PREDICT",
    "WS04_P3_RESULT",
    "WS05_P1_COIN", "WS05_P1_LIKELIHOOD", "WS05_P1_PREDICT",
    "WS05_P2_DATA", "WS05_P2_LAB", "WS05_P2_MARBLES",
    "WS05_P3_CONCLUDE", "WS05_P3_SORT_SUMMARY", "WS05_P3_SURVEY",
    # FORM_
    "FORM_Q1_EVENTS", "FORM_Q1_SPINNER", "FORM_Q1_WORD",
    "FORM_Q2_COINS", "FORM_Q2_COMPARE", "FORM_Q2_COMPLEMENT",
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _likelihood_scale() -> Image.Image:
    canvas, draw = _new("Likelihood Scale")
    # horizontal scale with 5 stops. Margin set to 130 so the leftmost label
    # "IMPOSSIBLE" (≈12 chars × ~20px = 240px wide at the chosen font) fits
    # entirely inside the canvas — pre-fix margin=60 clipped the leading "I"
    # so the label rendered as "MPOSSIBLE" at 1024-px slide width.
    labels = ["IMPOSSIBLE", "UNLIKELY", "EQUAL CHANCE", "LIKELY", "CERTAIN"]
    margin = 130
    y = 320
    n = len(labels)
    width = 1024 - 2 * margin
    draw.line([(margin, y), (1024 - margin, y)], fill=(20, 20, 20), width=4)
    for i, label in enumerate(labels):
        x = margin + width * i // (n - 1)
        # tick
        draw.line([(x, y - 20), (x, y + 20)], fill=(20, 20, 20), width=3)
        # label below — use slightly smaller font for the long "EQUAL CHANCE"
        # mid-label so it doesn't crash into its neighbours
        font_size = 16 if label == "EQUAL CHANCE" else 18
        TC._text_centered(draw, (x, y + 60), label, TC._font(font_size, bold=True))
        # numeric below
        frac_label = ["0", "1/4", "1/2", "3/4", "1"][i] if i < 5 else ""
        TC._text_centered(draw, (x, y + 100), frac_label,
                          TC._font(22, bold=True))
    # arrowheads
    draw.polygon([(margin - 24, y - 12), (margin - 24, y + 12),
                  (margin - 40, y)], fill=(20, 20, 20))
    draw.polygon([(1024 - margin + 24, y - 12), (1024 - margin + 24, y + 12),
                  (1024 - margin + 40, y)], fill=(20, 20, 20))
    return canvas


def _probability_line() -> Image.Image:
    canvas, draw = _new("Probability Line")
    margin = 80
    y = 384
    draw.line([(margin, y), (1024 - margin, y)], fill=(20, 20, 20), width=4)
    # ticks at 0, 1/4, 1/2, 3/4, 1
    for i in range(5):
        x = margin + (1024 - 2 * margin) * i // 4
        draw.line([(x, y - 16), (x, y + 16)], fill=(20, 20, 20), width=3)
        label = ["0", "1/4", "1/2", "3/4", "1"][i]
        TC._text_centered(draw, (x, y + 40), label, TC._font(24, bold=True))
    # 3 placeholders for student to write
    for i in range(3):
        bx = margin + (1024 - 2 * margin) * (i + 1) // 4
        draw.line([(bx, y - 60), (bx, y - 30)],
                  fill=(20, 20, 20), width=2)
        draw.text((bx - 50, y - 90), f"event {i+1}",
                  font=TC._font(18), fill=(120, 120, 120))
    return canvas


def _spinner(sectors: int = 4, labels: list[str] | None = None) -> Image.Image:
    canvas, draw = _new("Spinner")
    cx, cy = 512, 400
    r = 200
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 outline=(20, 20, 20), width=4)
    for i in range(sectors):
        ang = -math.pi / 2 + 2 * math.pi * i / sectors
        x2 = cx + r * math.cos(ang)
        y2 = cy + r * math.sin(ang)
        draw.line([(cx, cy), (x2, y2)], fill=(20, 20, 20), width=3)
        # label in middle of sector
        mid_ang = ang + math.pi / sectors
        lx = cx + (r * 0.65) * math.cos(mid_ang)
        ly = cy + (r * 0.65) * math.sin(mid_ang)
        lab = (labels[i] if labels and i < len(labels) else str(i + 1))
        TC._text_centered(draw, (int(lx), int(ly)),
                          lab, TC._font(28, bold=True))
    # pointer
    draw.polygon([(cx - 16, cy - r - 10), (cx + 16, cy - r - 10),
                  (cx, cy - r + 10)], fill=(20, 20, 20))
    return canvas


def _coins(n: int = 2) -> Image.Image:
    canvas, draw = _new(f"{n} Coin{'s' if n > 1 else ''}")
    r = 90
    spacing = 220
    total_w = spacing * (n - 1)
    start_x = (1024 - total_w) // 2
    for i in range(n):
        cx = start_x + i * spacing
        cy = 400
        draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                     outline=(20, 20, 20), width=4)
        draw.ellipse((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14),
                     outline=(20, 20, 20), width=2)
        # H or T alternating
        face = "H" if i % 2 == 0 else "T"
        TC._text_centered(draw, (cx, cy),
                          face, TC._font(72, bold=True))
    # H/T legend
    TC._text_centered(draw, (512, 600), "H = Heads   T = Tails",
                      TC._font(26))
    return canvas


def _dice(faces: list[int] | None = None) -> Image.Image:
    canvas, draw = _new("Dice")
    faces = faces or [3, 5]
    spacing = 280
    total_w = spacing * (len(faces) - 1)
    start_x = (1024 - total_w) // 2
    for i, face in enumerate(faces):
        cx = start_x + i * spacing
        cy = 400
        # Cube
        size = 180
        draw.rectangle((cx - size // 2, cy - size // 2,
                        cx + size // 2, cy + size // 2),
                       outline=(20, 20, 20), width=4)
        # dots based on face
        offsets = {
            1: [(0, 0)],
            2: [(-0.5, -0.5), (0.5, 0.5)],
            3: [(-0.5, -0.5), (0, 0), (0.5, 0.5)],
            4: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
            5: [(-0.5, -0.5), (0.5, -0.5), (0, 0),
                (-0.5, 0.5), (0.5, 0.5)],
            6: [(-0.5, -0.5), (0.5, -0.5),
                (-0.5, 0), (0.5, 0),
                (-0.5, 0.5), (0.5, 0.5)],
        }
        for ox, oy in offsets.get(face, []):
            dx = cx + int(ox * size * 0.6)
            dy = cy + int(oy * size * 0.6)
            draw.ellipse((dx - 14, dy - 14, dx + 14, dy + 14),
                         fill=(20, 20, 20))
    return canvas


def _marble_bag(red: int = 3, blue: int = 2) -> Image.Image:
    canvas, draw = _new(f"Marble Bag ({red} solid, {blue} hollow)")
    # bag shape
    draw.polygon([(380, 220), (644, 220), (700, 280), (700, 580),
                  (640, 640), (384, 640), (324, 580), (324, 280)],
                 outline=(20, 20, 20), width=4)
    # tie at top
    draw.line([(380, 220), (350, 180)], fill=(20, 20, 20), width=3)
    draw.line([(644, 220), (674, 180)], fill=(20, 20, 20), width=3)
    # marbles
    import random
    rng = random.Random(red * 31 + blue)
    n_total = red + blue
    spots = []
    for _ in range(n_total):
        for _ in range(40):
            x = 380 + rng.randint(0, 244)
            y = 320 + rng.randint(0, 280)
            ok = all((x - sx) ** 2 + (y - sy) ** 2 > 70 ** 2
                     for sx, sy in spots)
            if ok:
                spots.append((x, y))
                break
    for i, (x, y) in enumerate(spots):
        if i < red:
            draw.ellipse((x - 28, y - 28, x + 28, y + 28),
                         fill=(40, 40, 40), outline=(20, 20, 20), width=2)
        else:
            draw.ellipse((x - 28, y - 28, x + 28, y + 28),
                         outline=(20, 20, 20), width=3)
    return canvas


def _outcome_table(rows: int = 5) -> Image.Image:
    canvas, draw = _new("Outcome Table")
    headers = ["Trial", "Outcome", "Tally", "Probability"]
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


def _event_cards() -> Image.Image:
    events = ["The sun rises tomorrow.",
              "It will snow today.",
              "I will pick a red marble.",
              "I will roll a 7.",
              "Coin lands on heads.",
              "Tomorrow is Wednesday.",
              "The ice will melt in the sun.",
              "Dog will bark at noon."]
    canvas, draw = _new("Event Cards")
    cols = 2
    rows = 4
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, ev in enumerate(events):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        # wrap text
        words = ev.split()
        font = TC._font(20)
        line, ly = "", y0 + 30
        for w in words:
            test = (line + " " + w).strip()
            tb = draw.textbbox((0, 0), test, font=font)
            if tb[2] - tb[0] > cw - 40:
                draw.text((x0 + 24, ly), line, font=font,
                          fill=(20, 20, 20))
                ly += 26
                line = w
            else:
                line = test
        if line:
            draw.text((x0 + 24, ly), line, font=font, fill=(20, 20, 20))
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


def compose_probability_image(image_id: str, grade: str | None = None,
                              unit_id: str | None = None) -> Image.Image | None:
    # Manipulatives
    if image_id in ("M1_LIKELIHOOD", "M1_SCALE", "M7_LIKELIHOOD"):
        return _likelihood_scale()
    if image_id in ("M1_EVENTS", "M2_EVENTS", "M7_EVENT_CARDS"):
        return _event_cards()
    if image_id in ("M2_COMPLEMENTS", "M8_COMPLEMENTS"):
        # Grade 2: child-friendly complement language (no P(A) notation).
        # Grade 3+: keep formal complement notation.
        if grade in ("Kindergarten", "Grade 1", "Grade 2"):
            return _poster("Complementary Events", [
                "When ONE happens, the OTHER doesn't.",
                "Heads ↔ Tails. Rain ↔ No Rain.",
                "Win ↔ Lose. Day ↔ Night.",
                "Find ONE, get the OTHER for free.",
            ])
        return _poster("Complement Events", [
            "If P(A) = 1/4, then P(NOT A) = 3/4.",
            "Complements add to 1.",
            "Find ONE, get the OTHER for free.",
        ])
    if image_id == "M2_MAT":
        return _likelihood_scale()
    if image_id == "M3_COINDICE":
        return _coins(2)
    if image_id == "M3_COINS":
        return _coins(3)
    if image_id == "M3_SPINNERS":
        return _spinner(4, ["A", "B", "C", "D"])
    if image_id == "M4_DICE":
        return _dice([3, 5])
    if image_id == "M4_POPCHART":
        return _outcome_table(rows=6)
    if image_id == "M5_MEANMODE":
        return _poster("Mean / Mode", [
            "MEAN: average of values.",
            "MODE: most common value.",
            "Use mean for typical value.",
            "Use mode for most likely.",
        ])
    if image_id == "M5_PRED_MAT":
        return _outcome_table(rows=6)
    if image_id == "M8_CYCLE":
        return _poster("Predict-Test-Refine", [
            "1. PREDICT: what do I think?",
            "2. TEST: try it many times.",
            "3. RECORD: tally results.",
            "4. COMPARE: predicted vs actual.",
            "5. REFINE: update prediction.",
        ])
    if image_id == "M8_PRED":
        return _outcome_table(rows=6)
    if image_id == "M9_OUTCOMES":
        # Grade 2 manipulative is a CARD GRID of 12 outcomes (Heads, Tails,
        # Red, Blue, Green, Yellow, Sun, Rain, Number 1-4), NOT a record-
        # keeping table (which is what M5_PRED_MAT already is). Defer so
        # smart_fallback renders the actual outcome labels in a card grid.
        if grade in ("Kindergarten", "Grade 1", "Grade 2"):
            return None
        return _outcome_table(rows=8)

    # Worksheets — most are workspaces with specific prompts
    workspaces = {
        "WS01_P1_EVENTS": ("List 4 events. Place each on the scale.",
                           "Events on the Scale"),
        "WS01_P1_MATCH": ("Match each event to a likelihood word.",
                          "Match Events"),
        "WS01_P2_BOX": ("Sort 6 events into the 3 boxes.",
                        "Sort by Likelihood"),
        "WS01_P2_TABLE": ("Fill the table.", "Likelihood Table"),
        "WS01_P3_WHY": ("Explain WHY each event is where it is.",
                        "Explain Your Sort"),
        "WS02_P1_EVENTS": ("Look at 4 events. Use real data.",
                           "Use Data"),
        "WS02_P1_MATCH": ("Match data → likelihood.",
                          "Match with Data"),
        "WS02_P2_DECIDE": ("Decide: likely or unlikely?",
                           "Decide"),
        "WS02_P2_SORT": ("Sort with reasons.", "Sort and Explain"),
        "WS02_P2_TABLE": ("Complete the table from data.",
                          "Data Table"),
        "WS02_P3_REVISE": ("Revise based on new data.",
                           "Revise"),
        "WS02_P3_TRICKY": ("Why are these tricky?", "Tricky Cases"),
        "WS03_P1_PREDICT": ("Predict the outcome of 10 trials.",
                            "Predict First"),
        "WS03_P2_BAG": ("Use the marble bag. Predict each pick.",
                        "Marble Bag Predictions"),
        "WS03_P2_DATA": ("Run 20 trials. Tally results.",
                         "Run Trials"),
        "WS03_P3_CHECK": ("Check predictions vs data.",
                          "Check Predictions"),
        "WS04_P1_CLASSES": ("Compare classroom data.",
                            "Compare Classes"),
        "WS04_P1_PREDICT": ("Predict before testing.",
                            "Predict First"),
        "WS04_P1_TALLY": ("Tally results.", "Tally Time"),
        "WS04_P2_CALC": ("Calculate the probability.",
                         "Calculate"),
        "WS04_P3_BOX": ("Use the box-and-arrow.",
                        "Box and Arrow"),
        "WS04_P3_PREDICT": ("Make a final prediction.",
                            "Final Prediction"),
        "WS04_P3_RESULT": ("Compare to actual results.",
                           "Compare Results"),
        "WS05_P1_COIN": ("Capstone: coin probabilities.",
                         "Coin Capstone"),
        "WS05_P1_LIKELIHOOD": ("Capstone: likelihood scale.",
                               "Likelihood Capstone"),
        "WS05_P1_PREDICT": ("Capstone: predict outcomes.",
                            "Predict Capstone"),
        "WS05_P2_DATA": ("Run trials and record.",
                         "Capstone Data"),
        "WS05_P2_LAB": ("Run a lab. Record carefully.",
                        "Capstone Lab"),
        "WS05_P2_MARBLES": ("Marble lab.", "Marble Capstone"),
        "WS05_P3_CONCLUDE": ("Write your conclusion.",
                             "Capstone Conclusion"),
        "WS05_P3_SORT_SUMMARY": ("Summarise your sort.",
                                 "Sort Summary"),
        "WS05_P3_SURVEY": ("Survey the class.",
                           "Survey"),
    }
    if image_id in workspaces:
        prompt, title = workspaces[image_id]
        return _workspace(prompt, title=title, box_h=460)

    # Specialized worksheets
    if image_id == "WS01_P2_SCALE":
        return _likelihood_scale()
    if image_id in ("WS01_P3_LINES", "WS02_P3_LINES", "WS03_P3_LINES"):
        return _probability_line()
    if image_id == "WS02_P1_COINDICE":
        return _coins(2)
    if image_id == "WS03_P1_COINS":
        return _coins(3)
    if image_id == "WS03_P1_SPINNERS":
        return _spinner(4, ["RED", "BLUE", "GREEN", "YELLOW"])

    # Formative
    if image_id == "FORM_Q1_EVENTS":
        return _event_cards()
    if image_id == "FORM_Q1_SPINNER":
        return _spinner(3, ["A", "B", "C"])
    if image_id == "FORM_Q1_WORD":
        return _likelihood_scale()
    if image_id == "FORM_Q2_COINS":
        return _coins(2)
    if image_id == "FORM_Q2_COMPARE":
        return _outcome_table(rows=4)
    if image_id == "FORM_Q2_COMPLEMENT":
        if grade in ("Kindergarten", "Grade 1", "Grade 2"):
            return _poster("Complement Check", [
                "Name the complement of each event:",
                "RAIN → ?    HEADS → ?",
                "WIN → ?     DAY → ?",
                "When one happens, the other doesn't."])
        return _poster("Complement Check", [
            "If P(A) = 2/5, find P(NOT A).",
            "Complements add to 1."])

    return None
