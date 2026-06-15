# Branding Plan — add "The Classroom Exchange" mark to every coding PDF

**Status: PENDING (not started).** A future-session runbook. Sample-first; do not roll out
without user approval. Companion to `LESSONS_LEARNED.md` and the `coding-worksheet-builder` skill.

## Goal
Add the green **chalkboard mascot + serif "The Classroom Exchange" wordmark** to the
**bottom-center footer** of every coding **Worksheet** and **Teacher Guide**, matching the brand
mark on the user's sample marketing PDFs (wordmark with the small mascot to its right). Size it to
sit inside the existing **18mm bottom margin** so it never blocks content; it appears on every page
of both documents.

## Source asset (confirmed)
`~/Desktop/TCE/TCE/public/Mascot with Transparent Background.png` — 1024×1035 transparent PNG of
the green chalkboard character (red frame, sneakers, maple leaves). **Verified identical** to the
image embedded in the user's sample PDF. Also used by the website header.
**Prep:** auto-trim transparent padding (PIL `getbbox`) + downscale to ~96px tall → save optimized
as **`assets/brand/tce_chalkboard.png`** (self-contained; keeps PDFs small).

## Where / how (renderer change)
The footer is built in `pipeline/worksheet_pdf.py::_css()` as CSS Paged-Media margin boxes:
`@bottom-left` = topic · `@bottom-center` = static text **"The Canadian Classroom Exchange"** ·
`@bottom-right` = "page N". Page = Letter, margins `14mm 15mm 18mm 15mm`. The footer is shared by
the Worksheet and Teacher Guide (only `footer_topic` and the `compact` body typography differ), so
one change covers both.

**Recommended:** replace the `@bottom-center` text with the logo + wordmark via a WeasyPrint
**running element**:
- Emit in the HTML body: `<div class="tce-brand"><span>The Classroom Exchange</span><img src="file://…/assets/brand/tce_chalkboard.png"/></div>`
- CSS: `.tce-brand { position: running(tcebrand); … }` and `@bottom-center { content: element(tcebrand); }`.
- Keep `@bottom-left` (topic) and `@bottom-right` (page N). Wordmark ~8.5pt **serif** dark-slate;
  mascot ~16px tall, vertically centered to the right of the text (mirrors the sample).
- **Fallback** if running elements misbehave in WeasyPrint 69: a `position: fixed` bottom strip
  pinned in the bottom margin (`bottom: ~6mm`, full width, centered) with the `@bottom-center` text
  removed. The sample render decides.

Reuse the existing `Path(...).resolve().as_uri()` asset-embedding idiom (header mascot,
`_render_image`). This is a single edit to `_css()` + a few lines in the HTML body builder — no
`content.json`, schema, or grade changes.

## Sample-first gate (REQUIRED)
Re-render **one** existing sheet so both PDFs pick up the new footer:
```
DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python -c "
from pathlib import Path; from pipeline import coding_build
coding_build.render_sheet(Path('coding/g2_block_concurrent/01_two_sprites_at_once'))"
```
`pdftoppm -png -r 110` every page of both PDFs, inspect (brand centered in the bottom margin,
~16px mascot + serif wordmark, no overlap with topic/page-number or body; PDF size stays small).
**Show the user both PDFs and STOP for approval.**

## Rollout (only after approval + the user sets a /goal)
Renderer-only change → every PDF just needs re-rendering from its existing `content.json` (no
re-grading). Per subject batch (12 of them):
- `coding_build.render_sheet(dir)` for each sheet (re-renders both PDFs),
- spot-check a couple of rendered pages per subject (footer-only change),
- ensure each `topics.json`'s statuses are `"built"`, then `drive_publish.publish_batch(<batch_dir>)`
  (idempotent — updates the 2 PDFs/topic in place; hygiene-checked),
- re-audit each Drive subject folder (N topic folders × 2 PDFs, 0 strays),
- checkpoint docs + commit/push per batch (additive cadence, same as the build).

## Open choice (settle at the sample)
Recommended to **replace** the old "The Canadian Classroom Exchange" footer text with the logo +
"The Classroom Exchange" wordmark (the brand and website use "The Classroom Exchange"; avoids two
brand lines). If preferred, the logo can instead go top-right of the header band — a one-line move.
