"""
worksheet_pdf.py — WeasyPrint HTML/CSS → branded PDF renderer for the
coding-worksheet pipeline.

One reusable page template in the source "house style":
  • header band: mascot-in-a-circle (left) + centered title/subtitle
  • optional "I can …" learning-goal banner
  • body = ordered parts, each one of:
        prose     — instructional paragraphs (str or list[str])
        blocks    — Scratch-style colour-chip pseudo-code (block coding)
        code      — monospace code block (Python / Turtle), optional output
        exercise  — numbered task box with ruled answer lines / grid
        image     — a rendered figure (PNG/SVG path) with a caption
  • branded footer: "N. Topic   ·   The Classroom Exchange   ·   page N"

This is the single biggest new piece of the pipeline and the thing the pilot
gates on first. Kept deliberately data-driven (a plain dict `spec`) so it can be
fed from the `Worksheet` Pydantic schema later without a rewrite.

Render note: WeasyPrint needs its native libs discoverable. On this machine run
the interpreter with `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib` (Homebrew libs).

Usage:
    from pipeline.worksheet_pdf import render_pdf, sample_spec
    render_pdf(sample_spec(), Path("/tmp/sample.pdf"))
"""

from __future__ import annotations

import html as _html
from pathlib import Path
from typing import Any

# ── Brand palette (anchored to the "Bit" mascot) ────────────────────────────
MINT = "#39C9A6"
MINT_DARK = "#2BB293"
MINT_TINT = "#E9FBF5"
NAVY = "#102A43"
INK = "#243B53"
SLATE = "#486581"
YELLOW = "#FFC857"
PAPER = "#FFFFFF"

# Scratch-style block category colours (original palette, evokes the genre
# without copying MIT's exact hex values).
BLOCK_COLORS = {
    "motion": "#4C8BF5",
    "looks": "#9B6CF0",
    "events": "#F2A23C",
    "control": "#F5A623",
    "sensing": "#2CA6C9",
    "operators": "#3FB66E",
    "value": "#5B7083",
}


def _esc(s: Any) -> str:
    return _html.escape(str(s))


# ── Part renderers ──────────────────────────────────────────────────────────
def _render_prose(part: dict) -> str:
    body = part.get("text", "")
    paras = body if isinstance(body, list) else [body]
    title = part.get("title")
    head = f'<h3 class="part-title">{_esc(title)}</h3>' if title else ""
    ps = "".join(f"<p>{_esc(p)}</p>" for p in paras)
    return f'<section class="part prose">{head}{ps}</section>'


def _render_blocks(part: dict) -> str:
    """Scratch-style stacked colour chips. Each block: {cat, label}.

    Optional part-level ``size`` ("md"|"lg") scales the whole stack up — used
    for K ScratchJr-style symbol-only blocks so a single arrow/flag glyph reads
    large. Default (unset) is unchanged, so every existing sheet is unaffected.
    A block with ``blank: true`` renders as a dashed empty block the child
    fills in (the "draw the missing block" answer slot).
    """
    title = part.get("title")
    head = f'<h3 class="part-title">{_esc(title)}</h3>' if title else ""
    size = part.get("size")
    stack_cls = "sb-stack" + ({"md": " sb-md", "lg": " sb-lg"}.get(size, ""))
    chips = []
    for b in part.get("blocks", []):
        cat = b.get("cat", "value")
        color = BLOCK_COLORS.get(cat, BLOCK_COLORS["value"])
        indent = int(b.get("indent", 0))
        # Each block sits on its own row (vertical stack); the row's left
        # margin shows nesting (children indented under repeat/if).
        if b.get("blank"):
            chip = '<span class="sb-block sb-blank"></span>'
        else:
            chip = (f'<span class="sb-block" style="background:{color}">'
                    f'{_esc(b.get("label", ""))}</span>')
        chips.append(
            f'<div class="sb-row" style="margin-left:{indent * 24}px">{chip}</div>'
        )
    note = part.get("note")
    note_html = f'<p class="block-note">{_esc(note)}</p>' if note else ""
    return (
        f'<section class="part blocks">{head}'
        f'<div class="{stack_cls}">{"".join(chips)}</div>{note_html}</section>'
    )


def _render_code(part: dict) -> str:
    title = part.get("title")
    lang = part.get("language", "python")
    head = f'<h3 class="part-title">{_esc(title)}</h3>' if title else ""
    code = _esc(part.get("code", ""))
    out = part.get("output")
    out_html = (
        f'<div class="code-output"><span class="out-label">Output</span>'
        f'<pre>{_esc(out)}</pre></div>'
        if out
        else ""
    )
    return (
        f'<section class="part code">{head}'
        f'<div class="code-block"><span class="lang-tag">{_esc(lang)}</span>'
        f'<pre>{code}</pre></div>{out_html}</section>'
    )


def _render_exercise(part: dict) -> str:
    num = part.get("number")
    badge = f'<span class="ex-badge">{_esc(num)}</span>' if num is not None else ""
    title = part.get("title", "Your turn")
    prompt = part.get("prompt", "")
    lines = int(part.get("answer_lines", 0))
    grid = part.get("grid")  # optional dict {rows, cols}
    body = ""
    if grid:
        rows, cols = int(grid.get("rows", 1)), int(grid.get("cols", 1))
        cells = "".join('<div class="grid-cell"></div>' for _ in range(rows * cols))
        body = (
            f'<div class="ex-grid" style="grid-template-columns:repeat({cols},1fr)">'
            f"{cells}</div>"
        )
    elif lines:
        body = '<div class="answer-lines">' + "".join(
            '<div class="rule"></div>' for _ in range(lines)
        ) + "</div>"
    return (
        f'<section class="part exercise"><div class="ex-head">{badge}'
        f'<h3 class="ex-title">{_esc(title)}</h3></div>'
        f'<p class="ex-prompt">{_esc(prompt)}</p>{body}</section>'
    )


def _render_symbols(part: dict) -> str:
    """A horizontal row of large symbol "cards" — the K visual primitive.

    Each item is either a string (the symbol) or a dict {sym, label, blank}.
    A symbol of "?" (or item with ``blank: true``) renders as a dashed
    answer card the child fills in. ``size`` ("md"|"lg"|"xl", default "lg")
    scales the glyph. Crisp geometric Unicode (★ ● ▲ ■ ◆ ➡ ⬆ ↻ …) renders
    reliably and large; this is what makes K sheets genuinely picture/symbol
    driven without per-sheet image assets. Optional ``note`` prints below.
    """
    title = part.get("title")
    head = f'<h3 class="part-title">{_esc(title)}</h3>' if title else ""
    size = part.get("size", "lg")
    size_cls = {"md": "sym-md", "lg": "sym-lg", "xl": "sym-xl"}.get(size, "sym-lg")
    cards = []
    for it in part.get("items", []):
        if isinstance(it, dict):
            sym = it.get("sym", "")
            label = it.get("label")
            blank = bool(it.get("blank")) or sym == "?"
        else:
            sym = it
            label = None
            blank = sym == "?"
        cls = "sym-card sym-blank" if blank else "sym-card"
        glyph = "" if blank else _esc(sym)
        cap = f'<span class="sym-cap">{_esc(label)}</span>' if label else ""
        cards.append(
            f'<div class="{cls}"><span class="sym {size_cls}">{glyph}</span>{cap}</div>'
        )
    note = part.get("note")
    note_html = f'<p class="block-note">{_esc(note)}</p>' if note else ""
    return (
        f'<section class="part symbols">{head}'
        f'<div class="sym-row">{"".join(cards)}</div>{note_html}</section>'
    )


def _render_image(part: dict) -> str:
    src = Path(part["src"]).resolve().as_uri()
    cap = part.get("caption", "")
    width = part.get("width", "60%")
    cap_html = f'<figcaption>{_esc(cap)}</figcaption>' if cap else ""
    return (
        f'<figure class="part image">'
        f'<img src="{src}" style="width:{_esc(width)}"/>{cap_html}</figure>'
    )


def _img_uri(src: str) -> str:
    return Path(src).resolve().as_uri()


def _bold_target(text: str, target: str) -> str:
    """Escape ``text`` then bold every case-insensitive occurrence of ``target``."""
    esc = _esc(text)
    if not target:
        return esc
    t = _esc(target)
    import re as _re
    return _re.sub("(" + _re.escape(t) + ")", r"<b>\1</b>", esc, flags=_re.IGNORECASE)


def _render_reading_rows(part: dict) -> str:
    """'I Can Read Sentences' body: a bordered 2-column table — big decodable
    sentence (target pattern bolded) on the left, a large picture on the right.
    Rows are tall so 5 fill the page (the "A Teachable Teacher" design)."""
    title = part.get("title")
    title_html = f'<h2 class="part-title">{_esc(title)}</h2>' if title else ""
    target = part.get("bold", part.get("target", ""))
    # reveal=="first": only the first row shows the underlined target (the worked
    # example); the rest render plain so the child finds the pattern. Default
    # (absent) underlines every row — used by reading-aid sheets (schwa/morphemes).
    reveal_first = part.get("reveal") == "first"
    size_cls = "rr-" + part.get("size", "lg")  # rr-lg (default) | rr-md
    part_rows = part.get("rows", [])
    has_pics = any(r.get("img") for r in part_rows)
    rows = []
    for i, r in enumerate(part_rows):
        row_target = "" if (reveal_first and i > 0) else r.get("bold", target)
        txt = _bold_target(r.get("text", ""), row_target)
        cells = f'<td class="rr-text">{txt}</td>'
        if has_pics:
            img = f'<img src="{_img_uri(r["img"])}"/>' if r.get("img") else ""
            cells += f'<td class="rr-pic">{img}</td>'
        rows.append(f'<tr>{cells}</tr>')
    return (f'<section class="part reading {size_cls}">{title_html}'
            f'<table class="rr-table">{"".join(rows)}</table></section>')


def _render_read_tracker(part: dict) -> str:
    label = part.get("label", "Read the page 3 times. Colour a face each time you read it.")
    count = int(part.get("count", 3))
    faces = "".join('<span class="rt-face">☺</span>' for _ in range(count))
    return (f'<section class="part tracker"><span class="rt-label">{_esc(label)}</span>'
            f'<span class="rt-faces">{faces}</span></section>')


def _render_sound_boxes(part: dict) -> str:
    """Word-mapping: each row = picture + N empty sound boxes (one per phoneme) +
    a write-the-word line. say-it -> map-it -> write-it."""
    title = part.get("title")
    title_html = f'<h2 class="part-title">{_esc(title)}</h2>' if title else ""
    rows = []
    for r in part.get("rows", []):
        img = (f'<span class="sbx-pic"><img src="{_img_uri(r["img"])}"/></span>'
               if r.get("img") else '<span class="sbx-pic"></span>')
        n = int(r.get("boxes", 3))
        boxes = "".join('<span class="sbx-box"></span>' for _ in range(n))
        write = '<span class="sbx-write"></span>'
        rows.append(f'<div class="sbx-row">{img}<span class="sbx-boxes">{boxes}</span>{write}</div>')
    return f'<section class="part soundboxes">{title_html}{"".join(rows)}</section>'


def _render_formation(part: dict) -> str:
    """Letter-formation card: big keyword picture + the letter pair, dotted trace
    copies, then blank handwriting lines (sky/grass/ground guide)."""
    title = part.get("title")
    title_html = f'<h2 class="part-title">{_esc(title)}</h2>' if title else ""
    letter = _esc(part.get("letter", ""))
    keyword = _esc(part.get("keyword", ""))
    img = (f'<img class="fm-pic" src="{_img_uri(part["img"])}"/>' if part.get("img") else "")
    trace = part.get("trace", (letter + " ") * 4).strip()
    n_lines = int(part.get("lines", 2))
    head = (f'<div class="fm-head"><span class="fm-letter">{letter}</span>'
            f'<span class="fm-key">{img}<span class="fm-keyword">{keyword}</span></span></div>')
    tracecells = f'<div class="fm-trace">{_esc(trace)}</div>'
    lines = "".join('<div class="fm-line"><span class="fm-sky"></span>'
                    '<span class="fm-grass"></span><span class="fm-ground"></span></div>'
                    for _ in range(n_lines))
    return f'<section class="part formation">{title_html}{head}{tracecells}{lines}</section>'


def _render_picture_row(part: dict) -> str:
    """K beginning-sound task: a prompt + a row of pictures, each with a circle to
    mark. Pictures whose word starts with the target sound are the answers (key in TG)."""
    title = part.get("title")
    title_html = f'<h2 class="part-title">{_esc(title)}</h2>' if title else ""
    prompt = f'<p class="pr-prompt">{_esc(part["prompt"])}</p>' if part.get("prompt") else ""
    cells = []
    for it in part.get("items", []):
        img = f'<img src="{_img_uri(it["img"])}"/>' if it.get("img") else ""
        cap = f'<span class="pr-cap">{_esc(it.get("label",""))}</span>' if it.get("label") else ""
        cells.append(f'<span class="pr-cell"><span class="pr-mark"></span>{img}{cap}</span>')
    return (f'<section class="part picturerow">{title_html}{prompt}'
            f'<div class="pr-row">{"".join(cells)}</div></section>')


_PART_RENDERERS = {
    "prose": _render_prose,
    "blocks": _render_blocks,
    "code": _render_code,
    "exercise": _render_exercise,
    "symbols": _render_symbols,
    "image": _render_image,
    # phonics/language part types (unused by coding sheets)
    "reading_rows": _render_reading_rows,
    "read_tracker": _render_read_tracker,
    "sound_boxes": _render_sound_boxes,
    "formation": _render_formation,
    "picture_row": _render_picture_row,
}


# ── CSS (the house style) ───────────────────────────────────────────────────
def _css_str(s: Any) -> str:
    """Escape a string for use inside a CSS ``content: "..."`` value. Unlike
    HTML escaping, CSS does NOT decode entities — so an apostrophe must stay a
    literal ' (html.escape would turn it into &#x27;, which then prints
    verbatim in the footer). Only backslash and double-quote need escaping."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def _roomy_css() -> str:
    """Size/spacing overrides for Kindergarten & Grade 1 worksheets.

    Appended AFTER the base house style so equal-specificity rules win by
    source order. Scales write-in slots, symbol/block primitives, the mascot,
    and the goal/name bars UP — bigger images and more writing room for young
    hands. Emitted only when ``spec['roomy']`` is set, so G2/G3 are untouched.
    Braces are single here (plain string, not an f-string).
    """
    return """
/* ── roomy mode (K & G1): bigger images + more writing room ── */
/* Keep each question on the same page as its stimulus: render_worksheet_html
   wraps an exercise together with the blocks/images/prose that set it up, and
   this stops that group splitting across a page break. */
.qgroup { break-inside: avoid; }
.part-title { font-size: 14.5pt; margin: 0 0 6px 0; }
.goal { font-size: 12.5pt; padding: 8px 14px; margin: 7px 0 11px 0; }
.namebar { font-size: 11pt; gap: 28px; margin-top: 5px; }
.subtitle { font-size: 11.5pt; }
/* header: keep a generous mascot but trim padding so the first question-group
   shares page 1 with the header rather than being pushed whole to page 2. */
.header { padding: 10px 16px; margin-bottom: 4px; }
.mascot-circle { width: 80px; height: 80px; }
.mascot-circle img { width: 70px; height: 70px; }
/* taller write-in slots */
.answer-lines { margin-top: 8px; }
.answer-lines .rule { height: 34px; }
.ex-grid { gap: 6px; margin-top: 8px; }
.ex-grid .grid-cell { height: 64px; }
/* A single-answer box (grid 1x1 — "Run Code A", "You try") becomes a large
   full-width write area. Multi-cell grids (write-the-order, maps) keep 64px. */
.ex-grid .grid-cell:only-child { height: 100px; }
.exercise { padding: 14px 18px; }
.ex-title { font-size: 14pt; }
.ex-prompt { margin: 0 0 8px 0; }
/* bigger symbol cards (the K/G1 picture primitive). min-width stays modest so
   a full 0-5 number path (6 cards) still fits one row — wrapping it would
   reorder the cards and read poorly. The glyph point-size is what makes them
   read large. */
.sym-row { gap: 12px; margin: 7px 0 2px 0; }
.sym-card { min-width: 64px; min-height: 72px; padding: 9px 12px; }
.sym-md { font-size: 30pt; }
.sym-lg { font-size: 42pt; }
.sym-xl { font-size: 54pt; }
.sym-cap { font-size: 11pt; margin-top: 7px; }
/* bigger block chips */
.sb-stack { margin: 5px 0; }
.sb-row { margin: 0 0 6px 0; }
.sb-block { font-size: 13pt; padding: 9px 18px; }
.sb-md .sb-block { font-size: 17pt; padding: 10px 20px; }
.sb-lg .sb-block { font-size: 22pt; padding: 12px 24px; min-width: 38px; }
.sb-md .sb-row, .sb-lg .sb-row { margin: 0 0 7px 0; }
.sb-block.sb-blank { min-width: 72px; min-height: 1.4em; }
.block-note { font-size: 11pt; }
"""


# Per-level main-CSS vars (body/line/spacing). Level 0 == the original roomy
# output (byte-identical). Higher levels compact progressively so a too-tall
# question-group fits its page and small trailing spills pull back — killing
# near-empty pages. Level 3 reuses level-2 sizes but disables question-grouping.
_ROOMY_LEVELS = {
    0: {"body": "13pt", "line": "1.55", "part_mb": "16px", "prose_mb": "9px"},
    1: {"body": "13pt", "line": "1.50", "part_mb": "13px", "prose_mb": "7px"},
    2: {"body": "12pt", "line": "1.45", "part_mb": "10px", "prose_mb": "6px"},
    3: {"body": "12pt", "line": "1.45", "part_mb": "10px", "prose_mb": "6px"},
}


def _roomy_overrides(level: int) -> str:
    """Append-only compaction deltas for roomy_level >= 1. Level 0 appends
    nothing, so level-0 output stays byte-identical to the original roomy CSS."""
    if level <= 0:
        return ""
    if level == 1:
        return """
/* roomy_level 1 — mild compaction so an over-tall first group fits its page */
.goal { margin: 6px 0 9px 0; }
.answer-lines .rule { height: 30px; }
.ex-grid .grid-cell { height: 58px; }
.ex-grid .grid-cell:only-child { height: 90px; }
.exercise { padding: 12px 16px; }
.sym-row { gap: 10px; margin: 6px 0 2px 0; }
.sym-card { min-height: 66px; padding: 8px 11px; }
.sb-row { margin: 0 0 5px 0; }
.sb-md .sb-row, .sb-lg .sb-row { margin: 0 0 6px 0; }
"""
    return """
/* roomy_level 2+ — stronger compaction to pull spilled content back on-page */
.part-title { font-size: 13.5pt; margin: 0 0 5px 0; }
.goal { font-size: 12pt; padding: 7px 12px; margin: 5px 0 8px 0; }
.answer-lines .rule { height: 28px; }
.ex-grid .grid-cell { height: 54px; }
.ex-grid .grid-cell:only-child { height: 80px; }
.exercise { padding: 11px 15px; }
.ex-title { font-size: 13pt; }
.sym-row { gap: 9px; margin: 5px 0 2px 0; }
.sym-card { min-width: 60px; min-height: 60px; padding: 7px 10px; }
.sym-md { font-size: 27pt; }
.sym-lg { font-size: 38pt; }
.sym-xl { font-size: 48pt; }
.sym-cap { font-size: 10pt; margin-top: 5px; }
.sb-stack { margin: 4px 0; }
.sb-row { margin: 0 0 4px 0; }
.sb-block { font-size: 12pt; padding: 7px 15px; }
.sb-md .sb-block { font-size: 15pt; padding: 8px 17px; }
.sb-lg .sb-block { font-size: 19pt; padding: 10px 20px; }
.sb-md .sb-row, .sb-lg .sb-row { margin: 0 0 5px 0; }
.mascot-circle { width: 74px; height: 74px; }
.mascot-circle img { width: 64px; height: 64px; }
"""


def _css(spec: dict) -> str:
    footer_topic = _css_str(spec.get("footer_topic", spec.get("title", "")))
    # Compact mode (used for teacher guides): tightens vertical rhythm so a
    # full guide — including the two verbatim C3 citations — reliably fits one
    # page without per-sheet hand-trimming.
    compact = bool(spec.get("compact"))
    # Roomy mode (used for Kindergarten & Grade 1 worksheets): scales fonts,
    # vertical rhythm, write-in slots, and visual primitives UP so young
    # learners get bigger images and far more room to write. Content is
    # untouched — only size/spacing changes. Never combined with compact
    # (compact is teacher-guides only); roomy is worksheet-only.
    roomy = bool(spec.get("roomy"))
    level = max(0, min(3, int(spec.get("roomy_level", 0)))) if roomy else 0
    if compact:
        body_pt, line_h, part_mb, prose_mb = "10.2pt", "1.30", "5px", "3px"
    elif roomy:
        lv = _ROOMY_LEVELS[level]
        body_pt, line_h, part_mb, prose_mb = lv["body"], lv["line"], lv["part_mb"], lv["prose_mb"]
    else:
        body_pt, line_h, part_mb, prose_mb = "11pt", "1.5", "14px", "6px"
    roomy_css = (_roomy_css() + _roomy_overrides(level)) if roomy else ""
    return f"""
@page {{
    size: Letter;
    margin: 14mm 15mm 18mm 15mm;
    @bottom-left {{
        content: "{footer_topic}";
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 8pt; color: {SLATE};
    }}
    @bottom-center {{
        content: "The Classroom Exchange";
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 8pt; color: {MINT_DARK}; font-weight: 600;
    }}
    @bottom-right {{
        content: "page " counter(page);
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 8pt; color: {SLATE};
    }}
}}
* {{ box-sizing: border-box; }}
body {{
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: {INK}; font-size: {body_pt}; line-height: {line_h}; margin: 0;
}}

/* ── header band ── */
.header {{
    display: flex; align-items: center; gap: 14px;
    background: {MINT_TINT};
    border: 2px solid {MINT};
    border-radius: 18px;
    padding: 12px 18px; margin-bottom: 6px;
}}
.mascot-circle {{
    flex: 0 0 auto; width: 74px; height: 74px; border-radius: 50%;
    background: {PAPER}; border: 3px solid {MINT};
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
}}
.mascot-circle img {{ width: 64px; height: 64px; }}
.header-text {{ flex: 1 1 auto; text-align: center; }}
.eyebrow {{
    font-size: 9pt; letter-spacing: 1.5px; text-transform: uppercase;
    color: {MINT_DARK}; font-weight: 700; margin: 0;
}}
h1.title {{
    font-size: 21pt; color: {NAVY}; margin: 2px 0 0 0; line-height: 1.15;
}}
.subtitle {{ font-size: 10.5pt; color: {SLATE}; margin: 3px 0 0 0; }}

/* name / date row */
.namebar {{
    display: flex; gap: 24px; font-size: 9.5pt; color: {SLATE};
    margin: 4px 2px 0 2px;
}}
.namebar .field {{ flex: 1; border-bottom: 1.5px dotted {SLATE}; padding-bottom: 2px; }}

/* "I can" goal banner */
.goal {{
    background: {NAVY}; color: {PAPER}; border-radius: 12px;
    padding: 8px 14px; margin: 10px 0 14px 0; font-size: 11pt; font-weight: 600;
}}
.goal .star {{ color: {YELLOW}; margin-right: 6px; }}

/* parts */
.part {{ margin: 0 0 {part_mb} 0; }}
/* keep self-contained boxes from splitting across a page break */
.exercise, figure.image, .code-block, .code-output, .sb-stack {{
    break-inside: avoid;
}}
.part-title {{
    font-size: 12.5pt; color: {NAVY}; margin: 0 0 5px 0;
    border-left: 4px solid {MINT}; padding-left: 8px;
}}
.prose p {{ margin: 0 0 {prose_mb} 0; }}

/* Scratch-style blocks — stacked vertically, children indented */
.sb-stack {{ margin: 4px 0; }}
.sb-row {{ margin: 0 0 4px 0; }}
.sb-block {{
    color: {PAPER}; font-weight: 600; font-size: 10.5pt;
    padding: 7px 14px; border-radius: 7px;
    display: inline-block;
    box-shadow: 0 1.5px 0 rgba(0,0,0,0.18);
}}
/* K size variants — scale the whole stack so a single symbol/arrow reads large */
.sb-md .sb-block {{ font-size: 15pt; padding: 9px 18px; border-radius: 8px; }}
.sb-lg .sb-block {{ font-size: 20pt; padding: 11px 22px; border-radius: 9px; min-width: 30px; text-align: center; }}
.sb-md .sb-row, .sb-lg .sb-row {{ margin: 0 0 6px 0; }}
.sb-block.sb-blank {{
    background: #FBFFFE; border: 2px dashed {SLATE}; box-shadow: none;
    display: inline-block; min-width: 54px; min-height: 1.2em;
}}
.block-note {{ font-size: 9.5pt; color: {SLATE}; font-style: italic; margin: 4px 0 0 0; }}

/* code block */
.code-block {{
    position: relative; background: {NAVY}; border-radius: 10px;
    padding: 12px 14px 12px 14px; margin: 4px 0;
}}
.code-block pre, .code-output pre {{
    font-family: 'SFMono-Regular', 'Menlo', 'Consolas', monospace;
    font-size: 10pt; color: #DCEAFB; margin: 0; white-space: pre-wrap;
    line-height: 1.45;
}}
.lang-tag {{
    position: absolute; top: 0; right: 0;
    background: {MINT}; color: {NAVY}; font-size: 8pt; font-weight: 700;
    padding: 2px 8px; border-radius: 0 10px 0 10px; text-transform: uppercase;
}}
.code-output {{ margin: 6px 0 0 0; }}
.code-output .out-label {{
    font-size: 8pt; font-weight: 700; color: {MINT_DARK};
    text-transform: uppercase; letter-spacing: 1px;
}}
.code-output pre {{
    background: {MINT_TINT}; color: {INK}; border-radius: 8px;
    padding: 8px 12px; margin-top: 3px; border: 1px solid {MINT};
}}

/* exercise box */
.exercise {{
    border: 2px solid {MINT}; border-radius: 14px; padding: 12px 16px;
    background: #FBFFFE;
}}
.ex-head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }}
.ex-badge {{
    flex: 0 0 auto; width: 26px; height: 26px; border-radius: 50%;
    background: {YELLOW}; color: {NAVY}; font-weight: 800; font-size: 12pt;
    display: flex; align-items: center; justify-content: center;
}}
.ex-title {{ font-size: 12.5pt; color: {NAVY}; margin: 0; }}
.ex-prompt {{ margin: 0 0 8px 0; }}
.answer-lines {{ margin-top: 6px; }}
.answer-lines .rule {{ border-bottom: 1.5px solid {SLATE}; height: 22px; }}
.ex-grid {{ display: grid; gap: 4px; margin-top: 6px; }}
.ex-grid .grid-cell {{
    border: 1.5px solid {SLATE}; border-radius: 6px; height: 40px; background: {PAPER};
}}

/* symbol cards (K visual primitive) */
.sym-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0 2px 0; }}
.symbols {{ break-inside: avoid; }}
.sym-card {{
    flex: 0 0 auto; min-width: 56px; min-height: 56px;
    border: 2px solid {MINT}; border-radius: 12px; background: {PAPER};
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 8px 12px;
}}
.sym-card.sym-blank {{ border-style: dashed; border-color: {SLATE}; background: #FBFFFE; }}
.sym {{ color: {NAVY}; line-height: 1; }}
.sym-md {{ font-size: 24pt; }}
.sym-lg {{ font-size: 34pt; }}
.sym-xl {{ font-size: 46pt; }}
.sym-blank .sym {{ min-width: 0.7em; }}
.sym-cap {{ font-size: 9pt; color: {SLATE}; margin-top: 5px; }}

/* figure */
figure.image {{ text-align: center; margin: 6px 0 14px 0; }}
figure.image img {{ border-radius: 10px; }}
figure.image figcaption {{ font-size: 9pt; color: {SLATE}; margin-top: 4px; }}

/* ── phonics / language: BIG kid-friendly design (A Teachable Teacher style) ── */
/* corner-tab header */
.ph-header {{ display: flex; align-items: stretch; gap: 16px; margin-bottom: 10px; }}
.ph-tab {{
    flex: 0 0 auto; width: 1.05in; min-height: 1.05in;
    background: {MINT}; color: {PAPER};
    border-radius: 14px 14px 60px 14px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 6px;
}}
.ph-tab-main {{ font-size: 27pt; font-weight: 800; line-height: 1.02; overflow-wrap: anywhere;
    max-width: 1.0in; text-align: center; }}
.ph-tab-sub {{ font-size: 10.5pt; font-weight: 600; margin-top: 2px; letter-spacing: 0.5px;
    overflow-wrap: anywhere; max-width: 1.0in; text-align: center; }}
.ph-titlewrap {{ flex: 1 1 auto; }}
.ph-name {{ font-size: 13pt; color: {SLATE}; margin: 4px 0 2px 0; }}
.ph-name-rule {{ display: inline-block; width: 62%; border-bottom: 2px dotted {SLATE};
    height: 1em; vertical-align: middle; }}
.ph-title {{ font-size: 38pt; font-weight: 800; color: {NAVY}; text-align: center;
    margin: 2px 0 0 0; line-height: 1.05; }}
.ph-subtitle {{ font-size: 14pt; color: {SLATE}; text-align: center; margin: 4px 0 0 0; }}

/* big reading table */
.part.reading {{ margin: 6px 0 10px 0; }}
.rr-table {{ width: 100%; border-collapse: collapse; }}
.rr-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
.rr-table td {{ border: 2.5px solid {NAVY}; vertical-align: middle; }}
.rr-text {{ padding: 10px 18px; color: {INK}; font-weight: 700; }}
.rr-text b {{ color: {NAVY}; text-decoration: underline; }}
.rr-pic {{ width: 1.45in; text-align: center; padding: 6px; }}
.rr-pic img {{ max-width: 1.25in; max-height: 1.05in; }}
.rr-lg .rr-text {{ font-size: 23pt; }}
.rr-md .rr-text {{ font-size: 18pt; padding: 9px 16px; }}

/* big read tracker */
.part.tracker {{ display: flex; align-items: center; gap: 18px; margin: 10px 0 6px 0;
    justify-content: center; }}
.rt-label {{ font-size: 12pt; color: {SLATE}; font-style: italic; }}
.rt-faces {{ display: flex; gap: 18px; }}
.rt-face {{ font-size: 40pt; color: {MINT_DARK}; line-height: 1; }}

/* sound boxes — big */
.part.soundboxes .sbx-row {{
    display: flex; align-items: center; gap: 18px; margin: 0 0 16px 0; break-inside: avoid;
}}
.sbx-pic {{ flex: 0 0 auto; width: 1.0in; height: 1.0in; display: flex;
    align-items: center; justify-content: center; }}
.sbx-pic img {{ max-width: 1.0in; max-height: 1.0in; }}
.sbx-boxes {{ display: flex; gap: 12px; }}
.sbx-box {{ width: 0.85in; height: 0.85in; border: 3px solid {SLATE}; border-radius: 10px; }}
.sbx-write {{ flex: 1 1 auto; min-width: 1.5in; border-bottom: 3px solid {SLATE};
    height: 0.7in; margin-left: 10px; }}

/* letter formation — big */
/* Serif the letter displays on letter-sound sheets so a capital I is legible
   (a sans capital I is a bare stroke → "Ii" misreads as "li"). Scoped to
   .lettersheet so reading-sentence tabs/titles keep the house sans. */
.lettersheet .ph-tab-main, .lettersheet .ph-title, .lettersheet .title,
.fm-letter, .fm-trace {{ font-family: Georgia, 'Times New Roman', 'DejaVu Serif', serif; }}
.part.formation .fm-head {{ display: flex; align-items: center; gap: 26px; margin: 2px 0 6px 0; }}
.fm-letter {{ font-size: 60pt; color: {NAVY}; line-height: 1; font-weight: 800; }}
.fm-key {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
.fm-pic {{ width: 1.0in; height: 1.0in; }}
.fm-keyword {{ font-size: 16pt; color: {SLATE}; }}
.fm-trace {{ font-size: 38pt; letter-spacing: 0.45em; color: #C2D0DE; white-space: nowrap;
    border-bottom: 2px dashed {SLATE}; padding-bottom: 5px; margin: 4px 0 10px 0; }}
.fm-line {{ position: relative; height: 0.55in; margin: 0 0 9px 0; }}
.fm-sky {{ display: block; height: 0.275in; border-bottom: 1.5px dashed #9FB3C8; }}
.fm-grass {{ display: block; height: 0.275in; border-bottom: 2.5px solid {SLATE}; }}
.fm-ground {{ display: none; }}

/* picture sort — big */
.part.picturerow .pr-prompt {{ font-size: 16pt; color: {INK}; font-weight: 600; margin: 0 0 12px 0; }}
.pr-row {{ display: block; text-align: center; }}
.pr-cell {{ display: inline-block; vertical-align: top; text-align: center;
    width: 1.18in; margin: 0 0.02in 12px 0.02in; }}
.pr-cell img {{ width: 1.0in; height: 1.0in; display: block; margin: 6px auto 0 auto; }}
.pr-mark {{ width: 0.32in; height: 0.32in; border: 2.5px solid {SLATE};
    border-radius: 50%; display: block; margin: 0 auto; }}
.pr-cap {{ font-size: 13pt; color: {SLATE}; display: block; margin-top: 5px; }}{roomy_css}
"""


# ── Document assembly ───────────────────────────────────────────────────────
def render_worksheet_html(spec: dict) -> str:
    eyebrow = spec.get("eyebrow", "")
    subtitle = spec.get("subtitle", "")
    goal = spec.get("learning_goal")

    # Mascot is optional: coding sheets pass an SVG; language sheets may omit it.
    mascot_html = ""
    if spec.get("mascot"):
        mascot = Path(spec["mascot"]).resolve().as_uri()
        mascot_html = f'<div class="mascot-circle"><img src="{mascot}"/></div>'

    # Two header styles. The corner-tab style (spec['tab']) follows the big,
    # kid-friendly "I Can Read Sentences" design — a coloured corner tab carrying
    # the target sound, a large centred title, a generous Name line, and big
    # directions. Used by phonics student worksheets. Otherwise the mint band.
    tab = spec.get("tab")
    namebar = ""
    if tab:
        tab_main = _esc(tab.get("main", ""))
        tab_sub = f'<span class="ph-tab-sub">{_esc(tab["sub"])}</span>' if tab.get("sub") else ""
        name_line = ('<div class="ph-name">Name: '
                     '<span class="ph-name-rule"></span></div>') if spec.get("name_date", True) else ""
        header = f"""
        <div class="ph-header">
          <div class="ph-tab"><span class="ph-tab-main">{tab_main}</span>{tab_sub}</div>
          <div class="ph-titlewrap">
            {name_line}
            <h1 class="ph-title">{_esc(spec['title'])}</h1>
            {f'<p class="ph-subtitle">{_esc(subtitle)}</p>' if subtitle else ''}
          </div>
        </div>
        """
    else:
        header = f"""
        <div class="header">
          {mascot_html}
          <div class="header-text">
            {f'<p class="eyebrow">{_esc(eyebrow)}</p>' if eyebrow else ''}
            <h1 class="title">{_esc(spec['title'])}</h1>
            {f'<p class="subtitle">{_esc(subtitle)}</p>' if subtitle else ''}
          </div>
        </div>
        """
        if spec.get("name_date", True):
            namebar = (
                '<div class="namebar"><div class="field">Name:</div>'
                '<div class="field">Date:</div></div>'
            )

    goal_html = (
        f'<div class="goal"><span class="star">★</span>{_esc(goal)}</div>'
        if goal
        else ""
    )

    parts = [p for p in spec.get("parts", []) if _PART_RENDERERS.get(p.get("type"))]

    # The qgroup (stimulus↔question no-break) pairing is coding-specific. Phonics
    # sheets have independent activities that should flow and break naturally, so
    # disable qgroup whenever any phonics part type is present (or a corner tab).
    _PHONICS_TYPES = {"reading_rows", "read_tracker", "sound_boxes", "formation", "picture_row"}
    is_phonics = bool(spec.get("tab")) or any(p.get("type") in _PHONICS_TYPES for p in parts)

    if spec.get("roomy") and int(spec.get("roomy_level", 0)) < 3 and not is_phonics:
        # Keep each question on the same page as its stimulus, WITHOUT forcing a
        # whole long activity onto one page (which would dump it to the next page
        # and leave a near-empty page). Each group is [stimulus parts + the FIRST
        # following exercise]; every additional consecutive exercise becomes its
        # own group. So the primary stimulus↔question pairing can't split, while
        # extra same-stimulus questions flow and only break when a page is full.
        # Each group is wrapped in a no-break .qgroup. Text order is unchanged →
        # the content-lock still passes.
        groups: list[list[dict]] = []
        cur: list[dict] = []
        cur_has_ex = False
        for part in parts:
            is_ex = part.get("type") == "exercise"
            if not is_ex:
                if cur and cur_has_ex:        # stimulus after a closed group → new group
                    groups.append(cur)
                    cur, cur_has_ex = [], False
                cur.append(part)
            else:
                if not cur_has_ex:            # first exercise joins its stimulus
                    cur.append(part)
                    cur_has_ex = True
                else:                          # subsequent exercise → its own group
                    groups.append(cur)
                    cur, cur_has_ex = [part], True
        if cur:
            groups.append(cur)
        body_parts = []
        for g in groups:
            inner = "".join(_PART_RENDERERS[p["type"]](p) for p in g)
            body_parts.append(f'<div class="qgroup">{inner}</div>')
        parts_html = "".join(body_parts)
    else:
        parts_html = "".join(_PART_RENDERERS[p["type"]](p) for p in parts)

    # Letter-sound sheets show the letter pair (e.g. "Ii") in the tab, title and big
    # glyph. In a sans font a capital I is a bare stroke indistinguishable from
    # lowercase l ("Ii" reads as "li"), so those sheets render the letter in a serif.
    body_cls = ' class="lettersheet"' if any(p.get("type") == "formation" for p in parts) else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{_css(spec)}</style></head>
<body{body_cls}>{header}{namebar}{goal_html}{parts_html}</body></html>"""


def render_pdf(spec: dict, out_path: Path) -> Path:
    """Render `spec` to a PDF at `out_path`. Returns the path."""
    from weasyprint import HTML  # imported lazily (needs native libs)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_worksheet_html(spec)
    HTML(string=html, base_url=str(Path.cwd())).write_pdf(str(out_path))
    return out_path


# ── Throwaway sample (P1 gate) ──────────────────────────────────────────────
def sample_spec() -> dict:
    """A representative Grade 3 · Block Coding sheet used ONLY to prove the
    template renders in the house style. Content is illustrative, not final."""
    mascot = str(Path(__file__).resolve().parent.parent / "assets" / "mascots" / "bit_wave.svg")
    return {
        "mascot": mascot,
        "eyebrow": "Grade 3 · Block Coding",
        "title": "Looping with Bit",
        "subtitle": "Ontario Math C3.1 — repeating events",
        "footer_topic": "3. Looping with Bit",
        "learning_goal": "I can use a repeat loop to make a sprite do the same thing many times.",
        "parts": [
            {
                "type": "prose",
                "title": "What is a loop?",
                "text": [
                    "When you want a sprite to do the same action again and again, you do not "
                    "have to add the same block many times. A loop block does the repeating for you.",
                    "Bit wants to take 4 steps forward. Watch how a repeat block makes that short.",
                ],
            },
            {
                "type": "blocks",
                "title": "Read this script",
                "blocks": [
                    {"cat": "events", "label": "when green flag clicked"},
                    {"cat": "control", "label": "repeat 4"},
                    {"cat": "motion", "label": "move 10 steps", "indent": 1},
                    {"cat": "motion", "label": "wait 1 second", "indent": 1},
                ],
                "note": "The two blocks inside repeat run 4 times before the script ends.",
            },
            {
                "type": "code",
                "title": "The same idea in Python Turtle",
                "language": "python",
                "code": "for step in range(4):\n    bit.forward(10)\n    bit.wait(1)",
                "output": "Bit moves forward 10, four times.",
            },
            {
                "type": "exercise",
                "number": 1,
                "title": "Predict",
                "prompt": "If you change repeat 4 to repeat 6, how many times does Bit move? Write your answer.",
                "answer_lines": 2,
            },
            {
                "type": "exercise",
                "number": 2,
                "title": "Draw the path",
                "prompt": "Colour one square for each step Bit takes with repeat 5.",
                "grid": {"rows": 1, "cols": 5},
            },
        ],
    }


if __name__ == "__main__":
    out = render_pdf(sample_spec(), Path("/tmp/coding_sample.pdf"))
    print(f"wrote {out}")
