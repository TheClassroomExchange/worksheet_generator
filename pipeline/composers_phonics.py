"""Phonics composers — Language Strand B (2023 SoR).

Renders worksheet hero images and manipulatives for K-G3 Language phonics
units. The first user is g1_language_cvc_decoders. As more Language units
are written, extend HANDLED_IDS and the dispatch in
compose_phonics_image().

All composers return PIL.Image. Conventions match
pipeline.template_composers (white bg, dark grey strokes, 1024x768 default,
phoneme notation /c/-/a/-/t/ with slashes).
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import template_composers as TC


HANDLED_IDS = {
    # g1_language_cvc_decoders worksheets
    "WS01_P1_MATCH", "WS01_P2_BOXES", "WS01_P3_LAST",
    "WS02_P1_LETTER", "WS02_P2_BUILD", "WS02_P3_READ",
    "WS03_P1_SLIDE", "WS03_P2_MATCH", "WS03_P3_NEW",
    "WS04_P1_SENTENCE", "WS04_P2_MATCH", "WS04_P3_FILL",
    "WS05_P1_HEAR", "WS05_P2_BLEND", "WS05_P3_READ",
    # Manipulatives
    "M1_BOXES",        # 3-box sound box cards (2x3 grid)
    "M2_PICTURES",     # 20 CVC picture cards (4x5 grid)
    "M3_LETTERS",      # 26 letter index cards (4x7 grid)
    "M4_STRIPS",       # 6 decodable sentence strips
    "M5_CAPSTONE",     # capstone template (4 stations)
    "M6_VOCAB",        # phonics vocabulary chart (5 rows)
    "M7_POSTER",       # CVC Decoders poster (Sounder + Blendy + 4 jobs)
    # Formative
    "FORM_Q1_SEGMENT", "FORM_Q2_LETTER",
    # Assessment-suite trackers (rendered as a 4-col tick table)
    "AS_DIAG_TRACKER", "AS_FORM_TRACKER_L2",
    "AS_FORM_TRACKER_L3", "AS_FORM_TRACKER_L4",
    "AS_CERT_BORDER", "AS_CERT_SOUNDER",
}


# ── Helpers ───────────────────────────────────────────────────────────────

def _new(title: str | None = None, subtitle: str | None = None,
         w: int = 1024, h: int = 768):
    canvas = TC._new(w, h)
    draw = ImageDraw.Draw(canvas)
    if title:
        TC._text_centered(draw, (w // 2, 50), title, TC._font(36, bold=True))
    if subtitle:
        TC._text_centered(draw, (w // 2, 92), subtitle, TC._font(22))
    return canvas, draw


def _phoneme_bubble(draw: ImageDraw.ImageDraw, cx: int, cy: int,
                    label: str, r: int = 38) -> None:
    """Draw an oval with the phoneme like /c/ inside."""
    ry = int(r * 0.7)
    draw.ellipse((cx - r, cy - ry, cx + r, cy + ry),
                 fill="white", outline="black", width=3)
    TC._text_centered(draw, (cx, cy), label, TC._font(28, bold=True))


def _picture_box(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int,
                 label: str) -> None:
    """A simple bordered box with a child-friendly label inside.

    We don't have CVC-specific clipart, so we draw a labelled icon box —
    the child sees the WORD and decodes it. This is honest about the
    rendering capability without faking pictures.
    """
    draw.rectangle((x, y, x + w, y + h), fill="white", outline="black", width=2)
    TC._text_centered(draw, (x + w // 2, y + h // 2),
                      label.upper(), TC._font(28, bold=True))


def _sound_box_row(draw: ImageDraw.ImageDraw, x: int, y: int, cell_w: int = 60,
                   cell_h: int = 60, fills: tuple[str, ...] = ("", "", "")) -> None:
    """Three cells in a row with optional letters/marks inside."""
    for i, fill in enumerate(fills):
        x0 = x + i * cell_w
        draw.rectangle((x0, y, x0 + cell_w, y + cell_h),
                       fill="white", outline="black", width=2)
        if fill:
            TC._text_centered(draw, (x0 + cell_w // 2, y + cell_h // 2),
                              fill.lower(), TC._font(34, bold=True))


# ── Worksheet composers ──────────────────────────────────────────────────

def _ws01_p1_match() -> Image.Image:
    """First-sound match: 4 picture boxes on left, 4 phoneme bubbles on right."""
    canvas, draw = _new(title="First-Sound Match",
                        subtitle="Draw a line from each picture to its first sound.")
    pictures = ["cat", "dog", "sun", "mat"]
    bubbles = ["/c/", "/d/", "/s/", "/m/"]
    # Scramble bubble order so it's a real match
    bubble_order = ["/m/", "/c/", "/s/", "/d/"]
    n = 4
    pic_x, pic_w, pic_h = 120, 180, 110
    bub_x = 760
    spacing = 130
    top = 160
    for i in range(n):
        y = top + i * spacing
        _picture_box(draw, pic_x, y, pic_w, pic_h, pictures[i])
        _phoneme_bubble(draw, bub_x, y + pic_h // 2, bubble_order[i], r=46)
        # faint match guide
        draw.line((pic_x + pic_w + 20, y + pic_h // 2,
                   bub_x - 50, y + pic_h // 2),
                  fill=(220, 220, 220), width=1)
    return canvas


def _ws01_p2_boxes() -> Image.Image:
    """Sound box rows: 4 pictures each with a 3-cell sound box below."""
    canvas, draw = _new(title="Sound Boxes",
                        subtitle="Write one sound in each box.")
    words = ["pin", "cup", "run", "lid"]
    box_w, box_h = 60, 60
    cols = 2
    cell_box_total_w = box_w * 3
    horizontal_spacing = 380
    vertical_spacing = 230
    start_x = 175
    start_y = 150
    for idx, word in enumerate(words):
        col = idx % cols
        row = idx // cols
        cx = start_x + col * horizontal_spacing
        cy = start_y + row * vertical_spacing
        _picture_box(draw, cx, cy, cell_box_total_w + 40, 100, word)
        _sound_box_row(draw, cx + 20, cy + 120, cell_w=box_w, cell_h=box_h,
                       fills=("", "", ""))
    return canvas


def _ws01_p3_last() -> Image.Image:
    """Last-sound circle: 3 picture rows, each with 3 phoneme choices."""
    canvas, draw = _new(title="Last-Sound Circle",
                        subtitle="Circle the LAST sound you hear.")
    rows = [
        ("bag", ["/b/", "/a/", "/g/"]),
        ("fox", ["/f/", "/o/", "/x/"]),
        ("jet", ["/j/", "/e/", "/t/"]),
    ]
    pic_x, pic_w, pic_h = 120, 180, 110
    spacing = 170
    top = 160
    for i, (word, choices) in enumerate(rows):
        y = top + i * spacing
        _picture_box(draw, pic_x, y, pic_w, pic_h, word)
        # Three phoneme bubbles
        for j, choice in enumerate(choices):
            cx = 460 + j * 170
            _phoneme_bubble(draw, cx, y + pic_h // 2, choice, r=46)
    return canvas


def _ws02_p1_letter() -> Image.Image:
    """Letter-to-sound match: 4 letter cards on left, 4 phoneme bubbles on right."""
    canvas, draw = _new(title="Letter to Sound",
                        subtitle="Draw a line from each letter to its sound.")
    letters = ["c", "m", "s", "t"]
    bubbles_scrambled = ["/s/", "/c/", "/t/", "/m/"]
    letter_x, letter_w, letter_h = 200, 100, 100
    bub_x = 760
    spacing = 130
    top = 160
    for i in range(4):
        y = top + i * spacing
        # Letter card
        draw.rectangle((letter_x, y, letter_x + letter_w, y + letter_h),
                       fill="white", outline="black", width=3)
        TC._text_centered(draw, (letter_x + letter_w // 2, y + letter_h // 2),
                          letters[i], TC._font(60, bold=True))
        _phoneme_bubble(draw, bub_x, y + letter_h // 2,
                        bubbles_scrambled[i], r=46)
        draw.line((letter_x + letter_w + 30, y + letter_h // 2,
                   bub_x - 50, y + letter_h // 2),
                  fill=(220, 220, 220), width=1)
    return canvas


def _ws02_p2_build() -> Image.Image:
    """Build the word: 4 pictures with empty sound boxes for letters."""
    canvas, draw = _new(title="Build the Word",
                        subtitle="Write the letter for each sound.")
    words = ["cat", "dog", "sun", "mat"]
    box_w, box_h = 70, 70
    cols = 2
    horizontal_spacing = 380
    vertical_spacing = 230
    start_x = 165
    start_y = 150
    for idx, word in enumerate(words):
        col = idx % cols
        row = idx // cols
        cx = start_x + col * horizontal_spacing
        cy = start_y + row * vertical_spacing
        _picture_box(draw, cx, cy, box_w * 3 + 40, 100, word)
        _sound_box_row(draw, cx + 20, cy + 120, cell_w=box_w, cell_h=box_h)
    return canvas


def _ws02_p3_read() -> Image.Image:
    """Read and circle: 3 sound-box words on left, 3 picture choices on right."""
    canvas, draw = _new(title="Read and Match",
                        subtitle="Read each word. Circle the matching picture.")
    rows = [
        ("pin",  ["pin", "pen", "pan"]),
        ("cup",  ["cap", "cup", "cop"]),
        ("run",  ["ran", "run", "rin"]),
    ]
    word_x, box_w, box_h = 100, 70, 70
    spacing = 175
    top = 160
    for i, (word, choices) in enumerate(rows):
        y = top + i * spacing
        # Word in sound boxes
        for j, ch in enumerate(word):
            cx = word_x + j * box_w
            draw.rectangle((cx, y, cx + box_w, y + box_h),
                           fill="white", outline="black", width=2)
            TC._text_centered(draw, (cx + box_w // 2, y + box_h // 2),
                              ch, TC._font(40, bold=True))
        # Three picture choices
        for j, choice in enumerate(choices):
            x0 = 400 + j * 180
            _picture_box(draw, x0, y, 150, box_h * 2, choice)
    return canvas


def _ws03_p1_slide() -> Image.Image:
    """Sound and slide: 4 sound-box words with slide arrows."""
    canvas, draw = _new(title="Sound and Slide",
                        subtitle="Sound each letter, then slide them together.")
    words = ["cat", "map", "sun", "lid"]
    box_w, box_h = 80, 80
    cols = 2
    horiz = 460
    vert = 220
    start_x = 130
    start_y = 150
    for idx, word in enumerate(words):
        col = idx % cols
        row = idx // cols
        cx = start_x + col * horiz
        cy = start_y + row * vert
        # Three letter cells
        for j, ch in enumerate(word):
            x0 = cx + j * box_w
            draw.rectangle((x0, cy, x0 + box_w, cy + box_h),
                           fill="white", outline="black", width=3)
            TC._text_centered(draw, (x0 + box_w // 2, cy + box_h // 2),
                              ch, TC._font(46, bold=True))
        # Slide arrow underneath
        ax0 = cx
        ax1 = cx + box_w * 3
        ay = cy + box_h + 28
        draw.line((ax0, ay, ax1, ay), fill="black", width=3)
        # arrow head
        draw.polygon([(ax1, ay), (ax1 - 14, ay - 8), (ax1 - 14, ay + 8)], fill="black")
        # dots along arrow
        for d in range(1, 6):
            dx = ax0 + (ax1 - ax0) * d / 7
            draw.ellipse((dx - 2, ay - 14, dx + 2, ay - 10), fill="black")
    return canvas


def _ws03_p2_match() -> Image.Image:
    """Word to picture: 4 sound-box words on left, 4 pictures on right."""
    canvas, draw = _new(title="Word to Picture",
                        subtitle="Read each word. Draw a line to its picture.")
    pairs = [
        (["d", "o", "g"], "dog"),
        (["p", "i", "n"], "pin"),
        (["c", "u", "p"], "cup"),
        (["b", "a", "g"], "bag"),
    ]
    box_w, box_h = 60, 60
    word_x = 110
    pic_x = 700
    spacing = 130
    top = 160
    for i, (word_letters, pic) in enumerate(pairs):
        y = top + i * spacing
        for j, ch in enumerate(word_letters):
            x0 = word_x + j * box_w
            draw.rectangle((x0, y, x0 + box_w, y + box_h),
                           fill="white", outline="black", width=2)
            TC._text_centered(draw, (x0 + box_w // 2, y + box_h // 2),
                              ch, TC._font(34, bold=True))
        _picture_box(draw, pic_x, y - 10, 180, box_h + 20, pic)
        draw.line((word_x + box_w * 3 + 20, y + box_h // 2,
                   pic_x - 30, y + box_h // 2),
                  fill=(220, 220, 220), width=1)
    return canvas


def _ws03_p3_new() -> Image.Image:
    """Read a new word: 2 sound-box words with handwriting lines below."""
    canvas, draw = _new(title="Read a NEW Word",
                        subtitle="Read each word. Write it on the line.")
    words = ["fox", "jet"]
    box_w, box_h = 95, 95
    horiz = 480
    start_x = 145
    start_y = 200
    for idx, word in enumerate(words):
        cx = start_x + idx * horiz
        # Three letter cells
        for j, ch in enumerate(word):
            x0 = cx + j * box_w
            draw.rectangle((x0, start_y, x0 + box_w, start_y + box_h),
                           fill="white", outline="black", width=3)
            TC._text_centered(draw, (x0 + box_w // 2, start_y + box_h // 2),
                              ch, TC._font(54, bold=True))
        # Handwriting line
        line_y = start_y + box_h + 80
        draw.line((cx, line_y, cx + box_w * 3, line_y),
                  fill="black", width=3)
        TC._text_centered(draw,
                          (cx + box_w * 3 // 2, line_y + 25),
                          "write the word", TC._font(18))
    return canvas


def _ws04_p1_sentence() -> Image.Image:
    """Read and circle: 3 decodable sentences."""
    canvas, draw = _new(title="Read the Sentence",
                        subtitle="Read aloud. Circle each CVC word.")
    sentences = [
        "The cat sat on a mat.",
        "Pat the dog.",
        "A pig in a hat.",
    ]
    spacing = 130
    top = 200
    for i, sent in enumerate(sentences):
        y = top + i * spacing
        # bordered strip
        draw.rectangle((100, y, 924, y + 80),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (512, y + 40), sent, TC._font(34))
    return canvas


def _ws04_p2_match() -> Image.Image:
    """Match sentence to picture."""
    canvas, draw = _new(title="Sentence to Picture",
                        subtitle="Read each sentence. Match it to its picture.")
    rows = [
        ("A pig in a hat.",       "pig + hat"),
        ("The dog sat on a bed.", "dog + bed"),
        ("A cat on a bus.",       "cat + bus"),
    ]
    spacing = 165
    top = 160
    for i, (sent, pic_label) in enumerate(rows):
        y = top + i * spacing
        # Sentence on left
        draw.rectangle((90, y, 540, y + 80),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (315, y + 40), sent, TC._font(26))
        # Picture box on right
        _picture_box(draw, 660, y - 10, 240, 100, pic_label)
        draw.line((545, y + 40, 655, y + 40),
                  fill=(220, 220, 220), width=1)
    return canvas


def _ws04_p3_fill() -> Image.Image:
    """Fill in the blank: 2 sentences with a CVC word missing."""
    canvas, draw = _new(title="Fill in the Word",
                        subtitle="Pick a word from the box. Write it in the blank.")
    # Word bank
    bank = ["cat", "dog", "sun", "mat", "pin"]
    bank_y = 150
    draw.rectangle((180, bank_y, 844, bank_y + 70),
                   fill="white", outline="black", width=3)
    TC._text_centered(draw, (260, bank_y + 35), "Word Bank:",
                      TC._font(22, bold=True))
    for i, w in enumerate(bank):
        TC._text_centered(draw, (400 + i * 90, bank_y + 35), w,
                          TC._font(26, bold=True))

    sentences = [
        "The ___ sat in a hat.",
        "A pig on the ___.",
    ]
    spacing = 130
    top = 320
    for i, sent in enumerate(sentences):
        y = top + i * spacing
        draw.rectangle((100, y, 924, y + 80),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (512, y + 40), sent, TC._font(32))
    return canvas


def _ws05_p1_hear() -> Image.Image:
    """Hear + Map: 2 pictures with 3-cell sound boxes for letters."""
    canvas, draw = _new(title="Hear + Map",
                        subtitle="Segment the word. Write a letter for each sound.")
    words = ["cat", "dog"]
    box_w, box_h = 95, 95
    horiz = 480
    start_x = 145
    start_y = 220
    for idx, word in enumerate(words):
        cx = start_x + idx * horiz
        _picture_box(draw, cx, start_y - 130, box_w * 3, 100, word)
        _sound_box_row(draw, cx, start_y, cell_w=box_w, cell_h=box_h)
    return canvas


def _ws05_p2_blend() -> Image.Image:
    """Blend: 2 sound-box words with handwriting lines below."""
    canvas, draw = _new(title="Blend and Read",
                        subtitle="Read each word. Write it on the line.")
    words = ["pin", "map"]
    box_w, box_h = 95, 95
    horiz = 480
    start_x = 145
    start_y = 220
    for idx, word in enumerate(words):
        cx = start_x + idx * horiz
        for j, ch in enumerate(word):
            x0 = cx + j * box_w
            draw.rectangle((x0, start_y, x0 + box_w, start_y + box_h),
                           fill="white", outline="black", width=3)
            TC._text_centered(draw, (x0 + box_w // 2, start_y + box_h // 2),
                              ch, TC._font(54, bold=True))
        # Handwriting line
        line_y = start_y + box_h + 60
        draw.line((cx, line_y, cx + box_w * 3, line_y),
                  fill="black", width=3)
    return canvas


def _ws05_p3_read() -> Image.Image:
    """Read: 2 decodable sentences with circle space."""
    canvas, draw = _new(title="Read a Sentence",
                        subtitle="Read each sentence. Circle the CVC words.")
    sentences = [
        "The pig sat in a hat.",
        "A bus on the mat.",
    ]
    spacing = 150
    top = 220
    for i, sent in enumerate(sentences):
        y = top + i * spacing
        draw.rectangle((100, y, 924, y + 90),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (512, y + 45), sent, TC._font(36))
    return canvas


# ── Manipulative composers ───────────────────────────────────────────────

def _m1_boxes() -> Image.Image:
    """6 sound box cards in a 2x3 grid."""
    canvas, draw = _new(title="3-Box Sound Box Cards",
                        subtitle="Print 5 pages. Cut into 6 cards per page.",
                        w=1024, h=768)
    card_w, card_h = 280, 130
    cell_w = card_w // 3 - 10
    margin_x = (1024 - card_w * 3 - 40) // 2
    margin_y = 160
    gap = 20
    for row in range(2):
        for col in range(3):
            cx = margin_x + col * (card_w + gap)
            cy = margin_y + row * (card_h + 80)
            # Card border
            draw.rectangle((cx, cy, cx + card_w, cy + card_h),
                           fill="white", outline="black", width=2)
            # Three cells inside
            inner_x = cx + 15
            inner_y = cy + 25
            inner_h = card_h - 50
            for j in range(3):
                x0 = inner_x + j * (cell_w + 5)
                draw.rectangle((x0, inner_y, x0 + cell_w, inner_y + inner_h),
                               fill="white", outline="black", width=3)
    return canvas


def _m2_pictures() -> Image.Image:
    """20 CVC picture cards in a 4x5 grid."""
    canvas, draw = _new(title="CVC Picture Cards",
                        subtitle="Print 10 sets. Cut into 20 cards.")
    words = ["cat", "dog", "sun", "mat", "pin",
             "cup", "run", "lid", "bag", "fox",
             "jet", "hat", "top", "web", "pig",
             "mop", "bed", "bus", "sit", "pen"]
    cols, rows = 5, 4
    card_w = (1024 - 60) // cols - 10
    card_h = (768 - 200) // rows - 10
    margin_x = 30
    margin_y = 140
    for i, w in enumerate(words):
        col = i % cols
        row = i // cols
        cx = margin_x + col * (card_w + 12)
        cy = margin_y + row * (card_h + 12)
        _picture_box(draw, cx, cy, card_w, card_h, w)
    return canvas


def _m3_letters() -> Image.Image:
    """26 lowercase letter cards in a 7x4 grid."""
    canvas, draw = _new(title="Letter Index Cards",
                        subtitle="Print 10 sets. Cut into 26 cards.")
    letters = list("abcdefghijklmnopqrstuvwxyz")
    cols, rows = 7, 4
    card_w = (1024 - 80) // cols - 10
    card_h = (768 - 220) // rows - 10
    margin_x = 40
    margin_y = 150
    for i, ch in enumerate(letters):
        col = i % cols
        row = i // cols
        cx = margin_x + col * (card_w + 12)
        cy = margin_y + row * (card_h + 12)
        draw.rectangle((cx, cy, cx + card_w, cy + card_h),
                       fill="white", outline="black", width=3)
        TC._text_centered(draw, (cx + card_w // 2, cy + card_h // 2),
                          ch, TC._font(48, bold=True))
    return canvas


def _m4_strips() -> Image.Image:
    """6 decodable sentence strips, one per row."""
    canvas, draw = _new(title="Decodable Sentence Strips",
                        subtitle="Print 10 sets. Cut into 6 strips.")
    sentences = [
        "The cat sat on a mat.",
        "Pat the dog.",
        "A pig in a hat.",
        "The bus is red.",
        "A pen on the bed.",
        "The fox ran.",
    ]
    strip_h = 70
    margin_x = 80
    start_y = 145
    gap = 15
    for i, sent in enumerate(sentences):
        y = start_y + i * (strip_h + gap)
        draw.rectangle((margin_x, y, 1024 - margin_x, y + strip_h),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (512, y + strip_h // 2), sent, TC._font(28))
    return canvas


def _m5_capstone() -> Image.Image:
    """Capstone template: 4 station response areas."""
    canvas, draw = _new(title="Big Decoder Capstone",
                        subtitle="HEAR · MAP · BLEND · READ")
    # 2x2 grid of station boxes
    stations = [
        ("HEAR", "Segment 2 picture words into 3 sounds."),
        ("MAP", "Match 4 letter cards to phoneme bubbles."),
        ("BLEND", "Build and read 2 CVC words."),
        ("READ", "Decode 2 sentences. Circle CVC words."),
    ]
    box_w, box_h = 430, 230
    margin_x = (1024 - box_w * 2 - 40) // 2
    margin_y = 150
    gap_x, gap_y = 40, 30
    for i, (title, desc) in enumerate(stations):
        col = i % 2
        row = i // 2
        cx = margin_x + col * (box_w + gap_x)
        cy = margin_y + row * (box_h + gap_y)
        draw.rectangle((cx, cy, cx + box_w, cy + box_h),
                       fill="white", outline="black", width=3)
        # Station number badge
        badge_r = 30
        draw.ellipse((cx + 20, cy + 20, cx + 20 + badge_r * 2, cy + 20 + badge_r * 2),
                     fill="black")
        TC._text_centered(draw, (cx + 20 + badge_r, cy + 20 + badge_r),
                          str(i + 1), TC._font(28, bold=True), fill="white")
        # Title
        TC._text_centered(draw, (cx + box_w // 2 + 20, cy + 50),
                          title, TC._font(32, bold=True))
        # Description (wrap)
        TC._text_centered(draw, (cx + box_w // 2, cy + 110),
                          desc, TC._font(18))
        # Empty answer box
        draw.rectangle((cx + 25, cy + 145, cx + box_w - 25, cy + box_h - 25),
                       fill="white", outline=(140, 140, 140), width=2)
    return canvas


def _m6_vocab() -> Image.Image:
    """Phonics vocabulary chart: 5 rows."""
    canvas, draw = _new(title="Phonics Words",
                        subtitle="Anchor chart for the unit.")
    rows = [
        ("phoneme", "A sound in a spoken word."),
        ("segment", "Break a word into separate sounds."),
        ("letter-sound", "The sound a letter makes."),
        ("blend", "Slide sounds together: /c/-/a/-/t/ → cat."),
        ("decode", "Use letter-sounds to read a word."),
    ]
    row_h = 95
    start_y = 145
    margin_x = 60
    box_w = 1024 - margin_x * 2
    for i, (term, defn) in enumerate(rows):
        y = start_y + i * (row_h + 5)
        draw.rectangle((margin_x, y, margin_x + box_w, y + row_h),
                       fill="white", outline="black", width=2)
        # Term column (left)
        draw.rectangle((margin_x, y, margin_x + 240, y + row_h),
                       fill="white", outline="black", width=2)
        TC._text_centered(draw, (margin_x + 120, y + row_h // 2),
                          term, TC._font(28, bold=True))
        # Definition column (right)
        TC._text_centered(draw,
                          (margin_x + 240 + (box_w - 240) // 2, y + row_h // 2),
                          defn, TC._font(22))
    return canvas


def _m7_poster() -> Image.Image:
    """CVC Decoders poster: 4-step process."""
    canvas, draw = _new(title="CVC Decoders",
                        subtitle="Sounder Sam + Blendy the Bear")
    steps = ["1. HEAR", "2. MAP", "3. BLEND", "4. READ"]
    step_descs = [
        "the sounds",
        "letters to sounds",
        "sounds together",
        "the word",
    ]
    box_w, box_h = 200, 180
    total = box_w * 4 + 30 * 3
    start_x = (1024 - total) // 2
    start_y = 280
    for i, (step, desc) in enumerate(zip(steps, step_descs)):
        cx = start_x + i * (box_w + 30)
        # Numbered box
        draw.rectangle((cx, start_y, cx + box_w, start_y + box_h),
                       fill="white", outline="black", width=3)
        TC._text_centered(draw, (cx + box_w // 2, start_y + 50),
                          step, TC._font(32, bold=True))
        TC._text_centered(draw, (cx + box_w // 2, start_y + 110),
                          desc, TC._font(20))
        # Connecting arrow to next box (except last)
        if i < 3:
            ax = cx + box_w
            ay = start_y + box_h // 2
            draw.line((ax + 2, ay, ax + 28, ay), fill="black", width=3)
            draw.polygon([(ax + 28, ay), (ax + 22, ay - 6), (ax + 22, ay + 6)],
                         fill="black")
    # Footer slogan
    TC._text_centered(draw, (512, 540),
                      "HOO knows the sounds? YOU do!",
                      TC._font(28, bold=True))
    return canvas


# ── Formative + assessment composers ─────────────────────────────────────

def _form_q1_segment() -> Image.Image:
    canvas, draw = _new(title="Segment the Word",
                        subtitle="Write one sound in each box.")
    _picture_box(draw, 360, 200, 300, 130, "cat")
    _sound_box_row(draw, 380, 380, cell_w=90, cell_h=90)
    return canvas


def _form_q2_letter() -> Image.Image:
    canvas, draw = _new(title="Letter to Sound",
                        subtitle="Match each letter to its sound.")
    letters = ["c", "m", "s"]
    bubbles = ["/m/", "/c/", "/s/"]
    letter_x, letter_w, letter_h = 230, 100, 100
    bub_x = 740
    spacing = 140
    top = 200
    for i in range(3):
        y = top + i * spacing
        draw.rectangle((letter_x, y, letter_x + letter_w, y + letter_h),
                       fill="white", outline="black", width=3)
        TC._text_centered(draw, (letter_x + letter_w // 2, y + letter_h // 2),
                          letters[i], TC._font(60, bold=True))
        _phoneme_bubble(draw, bub_x, y + letter_h // 2, bubbles[i], r=46)
    return canvas


def _diagnostic_tracker(title: str, columns: list[str]) -> Image.Image:
    """4-column diagnostic tracker as a tick table (simplified for the slide preview)."""
    canvas, draw = _new(title=title,
                        subtitle="Walk between pairs. Tick where evidence is clear.")
    n_cols = len(columns)
    n_rows = 8  # preview only; printable version has 24
    table_x, table_y = 60, 150
    table_w = 1024 - 120
    table_h = 530
    col_w = table_w // n_cols
    row_h = table_h // (n_rows + 1)
    # Header
    for c, label in enumerate(columns):
        x0 = table_x + c * col_w
        draw.rectangle((x0, table_y, x0 + col_w, table_y + row_h),
                       fill=(240, 240, 240), outline="black", width=2)
        TC._text_centered(draw, (x0 + col_w // 2, table_y + row_h // 2),
                          label, TC._font(15, bold=True))
    # Rows
    for r in range(1, n_rows + 1):
        y = table_y + r * row_h
        for c in range(n_cols):
            x0 = table_x + c * col_w
            draw.rectangle((x0, y, x0 + col_w, y + row_h),
                           fill="white", outline="black", width=2)
    return canvas


def _cert_border() -> Image.Image:
    """Certificate decorative border."""
    canvas, draw = _new(w=1024, h=768)
    # Outer dashed border
    margin = 40
    dash_len = 14
    gap = 8
    sides = [
        (margin, margin, 1024 - margin, margin),  # top
        (margin, 768 - margin, 1024 - margin, 768 - margin),  # bottom
        (margin, margin, margin, 768 - margin),  # left
        (1024 - margin, margin, 1024 - margin, 768 - margin),  # right
    ]
    for x0, y0, x1, y1 in sides:
        if x0 == x1:
            # vertical
            pos = y0
            while pos < y1:
                draw.line((x0, pos, x0, min(pos + dash_len, y1)), fill="black", width=4)
                pos += dash_len + gap
        else:
            pos = x0
            while pos < x1:
                draw.line((pos, y0, min(pos + dash_len, x1), y0), fill="black", width=4)
                pos += dash_len + gap
    # Inner ornament: corner sound-wave + letter motifs
    for corner_x, corner_y in [(80, 80), (944, 80), (80, 688), (944, 688)]:
        draw.ellipse((corner_x - 14, corner_y - 14, corner_x + 14, corner_y + 14),
                     fill="white", outline="black", width=2)
        draw.text((corner_x - 7, corner_y - 11), "♪", font=TC._font(24, bold=True),
                  fill="black")
    return canvas


def _cert_sounder() -> Image.Image:
    """Small Sounder watermark for certificate (re-uses the SVG)."""
    from .compose import _character_svg_path, render_svg
    canvas = TC._new(400, 400)
    svg = _character_svg_path("SOUNDER")
    if svg is not None:
        art = render_svg(svg, width=320, height=320).convert("RGBA")
        px = (400 - art.width) // 2
        py = (400 - art.height) // 2
        canvas.paste(art, (px, py), art)
    return canvas


# ── Dispatcher ───────────────────────────────────────────────────────────

def compose_phonics_image(image_id: str,
                          grade: str | None = None,
                          unit_id: str | None = None) -> Image.Image | None:
    """Return a hero image for a phonics image_id, or None if not handled.

    Called from pipeline.compose._compose_grade_override (added wiring) or
    from the grade-agnostic dispatcher chain.
    """
    if image_id not in HANDLED_IDS:
        return None

    # Worksheets
    if image_id == "WS01_P1_MATCH":   return _ws01_p1_match()
    if image_id == "WS01_P2_BOXES":   return _ws01_p2_boxes()
    if image_id == "WS01_P3_LAST":    return _ws01_p3_last()
    if image_id == "WS02_P1_LETTER":  return _ws02_p1_letter()
    if image_id == "WS02_P2_BUILD":   return _ws02_p2_build()
    if image_id == "WS02_P3_READ":    return _ws02_p3_read()
    if image_id == "WS03_P1_SLIDE":   return _ws03_p1_slide()
    if image_id == "WS03_P2_MATCH":   return _ws03_p2_match()
    if image_id == "WS03_P3_NEW":     return _ws03_p3_new()
    if image_id == "WS04_P1_SENTENCE": return _ws04_p1_sentence()
    if image_id == "WS04_P2_MATCH":   return _ws04_p2_match()
    if image_id == "WS04_P3_FILL":    return _ws04_p3_fill()
    if image_id == "WS05_P1_HEAR":    return _ws05_p1_hear()
    if image_id == "WS05_P2_BLEND":   return _ws05_p2_blend()
    if image_id == "WS05_P3_READ":    return _ws05_p3_read()

    # Manipulatives
    if image_id == "M1_BOXES":        return _m1_boxes()
    if image_id == "M2_PICTURES":     return _m2_pictures()
    if image_id == "M3_LETTERS":      return _m3_letters()
    if image_id == "M4_STRIPS":       return _m4_strips()
    if image_id == "M5_CAPSTONE":     return _m5_capstone()
    if image_id == "M6_VOCAB":        return _m6_vocab()
    if image_id == "M7_POSTER":       return _m7_poster()

    # Formative
    if image_id == "FORM_Q1_SEGMENT": return _form_q1_segment()
    if image_id == "FORM_Q2_LETTER": return _form_q2_letter()

    # Assessment trackers
    if image_id == "AS_DIAG_TRACKER":
        return _diagnostic_tracker(
            "G1 CVC Decoders — Day 1 Diagnostic",
            ["Student name", "Names picture", "Segments 3 sounds", "Notes"],
        )
    if image_id == "AS_FORM_TRACKER_L2":
        return _diagnostic_tracker(
            "Lesson 2 Formative — Letter-Sound",
            ["Student name", "Letter→sound", "Builds word", "Notes"],
        )
    if image_id == "AS_FORM_TRACKER_L3":
        return _diagnostic_tracker(
            "Lesson 3 Formative — Blending",
            ["Student name", "Sounds each letter", "Slides smoothly", "Notes"],
        )
    if image_id == "AS_FORM_TRACKER_L4":
        return _diagnostic_tracker(
            "Lesson 4 Formative — Decoding",
            ["Student name", "Tracks word", "Decodes CVC", "Notes"],
        )

    # Certificate
    if image_id == "AS_CERT_BORDER":  return _cert_border()
    if image_id == "AS_CERT_SOUNDER": return _cert_sounder()

    return None
