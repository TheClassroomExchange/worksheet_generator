# The Classroom Exchange — Worksheet Generator

Curriculum-aligned K-Grade 3 unit generator for The Classroom Exchange marketplace.
Each unit ships as a published Google Slides deck containing 5 lesson plans, 5 worksheets,
manipulatives, formative + reflection materials, an assessment suite, a marketplace listing,
and a graded rubric — all aligned to Ontario MOE expectations.

> **Architectural note.** This project does **not** call the Claude API. Claude (running inside
> Claude Code) is the *runner*: it reads stage prompts, generates each stage's JSON inline, and
> writes it via the editor's Write tool. Python in this repo is plumbing only — schema validation,
> drift gates, image composition, Slides API calls, manifest state, and rubric grading. If you
> remove Claude Code, the pipeline does not run.

---

## Table of contents

1. [How the system works](#how-the-system-works)
2. [Repository layout](#repository-layout)
3. [Stage flow per unit](#stage-flow-per-unit)
4. [Drift gates and the publication gate](#drift-gates-and-the-publication-gate)
5. [Local setup](#local-setup)
6. [Running a unit](#running-a-unit)
7. [Setting up the autonomous agent](#setting-up-the-autonomous-agent)
8. [Operating notes](#operating-notes)
9. [Troubleshooting](#troubleshooting)

---

## How the system works

```
 ┌────────────────────┐    ┌───────────────────┐    ┌─────────────────────┐
 │ unit_plan.json     │ →  │ Claude Code       │ →  │ generated_units/    │
 │ (40-unit queue)    │    │ + tce-unit-builder│    │ <batch>/<unit>/     │
 │                    │    │ skill             │    │ NN_stage.json files │
 │ canadian_classroom │    │                   │    │ manifest.json       │
 │ _content_batches   │    │ Reads prompts/,   │    │ run.log.jsonl       │
 │ .xlsx (input rows) │    │ writes stage JSON │    │ composed/*.png      │
 └────────────────────┘    │ via Write tool    │    │ unit.md             │
                           └─────────┬─────────┘    └──────────┬──────────┘
                                     │                          │
                                     ▼                          ▼
                           ┌───────────────────┐    ┌─────────────────────┐
                           │ pipeline/* (no    │    │ Drive: shared TCE   │
                           │ LLM): manifest,   │    │ folder              │
                           │ schemas, drift    │    │ <unit>/deck.gslides │
                           │ gates, rubric,    │    │  (pass)             │
                           │ compose, slides   │    │ _drafts/<unit>/...  │
                           └───────────────────┘    │  (fail)             │
                                                    └─────────────────────┘
```

**Per-unit lifecycle:**

1. `pipeline.unit_plan` reads the 40-unit queue and identifies the next planned/in-progress unit.
2. `init_unit_from_plan()` creates `generated_units/<batch>/<unit_slug>/` with `input_row.json`
   (verbatim Ontario curriculum text) and a fresh `manifest.json`.
3. Claude generates each of 17 stages one at a time:
   - Marks the stage `in_progress` in the manifest.
   - Generates the stage JSON inline in the chat.
   - Writes the JSON to disk.
   - Calls `manifest.complete_stage()`, which schema-validates against `pipeline/schemas.py`
     and runs advisory + hard drift checks.
4. After all 16 content stages pass, the rubric stage grades the unit against
   `assets/rubric_product_assessment.md` (threshold 17/20).
5. If the rubric passes **and** all three drift gates are clean, `pipeline.compose` builds
   image composites, `pipeline.slides` builds the Google Slides deck, and the deck publishes
   to the per-unit subfolder of the shared TCE Drive folder. Failures route to `_drafts/`.
6. A mandatory visual-inspection pass renders every slide to PNG and walks
   `VISUAL_INSPECTION_CHECKLIST` per slide type before the deck is considered shipped.

---

## Repository layout

```
worksheet_generator/
├── README.md                                  ← you are here
├── CLAUDE.md                                  ← runbook Claude Code reads at session start
├── AUTOMATED_RUN_PROMPT.md                    ← prompt template for fully autonomous runs
├── requirements.txt                           ← Python dependencies
├── .env.example                               ← copy → .env (legacy, not currently used)
├── .gitignore                                 ← excludes secrets, venv, caches
│
├── canadian_classroom_content_batches.xlsx    ← input queue (PM-owned; status column drives flow)
├── unit_plan.json                             ← 40-unit programme checkpoint state
│
├── auth_only.py                               ← one-shot Google OAuth helper (writes token.json)
├── credentials.json                           ← Google OAuth client (NOT committed)
├── token.json                                 ← Google OAuth access token (NOT committed)
│
├── assets/
│   └── rubric_product_assessment.md           ← gold-standard rubric — units must score ≥17/20
│
├── sample_assets/
│   ├── clipart/                               ← shared clipart library
│   │   ├── INDEX.json                         ← catalogue (filename, tags, caption, dims)
│   │   └── *.png                              ← 44+ images, LRU-rotated across units
│   └── *.svg                                  ← per-unit SVGs (Pattern Parade originals)
│
├── curriculum/                                ← Ontario MOE expectations (cached)
│   ├── kindergarten.json                      ← K 2026, all 4 frames, 127 rows
│   ├── math.json                              ← G1-3 math (2020), 159 rows
│   ├── sources.json                           ← provenance per fetched course
│   ├── raw/                                   ← raw Kontent.ai API responses (re-parsable)
│   └── README.md
│
├── pipeline/                                  ← orchestration (no LLM calls)
│   ├── manifest.py                            ← stage state machine; complete_stage entry-point
│   ├── stages.py                              ← canonical stage list + ordering
│   ├── schemas.py                             ← Pydantic schemas + cross-stage consistency_check
│   ├── unit_plan.py                           ← 40-unit queue, status_table, init_unit_from_plan
│   ├── curriculum.py                          ← read-only loader for the cached MOE reference
│   ├── curriculum_fetch.py                    ← one-shot fetcher (re-runnable when MOE updates)
│   ├── curriculum_reference.py                ← drift gate: input_row.json vs cached reference
│   ├── density.py                             ← advisory: lesson density vs grade band
│   ├── image_alignment.py                     ← drift gate: ImagePlaceholder keywords vs caption
│   ├── clipart.py                             ← read-only catalogue + LRU rotation
│   ├── compose.py                             ← assembles per-slide composite PNGs
│   ├── render.py                              ← renders unit.md from stage JSONs
│   ├── slides.py                              ← Google Slides deck builder + visual checklist
│   └── rubric.py                              ← criteria, threshold (17/20), pre-grade drift gate
│
├── prompts/                                   ← stage prompt templates (per stage key)
│
├── scripts/
│   └── generate_units.py                      ← legacy CLI (not used in current flow)
│
├── docs/
│   ├── AGENT_BOOTSTRAP.md                     ← fresh-machine setup script
│   ├── ENGINEER_README.md                     ← legacy notes
│   └── PM_REVIEW_GUIDE.md                     ← PM review checklist
│
├── .claude/
│   └── skills/tce-unit-builder/SKILL.md       ← vendored skill — symlink to ~/.claude/skills/
│
└── generated_units/                           ← output root
    ├── batch_1/<unit_slug>/
    ├── batch_2/<unit_slug>/
    └── batch_3/<unit_slug>/
        ├── input_row.json                     ← frozen spreadsheet row + curriculum text
        ├── manifest.json                      ← stage state (atomic writes only)
        ├── run.log.jsonl                      ← every stage transition
        ├── 0_blueprint.json                   ← unit blueprint (anchors all later stages)
        ├── 1_lesson_01.json … 1_lesson_05.json
        ├── 2_worksheet_01.json … 2_worksheet_05.json
        ├── 3_manipulatives.json
        ├── 4_formative_reflection.json
        ├── 5_assessment_suite.json
        ├── 6_marketplace.json
        ├── 7_rubric_grade.json                ← publication gate (≥17/20 to ship)
        ├── *.attempt_N.failed.json            ← preserved schema-failure outputs
        ├── composed/*.png                     ← image composites (cleared on pass-publish)
        └── unit.md                            ← assembled rendering
```

---

## Stage flow per unit

Defined authoritatively in `pipeline/stages.py`.

| Order | Stage key | Output | Depends on |
|---|---|---|---|
| 0 | `blueprint` | `0_blueprint.json` | — |
| 1.1–1.5 | `lesson_NN` | `1_lesson_NN.json` | blueprint |
| 2.1–2.5 | `worksheet_NN` | `2_worksheet_NN.json` | blueprint + matching lesson |
| 3 | `manipulatives` | `3_manipulatives.json` | blueprint + all lessons |
| 4 | `formative_reflection` | `4_formative_reflection.json` | blueprint + all lessons |
| 5 | `assessment_suite` | `5_assessment_suite.json` | blueprint + all lessons |
| 6 | `marketplace` | `6_marketplace.json` | everything above |
| 7 | `rubric_grade` | `7_rubric_grade.json` | everything above (publication gate) |

**Cardinal rule:** one stage per turn. The checkpoint design means a failure or context-window
exhaustion mid-stage is recoverable — the next session resumes from `next_pending`.

---

## Drift gates and the publication gate

Three **hard** drift checks must return zero issues for a unit to publish:

1. **`pipeline.schemas.consistency_check`** — cross-stage references (manipulative IDs,
   vocabulary, lesson titles, expectation codes) must match between blueprint and downstream.
2. **`pipeline.curriculum_reference.verify_curriculum_text`** — `input_row.json` text must
   match the cached Ontario MOE reference verbatim.
3. **`pipeline.image_alignment.validate_unit_alignment`** — every `ImagePlaceholder` must
   populate `keywords` + `text_image_alignment_check`; if `clipart_filename` is set, every
   keyword must appear in the chosen clipart's `caption + tags`.

Two **advisory** checks fire automatically inside `complete_stage()` and only print warnings:

- **`pipeline.density`** — lesson density (teacher script length, action steps, consolidation
  prompts) vs the grade band.
- **`pipeline.curriculum_reference`** also flags `needs_human` reference status for escalation.

The `RubricGrade` Pydantic schema rejects `status="pass"` if any hard drift gate has issues.
On a passing grade, `build_unit_deck` publishes to the per-unit subfolder of the shared TCE
Drive folder and deletes non-deck artifacts. On a failing grade (or ungraded), the deck routes
to `_drafts/<unit>/` instead.

After publish, **mandatory visual inspection** renders every slide via
`pipeline.slides.render_validation_pages` and walks the per-slide-type
`VISUAL_INSPECTION_CHECKLIST`. The deck is not considered shipped until every checkbox passes.

---

## Local setup

### Prerequisites

| Tool | Version | Why |
|---|---|---|
| Python | 3.10+ | Pipeline runtime |
| `librsvg` (system binary) | recent | SVG → PNG conversion (`rsvg-convert`) |
| Google Cloud project | — | OAuth client for Slides + Drive APIs |
| [Claude Code](https://claude.com/claude-code) | latest | This is the runner — required, not optional |

### 1. Clone and install

```bash
git clone https://github.com/TheClassroomExchange/worksheet_generator.git
cd worksheet_generator

python -m venv venv
source venv/bin/activate                        # macOS/Linux
# or: venv\Scripts\activate                     # Windows

pip install -r requirements.txt
brew install librsvg                            # macOS
# or: sudo apt-get install librsvg2-bin         # Debian/Ubuntu
```

### 2. Google OAuth (Slides + Drive)

The pipeline writes Google Slides decks and uploads composite PNGs to a shared Drive folder.

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project, enable the
   **Google Slides API** and **Google Drive API**.
2. Create an **OAuth 2.0 Client ID** of type **Desktop app**. Download the JSON.
3. Save it as `credentials.json` at the project root. (This file is `.gitignore`d.)
4. Run the one-shot auth helper:

   ```bash
   ./venv/bin/python auth_only.py
   ```

   A browser window opens for consent. On success, `token.json` is written next to
   `credentials.json` and the pipeline can call Slides + Drive.

> **Never commit `credentials.json` or `token.json`.** They are in `.gitignore` for a reason.
> If they leak, rotate the OAuth client secret in Google Cloud Console immediately.

### 3. Claude Code + the skill

The autonomous flow depends on the **`tce-unit-builder`** skill. The skill is **vendored in
this repo** at `.claude/skills/tce-unit-builder/SKILL.md`. Symlink it into your Claude Code
skills directory once:

```bash
mkdir -p ~/.claude/skills
ln -sf "$(pwd)/.claude/skills/tce-unit-builder" ~/.claude/skills/tce-unit-builder
```

Future `git pull`s on this repo automatically update the skill. The skill triggers on phrases
like "continue the unit", "next stage", "resume the worksheet generator", and on scheduled
cron firings.

For step-by-step setup on a fresh machine, see [docs/AGENT_BOOTSTRAP.md](docs/AGENT_BOOTSTRAP.md).

### 4. Sanity check

```bash
./venv/bin/python -c "
from pathlib import Path
from pipeline.manifest import status_table
from pipeline.curriculum_reference import report_reference_status

for batch in ['batch_1', 'batch_2', 'batch_3']:
    bd = Path(f'generated_units/{batch}')
    if bd.exists():
        print(f'=== {batch} ===')
        print(status_table(bd))

print('\n=== Curriculum reference status ===')
for line in report_reference_status(): print(line)
"
```

Expected output: a checkbox view of stage state across the three batches and a list of
verified Ontario MOE references. If you see import errors, your venv is missing deps. If you
see `needs_human` references, escalate before grading any unit that uses that grade.

---

## Running a unit

### Manual (interactive) run

Open Claude Code in the project root and start a new session. Claude reads `CLAUDE.md` at
session start and walks the stage loop:

```
You:    Continue the next pending unit.
Claude: [reads manifests, finds next_pending, generates one stage, writes JSON,
         calls complete_stage(), reports status]
You:    Continue.
Claude: [next stage]
...
```

One stage per turn — by design. Checkpointing means you can quit any time without losing
progress, and a new session picks up exactly where the previous one stopped.

### Fully autonomous run

Use `AUTOMATED_RUN_PROMPT.md` as the seed for a hands-off run. Paste it into a fresh Claude
Code session, walk away, return when the report appears. The session will:

- Make every content decision itself (no clarifying questions).
- Run consistency_check, density, curriculum_reference, image_alignment after each stage.
- On the last stage, grade against the rubric, build the Slides deck, render validation
  pages, and walk the visual checklist.
- Print a structured end-of-run report (stages completed, deck URL, judgment calls,
  observed issues).

### Resuming after failure

Schema validation failures are non-fatal — the bad output is preserved as
`<stage>.attempt_N.failed.json` and the stage is marked `failed` in the manifest. Resume with:

```bash
./venv/bin/python -c "
from pathlib import Path
from pipeline.manifest import status_table, list_failed, retry_failed
bd = Path('generated_units/batch_2')
print(status_table(bd))
list_failed(bd)
# To reset a specific stage:
# retry_failed(Path('generated_units/batch_2/<unit_slug>'), stage_key='lesson_04')
"
```

Then in a new Claude Code session, ask it to continue. It will pick up the reset stage.

---

## Setting up the autonomous agent

To run the 40-unit programme autonomously over weeks:

1. **Maintain the skill.** Keep `~/.claude/skills/tce-unit-builder/SKILL.md` accurate. The
   skill is what lets Claude resume cold without re-reading the entire `CLAUDE.md`.
2. **Maintain the memory file.** When you discover a new layout invariant, drift pattern,
   or content rule, write it into the project memory file under `~/.claude/projects/.../memory/`
   so future sessions inherit the lesson.
3. **Schedule with `/schedule` or cron.** From a Claude Code session in the project root:
   ```
   /schedule daily at 9am: Continue the K-G3 Math programme. Refresh state from disk,
   resume the next pending stage, and stop after one stage completes cleanly.
   ```
   Or use the `tce-unit-builder` skill's scheduling hook (it triggers on cron firings).
4. **Stop conditions.** A scheduled run should stop when:
   - All four drift gates are clean **and** a stage is marked `done` (safe stop).
   - Or it has been working for >N minutes (configurable per scheduler).
   - Never stop with an `in_progress` stage — the runbook either finishes it or reverts to `pending`.
5. **Monitor.** Each session prints `status_table()` at start and end. The plain-text checkbox
   view tells you at a glance how far the programme has progressed.
6. **Rotate clipart and curriculum.** New clipart goes in `sample_assets/clipart/` with an
   `INDEX.json` row added. When Ontario revises the curriculum, run
   `./venv/bin/python -m pipeline.curriculum_fetch`.

---

## Operating notes

- **The spreadsheet is the queue.** Only operate on rows whose `status` is `pending`,
  `needs_regen`, or `in_progress`. Skip `deprecated` and `generated`.
- **Atomic writes only.** Use `pipeline.manifest.save()` — never write `manifest.json` directly.
- **Never edit a `done` stage** without first marking it `pending` and recording why in the
  manifest's `errors` list.
- **No image generation in-pipeline.** Images come from the local clipart library or
  hand-drawn SVGs. To add a new clipart, drop a 1024-px PNG in `sample_assets/clipart/` and
  append a row to `INDEX.json`.
- **LRU rotation matters.** Use `clipart.suggest_for_unit()`, not `list_by_tag()`. Record
  chosen filenames in `Manipulative.clipart_files` so the rotation tracker sees them.
- **Coherence beats throughput.** Better to slow down and match the K Pattern Parade
  reference quality than ship five mediocre units.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `complete_stage` raises ValidationError | Stage JSON doesn't satisfy Pydantic schema | Read `<stage>.attempt_N.failed.json` and the `last_error` in manifest; regenerate the stage |
| `consistency_check` returns issues | Manipulative ID, lesson title, or expectation code drifted between blueprint and downstream stage | Reset the offending stage to `pending`, regenerate to match blueprint |
| `verify_curriculum_text` returns drift | `input_row.json` doesn't match cached MOE reference | Re-run `init_unit_from_plan` or paste the verbatim text from `pipeline.curriculum.get(grade, code)` |
| Rubric scores <17/20 | Content thin for the grade band | `mark_for_remediation(unit_dir)` resets stages flagged in `remediation[]`, regenerate richer content |
| Deck publishes to `_drafts/` | Rubric failed or drift gates dirty | Pre-grade drift gate refused to allow `status="pass"`; fix upstream first |
| Visual inspection finds overlap/truncation | New content shape exceeds layout budget | Either shorten upstream content or extend layout code in `pipeline/slides.py` |
| `rsvg-convert: command not found` | Missing system binary | `brew install librsvg` (macOS) / `apt-get install librsvg2-bin` (Linux) |
| Google API 403 / token expired | OAuth token invalid | Delete `token.json`, re-run `./venv/bin/python auth_only.py` |

---

## Files NOT in the repo (you must provide them)

- `credentials.json` — your Google OAuth client (see [Local setup](#local-setup) §2).
- `token.json` — generated by `auth_only.py` after first OAuth consent.
- `.env` — currently unused but reserved; copy from `.env.example` if needed.
- A shared TCE Drive folder ID — configured inside `pipeline/slides.py` constants;
  the OAuth user must have write access to it.

The `tce-unit-builder` skill that drives autonomous runs **is** vendored — see
`.claude/skills/tce-unit-builder/SKILL.md` and the symlink step in [Local setup](#local-setup) §3.
