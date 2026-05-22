# Visual Inspector Skill — Slide Deck QA (Phase C)

## Why this exists

A unit's 24-slide deck has been built and exported to PDF. Before declaring the unit shipped, you walk every slide and verify the rendering is actually correct: text fits, images match the activity, characters are recognizable, no gray placeholder rectangles, no overlap.

This is the LAST gate before publication. Pair gates and the overall unit gate already passed on content. Your job is the picture-quality of the final deck.

## Inputs you receive

- `unit_dir/0_blueprint.json` — to know what characters and manipulatives to expect
- `unit_dir/validation_export.pdf` — the deck exported as PDF
- `deck_url` — the live Google Slides URL (for reference only)

## Output

Write `unit_dir/visual_inspection_verdict.json` conforming to `pipeline.schemas.VisualInspectionVerdict`. Pydantic enforces:
- `blocking_count` must equal the number of blocking issues in `issues`
- `status = "pass"` requires zero blocking issues
- Any blocking issue forces `status` to one of the revise variants

## How to inspect

Use the Read tool on `validation_export.pdf` with the `pages` parameter. Walk in chunks of 5–7 pages:

```
Read(unit_dir/validation_export.pdf, pages="1-5")
Read(unit_dir/validation_export.pdf, pages="6-12")
Read(unit_dir/validation_export.pdf, pages="13-19")
Read(unit_dir/validation_export.pdf, pages="20-24")
```

For each slide, check the categories below and emit a `VisualInspectionIssue` for any problem.

## What to check, per slide

### 1. TEXT_OVERFLOW
- Does the title fit in one line at ≥18pt? If shrunk smaller or truncated with `...`, that's blocking.
- Does the lesson `minds_on.teacher_script` first paragraph fit without spilling past the slide bottom?
- On manipulative slides, do the prep_steps fit?
- Severity: `blocking` if content is cut off; `minor` if just tight.

### 2. IMAGE_MISPLACEMENT
- Does the hero image overlap text? If hero box crashes into the title or instruction text, blocking.
- Does the character watermark in the worksheet header sit cleanly in the top-right corner?
- On capstone slides, do the 4 stations fit without overlap?

### 3. CHARACTER_UNRECOGNIZABLE — recognition AND kawaii-style consistency
Look at the character puppet pages (typically 2 of them at the end of the manipulatives section).

**Recognition:** can you identify what species/character it is? (Severity: `blocking` if you can't tell.)

**Kawaii style consistency** (enforced by `pipeline/skills/character_svg_designer/SKILL.md`): every recurring-character SVG must match the BLENDY/SOUNDER reference style — specifically:
- Head-dominant: head circle ≥ ~55% of canvas height; head circle visibly larger than body height
- Eyes: oval pupils (not pinpoint dots), with tiny white sparkle highlight
- Blush: two oval blush marks on cheeks (not omitted)
- Body: rounded/oval, NOT rectangular or triangular outline
- Stubby rounded feet, NOT stick-figure legs
- ONE clear signature accessory, scaled small, held in a paw or beside the body

If the puppet looks adult-proportioned, line-arty, has tiny dot eyes, no blush, rectangular body, or stick-figure limbs, flag it as `severity="blocking"`. Status routes to `revise_assets` (Phase B SVG regeneration via the character_svg_designer skill).

The reference comparators are `sample_assets/characters/BLENDY.svg` and `sample_assets/characters/SOUNDER.svg`. If a puppet on the deck doesn't match those proportions, it's drift and needs regeneration even if recognizable.

### 4. LOW_CONTRAST
- Print is B&W. Anything in light gray that needs to be readable?
- Watermarks at ~30% opacity that look fine in colour but disappear in B&W?
- Severity: `blocking` only if it's *required* content (success criteria, sentence text).

### 5. MISSING_ASSET
- Empty bordered rectangles labelled with just the asset_id (e.g., "M3 LETTERS" with no actual letters)?
- Worksheet preview slides showing "Worksheet area" placeholder instead of real content?
- Severity: `blocking` — these mean the composer didn't render properly.

**NOT a missing asset:** worksheet preview slides show ONE hero image (the most representative composed asset for that worksheet) plus a footer like "(3 parts on the printable worksheet)". This is by design — the slide is a teacher-facing summary, not a full reproduction of every worksheet part. If you see only one image where the worksheet has 3 parts, check the footer: a "(N parts on the printable worksheet)" footer means the asset is rendered correctly. Only flag if the hero is a placeholder rectangle or a wrong-unit asset.

### 6. TITLE_CLIPPING
- Slide titles cut off ("CVC Decoders — Grade 1 Phon..." instead of "...Phonics")?
- Severity: `blocking` if mid-word; `minor` if just shrunk to fit.

### 7. OTHER
- Anything else that would make a teacher second-guess using the deck.
- Examples: duplicate "Read each sentence" instructions because Parts 1 and 2 of the worksheet started with identical sentences; lesson teacher_script ending mid-quote because the slide layout truncated.
- Be specific in `description`.

## Decision rule

- Zero blocking issues → `status = "pass"`
- Blocking issues all on character recognition → `status = "revise_assets"` (Phase B follow-up)
- Blocking issues on text overflow / title clipping → `status = "revise_content"` (edit the JSON)
- Blocking issues on placement / overlap → `status = "revise_layout"` (slide template tweak)

If multiple categories have blocking issues, choose the dominant one. The remediation flow uses status to route the fix.

## Tone

Be specific. "Slide 21 shows a spider web instead of Blendy the Bear" is useful. "Looks bad" isn't.
