# Language Worksheet — LOCKED Design Standard (approved 2026-06-30)

Every K-3 language worksheet MUST follow these principles (approved from 4 samples).
The pipeline defaults produce them; the rubric C4 gate enforces them.

## Layout (big, "A Teachable Teacher" style)
- **Sentence sheets** ("I Can Read Sentences" / Word Building): use the **corner tab**
  header (`worksheet.tab = {main, sub}`) — coloured rounded tab with the target sound +
  position/label, big centred title, Name line, big directions.
- **Big bordered table** for sentences (`reading_rows`, size `lg`): sentence cell in
  **large bold font (~23pt)**, target pattern **bold + underlined**, large picture
  (~1.5in) in a bordered right column. 5 rows fill the page.
- **Read tracker**: 3 big mint smiley faces.
- **K Letter & Sound**: mint band header + mascot; big formation letter, dashed trace,
  writing line(s); big picture sort (`picture_row`, ~1in pics, colour-circle); big word
  cards (`symbols`). One full page.
- One worksheet page + one teacher-guide page (combined PDF). No near-empty pages
  (`page_fill_ok`). K/G1 roomy.

## Images (kawaii, AI line-art)
- Backend = AI (`phonics_images.resolve(word, "ai")`, OpenRouter gemini image model).
- **Kawaii / Hello-Kitty style**: cute, rounded, thick clean B&W outlines, coloring-book.
- **Faces ONLY on animals/people/creatures** (`_ANIMATE` set → happy face + big eyes).
  **Objects/food/nature get NO face** (rounded cute, no eyes).
- Auto-trimmed white margins so the subject fills its cell.
- Every pictured word must appear in the decodable text (drift gate).

## Branding & border
- Footer: "The Classroom Exchange" (mint). Decorative **rounded double border**
  (solid outer + dashed inner) in the per-grade colour
  (K #F4CCCC / G1 #C9DAF8 / G2 #FCE5CD / G3 #D9EAD3), content-preserving.

## Teacher guide
- Plain language (T1=L4, no jargon). What it teaches · how to lead · answer key ·
  verbatim Ontario B2/A2 link + "In plain terms:" · make-easier/harder · success indicator.

## Gates (all must pass per unit before advancing)
1. decodability_run.json passed (+ target present)
2. teacher_guide_rubric pass (T1=L4, T4=L4)
3. language_rubric total ≥19/20, C2≥L3, C3=L4, C5=L4, drift clean
4. fit_render page_fill_ok (no near-empty), grade border gate (pdftotext-identical + 0 inner px)
