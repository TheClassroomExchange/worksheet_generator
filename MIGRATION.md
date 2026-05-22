# TCE Worksheet Generator — Migration Handoff

**Snapshot date:** 2026-05-03 ~07:30 EDT (Sunday)
**Author of this doc:** Claude session that paused the loop at clean state
**Reason for migration:** Moving from current Mac to a new computer

---

## Current programme state (read this first)

- **Programme:** 40-unit K-G3 Math curriculum, multi-session execution
- **Complete units (shipped to TCE folder):** 4
  - `k_patterns_pattern_parade`
  - `g1_patterns_pattern_parade`
  - `g2_patterns_pattern_parade`
  - `g3_patterns_pattern_parade`
- **In-progress unit:** `k_number_counting_crew` (Wave 1, K, A6 — Counting Crew)
  - **11 of 16 stages done** (blueprint, lessons 1-5, worksheets 1-5)
  - **Next pending stage: `manipulatives`**
  - All schema/consistency gates clean
- **Planned:** 35 units remaining (see `pipeline/unit_plan.py` `PLAN` list)
- **All scheduled tasks DISABLED** (resume-4h, drift-nightly, deep-qa-daily) so nothing fires during migration
- **`/loop` not armed** — no ScheduleWakeup pending

---

## What needs to migrate (8 things)

### 1. The project repository

```
/Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/
```

**Bring everything in this directory** (it's all required), but a few items deserve attention:

| Item | Why it matters |
|---|---|
| `pipeline/` | All Python orchestration (no LLM, just plumbing) |
| `pipeline/unit_plan.py` | Source of truth for the 40-unit queue and unit_id → disk-folder mapping |
| `unit_plan.json` | Checkpoint file at project root (status per unit_id) — refreshed from manifests on session start |
| `generated_units/batch_*/<slug>/manifest.json` | Per-unit state machine — the **single source of truth** for what's done. If this and the JSONs are present, work resumes cleanly. |
| `generated_units/batch_*/<slug>/*.json` | The actual generated stage outputs — irreplaceable work product |
| `curriculum/` | Local cache of Ontario MOE expectations (K 2026 + G1-3 math 2020). Re-fetchable via `python -m pipeline.curriculum_fetch` if lost. |
| `assets/rubric_product_assessment.md` | Gold-standard 17/20 publication rubric |
| `sample_assets/clipart/` | 44+ PNG library + `INDEX.json` for LRU rotation |
| `prompts/` | Stage prompt templates |
| `CLAUDE.md` | Project runbook (Claude reads this at session start) |
| `requirements.txt` | Python deps |
| `canadian_classroom_content_batches.xlsx` | Original input queue (reference) |

**Files NOT to migrate (regenerate or recreate on the new machine):**

- `venv/` — Python virtual environment, recreate via `python3 -m venv venv && ./venv/bin/pip install -r requirements.txt`
- `__pycache__/` directories — auto-regenerated
- `*.pyc` files — auto-regenerated

### 2. Credentials (Google Slides + Drive API)

These are sensitive — copy via secure channel (encrypted USB, 1Password vault, etc.), do **not** include in any git push:

```
/Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/credentials.json   # OAuth client credentials
/Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/token.json         # Refreshable user token (will need re-auth if expired)
```

If `token.json` doesn't refresh on the new machine, run `./venv/bin/python auth_only.py` to re-authenticate (browser flow).

### 3. Memory files (~/.claude/projects/.../memory/)

Source path:
```
~/.claude/projects/-Users-anthonnymonterroso-Documents-TheClassroomExchange-claude-code-handoff-worksheet-generator/memory/
```

Files inside:
- `MEMORY.md` — the index of what each memory file covers
- `multi_unit_programme.md` — 40-unit programme contract (resume rules)
- `visual_inspection.md` — mandatory final-gate per-slide checklist
- `rubric_gate.md` — 17/20 publication threshold
- `clipart_library.md` — 44-PNG catalogue rules + LRU rotation
- `image_text_alignment.md` — 3rd hard drift gate (keywords + alignment_check)
- `reference_curriculum.md` — Ontario K + G1-3 math local cache rules

**Important:** the directory name on the new machine **must match the absolute project path on the new machine** (Claude Code maps memory directories by full path). If the user/path differs on the new computer, the memory directory needs to be renamed accordingly. For example, if the new machine's user is `tce` and the project lives at `/Users/tce/work/worksheet_generator`, the memory directory becomes `~/.claude/projects/-Users-tce-work-worksheet_generator/memory/`.

### 4. Skills (~/.claude/skills/)

Source path:
```
~/.claude/skills/tce-unit-builder/
```

This is the project-specific unit-builder skill. Copy the entire directory.

### 5. Scheduled tasks (~/.claude/scheduled-tasks/)

Source path:
```
~/.claude/scheduled-tasks/
```

**Bring these three (currently DISABLED — re-enable after verifying clean resume on new machine):**
- `tce-math-programme-resume-4h/` — hourly 8am-11pm queue drainer
- `tce-math-programme-drift-nightly/` — 4am drift sweep
- `tce-math-programme-deep-qa-daily/` — 5pm deep-QA on stalest 15 units

**Optional (keep for archive, don't re-enable):**
- `g1-pattern-parade-resume-5am/`, `g1-pattern-parade-resume-7pm/`, `tce-pipeline-fixes-resume-4h/`, `tce-math-programme-weekly-qa/` — historical one-shots and superseded recurring tasks

### 6. Project-level Claude config

```
/Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/CLAUDE.md
```

(This is in the repo, but worth calling out — it's the runbook Claude reads on every session start.)

### 7. TCE Drive folder access

The shared Google Drive folder where decks publish requires the new machine's user to have access. Ensure the Google account used for `token.json` retains permissions on the destination folder.

### 8. macOS keychain entries (if using OS keychain auth)

If you've stored any API keys or OAuth tokens in macOS Keychain on the current machine (vs. plain `token.json`), export and re-import on the new machine via Keychain Access → File → Export Items.

---

## New machine setup checklist

```bash
# 1. Restore the repo (rsync, scp, or USB copy)
mkdir -p ~/Documents/TheClassroomExchange/claude_code_handoff/
# Copy worksheet_generator/ here, preserving timestamps and file modes
rsync -av --exclude=venv --exclude=__pycache__ --exclude='*.pyc' \
  source:/path/to/worksheet_generator/ \
  ~/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/

# 2. Recreate the venv and install deps
cd ~/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator/
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Restore credentials
# Copy credentials.json and token.json from secure channel into the project root.

# 4. Restore Claude Code memory + skills + scheduled tasks
# (Adjust the project-path encoding to match the new machine's actual user/path)
mkdir -p ~/.claude/projects/<encoded-project-path>/memory/
cp -r source-memory/* ~/.claude/projects/<encoded-project-path>/memory/
cp -r source-skills/tce-unit-builder ~/.claude/skills/
cp -r source-scheduled-tasks/tce-math-programme-* ~/.claude/scheduled-tasks/

# 5. Verify clean resume
./venv/bin/python -c "
from pipeline import unit_plan, manifest
from pathlib import Path
unit_plan.refresh_state_from_disk()
print(unit_plan.status_table())
nxt = unit_plan.next_unit_to_generate()
ud = Path('generated_units') / nxt.batch / nxt.unit_id
m = manifest.load(ud)
print(f'\\nNEXT UNIT:  {nxt.unit_id}')
print(f'NEXT STAGE: {manifest.next_pending(m)}')
active, reason = unit_plan.is_stage_generation_in_flight(threshold_minutes=10)
print(f'In-flight check: {active} ({reason})')
"
# Expected output (matches snapshot above):
#   K-G3 Math programme: 40 units total
#     complete:    4
#     in_progress: 1
#     planned:     35
#   ... [tables] ...
#   NEXT UNIT:  k_number_counting_crew
#   NEXT STAGE: manipulatives
#   In-flight check: False (no in-flight stage generation)

# 6. Sanity-check the drift gates on the 4 shipped units
./venv/bin/python -c "
from pipeline import unit_plan, rubric
from pathlib import Path
for entry in unit_plan.PLAN:
    if entry.status != 'complete': continue
    ud = Path('generated_units') / entry.batch / entry.unit_id
    d = rubric.pre_grade_drift_check(ud)
    print(f'{entry.unit_id}: c={len(d[\"consistency\"] or [])} curr={len(d[\"curriculum_text\"] or [])} img={len(d[\"image_alignment\"] or [])} passed={d[\"passed\"]}')
"
# Expected: all four show c=0 curr=0 img=0 passed=True

# 7. Re-enable scheduled tasks ONLY after step 5 + 6 verify clean
# Use Claude Code's scheduled-tasks MCP, or update directly in ~/.claude/scheduled-tasks/<task>/SKILL.md
# (frontmatter: enabled: true)
```

---

## How to resume the programme (new session, new machine)

1. Open Claude Code in the worksheet_generator project directory.
2. The project's `CLAUDE.md` will load automatically. The memory files load when their topics are mentioned.
3. Run the session-start status command from `CLAUDE.md`:
   ```bash
   ./venv/bin/python -c "
   from pipeline import unit_plan
   unit_plan.refresh_state_from_disk()
   print(unit_plan.status_table())
   nxt = unit_plan.next_unit_to_generate()
   if nxt: print(f'NEXT UNIT: {nxt.unit_id} (anchor {nxt.anchor_code}, {nxt.grade})')
   "
   ```
4. To resume the loop, invoke:
   ```
   /loop drain the K-G3 math programme — generate the next pending stage, run gates, repeat until you hit a real blocker or queue is empty
   ```
5. To resume cron coverage, re-enable the three tasks in `~/.claude/scheduled-tasks/` (set `enabled: true` in each SKILL.md frontmatter, or use the scheduled-tasks MCP).

---

## What "clean state" means here

A clean state requires ALL of:

- ✅ No stage in `in_progress` status anywhere (currently true after manipulatives reverted to `pending`)
- ✅ No partially-written stage JSON without a corresponding `done` manifest entry (currently true)
- ✅ All 3 hard drift gates clean for every shipped unit (currently 0/0/0 for all 4 Pattern Parade units — verified earlier this session)
- ✅ All scheduled tasks disabled OR not due to fire imminently (currently disabled)
- ✅ No `/loop` ScheduleWakeup armed (currently true — this turn skips it)
- ✅ `unit_plan.json` matches manifest reality (auto-refreshed via `refresh_state_from_disk()`)

The new session's first action is `refresh_state_from_disk()`, which rebuilds `unit_plan.json` from manifests — so even if `unit_plan.json` was stale, manifests are the truth and it converges within seconds.

---

## Known caveats / things to watch on the new machine

1. **Path encoding for the memory directory** — Claude Code encodes the project's absolute path into the directory name under `~/.claude/projects/`. If the new machine's user or path differs, you must rename the directory accordingly OR symlink. Forgetting this means memory files won't auto-load.

2. **Token refresh** — `token.json` is a refreshable Google OAuth token. If it has expired beyond the refresh window or the refresh secret changed, run `./venv/bin/python auth_only.py` to re-authenticate. This requires a browser; do this on the new machine before kicking off the loop.

3. **TCE Drive folder ID** — should be set in code or env. Verify the new machine can write to the same folder by manually publishing one already-shipped deck (`build_unit_deck` is idempotent enough that you can run it on, say, `g3_patterns_pattern_parade` and it will just re-overwrite).

4. **Clipart catalogue freshness** — `sample_assets/clipart/INDEX.json` tracks `caption` per image. Some seed entries have empty captions. As you use clipart in new units, append captions so the LRU + alignment validator gets richer signal. Not migration-critical; just a hygiene reminder.

5. **Curriculum cache age** — `curriculum/sources.json` records when each course was fetched. If Ontario revises the curriculum, re-run `./venv/bin/python -m pipeline.curriculum_fetch` to refresh.

6. **Time-of-day for scheduled tasks** — cron expressions are in **LOCAL** time. If the new machine is in a different timezone, the 8am-11pm window in `tce-math-programme-resume-4h` will fire on the new machine's local clock. Adjust if needed.

---

## Quick mental model of the codebase

- `pipeline/manifest.py` — per-unit state machine (`mark`, `complete_stage`, `next_pending`, `retry_failed`, `mark_for_remediation`)
- `pipeline/schemas.py` — every stage has a strict Pydantic schema; `complete_stage()` validates on write
- `pipeline/unit_plan.py` — the 40-unit queue, `PLAN` list, `next_unit_to_generate`, `is_stage_generation_in_flight`, `refresh_state_from_disk`
- `pipeline/rubric.py` — pre-grade drift check (3 gates), 17/20 threshold
- `pipeline/curriculum.py` — read-only Ontario reference loader
- `pipeline/clipart.py` — read-only clipart catalogue with LRU rotation (`suggest_for_unit`)
- `pipeline/slides.py` — Slides deck builder + visual inspection helpers (`build_unit_deck`, `render_validation_pages`, `VISUAL_INSPECTION_CHECKLIST`)
- `pipeline/compose.py`, `pipeline/render.py` — deck composition + markdown rendering

The 16 stages per unit (in order):
`blueprint → lesson_01..05 → worksheet_01..05 → manipulatives → formative_reflection → assessment_suite → marketplace → rubric_grade`

`rubric_grade` is the publication gate. If it scores ≥17/20 with all drift gates 0, the deck publishes to the per-unit subfolder under TCE Drive. If it fails, the deck routes to `_drafts/` and the failed criteria's stages reset to pending for regeneration.

---

## In-progress unit detail (k_number_counting_crew)

Stages on disk:

| Stage | Status | File |
|---|---|---|
| blueprint | done | `0_blueprint.json` |
| lesson_01 | done | `1_lesson_01.json` |
| lesson_02 | done | `1_lesson_02.json` |
| lesson_03 | done | `1_lesson_03.json` |
| lesson_04 | done | `1_lesson_04.json` |
| lesson_05 | done | `1_lesson_05.json` |
| worksheet_01 | done | `2_worksheet_01.json` |
| worksheet_02 | done | `2_worksheet_02.json` |
| worksheet_03 | done | `2_worksheet_03.json` |
| worksheet_04 | done | `2_worksheet_04.json` |
| worksheet_05 | done | `2_worksheet_05.json` |
| manipulatives | **pending** | (none yet — next to generate) |
| formative_reflection | pending | (none yet) |
| assessment_suite | pending | (none yet) |
| marketplace | pending | (none yet) |
| rubric_grade | pending | (none yet — final publication gate) |

The blueprint defines 7 manipulatives (M1_counting_cubes, M2_ten_frames, M3_dot_cards, M4_number_cards, M5_counting_objects_set, M6_compare_strip, M7_counting_path) and 3 recurring characters (Mae, Theo, Buddy). The `manipulatives` stage will generate `ManipulativeAsset` entries for each (schema in `pipeline/schemas.py`, lines ~410-455).

---

## Final sanity check before you migrate

Run this once on the current machine before powering down:

```bash
cd /Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator
./venv/bin/python -c "
from pipeline import unit_plan, manifest
from pathlib import Path
unit_plan.refresh_state_from_disk()
print(unit_plan.status_table())
print()
ud = Path('generated_units/batch_3/k_number_counting_crew')
m = manifest.load(ud)
print(f'k_number_counting_crew next pending: {manifest.next_pending(m)}')
active, reason = unit_plan.is_stage_generation_in_flight(threshold_minutes=10)
print(f'live in-flight: {active} ({reason})')
"
```

You should see:
```
K-G3 Math programme: 40 units total
  complete:    4
  in_progress: 1
  planned:     35
... [tables] ...
k_number_counting_crew next pending: manipulatives
live in-flight: False (no in-flight stage generation)
```

If the in-flight check returns True, **do not migrate yet** — wait for the in-flight stage to finish, or revert it to pending using:
```python
from pipeline.manifest import load, save
m = load(unit_dir)
m['stages'][stage_key]['status'] = 'pending'
m['stages'][stage_key]['started_at'] = None
save(unit_dir, m)
```

That's it. Safe to migrate.
