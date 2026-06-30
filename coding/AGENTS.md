# AGENTS.md — Coding-Worksheet Pipeline (operations guide)

**Audience: a future AI agent (or engineer) operating this pipeline.** This is the
single entry point. It documents how the K–G3 Ontario **coding** worksheet
catalogue is built, graded, rendered to **one combined PDF per topic**, and
published to Google Drive — plus every gotcha learned. The sibling **Math**
pipeline (Google Slides) is documented in the repo root `CLAUDE.md`; this file is
the **coding** pipeline only.

> **You are the runner.** Python here is plumbing only — no LLM calls inside the
> pipeline. The agent authors content (worksheet specs, teacher guides, solutions)
> in chat and writes JSON; Python validates, renders, gates, and publishes.

---

## 1. What exists today (state)

- **93 sheets, 12 subjects, K–G3** — all complete, every teacher guide 20/20 on the
  teacher-guide rubric, each shipped as **ONE combined PDF** (`<Title>.pdf` =
  worksheet pages first, teacher guide/answer key appended last).
- **Published** to Google Drive under `Generated Coding Worksheets/<Grade>/<Subject>/<NN>. <Title>/`,
  exactly **one PDF per folder** (root `1HkbqjbPjSiQbZeW7OCJl7eZuAF_mvw7j`).
- Footer brand on every page: **"The Classroom Exchange"**.

| Grade | Subjects (batch dir) | Sheets |
|---|---|---|
| K | `k_unplugged_ct` · `k_sequencing` · `k_intro_block` | 24 |
| G1 | `g1_unplugged_sequencing` · `g1_block_sequential` · `g1_intro_debugging` | 24 |
| G2 | `g2_block_concurrent` · `g2_events_parallel` · `g2_debugging_reading` | 24 |
| G3 | `pilot_g3_block_coding` · `g3_python_turtle` · `g3_debugging` | 21 |

---

## 2. Repo / file map

```
coding/
├── AGENTS.md                  ← THIS FILE (start here)
├── README.md                  ← original planning doc (historical)
├── subjects.json              ← the 12-subject queue (status, build order, dir)
├── <batch_dir>/               ← one per subject (e.g. g3_python_turtle/)
│   ├── topics.json            ← {grade, subject, topics:[{nn,dir,title,status}]}
│   └── <NN_topic>/            ← one per sheet (e.g. 03_square_loop/)
│       ├── content.json       ← {title, file_title, worksheet:{spec}, teacher_guide:{spec}}
│       ├── solution.py        ← the code-runs gate (asserts the answer key)
│       ├── solution_run.json  ← {passed, stdout} from running solution.py
│       ├── content_grade.json ← worksheet rubric score (C1–C5)
│       ├── tg_grade.json      ← teacher-guide rubric score (T1–T5)  ← NEW
│       ├── visual_grade.json  ← visual-inspection record
│       ├── render.json        ← {combined_pdf: "<Title>.pdf"}
│       ├── publish.json       ← Drive folder id + uploaded file + hygiene
│       ├── manifest.json      ← per-sheet stage state machine
│       └── <Title>.pdf        ← THE deliverable (one combined PDF)
├── rubrics/
│   ├── rubric_coding_{K,G1,G2,G3}.md   ← worksheet rubric (5 crit, /20)
│   └── rubric_teacher_guide.md         ← teacher-guide rubric (T1–T5, /20)  ← NEW
├── TG_REWRITE_PROGRESS.md / TG_REWRITE_HANDOFF.md   ← the TG-rewrite tracker/handoff
├── LESSONS_LEARNED.md / AUTONOMOUS_BUILD.md / *_BUILD_PLAN.md   ← build history
└── BRANDING_PLAN.md           ← (pending) mascot+wordmark footer plan

pipeline/
├── worksheet_pdf.py     ← WeasyPrint renderer (data-driven spec → PDF). Footer line ~240.
├── coding_build.py      ← run_solution / render_sheet(roomy_level=) / combine_sheet / fit_render(auto-fit) / build_to_render / finalize_visual(page-fill gate)
├── coding_rubric.py     ← worksheet gate: classify(), pre_grade_drift_check(), select_rubric()
├── teacher_guide_rubric.py ← TG gate: classify(), lint_teacher_guide(), record_grade()   ← NEW
├── layout_rubric.py     ← page_fill_ok() (no near-empty page) + content_unchanged() (layout-only diff)  ← NEW
└── drive_publish.py     ← publish_batch(batch_dir): one combined PDF/topic, idempotent
```

**Run python with WeasyPrint:** prefix every interpreter call with
`DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python ...` or the import fails.

---

## 3. content.json shape

```jsonc
{
  "title": "Draw a Square with a Loop",
  "file_title": "Draw a Square with a Loop",   // filename base
  "worksheet":     { <worksheet_pdf spec> },    // student page — DO NOT edit on a TG-only pass
  "teacher_guide": { <worksheet_pdf spec> }     // teacher page (all parts type:"prose")
}
```
A `worksheet_pdf` spec: `mascot, eyebrow, title, subtitle, footer_topic, name_date,
learning_goal?, compact?, parts:[]`. Part types: `prose` (text = string OR list[str]),
`blocks`, `code`, `exercise`, `symbols`, `image`. **Teacher guides use only `prose`**,
set `name_date:false`, and render in **compact** mode (auto-set by `render_sheet`).
Asset paths (`mascot`, image `src`) are stored repo-relative and resolved at render.

---

## 4. The teacher-guide standard (plain-language, for a non-coder)

Every teacher guide is written for **a teacher who has never coded**. Section order:

1. **What this worksheet teaches** — 1 short plain paragraph + "No coding experience needed."
2. **Before you start** — tool setup. Unplugged/K = "No computer needed, paper & pencil";
   block coding = print + optional Scratch-style app; Turtle = optional online playground (click-level).
3. **How to lead it (about N min)** — show-it → do-together → try-alone, sample teacher talk, a "big idea" line.
4. **Answer key (these are the verified correct answers)** — every exercise, plain reasoning; **must match `solution_run.json`**.
5. **If students get stuck — and ways to adjust** — one "watch for" + make-it-easier + make-it-harder.
6. **Ontario curriculum link (official wording)** — the **verbatim** C3 (or K-frame) quote, then an **"In plain terms:"** gloss line.
7. **You'll know it worked when** — 1-line success indicator.

**Rules:** keep it tight (one page); never use unexplained jargon. Say "repeat N times"
not `for-loop`/`range()`; "character" not `sprite`; "at the same time" not `concurrent`
(except inside the verbatim quote). Keep the Ontario quote word-for-word; add the gloss
beneath it, never edit it. Preserve named learning concepts and gloss them once:
K-frame; two characters (Bit green / Pixel purple) running at the same time; send/get a
message (broadcast/receive); SHOULD → DOES → FIX; repeat loops.

---

## 5. Gates (a sheet ships only if ALL pass)

- **Code-runs gate** — `solution.py` runs clean → `solution_run.json.passed == true`. The answer key derives from this.
- **Worksheet rubric** — `coding_rubric.classify(scores)` → `pass`. Publish gate: total ≥ 19/20 AND C2≥L3 AND C3=L4 AND C5=L4 (`rubric_coding_<grade>.md`).
- **Teacher-guide rubric** — `teacher_guide_rubric.classify(scores)` → `pass`. Gate: total ≥ 18/20 AND **T1=L4** (plain language) AND **T4=L4** (answer-key correctness). `rubric_teacher_guide.md`.
- **Lint (jargon)** — `teacher_guide_rubric.lint_teacher_guide(dir)['clean'] == True` (no jargon tokens in non-citation prose; "In plain terms:" gloss present when a citation is present).
- **Lint (prose copy-edit)** — `prose_lint.lint_prose(dir)['clean'] == True` (no duplicate adjacent words, common misspellings, double-punctuation, or space-before-punctuation across BOTH `worksheet` + `teacher_guide`). Advisory: it's also captured under `tg_grade.json::prose_lint` by `record_grade`. Tuned for 0 false positives on the catalogue (ignores `____` blanks, `code`/symbol `label` fields, the standalone "?" placeholder, ellipses). Does NOT do homophones/grammar — that stays with the human/LLM pass.
- **Drift** — `coding_rubric.pre_grade_drift_check(dir)['passed'] == True` (solution ran; cited C3 codes/text verbatim vs the Ontario cache — K skips curriculum). NOTE: drift reads `input_row.json`, **not** the TG text, so TG wording never breaks it.
- **Page-fill (hard, all grades)** — `layout_rubric.page_fill_ok(<combined pdf>)['ok']` — **no near-empty worksheet page** (header/goal-only, or a lone trailing line). Enforced inside `finalize_visual`: a blank-ish page → it raises, so the sheet can't finalize or publish. Fix by re-rendering via `coding_build.fit_render(dir)` (auto-fit). Ink-band oracle; TG pages excluded by footer.
- **Visual** — combined PDF page count = worksheet pages + 1 (TG must be 1 page); footer correct; rendered page Read with `pdftoppm -png`. For a CHANGED sheet, Read each page **full-size** — a thumbnail montage can hide a blank page (use `page_fill_ok` for that, not eyeballing a contact sheet).

> **K & G1 render "roomy" (bigger images + more writing room).** `render_sheet` sets `roomy=True` by grade (`ROOMY_GRADES = {Kindergarten, Grade 1}`); `roomy_level` (0→3) is a compaction ladder, and `fit_render` auto-picks the roomiest level with no near-empty page. G2/G3 are untouched (level 0, no roomy). See `LAYOUT_REVISION_PLAN.md`.

---

## 6. Workflows (copy/paste)

### 6a. Rewrite/author a teacher guide for one batch (the proven loop)
```
export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib
# 1. Dump current content (exercises + answer keys) to author from:
./venv/bin/python -c "import json,glob,os; [print(os.path.basename(d), json.load(open(d+'/content.json'))['title']) for d in sorted(glob.glob('coding/<batch>/*')) if os.path.isdir(d)]"
# 2. Author new teacher_guide.parts in a /tmp script (keeps repo clean), load each
#    content.json, set c['teacher_guide']['parts']=[...], dump. (See git history /tmp/tg_*.py pattern.)
# 3. Gate + render + combine + finalize, per sheet:
./venv/bin/python - <<'PY'
import json,glob,subprocess
from pathlib import Path
from pipeline import teacher_guide_rubric as tg, coding_rubric, coding_build
B=Path('coding/<batch>')
dirs=[B/t['dir'] for t in json.loads((B/'topics.json').read_text())['topics']]  # handles non-NN dirs (e.g. sheet_01_loops)
for p in dirs:
    json.loads((p/'content.json').read_text())                 # JSON valid
    assert tg.lint_teacher_guide(p)['clean']                   # jargon lint
    from pipeline.prose_lint import lint_prose
    assert lint_prose(p)['clean'], lint_prose(p)['hits']       # prose copy-edit lint
    rec=tg.record_grade(p,'<G1|G2|G3|K>',{'T1':4,'T2':4,'T3':4,'T4':4,'T5':4})
    assert rec['status']=='pass', rec
    assert coding_rubric.pre_grade_drift_check(p)['passed']     # drift
    coding_build.fit_render(p)                                  # render+combine, AUTO-FIT (K/G1 roomy; no near-empty page) → one <Title>.pdf
    coding_build.finalize_visual(p, status='pass', notes='...', inspected_pages=[1])  # hard page-fill gate
    print(p.name,'OK')
PY
# 4. Spot-Read one TG page: pdftoppm -png -f <ws_pages+1> -l <same> "coding/<batch>/<dir>/<Title>.pdf" /tmp/x ; then Read it.
# 5. git add coding/ pipeline/ && git commit  (one commit per subject)
```

### 6b. Combine = one PDF per folder
`coding_build.combine_sheet(dir)` runs `pdfunite "<fbase> — Worksheet.pdf" "<fbase> — Teacher Guide.pdf" "<fbase>.pdf"`,
then deletes the two component PDFs. Folder ends with exactly one `<fbase>.pdf`. (`pdfunite` from poppler; `pypdf` fallback if absent.)

### 6c. Publish a batch to Drive
```
# Auth (first time / token expired — interactive, opens a browser the USER approves):
#   if token revoked, move token.json aside first so it forces the browser flow:
#   mv token.json token.json.revoked.$(date +%s)
DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib ./venv/bin/python -c "from pipeline import slides; slides.get_credentials()"
# Publish (dry-run first):
./venv/bin/python -c "from pathlib import Path; from pipeline import drive_publish; drive_publish.publish_batch(Path('coding/<batch>'), dry_run=True)"
./venv/bin/python -c "from pathlib import Path; from pipeline import drive_publish; drive_publish.publish_batch(Path('coding/<batch>'))"
```
`publish_batch` uploads the single combined PDF, **deletes any stale component PDFs**
from the Drive folder, and asserts the hygiene gate (**exactly 1 file/topic**). Idempotent:
re-runs update the same file in place — no duplicates. Only topics with `status=="built"` publish.

### 6d. Extend the catalogue (new subject)
Add a row to `coding/subjects.json` (status != done) + a new `<batch>/topics.json` + per-topic
`content.json` + `solution.py`, then run the per-sheet loop. Author worksheet specs from the
renderer primitives in `pipeline/worksheet_pdf.py` (`symbols`, `blocks` with `cat` colours +
`blank` write-slots, `code`, `exercise`). Grade BEFORE render. Match the grade's concept ceiling
(K unplugged/symbol-only no loops; G1 sequential; G2 concurrent; G3 loops + typed Turtle).

---

## 7. Gotchas (learned the hard way)

- **WeasyPrint import** needs `DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib`.
- **Non-`NN` topic dir**: `pilot_g3_block_coding` topic 01 is `sheet_01_loops`. **Always iterate `topics.json` dirs**, not a `0*_*` glob.
- **Drive token expires/revokes** (`invalid_grant`). Re-auth is an interactive Google login an agent can't click through — move the dead `token.json` aside, run `get_credentials()` so it opens the browser for the user, then publish. `token.json` is gitignored — never commit it.
- **TG overflow to 2 pages**: the compact CSS is already tightened (`worksheet_pdf._css`, compact branch). If a guide still spills, **trim wording** (don't loosen CSS — it would affect every TG).
- **Near-empty worksheet page (K/G1 roomy)**: a roomy question-group too tall for its page got force-pushed by `break-inside:avoid`, leaving the page it left header-only. **Build/re-render via `coding_build.fit_render(dir)`** — it climbs the `roomy_level` compaction ladder (0→3) until `page_fill_ok` passes. `finalize_visual` hard-fails any near-empty page, so this can't ship. **Don't trust a thumbnail montage to spot a blank page** — montages hid this; rely on `page_fill_ok` + full-size page Reads for changed sheets.
- **Layout-only revision must keep content byte-identical**: `layout_rubric.content_unchanged(old, new, footers)` (pdftotext; multiset fallback tolerates pdftotext dehyphenation + symbol-card reflow). `fit_render(dir, baseline_pdf=<original>)` enforces it; for a FRESH build pass no baseline (fill gate only).
- **Lint false-positives**: `lint_teacher_guide` excludes lines starting `C1./C2./C3./k-frame` from the jargon scan (those are the verbatim quotes). Jargon tokens to avoid in prose: `for-loop`, `range(`, `sprite`, `concurrent`, `run-gate`, "computational representation".
- **`text` field is string OR list[str]** — handle both when editing.
- **topics.json statuses** were already `built` after the original build — no flip needed before publish (the old "flip to built" note applies only if they were advanced to `done`).
- **Brand string**: the footer wordmark lives ONLY at `pipeline/worksheet_pdf.py` `@bottom-center` (~line 240). `BRANDING_PLAN.md` keeps historical "Canadian" mentions on purpose — leave them.

---

## 8. Provenance / IP
Source corpus is two companies' copyrighted curriculum + MIT Scratch cards. We mirror
**structure only** and generate **original** prose, code, answer keys, and mascots
(`assets/mascots/*.svg`, original kawaii). Never clone verbatim text or their art.

## 9. Related docs
- `coding/rubrics/*` — the gates' source of truth.
- `coding/LESSONS_LEARNED.md` — build-phase lessons.
- `coding/TG_REWRITE_{PROGRESS,HANDOFF}.md` — the teacher-guide rewrite record.
- Root `CLAUDE.md` — the Math (Slides) pipeline + shared infra (manifest, curriculum cache, clipart).
- Skill `coding-worksheet-builder` (in `~/.claude/skills` + `TheClassroomExchange/skills`) — the build process as a reusable skill.
