# Math Retrofit Orchestrator Skill

## Purpose

Drain the 35-unit K-G3 math retrofit queue autonomously. Fired every 20 minutes by `tce-math-retrofit-continuous`. Each fire advances ONE unit (or part of one) through Phase A (content gates) → Phase C (deck build + visual inspection). Self-disables when programme state shows zero pending/in_progress units.

Working directory: `/Users/aria/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator`. Use `venv/bin/python` for everything.

## Hard rules — read these every fire

- **Pydantic schemas govern verdicts.** Pair gate: pass requires no score < 3 AND ≤ 1 score = 3. Overall gate: foundational four (pedagogical_depth, alignment, instructional_balance, clarity_voice) must each be 4, ≤ 1 arc-level 3, no arc-level < 3. Visual inspection: blocking_count must equal blocking issues; status="pass" requires zero blocking.
- **Pair gates spawn 5 parallel agents — one Agent tool call each, sent in a single message** so they run concurrently. Math units always set `mathematical_authenticity` and leave `sor_alignment` null.
- **Always validate the verdict JSON before treating it as written**: `venv/bin/python -c "from pipeline.schemas import PairRubricVerdict, OverallUnitVerdict, VisualInspectionVerdict; ..."`
- **Atomic writes only.** All programme_state and manifest updates go through their library functions (which use temp-file + rename). Never write JSON by hand.
- **Per-fire cap: ≤ 2 phases worth of work.** A typical fire drains exactly one unit if both phases first-try. If the unit is hard, you may finish one phase and stop — the next fire picks up from manifest state.

## Step 0 — in-flight + budget guards (cardinal)

ALWAYS run these two checks first. They keep concurrent fires from racing and protect the 5-hour token window.

```python
venv/bin/python <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from pipeline import programme_state as ps

state = ps.load("math_retrofit_2026_05")
now = datetime.now(timezone.utc)

# In-flight check: any unit with a stage in_progress < 12 min ago?
STALE_MIN = 12
hot = []
for u in state["units"].values():
    mp = Path(u["unit_dir"]) / "manifest.json"
    if not mp.exists():
        continue
    try:
        m = json.loads(mp.read_text())
    except Exception:
        continue
    for k, s in m.get("stages", {}).items():
        if s.get("status") != "in_progress":
            continue
        sa = s.get("started_at")
        if not sa:
            continue
        age = (now - datetime.fromisoformat(sa.replace("Z", "+00:00"))).total_seconds() / 60
        if age < STALE_MIN:
            hot.append((u["unit_id"], k, round(age, 1)))

if hot:
    print(f"DEFER: {len(hot)} stage(s) in-flight (younger than {STALE_MIN} min): {hot[:3]}")
    raise SystemExit(0)
print("OK: no in-flight stage, proceeding")
PY
```

If that prints `DEFER:`, exit the fire immediately. The cron's next tick re-checks.

Token guard: if your remaining 5-hour Pro/Max budget is below ~15%, log `DEFERRED — budget low` and exit. Better to wait for the next fire than to die mid-stage.

## Step 1 — pick the next unit and snapshot state

```python
venv/bin/python <<'PY'
from pipeline import programme_state as ps
nxt = ps.next_unit("math_retrofit_2026_05")
if nxt is None:
    # Programme complete — disable this scheduled task and exit
    print("PROGRAMME_COMPLETE")
    raise SystemExit(42)   # signal to outer loop to disable the task
print(nxt["unit_id"], nxt["phase"], nxt["status"], nxt["unit_dir"])
PY
```

If exit code 42 (programme complete): disable the task via `mcp__scheduled-tasks__update_scheduled_task` with `enabled=False`, then exit. Print a one-line `"All 35 math units retrofitted; task self-disabled."`

Otherwise mark the unit `in_progress`:

```python
venv/bin/python -c "
from pipeline.programme_state import update_unit
update_unit('math_retrofit_2026_05', '<UNIT_ID>',
            status='in_progress', event='fire start')
"
```

## Step 2 — drain phases for this unit

Run Phase A if `phase == "content"`. Run Phase C if `phase == "build"`. (Math units skip Phase B.)

### Phase A — content gates

1. **Extend manifest** (idempotent):
   ```
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.manifest import extend_manifest_with_gates
   added = extend_manifest_with_gates(Path('<unit_dir>'))
   print('added gate stages:', added)
   "
   ```

2. **Build all 5 pair-gate prompts and write to /tmp**:
   ```
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.gates import build_pair_gate_prompt
   ud = Path('<unit_dir>').resolve()
   for n in range(1, 6):
       p = build_pair_gate_prompt(ud, n)
       Path(f'/tmp/retrofit_pair_{n}.prompt.txt').write_text(p)
   print('5 pair prompts ready')
   "
   ```

3. **Spawn 5 pair-grader Agents in ONE message** (parallel, single tool call block):
   - Each Agent prompt:
     - "Read /tmp/retrofit_pair_N.prompt.txt fully."
     - "Math unit — set mathematical_authenticity, leave sor_alignment null."
     - "Strict bar: no score <3 AND ≤1 three; otherwise revise."
     - "Write JSON verdict to <unit_dir>/pair_NN_verdict.json conforming to PairRubricVerdict."
     - "Validate: `venv/bin/python -c 'from pipeline.schemas import PairRubricVerdict; from pathlib import Path; PairRubricVerdict.model_validate_json(Path(\"<...>\").read_text())'`"
     - "Return one line: status | scores | 30-word summary."

4. **Read the 5 verdicts** and apply targeted lifts to any `revise_*` pair using its `category_feedback`. The proven-on-demo lift recipes (use these literally; agents have seen them before):
   - **clarity_voice → 4**: add a unit-wide chantable refrain into `consolidation.exit_routine` and reference in `minds_on.hook` and `teacher_script`. Use a 4-7 word chant that fits the theme.
   - **pedagogical_depth → 4**: cite a named research source in `expanded_walkthrough.rationale` (Sarama & Clements 2009 for early-K math; Carpenter, Fennema & Empson for fractions/operations; Battista for spatial; Friel/Curcio/Bright 2001 for data; Inhelder & Piaget 1964 for classification; NCTM trajectories for everything else). Branch `recovery_moves` into 3 diagnostic-specific paths (DIAGNOSTIC A/B/C).
   - **alignment → 4**: add a forward-bridge in `consolidation.discussion_prompts` referencing the next 1-2 lesson days in the unit arc using the named expectation codes.
   - **mathematical_authenticity → 4**: add an explicit STRATEGY COMPARE moment to `action.steps` where two pairs/groups defend different approaches; name the underlying principle in research terms.
   - **lesson_worksheet_consistency → 4**: ensure worksheet's parts mirror the lesson's success_criteria one-to-one; flag specific drift in the verdict.

5. **Re-run only failing pair gates** (rebuild only those /tmp prompts; spawn only those Agents in parallel). Cap at **3 rounds total** per unit.

6. **Once all 5 pair gates `pass`**, run the overall gate:
   ```
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.gates import build_overall_gate_prompt
   p = build_overall_gate_prompt(Path('<unit_dir>').resolve())
   Path('/tmp/retrofit_overall.prompt.txt').write_text(p)
   print(len(p), 'chars')
   "
   ```
   Spawn ONE overall_unit_grader Agent. Strict pass bar: foundational four all 4, ≤1 arc-level 3, no arc < 3. If revise: read `category_feedback`, apply lifts to the named pairs (use the same recipes as step 4), re-run pair gates → overall. Cap **2 overall-gate rounds**.

7. **If overall gate passes**: advance phase to `build`:
   ```
   venv/bin/python -c "
   from pipeline.programme_state import advance_phase, advance_phase  # content -> svg
   from pipeline.programme_state import advance_phase
   advance_phase('math_retrofit_2026_05', '<UNIT_ID>')  # content -> svg
   advance_phase('math_retrofit_2026_05', '<UNIT_ID>')  # svg -> build  (math = no-op SVG phase)
   "
   ```

8. **If still failing after caps**: mark unit blocked and continue:
   ```
   venv/bin/python -c "
   from pipeline.programme_state import update_unit
   update_unit('math_retrofit_2026_05', '<UNIT_ID>',
               status='blocked',
               blockers=['<short reason — failing categories from last verdict>'],
               event='content phase blocked')
   "
   ```

If the fire has used ≥ 1 phase of effort and there's still Phase C to do, you may either continue (if budget permits) or stop here — the next fire will pick up from `phase=build`.

### Phase C — build + visual inspection

1. **Hard-delete old Drive subfolder** (idempotent — no-op if missing):
   ```
   venv/bin/python -c "
   import json
   from pathlib import Path
   from pipeline.drive_helpers import hard_delete_unit_subfolder
   bp = json.loads(Path('<unit_dir>/0_blueprint.json').read_text())
   res = hard_delete_unit_subfolder(bp['thematic_title'], dry_run=False)
   print('drive cleanup:', res)
   "
   ```

2. **Compose worksheets** (subject-gated phonics dispatcher; attribute-card padding now in place):
   ```
   rm -rf <unit_dir>/composed && \
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.compose import compose_for_unit
   res = compose_for_unit(Path('<unit_dir>'))
   print('composed', len(res), 'images')
   "
   ```

3. **Validate slides** — auto-trim long fields if any:
   ```
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.slides import validate_unit_for_slides
   issues = validate_unit_for_slides(Path('<unit_dir>'))
   print('slides validation:', issues or 'clean')
   "
   ```
   If issues: trim per the rules (big_idea ≤100, lesson titles ≤30, discussion_prompts not too long). Re-validate. If still failing after one pass, mark blocked.

4. **Build deck with retry**:
   ```
   venv/bin/python <<'PY'
   import time
   from pathlib import Path
   from pipeline.slides import build_unit_deck
   from pipeline.drive_helpers import hard_delete_unit_subfolder
   import json
   ud = Path('<unit_dir>')
   bp = json.loads((ud / '0_blueprint.json').read_text())
   tt = bp['thematic_title']
   last_err, url = None, None
   for attempt in range(1, 6):
       if attempt > 1:
           hard_delete_unit_subfolder(tt, dry_run=False)
       try:
           url = build_unit_deck(ud, run_preflight=False)
           print(f'OK attempt {attempt}: {url}')
           break
       except Exception as e:
           last_err = e
           if 'publicly accessible' in str(e) or 'createImage' in str(e):
               time.sleep(30 * attempt)
           else:
               raise
   if last_err:
       print('FAILED:', last_err)
       raise SystemExit(1)
   PY
   ```
   Capture the URL. Save it to programme_state:
   ```
   venv/bin/python -c "
   from pipeline.programme_state import update_unit
   update_unit('math_retrofit_2026_05', '<UNIT_ID>',
               deck_url='<URL>', event='deck built')
   "
   ```

5. **Build visual_inspection prompt and spawn one Agent**:
   ```
   venv/bin/python -c "
   from pathlib import Path
   from pipeline.gates import build_visual_inspection_prompt
   p = build_visual_inspection_prompt(Path('<unit_dir>').resolve(), '<URL>')
   Path('/tmp/retrofit_visual.prompt.txt').write_text(p)
   "
   ```
   Spawn ONE visual_inspector Agent: instruct it to read /tmp/retrofit_visual.prompt.txt, walk the PDF in 5-7 page chunks, write `visual_inspection_verdict.json`, and validate via Pydantic. Pass bar: `blocking_count == 0`.

6. **If visual passes**: advance phase to `done`, update deck_url:
   ```
   venv/bin/python -c "
   from pipeline.programme_state import update_unit, advance_phase
   advance_phase('math_retrofit_2026_05', '<UNIT_ID>')  # build -> done (also sets status=done)
   update_unit('math_retrofit_2026_05', '<UNIT_ID>',
               event='unit complete')
   "
   ```

7. **If visual fails**: read the verdict's `issues`. Apply targeted fixes to lessons/composers/slides (see demo precedent: trim long discussion prompts, trim rubric descriptors, ensure phonics composers are subject-gated). Rebuild deck + re-inspect. Cap **2 visual rounds**. If still failing, mark blocked.

## Step 3 — final summary line

End every fire with one line:
```
[fire <ts>] picked=<unit_id> from=<phase_in> to=<phase_out> status=<status> blockers=<n>
```

## Step 4 — programme summary every 5th fire

Every 5th fire (track via a counter in programme_state.metadata if needed, or just always print): print `progress_summary("math_retrofit_2026_05")`. Surface any units with status=blocked at the top.

## Stop conditions

- Per-fire wall-clock approaching 18 minutes → stop after the current phase, do not start another.
- Token budget < 15% of 5-hour window → exit cleanly with `DEFERRED — budget low`.
- Any code raising an unexpected exception → log + mark unit blocked + exit. Do not retry blindly.
- `programme_state.next_unit()` returns None → disable the task via `mcp__scheduled-tasks__update_scheduled_task(taskId='tce-math-retrofit-continuous', enabled=False)`, print `"All 35 math units retrofitted; task self-disabled."`.

## What's already proven on g1_data_detectives

Every step above worked end-to-end on the demo. The pipeline:
- 5 parallel pair gates ran in ~2 min
- 2 rounds of lifts (puppet fix + lesson 1/3 surgical edits) cleared all 5 pair gates
- Overall gate passed first try
- Drive hard-delete + 1 retry on Slides API propagation built the deck
- Visual inspection found 5 → 3 → 0 blocking issues across 3 rounds (all addressed by composer fixes + content trims + a SKILL clarification)

Trust the recipe. Don't innovate inside a fire.
