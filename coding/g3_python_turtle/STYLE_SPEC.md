# Style Spec — G3 · Intro Python Turtle batch

Inherits the base look from `../pilot_g3_block_coding/STYLE_SPEC.md`. Turtle-specific rules:

## Coding genre rules (Intro Python Turtle, G3)
- This is students' **first typed code**. Keep each typed line short; use a **copy-this** model.
- **Block→text bridge on every sheet** (the C3-L4 path): show the familiar Scratch `blocks` worked
  example first, then the **`code`** part with its Python Turtle equivalent. Same idea, typed.
- **Angles are GIVEN, never derived** (e.g. "a square turns 90", "a triangle turns 120"). Students
  type/change the numbers; they do not compute turn = 360 ÷ sides (that's beyond grade 3).
- Mascot **Bit** IS the turtle (the pen/sprite). Code uses `bit.forward(...)`, `bit.right(...)`.
- Loops appear from sheet 3 (`for step in range(n):`) so C1 reaches G3 repeating events.
- The run-gate (`solution.py`) **models** the turtle path (track x, y, heading from forward/left/right)
  and asserts the resulting figure/positions. No Tk/GUI — "executes clean" via the model.

## Worksheet shape (same skeleton as Block Coding)
intro (real-world hook + the typed idea) · **blocks worked example → its Python code** (the bridge) ·
diagram of what Bit draws · 4 exercises (read/count → alter+predict-then-run → write/complete a line →
challenge) · Big idea. Teacher guide 1 page (cite C3.1/C3.2 verbatim; answer key from the run-gate).

## Code formatting
Python in the `code` part (monospace). Keep to ≤4 short lines. Show output where deterministic
("Bit draws a square"). Indentation must be correct (the loop body indented under `for`).
