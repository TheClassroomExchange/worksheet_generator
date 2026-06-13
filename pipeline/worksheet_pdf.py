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
  • branded footer: "N. Topic   ·   The Canadian Classroom Exchange   ·   page N"

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
    """Scratch-style stacked colour chips. Each block: {cat, label}."""
    title = part.get("title")
    head = f'<h3 class="part-title">{_esc(title)}</h3>' if title else ""
    chips = []
    for b in part.get("blocks", []):
        cat = b.get("cat", "value")
        color = BLOCK_COLORS.get(cat, BLOCK_COLORS["value"])
        indent = int(b.get("indent", 0))
        # Each block sits on its own row (vertical stack); the row's left
        # margin shows nesting (children indented under repeat/if).
        chips.append(
            f'<div class="sb-row" style="margin-left:{indent * 24}px">'
            f'<span class="sb-block" style="background:{color}">'
            f'{_esc(b.get("label", ""))}</span></div>'
        )
    note = part.get("note")
    note_html = f'<p class="block-note">{_esc(note)}</p>' if note else ""
    return (
        f'<section class="part blocks">{head}'
        f'<div class="sb-stack">{"".join(chips)}</div>{note_html}</section>'
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


def _render_image(part: dict) -> str:
    src = Path(part["src"]).resolve().as_uri()
    cap = part.get("caption", "")
    width = part.get("width", "60%")
    cap_html = f'<figcaption>{_esc(cap)}</figcaption>' if cap else ""
    return (
        f'<figure class="part image">'
        f'<img src="{src}" style="width:{_esc(width)}"/>{cap_html}</figure>'
    )


_PART_RENDERERS = {
    "prose": _render_prose,
    "blocks": _render_blocks,
    "code": _render_code,
    "exercise": _render_exercise,
    "image": _render_image,
}


# ── CSS (the house style) ───────────────────────────────────────────────────
def _css(spec: dict) -> str:
    footer_topic = _esc(spec.get("footer_topic", spec.get("title", "")))
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
        content: "The Canadian Classroom Exchange";
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
    color: {INK}; font-size: 11pt; line-height: 1.5; margin: 0;
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
.part {{ margin: 0 0 14px 0; }}
.part-title {{
    font-size: 12.5pt; color: {NAVY}; margin: 0 0 5px 0;
    border-left: 4px solid {MINT}; padding-left: 8px;
}}
.prose p {{ margin: 0 0 6px 0; }}

/* Scratch-style blocks — stacked vertically, children indented */
.sb-stack {{ margin: 4px 0; }}
.sb-row {{ margin: 0 0 4px 0; }}
.sb-block {{
    color: {PAPER}; font-weight: 600; font-size: 10.5pt;
    padding: 7px 14px; border-radius: 7px;
    display: inline-block;
    box-shadow: 0 1.5px 0 rgba(0,0,0,0.18);
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

/* figure */
figure.image {{ text-align: center; margin: 6px 0 14px 0; }}
figure.image img {{ border-radius: 10px; }}
figure.image figcaption {{ font-size: 9pt; color: {SLATE}; margin-top: 4px; }}
"""


# ── Document assembly ───────────────────────────────────────────────────────
def render_worksheet_html(spec: dict) -> str:
    mascot = Path(spec["mascot"]).resolve().as_uri()
    eyebrow = spec.get("eyebrow", "")
    subtitle = spec.get("subtitle", "")
    goal = spec.get("learning_goal")

    header = f"""
    <div class="header">
      <div class="mascot-circle"><img src="{mascot}"/></div>
      <div class="header-text">
        {f'<p class="eyebrow">{_esc(eyebrow)}</p>' if eyebrow else ''}
        <h1 class="title">{_esc(spec['title'])}</h1>
        {f'<p class="subtitle">{_esc(subtitle)}</p>' if subtitle else ''}
      </div>
    </div>
    """

    namebar = ""
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

    parts_html = []
    for part in spec.get("parts", []):
        renderer = _PART_RENDERERS.get(part.get("type"))
        if renderer:
            parts_html.append(renderer(part))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{_css(spec)}</style></head>
<body>{header}{namebar}{goal_html}{''.join(parts_html)}</body></html>"""


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
