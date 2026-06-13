"""
content.py — Grade 3 · Block Coding · Sheet 1 "Loops: Code That Repeats".

Authors the two PUBLISHED artifacts (student worksheet + teacher guide) as
data-driven specs and renders them via pipeline.worksheet_pdf. Original,
Ontario-aligned content. The Grade-3 focus is the REPEAT COUNT (count it,
change it, write it) — not angle geometry. Answer key proved by solution.py.

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
        "learning_goal": "I can use a repeat loop to make Bit do something many times.",
        "parts": [
            {
                "type": "prose",
                "title": "What is a loop?",
                "text": [
                    "A loop is a block that repeats. You put the actions inside it one time. "
                    "The loop runs them again and again for you.",
                    "So you do not have to add the same block over and over. Bit will show you how.",
                ],
            },
            {
                "type": "blocks",
                "title": "Look at this loop",
                "blocks": [
                    {"cat": "events", "label": "when green flag clicked"},
                    {"cat": "control", "label": "repeat 4"},
                    {"cat": "motion", "label": "move 10 steps", "indent": 1},
                    {"cat": "motion", "label": "turn 90 degrees", "indent": 1},
                ],
                "note": "The 2 blocks inside repeat run 4 times. Bit moves and turns, 4 times. "
                        "That draws a square.",
            },
            {
                "type": "image",
                "src": SQUARE,
                "caption": "Bit repeats move and turn 4 times — and draws a square.",
                "width": "50%",
            },
            {
                "type": "exercise",
                "number": 1,
                "title": "Count it",
                "prompt": "Look at the loop above. It says repeat 4. "
                          "How many times does Bit MOVE? ______   How many times does Bit TURN? ______",
                "answer_lines": 1,
            },
            {
                "type": "exercise",
                "number": 2,
                "title": "Change the number",
                "prompt": "Now change repeat 4 to repeat 6. Bit runs the inside blocks 6 times. "
                          "How many times does Bit move now? Is that MORE or FEWER than before?",
                "answer_lines": 2,
            },
            {
                "type": "exercise",
                "number": 3,
                "title": "Write your own",
                "prompt": "Bit wants to JUMP 5 times. Write the number in the repeat block "
                          "so the loop runs 5 times:   repeat ______ → jump",
                "answer_lines": 1,
            },
            {
                "type": "prose",
                "title": "Big idea",
                "text": "The number in the repeat block tells Bit how many times to run the blocks "
                        "inside. A bigger number means more repeats.",
            },
        ],
    }


def teacher_guide_spec() -> dict:
    return {
        "mascot": MASCOT,
        "eyebrow": "Teacher Guide · Grade 3 · Block Coding",
        "title": "Loops: Code That Repeats",
        "subtitle": "Quick facilitation notes & answer key",
        "footer_topic": "1. Loops — Teacher Guide",
        "name_date": False,
        "parts": [
            {
                "type": "prose",
                "title": "Goal",
                "text": "Students learn that a repeat loop runs the blocks inside it a set number "
                        "of times. They count the repeats, change the number, and write their own.",
            },
            {
                "type": "prose",
                "title": "Curriculum (Ontario Math 2020, Strand C3)",
                "text": [
                    f"C3.1 — {C31}.",
                    f"C3.2 — {C32}.",
                ],
            },
            {
                "type": "prose",
                "title": "Materials",
                "text": "A block-coding app (Scratch-style) to project for the worked example; "
                        "the printed worksheet and a pencil per student.",
            },
            {
                "type": "prose",
                "title": "Run it (about 30 min)",
                "text": [
                    "1. Hook: have the class clap 4 times. Say it as a loop — \"repeat 4: clap.\"",
                    "2. Show the repeat-4 square loop. Count the runs out loud together.",
                    "3. Students do Exercises 1–3 on their own or in pairs.",
                    "4. Share answers. Land the big idea: the repeat number = how many times.",
                ],
            },
            {
                "type": "prose",
                "title": "Answer key (checked by the run-gate)",
                "text": [
                    "Ex 1 — Bit moves 4 times and turns 4 times.",
                    "Ex 2 — Bit moves 6 times. That is MORE than before.",
                    "Ex 3 — repeat 5.",
                ],
            },
            {
                "type": "prose",
                "title": "Watch for & differentiate",
                "text": [
                    "Common slip: counting the blocks once instead of once per repeat.",
                    "Support: read \"repeat 6\" as \"do it 6 times\" and tap each run on fingers.",
                    "Extend: ask how many TOTAL moves if the loop had 2 move blocks and repeat 3.",
                ],
            },
        ],
    }


if __name__ == "__main__":
    ws = render_pdf(worksheet_spec(), HERE / "Loops — Worksheet.pdf")
    tg = render_pdf(teacher_guide_spec(), HERE / "Loops — Teacher Guide.pdf")
    print(f"wrote {ws}")
    print(f"wrote {tg}")
