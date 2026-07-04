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

## 2026-07-02 — Give-away underline fix (reveal:first)

- **Bug:** "I Can Read Sentences" pre-underlined the target grapheme in EVERY sentence
  (`_bold_target` in `pipeline/worksheet_pdf.py` used `re.sub` with no `count`, and
  `_render_reading_rows` ran it on every row; CSS `.rr-text b {text-decoration:underline}`).
  The student instruction ("underline/circle the X in each sentence") was already done for them.
- **Fix (opt-in, no regen):** per-part flag `"reveal":"first"` → underline the FIRST sentence only
  (worked example); rows 2..N render plain. Default (flag absent) keeps full-underline so
  reading-AID sheets (schwa "the bold word…", G3 morphemes) are untouched. `gen_content.py` now
  sets the flag for find-task sheets so a future rebuild stays correct.
- **Scope:** 72/112 units impacted (64%). 12 reading-aid units deliberately excluded. Set derived
  deterministically by `language/reveal_fix.py sweep` (find-task prose AND >1 underlined row).
- **No image spend:** re-rendered via `language_build.build_unit` directly (NOT `run_build`, which
  re-runs `gen_content` and could re-author). `materialize()` only fetches when a row's `img` is
  missing — all rows already had `img`, so cached assets were reused. 0 OpenRouter calls.
- **Gates (per unit, in `reveal_fix.py`):** HTML-structural (row0 has `<b>`, rows>0 none) +
  text-identity (`layout_rubric.content_unchanged`, all 72 EXACT — no reflow) + page-count +
  visual-locality (changes only in the left text column, never header/footer/image column) +
  the build's own decodability + border gates. 72/72 passed.
- **GOTCHA — buffered stdout hides truncation:** the bulk publish `python -c` (no `-u`) block-buffered
  its stdout to the background task file; the capture cut off mid-last-unit. The process reported
  exit 0 but the FINAL unit (`k_digraphs/09_wh-white`) had not been re-uploaded. The **live-Drive
  modifiedTime audit** (via `pipeline.slides.get_credentials`, not the expired claude.ai MCP token)
  caught the one stale file — trust the datastore audit, not stdout, for "did it publish."
  Use `python -u` for long publish runs.
- Fresh adversarial validator independently re-derived the exact 72-set and scored 5/5.

## 2026-07-02 — Repeated-example fix (distinct word+image per sentence)

- **Problem:** 52 of 88 reading worksheets repeated the same target word/image across
  sentences (au-pause: sauce×3/astronaut×2; gh-ghost: ghost×5) — child answers the same
  thing repeatedly. Fixed so each sheet shows distinct examples.
- **Scope:** 50 sentence-type units fixed to 5 distinct (49 to 5/5 + au-pause). Excluded 2
  word-building units (`er-faster`, `open-syllable-robot`: build-table primary, distinct;
  their secondary sentence list rebuilds to `[:3]` — layout risk, no real repeat problem).
  `oy-toy` left at 4/5 (oy inventory genuinely lacks 5 picturable decodable words — documented).
- **Method:** edit the AUTHORED source `language/<subject>/data.json`, keep every first-occurrence
  sentence VERBATIM, replace ONLY duplicate + pre-broken (pic∉sentence) rows with new distinct
  decodable words; rebuild via gen_content+build_unit (regenerates content.json, decodable_text,
  answer key, images; preserves the reveal:first underline fix). Orchestrator `language/dedup_fix.py`
  (sweep / report / vet / assemble / apply). Log `language/DEDUP_FIX_LOG.md`; backups `_dedup_fix_backup/`.
- **Division of labour that worked:** the MODEL authors the new words (kid-friendly, picturable);
  `decodability.check_text`/`segment_word` VET them before spend; a dry `assemble()` pre-check caught
  ~14 count/decodability/pic-in-sentence issues before any image gen.
- **Two gate lessons (from real failures):**
  - **Preservation must keep first-occurrences verbatim** — rewriting a non-duplicate sentence for
    "naturalness" fails the targeted-change gate. Only swap the true duplicate/broken rows.
  - **must_keep must exclude pre-broken rows** (original pic word not in its own sentence, e.g. ll-doll
    "Tell Nan to sell it." tagged pic=hill) — those are legitimately replaceable, not preservable.
- **GOTCHA — network image-gen hangs kill a long build run.** A single OpenRouter call stalling took
  down the whole 49-unit run at unit 15 (exit 0, silently incomplete). Fix that worked:
  **pre-generate ALL new images in an isolated, error-tolerant pass first** (42 imgs, 0 fail), then run
  the builds cache-only (no network) → 49/49 passed. Don't interleave network image-gen with a long build loop.
- **Image QA caught 4 bad/insensitive generations** (chief→feather-headdress figure = cultural-stereotype;
  bruise/vein→heart shapes = wrong; design→vague). Replaced words with fries/guitar/weight/gnu + regen.
  Always Read the new images — a contact-sheet montage of all new PNGs makes this one glance.
- ~46 new images generated (~$4). New-word images cached in `assets/ai_line_art/`.

## 2026-07-02 — Round 3: distinct example WORD per sentence

- **Problem:** even with distinct pictures (round 2), sheets repeated the same *example word* across
  sentences (z-zebra "zip"×3, oo-book "look"×3, ey-they "they"×4). Each sentence should demonstrate a
  DIFFERENT grapheme word.
- **Sweep:** 44/88 actionable; fixed **43** (reword to distinct grapheme words, KEEPING pictures →
  zero new images). Exceptions still repeating ONE word (inventory-limited, documented): oy(toy),
  zz(buzz), oll(roll), gh(rough), augh(caught), ey(grey), wh(what); `aigh-straight` unavoidable
  ("straight" only word); `er-faster` word-building excluded.
- **Tooling:** extended `dedup_fix.py` — `_gwords()` (grapheme content-words, function-word stoplist +
  true-segment check), `word_sweep`/`word_report`, and `apply(..., preserve=False,
  require_distinct_words=True, expect_pics=..., backup_dir=_wordfix_backup)`. Log `WORDFIX_LOG.md`.
- **Gate lessons:**
  - **Reword rounds need `preserve=False`** (we intentionally rewrite sentences) + `expect_pics` as a
    no-surprise-image guard (assert pic set unchanged) → confirmed 0 image spend.
  - **check_text (pre-vet) and check_unit (build gate) disagree on a few words** (e.g. `laugh` needs
    `au`>order; `like` magic-e; `where` `ere`). Pre-vet can pass what the build rejects — always let the
    build's `check_unit` be the hard gate, fix reactively.
  - **`gen_content.gen_word_building` caps sentences to `[:3]`** — rebuilding a word_building unit
    (ly/un/ed suffix/prefix sheets) through gen_content DROPS 2 of its 5 sentences → page-count change.
    Fix: for those, edit the "Read the sentences" rows in `content.json` DIRECTLY and call `build_unit`
    (which renders content.json as-is, no cap), keeping all 5 rows + the 3-page layout. Sync data.json too.
- New backups `_wordfix_backup/`. All prior fixes (reveal:first underline, distinct pictures) verified intact.

## 2026-07-02 — Touch-ups: "Ii" legibility + wrong "photo" image

- **Ii read as "li":** the house sans font draws capital I as a bare stroke = lowercase l, so "Ii"
  (letter shown both cases) misreads as "li" on letter-sound sheets. Fix: serif the letter displays,
  SCOPED to letter sheets via a `<body class="lettersheet">` flag (set when a `formation` part exists) →
  `.lettersheet .title/.ph-title/.ph-tab-main, .fm-letter, .fm-trace { font-family: Georgia,serif }`.
  Reading-sentence tabs/titles keep the sans. Content unchanged; 24 k_letter_sounds units re-rendered.
- **Bad AI image:** `photo.png` had been generated as a kawaii ANIMAL (the model read "photo" as a
  creature). Regenerated with an explicit prompt ("framed photograph = rectangular picture frame with a
  mountain/sun picture inside, no face") → clear photo. Lesson: abstract nouns (photo/echo/design/bruise)
  are the ones the image model gets wrong — always eyeball them, and prompt with a concrete depiction.
- Both shipped Drive-only; 25 touched units re-rendered, page counts + borders preserved, all fresh.

## 2026-07-02 — Wrong-image sweep + aigh word-family

- **Image-QA sweep:** built labeled contact sheets of all 345 used images, eyeballed every one.
  9 depicted the WRONG object (AI misread the word): wood=mushroom-forest, foil=fencing-sword,
  shop=mushroom-cottage, stick=stick-figure-person, nail=fingernail, bat=wingless-critter,
  page=cloud-scene, map=doodle, trunk=elephant-trunk. Regenerated all 9 with explicit concrete
  prompts (e.g. "a stack of chopped firewood logs", "a metal carpentry nail head+point"), rebuilt
  the 14 units referencing them (page/nail in 2 units, map in 4 K picture tasks). Lesson: the
  image model reliably fails on (a) abstract nouns and (b) words with a common homograph (foil sword,
  nail finger, bat mammal, stick figure) — contact-sheet the whole library and eyeball; don't trust
  per-word gen.
- **aigh single-word repeat:** aigh's only common word is "straight" → the sheet read straight×5.
  aigh word family = straight, straighten, straightaway, straightedge (all decodable, aigh segment).
  Used straight/straighten/straightedge (kid-appropriate) with distinct pics → straight×2 (was ×5),
  3 distinct aigh words. `apply(..., require_distinct_words=True, allow_word_repeats=2)`. Truly
  single-word graphemes can still be varied via the derived word family.
