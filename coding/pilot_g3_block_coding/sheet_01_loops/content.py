"""
content.py — Grade 3 · Block Coding · Sheet 1 "Loops: Code That Repeats".

Authors the two PUBLISHED artifacts (student worksheet + teacher guide) as
data-driven specs and renders them via pipeline.worksheet_pdf. Original,
Ontario-aligned content (no source/MIT material reused). Answer key is the one
proved correct by solution.py (the code-runs gate).

Run:  DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib \
      ./venv/bin/python coding/pilot_g3_block_coding/sheet_01_loops/content.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pipeline.worksheet_pdf import render_pdf  # noqa: E402

HERE = Path(__file__).resolve().parent
MASCOT = str(ROOT / "assets" / "mascots" / "bit_wave.svg")
SQUARE = str(HERE / "square_path.svg")

# Verbatim Ontario Math (2020), Strand C3, Grade 3 (from curriculum cache).
C31 = ("solve problems and create computational representations of mathematical "
       "situations by writing and executing code, including code that involves "
       "sequential, concurrent, and repeating events")
C32 = ("read and alter existing code, including code that involves sequential, "
       "concurrent, and repeating events, and describe how changes to the code "
       "affect the outcomes")


def worksheet_spec() -> dict:
    return {
        "mascot": MASCOT,
        "eyebrow": "Grade 3 · Block Coding",
        "title": "Loops: Code That Repeats",
        "subtitle": "Ontario Math C3.1 — repeating events",
        "footer_topic": "1. Loops: Code That Repeats",
        "learning_goal": "I can write and change a repeat loop to make a sprite repeat actions.",
        "parts": [
            {
                "type": "prose",
                "title": "What is a loop?",
                "text": [
                    "Sometimes you want your sprite to do the same thing again and again. "
                    "You could drag the same block many times — but that makes a long, messy script.",
                    "A repeat loop is a block that does the repeating for you. You put the actions "
                    "inside it once, and tell it how many times to run them. Bit will show you how.",
                ],
            },
            {
                "type": "blocks",
                "title": "Worked example — read this script",
                "blocks": [
                    {"cat": "events", "label": "when green flag clicked"},
                    {"cat": "control", "label": "repeat 4"},
                    {"cat": "motion", "label": "move 10 steps", "indent": 1},
                    {"cat": "motion", "label": "turn 90 degrees", "indent": 1},
                ],
                "note": "The two blocks inside repeat run 4 times. Move, turn — four times — "
                        "draws a square and brings Bit back to the start.",
            },
            {
                "type": "image",
                "src": SQUARE,
                "caption": "Bit draws a square: move 10, turn 90, four times.",
                "width": "52%",
            },
            {
                "type": "code",
                "title": "The same idea in Python",
                "language": "python",
                "code": "for side in range(4):\n    bit.forward(10)\n    bit.right(90)",
                "output": "Bit draws a square — 4 sides, back to the start.",
            },
            {
                "type": "exercise",
                "number": 1,
                "title": "Finish the loop (write)",
                "prompt": "Make Bit draw a TRIANGLE (3 sides). Fill in the two missing numbers: "
                          "repeat ___ , and turn ___ degrees. (Hint: a triangle's turns add up to 360.)",
                "answer_lines": 2,
            },
            {
                "type": "exercise",
                "number": 2,
                "title": "Change it, then predict (read & alter)",
                "prompt": "Anya changes repeat 4 to repeat 6, and turn 90 to turn 60. "
                          "What shape does Bit draw now, and how many sides does it have? "
                          "Write your answer and explain how you know.",
                "answer_lines": 3,
            },
            {
                "type": "exercise",
                "number": 3,
                "title": "Predict, then check",
                "prompt": "This loop has TWO move blocks inside it:  repeat 3 { move 20 steps, move 20 steps }. "
                          "How many steps does Bit move in total? Predict first, then run it to check.",
                "answer_lines": 2,
            },
        ],
    }


def teacher_guide_spec() -> dict:
    return {
        "mascot": MASCOT,
        "eyebrow": "Teacher Guide · Grade 3 · Block Coding",
        "title": "Loops: Code That Repeats",
        "subtitle": "Facilitation notes, answer key & differentiation",
        "footer_topic": "1. Loops — Teacher Guide",
        "name_date": False,
        "parts": [
            {
                "type": "prose",
                "title": "Learning objective",
                "text": "Students write and alter a repeat (count-controlled) loop in a block "
                        "environment to make a sprite repeat a move/turn action, and describe how "
                        "changing the repeat count or turn angle changes the figure Bit draws. "
                        "This is students' first formal work with repeating events in Grade 3.",
            },
            {
                "type": "prose",
                "title": "Ontario curriculum (Math 2020, Strand C3 — Coding)",
                "text": [
                    f"C3.1 — {C31}.",
                    f"C3.2 — {C32}.",
                    "This sheet exercises C3.1 (writing a repeat loop in Exercise 1) and C3.2 "
                    "(altering an existing loop and describing the effect in Exercise 2).",
                ],
            },
            {
                "type": "prose",
                "title": "Materials & setup",
                "text": [
                    "• A block-coding environment (Scratch-style) projected for the worked example.",
                    "• Printed worksheet, one per student. Pencils; optional crayons for the path diagram.",
                    "• Optional: a device per pair so students can run Exercise 3 to check their prediction.",
                ],
            },
            {
                "type": "prose",
                "title": "How to run the lesson (≈40 min)",
                "text": [
                    "1. Hook (5 min): Ask students to clap 4 times. Then say 'repeat 4: clap.' Same result, "
                    "fewer instructions — that is a loop.",
                    "2. Worked example (10 min): Project the repeat-4 square script. Trace it together: count "
                    "the runs aloud, point to the move and turn each time, watch the square close.",
                    "3. Bridge (5 min): Show the Python version side-by-side. Same idea, typed instead of dragged.",
                    "4. Guided → independent (15 min): Students do Exercises 1–3. Circulate; ask 'how many "
                    "times will the inside run?' to surface misconceptions.",
                    "5. Consolidate (5 min): Share Exercise 2 answers. Land the big idea: more repeats = more "
                    "sides; the turn angle decides the shape.",
                ],
            },
            {
                "type": "code",
                "title": "Answer key (all verified by the run-gate)",
                "language": "text",
                "code": "Ex 1 (write):   repeat 3 , turn 120  →  triangle (3 sides; 3 × 120 = 360)\n"
                        "Ex 2 (alter):   hexagon, 6 sides  →  6 repeats make 6 sides; turn 60 closes the shape\n"
                        "Ex 3 (predict): 120 steps  →  3 repeats × (20 + 20) = 6 moves × 20 = 120",
            },
            {
                "type": "prose",
                "title": "Common errors to watch for",
                "text": [
                    "• Counting the blocks once instead of once-per-repeat (Ex 3: forgetting to multiply by 3).",
                    "• Confusing repeat count with turn angle — changing repeats changes the number of sides, "
                    "not the angle.",
                    "• In Ex 1, picking a turn that doesn't divide 360 (e.g. turn 100) so the shape never closes.",
                ],
            },
            {
                "type": "prose",
                "title": "Differentiation",
                "text": [
                    "• Simplify: give Exercise 1 with the turn (120) filled in, so students supply only the "
                    "repeat count.",
                    "• Extend: ask students to write a loop that draws any regular shape — they choose the number "
                    "of sides and work out turn = 360 ÷ sides (a second loop / a 2nd parameter).",
                ],
            },
            {
                "type": "prose",
                "title": "Success indicator",
                "text": "A student meets the goal when they can both WRITE a repeat loop that draws a named "
                        "shape (Ex 1) and EXPLAIN how changing the repeat count changes the figure (Ex 2) — "
                        "the C3.1 + C3.2 pairing.",
            },
        ],
    }


if __name__ == "__main__":
    ws = render_pdf(worksheet_spec(), HERE / "Loops — Worksheet.pdf")
    tg = render_pdf(teacher_guide_spec(), HERE / "Loops — Teacher Guide.pdf")
    print(f"wrote {ws}")
    print(f"wrote {tg}")
