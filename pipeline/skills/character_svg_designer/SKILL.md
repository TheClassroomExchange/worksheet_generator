# Character SVG Designer Skill — Kawaii Style (Phase B)

## Why this exists

Every unit ships a 24-slide deck with character puppets. If the puppet style drifts from the reference (Sanrio/Hello-Kitty kawaii — round head dominant, big sparkle eyes, blush, signature accessory), the deck looks inconsistent across units even when each unit is fine on its own. This skill fixes the style at one canonical reference and enforces it for every new character.

**Reference characters (gold standard):**
- `sample_assets/characters/SOUNDER.svg` — round body, no extremities, simple
- `sample_assets/characters/BLENDY.svg` — bear with paws, signature blending strip

When you author a new character, **start by reading BLENDY.svg** and copying the eye/blush/snout/body geometry verbatim. Replace only the species-specific parts (ears, tail, signature accessory).

## When to use

- Adding a new recurring character to a blueprint (`recurring_characters[].name`)
- Replacing a non-kawaii legacy SVG (e.g. line-art puppet from a pre-kawaii batch)
- Visual_inspector flagged `character_unrecognizable` OR the new "kawaii style consistency" check

## Inputs you receive

- The character's name and species (e.g., "Detective Dot the Squirrel")
- The character's signature accessory (e.g., "magnifying glass + clipboard")
- Optional: existing legacy SVG to replace

## Output

A single SVG file at `sample_assets/characters/<NAME>.svg` (UPPERCASE first word of character name). The file must be black-line on white — no color. Used B&W on classroom prints.

## Hard rules — every kawaii character MUST satisfy these

These are the rules the visual_inspector now enforces. A character that violates any of them fails `character_unrecognizable` even if recognizable.

### 1. Canvas + proportions
- viewBox `0 0 512 512`
- Head circle: `cx=256, cy≈200, r=135` (pure white fill, black stroke 5px). **Head occupies ~55% of canvas height — head-dominant.**
- Body: rounded path from y≈310 to y≈432, width ~150px. NEVER rectangular or triangular outline.
- Body height ≤ head height (kawaii: head is bigger than body).

### 2. Eyes (kawaii signature)
- Two oval pupils: `rx=9 ry=13` filled black, at approximately `(212, 190)` and `(300, 190)`.
- Each pupil has a small white sparkle highlight: `r=3.5` at upper-right of pupil (e.g., `(215, 184)`).
- NEVER use stick-figure dot eyes (`r ≤ 4`) or tiny ovals.

### 3. Snout / nose / mouth
- Snout patch: `ellipse cx=256 cy=240 rx=58 ry=46` white fill, thin stroke 2.5px.
- Triangular nose: black filled triangle at top of snout, ~10px wide × 12px tall.
- Mouth: short vertical stroke from nose, optional tiny smile arc — NEVER a wide grin or visible teeth (except for species-specific traits like squirrel front teeth, kept tiny: 4.5×10px).

### 4. Blush
- Two oval blush marks on cheeks: `rx=16, ry=9`, no fill, stroke 2px, at approximately `(155, 240)` and `(357, 240)`.
- Inside each blush oval: 2 short crossing lines (2 strokes wide × 4 strokes tall) for a "stitched-blush" look.
- BLUSH IS REQUIRED. Without it, characters look generic, not kawaii.

### 5. Body + paws + feet
- Body path: soft rounded shoulders → narrows toward feet. Use `Q` curves, not straight `L` lines for sides.
- Belly patch: white ellipse `rx=54 ry=42` centered.
- Two paws as small circles `r=22` at the body sides (one paw can hold the signature accessory).
- Two stubby feet at the bottom: ovals `rx=30 ry=14` with a tiny inner circle (toe hint).

### 6. Species traits
Add ONE concise visual mark per species. Examples:
- Bear (BLENDY): two big round ears with inner-ear circles
- Bunny (SOUNDER): two long oval ears at top of head
- Squirrel (DOT): tufted ears + bushy curling tail on right side + 2 front teeth
- Cat (TALLY): triangle ears + 3 short whiskers per side + curled tail

Species traits NEVER replace the head circle — they sit on TOP of it (ears) or BESIDE the body (tail).

### 7. Signature accessory
ONE clear iconic prop, head-balanced, rendered with:
- Stroke width 3–4px (not 1px hairlines)
- Total accessory bounding box ≤ 30% of canvas height
- Held in a paw OR positioned next to body (never floating randomly)

Examples of head-balanced accessories:
- BLENDY: c-a-t blending strip in left paw at body height
- DOT: magnifying glass next to left paw + bushy tail (the tail IS the secondary accessory)
- TALLY: tally mini-clipboard next to left paw

### 8. Stroke + fill discipline
- Outer outline strokes: 4–5px black
- Inner detail strokes: 2–2.5px black
- NEVER use color fills (B&W classroom print constraint)
- White fill on every shape so overlapping shapes look clean
- All `stroke-linejoin="round"` for organic shapes, default for technical accessories

## What gets caught if you skip these rules

If you produce a stick-figure-proportion character (small head, dominant rectangular body, dot eyes, no blush), the visual_inspector now treats it as a `character_unrecognizable` blocking issue with `severity="blocking"`. This forces a Phase B regeneration before the unit can ship.

## Authoring workflow

1. Open `sample_assets/characters/BLENDY.svg` and read it top-to-bottom.
2. Copy verbatim the eye + blush + snout + body + foot blocks (rules 2, 3, 4, 5).
3. Replace ONLY the ears (rule 6) and the signature accessory (rule 7).
4. Render with `rsvg-convert -w 320 <file.svg> -o /tmp/check.png` and visually compare to BLENDY.png. The proportions should look identical except for ears + accessory.
5. If the new SVG looks adult-proportioned, line-arty, or stick-figure-like, restart from step 1.

## Tone

You are a careful illustrator preserving an existing brand. Don't innovate. Don't add color. Don't make the character look cooler. Make it look identical to BLENDY except for the species/accessory swap.
