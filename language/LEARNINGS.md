# Language Worksheet Pipeline — Learnings (built 2026-06-30 → 07-01)

Built the full **K–3 Ontario phonics worksheet catalogue** (112 sheets) by reusing the
coding worksheet pipeline. All 112 graded 20/20, published + verified on Drive. This
captures what worked, what bit us, and the design/decisions that are now locked.

## What we built
- **112 worksheets** (K 33 · G1 47 · G2 21 · G3 11), one combined PDF (student worksheet
  + plain-language teacher guide) per phonics target, following the TCDSB "Foundations of
  Language" scope & the "A Teachable Teacher" design, Ontario Strand B / Kindergarten A2.
- A **data-driven autonomous engine**: compact per-target `data.json` → `gen_content` →
  gated `build_unit` → `record_grade` → checkpoint. Runner is resumable.

## Design (LOCKED — see DESIGN_STANDARD.md)
1. **Big "I Can Read Sentences" template** beats a small/dense one for early readers:
   corner tab w/ target sound, huge bold sentences (~23pt), large pictures in a bordered
   column, big 3× read tracker. Approved only after 3 iterations (small → big → kawaii).
2. **Kawaii images, faces on ANIMALS/PEOPLE ONLY** — objects get cute rounded shapes, no
   face. User vetted raw images (not full PDFs) before locking — cheap way to pin style.
3. **Decorative rounded double border** (solid + dashed) per grade colour, applied in the
   margin band only so the content gate stays clean.
4. **Sample-first, iterate on images alone** — the user locked the template, then iterated
   only on image style. Generating *just images* (not full PDFs) to vet style saved cycles.

## Gates that earned their keep (the safety net)
The build auto-caught ~10 real errors; fix the DATA, re-run — never fight the gate:
- **Decodability run-gate** (`decodability.py`): a word is only allowed if it segments into
  graphemes taught ≤ this lesson (+ cumulative heart words). Caught `snake`/`cute` (magic-e
  too early), `bee`/`queen` (`ee` not taught), `boat`/`rain` (untaught vowel *team* even
  though the single letters were known), `laugh` (needs `augh`, not `gh`). The **vowel-team
  guard** (a single vowel followed by another vowel = untaught team) was the key insight.
- **Image-alignment gate**: every pictured word MUST appear in its sentence. Caught e_e
  sheet picturing dog/cat while text said "pets".
- **page-fill gate**: no near-empty page. Caught G3 word-building spilling to page 2 →
  capped word-building to 3 sentences.
- **content-preserving border gate** (pdftotext-identical + 0 inner-px): lets us stamp a
  decorative frame without touching content.
- **Always dry-run decodability + image-alignment BEFORE the expensive image build**
  (`dryrun.py`) — no key needed; fix data first.

## Gotchas / hard-won facts
- **macOS Python lacks root certs** → image/API fetch must use `curl` (or certifi ctx).
- **OpenRouter image model**: `google/gemini-2.5-flash-image` (preview id was retired).
  ~$0.09/image; ~450 images ≈ $41. A **per-KEY spend cap** (separate from account credit)
  returns HTTP 403 "Key limit exceeded" — raise it in the OpenRouter workspace.
- **AI images** arrive centered in a big white canvas → auto-trim white to fill the cell.
- **Background runs cap ~14 units** before stopping; runner is resumable (per-unit
  checkpoint in topics.json) — just re-run; it skips `built`.
- **Early digraphs are inventory-tight** (`qu`@25) — set data `order` to the band end so
  a fluency sheet can draw on the full cumulative inventory.
- **Pseudo-targets** (`a_e` magic-e, `i_open`, schwa, syllable types) aren't literal
  substrings → `target_optional` / pseudo detection skips the literal target-present check.
- **Corner tab overflows** on long labels (`contraction`) → short `tab_main` + CSS wrap.
- **Non-ASCII in tab_main** (`ə`) broke the filename → fall back to target for file names.
- **WeasyPrint flex containers don't page-break** → picture-sort used inline-block; the
  coding `qgroup` (stimulus↔question no-break) is wrong for phonics → disabled for our parts.
- **Give every reading row a picture, or none** — mixed empty picture cells look broken.
- **Drive creds** (`token.json`/`credentials.json`) are gitignored in the main clone — copy
  into a worktree; token auto-refreshes.

## Content-authoring pattern (the repeatable loop)
1. Get topics (`topics.json`) for a subject.
2. Author `data.json` — 5 decodable sentences per target, each with a concrete-noun picture
   that appears in the sentence; the target need not be the pictured word.
3. `python -m language.dryrun <subject>` → fix any decode/target/image flags (no key).
4. `python -m language.run_build <subject>` → gated build (resumable), spot-check 1 page.
5. Flip `topics.json` status → publish.

## Curriculum decisions
- Dropped 5 **open-syllable long-vowel** targets (idea/apron/oval/equal/unicorn): they don't
  make clean decodable K–G1 sheets. Documented for a future G2/G3 syllable unit (DEFERRED.md).
- 117 → **112** catalogue. Quality > exact count.

## Process learnings
- Reusing the coding pipeline (render, roomy fit, border, Drive publish, manifest) saved
  enormous effort — only ~5 new modules needed (decodability, rubric, images, build, gen).
- The human gate is best spent on **1–2 samples + the image style**, then let automated
  gates carry the rest — exactly the "validate samples then go autonomous" rule.
- Publish Drive first (idempotent, safe); hold the marketplace (prod DB) for explicit go
  + blast-radius protocol.

## Post-publish QA remediation (2026-07-01)
Live-catalogue review found what pre-publish gates missed — a second lesson in "the gate
you didn't write doesn't catch its bug":
- **Table row-splitting across a page** wasn't caught by any existing gate — `page-fill`
  only checks for near-empty pages, not a row sheared at a page boundary. `break-inside:avoid`
  needs to be on the actual `<tr>`, not just the outer `.qgroup`/`.symbols` wrapper classes
  that happened to cover the coding-sheet parts. New rule: any HTML `<table>` used for a
  repeating row layout needs its own explicit `tr { break-inside: avoid }` — don't assume a
  sibling component's page-break CSS covers it.
- **CVC/word-list content has no built-in "is this word appropriate for a kid" gate** —
  decodability only checks phonetic legality, not word content. A word can be perfectly
  decodable and still be a bad pick (kitchen knife, "fat"). No automated fix here; this is
  a genuine human-in-the-loop check, worth a periodic manual word-list skim per subject.
- **When swapping a decodable word, the replacement must be independently re-verified**
  against `phonics_scope.json`'s cumulative unlock order (or the heart-word list) for that
  lesson's exact `order` — don't assume a "simple" word decodes; a fresh adversarial pass
  caught that the first swap candidate (`"sat"`) worked but dropped the letter-F theme, and
  the fix was a K heart word (`"for"`) that was *already sitting in the same order-band*.
- **Regenerating `content.json` via `gen_content.generate()` can silently reintroduce schema
  drift** — a field added to the generator after a unit's original build (`target_optional`)
  gets stamped back in as an explicit `false` even though the original file never had the key.
  Harmless functionally (`.get(..., False)` downstream) but it fails a strict "diff is scoped
  to only the intended change" check. Fix: after any `generate()` call on an already-shipped
  unit, strip falsy default keys the pre-existing file didn't have before writing.
- **A fresh adversarial validator earns its keep even on "obviously fine" sample fixes** — it
  caught both of the above on the very first pass, neither of which surfaced during authoring.
