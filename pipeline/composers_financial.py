"""Financial-literacy composers: coins, bills, price tags, budgets.

  g1_financial_classroom_market — Penny + Coin Cassie
  g2_financial_tap_to_pay       — Tappy + Loonie
  g3_financial_plan_your_party  — Pat + Budget Bea
"""
from __future__ import annotations

import math
from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    "M1_COINS", "M1_MONEY", "M2_BILLS", "M2_TAGS",
    "M3_CHART", "M3_EST", "M3_VALUES",
    "M4_AMOUNTS", "M4_COMP", "M4_SUB",
    "M5_BUDGET", "M5_MARKET", "M5_TAP",
    "M8_CALCS", "M8_STRIPS", "M8_TAGS",
    "M9_PARTY", "M9_POUCH", "M9_TAGS",
    "WS01_P1_NAMES", "WS01_P1_ROUND", "WS01_P1_THREE",
    "WS01_P2_EST", "WS01_P2_MATCH", "WS01_P2_TF",
    "WS01_P3_BOTH", "WS01_P3_DIMES", "WS01_P3_MORE",
    "WS02_P1_CALC", "WS02_P1_FIND", "WS02_P1_THREE",
    "WS02_P2_CHECK", "WS02_P2_TF", "WS02_P2_VALUES",
    "WS02_P3_LOONIES", "WS02_P3_NICKELS", "WS02_P3_ONE",
    "WS03_P1_25", "WS03_P1_CENTS", "WS03_P1_COLOUR",
    "WS03_P2_COINS", "WS03_P2_TF", "WS03_P2_VALUES",
    "WS03_P3_FEW", "WS03_P3_ONE", "WS03_P3_SORT",
    "WS04_P1_COMP", "WS04_P1_MIXED",
    "WS04_P2_MORE", "WS04_P2_SHOW", "WS04_P2_TWO",
    "WS04_P3_150", "WS04_P3_ONE", "WS04_P3_RANK",
    "WS05_P1_DOLLAR", "WS05_P1_NAME", "WS05_P1_PICK",
    "WS05_P2_25", "WS05_P2_COMP", "WS05_P2_PAY",
    "WS05_P3_150", "WS05_P3_PAY", "WS05_P3_SWAP",
    "FORM_Q1_COINS", "FORM_Q1_DOLLAR",
    "FORM_Q2_35", "FORM_Q2_BILLS", "FORM_Q2_CENTS",
}


COIN_SPECS = {
    "1¢":   ("penny",   60),
    "5¢":   ("nickel",  72),
    "10¢":  ("dime",    56),
    "25¢":  ("quarter", 80),
    "$1":   ("loonie",  88),
    "$2":   ("toonie",  96),
}


def _new(title: str | None = None):
    canvas = TC._new(1024, 768)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (512, 50), title, TC._font(36, bold=True))
    return canvas, draw


def _draw_coin(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int,
               label: str, name: str = "") -> None:
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                 outline=(20, 20, 20), width=4)
    draw.ellipse((cx - radius + 8, cy - radius + 8,
                  cx + radius - 8, cy + radius - 8),
                 outline=(20, 20, 20), width=2)
    TC._text_centered(draw, (cx, cy - 6), label, TC._font(int(radius * 0.6), bold=True))
    if name:
        TC._text_centered(draw, (cx, cy + radius + 22),
                          name, TC._font(18))


def _coin_set(amounts: list[str] = None) -> Image.Image:
    canvas, draw = _new("Canadian Coins")
    coins = list((amounts or COIN_SPECS.keys()))
    n = len(coins)
    margin = 80
    spacing = (1024 - 2 * margin) // n
    for i, c in enumerate(coins):
        cx = margin + spacing // 2 + i * spacing
        cy = 380
        name, r = COIN_SPECS.get(c, ("?", 64))
        _draw_coin(draw, cx, cy, r, c, name)
    return canvas


def _bill_set(include_hundred: bool = True) -> Image.Image:
    canvas, draw = _new("Canadian Bills")
    bills = [("$5",  "five"),
             ("$10", "ten"),
             ("$20", "twenty"),
             ("$50", "fifty")]
    if include_hundred:
        bills.append(("$100", "hundred"))
    n = len(bills)
    bill_w, bill_h = 180, 90
    margin = 60
    spacing = (1024 - 2 * margin - bill_w * n) // (n - 1) if n > 1 else 0
    y = 320
    for i, (val, name) in enumerate(bills):
        x = margin + i * (bill_w + spacing)
        draw.rectangle((x, y, x + bill_w, y + bill_h),
                       outline=(20, 20, 20), width=4)
        draw.rectangle((x + 8, y + 8, x + bill_w - 8, y + bill_h - 8),
                       outline=(20, 20, 20), width=1)
        TC._text_centered(draw, (x + bill_w // 2, y + bill_h // 2),
                          val, TC._font(38, bold=True))
        TC._text_centered(draw, (x + bill_w // 2, y + bill_h + 30),
                          name, TC._font(18))
    return canvas


def _price_tag_grid(items: list[tuple[str, str]], cols: int = 3) -> Image.Image:
    canvas, draw = _new("Price Tags")
    n = len(items)
    rows = math.ceil(n / cols)
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, (item, price) in enumerate(items):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        # Tag shape: rounded rectangle with notch on left
        draw.polygon([(x0 + 30, y0 + 20),
                      (x0 + cw - 20, y0 + 20),
                      (x0 + cw - 20, y0 + ch - 20),
                      (x0 + 30, y0 + ch - 20),
                      (x0 + 14, y0 + ch // 2)],
                     outline=(20, 20, 20), width=3)
        draw.ellipse((x0 + 28, y0 + ch // 2 - 8,
                      x0 + 44, y0 + ch // 2 + 8),
                     outline=(20, 20, 20), width=2)
        TC._text_centered(draw, (x0 + cw // 2 + 10, y0 + ch // 2 - 16),
                          item, TC._font(24, bold=True))
        TC._text_centered(draw, (x0 + cw // 2 + 10, y0 + ch // 2 + 16),
                          price, TC._font(28, bold=True))
    return canvas


def _amount_card_grid(amounts: list[str], cols: int = 4) -> Image.Image:
    canvas, draw = _new("Amount Cards")
    n = len(amounts)
    rows = math.ceil(n / cols)
    margin = 50
    cw = (1024 - 2 * margin) // cols
    ch = (768 - 110 - margin) // rows
    for i, a in enumerate(amounts):
        r, c = divmod(i, cols)
        x0 = margin + c * cw
        y0 = 110 + r * ch
        draw.rectangle((x0 + 8, y0 + 8, x0 + cw - 8, y0 + ch - 8),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cw // 2, y0 + ch // 2),
                          a, TC._font(48, bold=True))
    return canvas


def _budget_table() -> Image.Image:
    canvas, draw = _new("Budget Worksheet")
    headers = ["Item", "Cost", "Subtotal"]
    n_cols = len(headers)
    cell_w = (1024 - 80) // n_cols
    top = 130
    cell_h = 70
    for j, h in enumerate(headers):
        x0 = 40 + j * cell_w
        draw.rectangle((x0, top, x0 + cell_w, top + cell_h),
                       outline=(20, 20, 20), width=3)
        TC._text_centered(draw, (x0 + cell_w // 2, top + cell_h // 2),
                          h, TC._font(24, bold=True))
    # 7 rows
    for r in range(7):
        y0 = top + cell_h * (r + 1)
        for j in range(n_cols):
            x0 = 40 + j * cell_w
            draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h),
                           outline=(20, 20, 20), width=2)
    # TOTAL row
    y0 = top + cell_h * 8
    draw.rectangle((40, y0, 40 + cell_w * 2, y0 + cell_h),
                   outline=(20, 20, 20), width=3)
    TC._text_centered(draw, (40 + cell_w, y0 + cell_h // 2),
                      "TOTAL", TC._font(28, bold=True))
    draw.rectangle((40 + cell_w * 2, y0, 40 + cell_w * 3, y0 + cell_h),
                   outline=(20, 20, 20), width=3)
    return canvas


def _tap_terminal() -> Image.Image:
    canvas, draw = _new("Tap-to-Pay Terminal")
    # Terminal box
    draw.rectangle((352, 170, 672, 600),
                   outline=(20, 20, 20), width=5)
    # Screen
    draw.rectangle((392, 220, 632, 380),
                   outline=(20, 20, 20), width=3)
    TC._text_centered(draw, (512, 270), "AMOUNT",
                      TC._font(22, bold=True))
    TC._text_centered(draw, (512, 320), "$ ___ . ___",
                      TC._font(36, bold=True))
    # Tap zone
    draw.ellipse((432, 420, 592, 580),
                 outline=(20, 20, 20), width=4)
    TC._text_centered(draw, (512, 470), "TAP", TC._font(28, bold=True))
    # WiFi-like waves
    for r in (40, 60, 80):
        draw.arc((512 - r, 480 - r, 512 + r, 580 - r),
                 start=210, end=330, fill=(20, 20, 20), width=3)
    return canvas


def _market_layout() -> Image.Image:
    canvas, draw = _new("Classroom Market")
    # 3 stalls
    stall_names = ["Snack Stall", "Toy Stall", "Book Stall"]
    n = len(stall_names)
    margin = 40
    sw = (1024 - 2 * margin) // n
    for i, name in enumerate(stall_names):
        x0 = margin + i * sw
        x1 = x0 + sw - 10
        # awning (triangle)
        draw.polygon([(x0, 200), (x1, 200), ((x0 + x1) // 2, 130)],
                     outline=(20, 20, 20), width=3)
        # stall body
        draw.rectangle((x0, 200, x1, 660),
                       outline=(20, 20, 20), width=3)
        # counter
        draw.rectangle((x0 + 20, 540, x1 - 20, 580),
                       fill=(60, 60, 60))
        TC._text_centered(draw, ((x0 + x1) // 2, 250),
                          name, TC._font(24, bold=True))
        # 3 price tags
        for k in range(3):
            ty = 320 + k * 60
            draw.rectangle((x0 + 30, ty, x1 - 30, ty + 40),
                           outline=(20, 20, 20), width=2)
            TC._text_centered(draw, ((x0 + x1) // 2, ty + 20),
                              f"$ ___", TC._font(20, bold=True))
    return canvas


def _calc_strip() -> Image.Image:
    canvas, draw = _new("Calculation Strip")
    # 5 vertical addition columns
    margin = 60
    n = 5
    cw = (1024 - 2 * margin) // n
    for i in range(n):
        x0 = margin + i * cw
        x1 = x0 + cw - 20
        draw.rectangle((x0, 130, x1, 720),
                       outline=(20, 20, 20), width=3)
        # +/= signs
        TC._text_centered(draw, ((x0 + x1) // 2, 360),
                          "+", TC._font(48, bold=True))
        draw.line([(x0 + 16, 540), (x1 - 16, 540)],
                  fill=(20, 20, 20), width=3)
    return canvas


def _coin_pouch() -> Image.Image:
    canvas, draw = _new("Coin Pouch")
    # pouch outline
    draw.polygon([(360, 220), (664, 220), (740, 320), (700, 600),
                  (640, 660), (384, 660), (324, 600), (284, 320)],
                 outline=(20, 20, 20), width=4)
    # ties
    draw.line([(360, 220), (340, 180)], fill=(20, 20, 20), width=3)
    draw.line([(664, 220), (684, 180)], fill=(20, 20, 20), width=3)
    # 6 coins inside
    coins = ["1¢", "5¢", "10¢", "25¢", "$1", "$2"]
    for i, c in enumerate(coins):
        cx = 360 + (i % 3) * 130
        cy = 360 + (i // 3) * 140
        _draw_coin(draw, cx, cy, 50, c)
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


def compose_financial_image(image_id: str, grade: str | None = None,
                            unit_id: str | None = None) -> Image.Image | None:
    if image_id in ("M1_COINS", "M1_MONEY"):
        return _coin_set()
    if image_id == "M2_BILLS":
        # F1.1 (Grade 1) is up to $50; F2.1 (Grade 2) adds $100; F3.x adds more.
        # g1_financial_classroom_market is Grade 1 → exclude $100.
        include_hundred = grade != "Grade 1"
        return _bill_set(include_hundred=include_hundred)
    if image_id in ("M2_TAGS", "M8_TAGS", "M9_TAGS"):
        return _price_tag_grid([
            ("Apple",   "25¢"), ("Pencil", "10¢"), ("Sticker", "5¢"),
            ("Eraser",  "15¢"), ("Toy",    "$1"),  ("Book",    "$2"),
            ("Drink",   "75¢"), ("Snack",  "50¢"), ("Cap",     "$5"),
        ], cols=3)
    if image_id in ("M3_CHART", "M3_VALUES"):
        return _coin_set()
    if image_id == "M3_EST":
        return _amount_card_grid(["$ 5", "$ 10", "$ 25", "$ 50",
                                  "$ 100", "$ 200", "$ 500", "$ 1000"], cols=4)
    if image_id == "M4_AMOUNTS":
        return _amount_card_grid(["35¢", "75¢", "$1.25", "$2.50",
                                  "$5.75", "$10.00", "$25.50", "$100.00"],
                                 cols=4)
    if image_id == "M4_COMP":
        return _amount_card_grid([
            "25¢", "30¢", "$1", "$1.10",
            "$5", "$5.50", "$10", "$11"], cols=4)
    if image_id == "M4_SUB":
        return _amount_card_grid([
            "$1 - 25¢", "$2 - 50¢", "$5 - $1",
            "$10 - $5", "$20 - $11", "$50 - $25"], cols=3)
    if image_id == "M5_BUDGET":
        return _budget_table()
    if image_id == "M5_MARKET":
        return _market_layout()
    if image_id == "M5_TAP":
        return _tap_terminal()
    if image_id in ("M8_CALCS", "M8_STRIPS"):
        return _calc_strip()
    if image_id == "M9_PARTY":
        return _budget_table()
    if image_id == "M9_POUCH":
        return _coin_pouch()

    # Worksheets — most are workspaces
    workspace_specs = {
        "WS01_P1_NAMES":   ("Name each coin and bill.", "Name the Money"),
        "WS01_P1_ROUND":   ("Round to the nearest amount.", "Round It"),
        "WS01_P1_THREE":   ("Show 3 ways to make this amount.", "Three Ways"),
        "WS01_P2_EST":     ("Estimate the total.", "Estimate"),
        "WS01_P2_MATCH":   ("Match coin → value.", "Match"),
        "WS01_P2_TF":      ("True or false?", "True/False"),
        "WS01_P3_BOTH":    ("Both pay. Compare totals.", "Both"),
        "WS01_P3_DIMES":   ("Show with dimes only.", "Dimes Only"),
        "WS01_P3_MORE":    ("Add 25¢ more. Show.", "Add 25¢"),
        "WS02_P1_CALC":    ("Calculate exactly.", "Calculate"),
        "WS02_P1_FIND":    ("Find the missing coin.", "Find Missing"),
        "WS02_P1_THREE":   ("Three ways to pay.", "Three Ways"),
        "WS02_P2_CHECK":   ("Check the change.", "Check Change"),
        "WS02_P2_TF":      ("True/False on values.", "T/F"),
        "WS02_P2_VALUES":  ("Write each value.", "Values"),
        "WS02_P3_LOONIES": ("Loonies only — show.", "Loonies Only"),
        "WS02_P3_NICKELS": ("Nickels only — show.", "Nickels Only"),
        "WS02_P3_ONE":     ("Pay with one coin.", "One Coin"),
        "WS03_P1_25":      ("Make 25¢ different ways.", "Make 25¢"),
        "WS03_P1_CENTS":   ("Add cent amounts.", "Cent Math"),
        "WS03_P1_COLOUR":  ("Colour the coins.", "Colour Coins"),
        "WS03_P2_COINS":   ("Sort coin groups.", "Sort Coins"),
        "WS03_P2_TF":      ("True/False checks.", "T/F"),
        "WS03_P2_VALUES":  ("Write coin values.", "Values"),
        "WS03_P3_FEW":     ("Use the fewest coins.", "Fewest Coins"),
        "WS03_P3_ONE":     ("One bill works?", "One Bill"),
        "WS03_P3_SORT":    ("Sort by value.", "Sort"),
        "WS04_P1_COMP":    ("Compare two prices.", "Compare"),
        "WS04_P1_MIXED":   ("Mixed money problems.", "Mixed"),
        "WS04_P2_MORE":    ("How much MORE is needed?", "More Needed"),
        "WS04_P2_SHOW":    ("Show the total.", "Show Total"),
        "WS04_P2_TWO":     ("Show with TWO bills.", "Two Bills"),
        "WS04_P3_150":     ("Reach $150.", "Target $150"),
        "WS04_P3_ONE":     ("One way to pay.", "One Way"),
        "WS04_P3_RANK":    ("Rank prices low → high.", "Rank Prices"),
        "WS05_P1_DOLLAR":  ("Plan a $1 spend.", "$1 Plan"),
        "WS05_P1_NAME":    ("Name your party.", "Name It"),
        "WS05_P1_PICK":    ("Pick a budget total.", "Budget"),
        "WS05_P2_25":      ("Stay within 25¢.", "25¢ Budget"),
        "WS05_P2_COMP":    ("Compare two budgets.", "Compare"),
        "WS05_P2_PAY":     ("Pay each item.", "Pay Each"),
        "WS05_P3_150":     ("Stay within $150.", "$150 Budget"),
        "WS05_P3_PAY":     ("Pay your party total.", "Pay Total"),
        "WS05_P3_SWAP":    ("Swap to fit budget.", "Swap"),
    }
    if image_id in workspace_specs:
        prompt, title = workspace_specs[image_id]
        return _workspace(prompt, title=title, box_h=460)

    if image_id == "FORM_Q1_COINS":
        return _coin_set()
    if image_id == "FORM_Q1_DOLLAR":
        return _bill_set()
    if image_id == "FORM_Q2_35":
        return _workspace("Show 35¢ in 3 ways.",
                          title="Show 35¢", box_h=440)
    if image_id == "FORM_Q2_BILLS":
        return _bill_set()
    if image_id == "FORM_Q2_CENTS":
        return _amount_card_grid(["1¢", "5¢", "10¢", "25¢"], cols=4)

    return None
