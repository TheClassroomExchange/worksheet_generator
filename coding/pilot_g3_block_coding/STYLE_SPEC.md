# Style Spec — G3 · Block Coding batch

Every sheet in this batch conforms to this spec. It is the cross-sheet consistency
contract (drift guard #4 in `AUTONOMOUS_BUILD.md`). Sheet 1 ("Loops") is the reference.

## Voice & reading level
- Child voice, short declarative sentences; Grade-3 decodable vocabulary.
- Learning goal banner always starts **"I can …"**.
- One new idea per sheet; name it plainly ("A loop is a block that repeats").
- Open with a **real-world hook** (something in a kid's life that shows the concept).

## Worksheet structure (the repeatable shape)
1. **Prose intro** — real-world hook + plain definition of the new idea.
2. **Worked example** — a `blocks` (Scratch-style stacked chips) script the kids read,
   with a one-line note explaining what it does. Mascot **Bit** is the actor.
3. **Diagram** (when it helps) — an original SVG showing the outcome; Bit appears in it.
4. **Exercises**, easy → hard:
   - low-floor **read/count** task (every student can start),
   - an **alter + predict-then-check** task (C3.2; the C4 predict-then-run),
   - a **write-your-own** task (C3.1),
   - a **Challenge** stretch (the C3-L4 genuine challenge).
5. **Big idea** — one-line takeaway.

## Teacher guide (single page, concise)
Goal · Curriculum (cite the C3 codes **verbatim** from the cache) · Materials ·
Run it (≈4 steps, ~30 min) · Answer key (run-gate verified) · Watch for & differentiate
(support + extend) · Success looks like (1 line). Keep it to **one page**.

## Coding genre rules (Block Coding, G3)
- Blocks only — **no typed/Python syntax** (text code is the separate Intro-Python-Turtle subject).
- Concept ceiling: sequential + concurrent + **repeating (loops)**; conditionals are *preview* only.
- Block chips use the renderer's category colours (events/control/motion/looks…), children indented under `repeat`/`if`.
- Every code idea on the sheet is modelled + asserted in `solution.py` (the run-gate); the answer key comes from it.

## Brand & layout (the `worksheet_pdf.py` template)
- Palette: mint `#39C9A6` / navy `#102A43` / accent yellow `#FFC857` (anchored to Bit).
- Header band = mascot-in-circle (left) + centered eyebrow/title/subtitle.
- Footer = `N. Topic · The Classroom Exchange · page N`.
- Exercise/figure/code boxes never split across a page break (`break-inside: avoid`).

## Mascot rotation
- Cast not yet drawn (deferred to post-pilot). Until then, **Bit** is the actor on every sheet.
- When the cast lands: rotate the *framing* mascot per sheet via the clipart LRU, but keep one
  consistent "actor" per worked example so the metaphor stays clear.

## Published artifacts (per topic)
Exactly two: `<Title> — Worksheet.pdf` + `<Title> — Teacher Guide.pdf`. Solution code,
`solution_run.json`, grades stay internal — never uploaded.
