# Agent bootstrap — fresh-machine setup

Step-by-step setup for a new operator (human or agent) to run the worksheet generator
end-to-end. After completing this guide, an agent can resume the K-G3 Math programme from
wherever the last session left off.

> **Time required:** ~20 min, plus a few manual clicks for Google OAuth consent.

---

## Prerequisites

Verify these exist on the target machine before starting:

```bash
python3 --version          # ≥ 3.10
git --version              # any modern version
which rsvg-convert         # /opt/homebrew/bin/rsvg-convert or /usr/bin/rsvg-convert
```

If `rsvg-convert` is missing:

```bash
# macOS
brew install librsvg

# Debian / Ubuntu
sudo apt-get update && sudo apt-get install -y librsvg2-bin

# Fedora / RHEL
sudo dnf install librsvg2-tools
```

You also need:

- A Google Cloud account (free tier is fine).
- Write access to the shared TCE Drive folder (ask the project owner for the folder ID).
- [Claude Code](https://claude.com/claude-code) installed and authenticated. The pipeline
  cannot run without it — Claude Code is the *runner*.

---

## 1. Clone and install

```bash
# Pick any parent directory you like; the agent does not care about its location.
cd ~/code        # or wherever you keep repos
git clone https://github.com/TheClassroomExchange/worksheet_generator.git
cd worksheet_generator

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Verify:

```bash
./venv/bin/python -c "from pipeline import unit_plan, manifest, schemas, slides; print('imports OK')"
```

---

## 2. Google OAuth — Slides + Drive APIs

The pipeline writes Google Slides decks and uploads composite PNGs to a shared Drive folder.
This step is manual; the agent cannot do it.

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `tce-worksheet-generator`) or select an existing one.
3. Enable two APIs:
   - **Google Slides API**
   - **Google Drive API**
4. **Credentials → Create Credentials → OAuth client ID → Desktop app.** Name it whatever.
5. Download the JSON. Save it at the project root as `credentials.json`:
   ```bash
   mv ~/Downloads/client_secret_*.json credentials.json
   ```
6. Run the one-shot auth helper. A browser window opens; click through the consent screen.
   ```bash
   ./venv/bin/python auth_only.py
   ```
   On success, `token.json` is written. Verify:
   ```bash
   ls -la credentials.json token.json
   ```

> **Both files are in `.gitignore` — never commit them.** If they leak, rotate the OAuth
> client secret in Google Cloud Console immediately.

---

## 3. Configure the shared Drive folder

The Drive folder ID where decks publish lives in `pipeline/slides.py` (search for the
`SHARED_FOLDER_ID` constant or equivalent). The OAuth user from step 2 must have **Editor**
access to that folder.

If the folder ID needs to change for a new deployment:

1. In Drive, create or pick the folder.
2. Copy the ID from the URL (`drive.google.com/drive/folders/<ID>`).
3. Update `pipeline/slides.py`.
4. Make sure the OAuth user has Editor access.

---

## 4. Install the Claude Code skill

The autonomous flow depends on the **`tce-unit-builder`** skill. The vendored copy lives in
this repo at `.claude/skills/tce-unit-builder/SKILL.md`. Symlink it into your Claude Code
skills directory so Claude can pick it up:

```bash
mkdir -p ~/.claude/skills
ln -sf "$(pwd)/.claude/skills/tce-unit-builder" ~/.claude/skills/tce-unit-builder
```

Verify:

```bash
ls -la ~/.claude/skills/tce-unit-builder/SKILL.md
```

The symlink means future `git pull`s on this repo automatically update the skill — no need to
re-install.

> Prefer copying instead of symlinking? Use `cp -r .claude/skills/tce-unit-builder ~/.claude/skills/`
> — but remember to re-copy after each `git pull`.

---

## 5. Sanity check

Run the full session-start protocol:

```bash
./venv/bin/python -c "
from pathlib import Path
from pipeline import unit_plan, manifest
from pipeline.curriculum_reference import report_reference_status

unit_plan.refresh_state_from_disk()
print(unit_plan.status_table())

print('\n=== Curriculum reference status ===')
for line in report_reference_status(): print(line)

nxt = unit_plan.next_unit_to_generate()
if nxt:
    ud = Path('generated_units') / nxt.batch / nxt.unit_id
    try:
        m = manifest.load(ud); ns = manifest.next_pending(m)
    except FileNotFoundError:
        ns = '(unit not initialised; will need init_unit_from_plan)'
    print(f'\nNEXT UNIT:  {nxt.unit_id}  ({nxt.grade})')
    print(f'NEXT STAGE: {ns}')
"
```

Expected output: a programme-wide status checklist, the curriculum reference verification
status (verified / best_effort / needs_human per grade), and the next unit + stage to work on.

If this prints without import errors and shows a sensible "NEXT" line, the install is good.

---

## 6. First autonomous run

Open Claude Code in the project root:

```bash
cd ~/code/worksheet_generator       # adjust to your path
claude
```

In the session, paste:

```
Continue the K-G3 Math programme. Refresh state from disk, resume the next pending stage,
and stop after one stage completes cleanly.
```

The `tce-unit-builder` skill should activate automatically (you'll see it triggered in the
session). Claude reads `CLAUDE.md`, runs the status table, picks the next pending stage,
generates it, validates, and stops.

For a fully hands-off batch run, paste `AUTOMATED_RUN_PROMPT.md` instead. Walk away. Return
when the report appears.

---

## 7. Schedule recurring runs (optional)

To progress the 40-unit programme automatically over weeks:

```
/schedule daily at 9am: Continue the K-G3 Math programme. Refresh state from disk, resume the
next pending stage, and stop after one stage completes cleanly. Print status_table() at the
end so the next session knows where to pick up.
```

Stop conditions for a scheduled run:

- A stage was marked `done` (safe stop).
- All four drift gates clean **and** progress was made this session.
- Never stop with a stage left in `in_progress` — the runbook either finishes it or reverts
  it to `pending`.

Monitor by:

- Running step 5's sanity-check command — it prints the full programme state.
- Reading `generated_units/<batch>/<unit>/run.log.jsonl` for per-stage transition history.
- Reading `generated_units/<batch>/<unit>/manifest.json` for current state.

---

## 8. Updating the curriculum reference

When Ontario revises the curriculum, refresh the cached reference:

```bash
./venv/bin/python -m pipeline.curriculum_fetch
```

This re-pulls `curriculum/kindergarten.json` and `curriculum/math.json` from the public
Kontent.ai delivery API behind dcp.edu.gov.on.ca. Re-run the sanity check afterwards — units
already generated against the old reference will start failing
`verify_curriculum_text` until their `input_row.json` is updated.

---

## What's NOT vendored

The repo intentionally does **not** vendor:

- `credentials.json` / `token.json` — your Google OAuth creds (you supply them).
- The shared TCE Drive folder ID — configured per-deployment in `pipeline/slides.py`.
- Long-form architectural memory files in `~/.claude/projects/.../memory/` — those are
  user-specific auto-memories. The operationally important bits are already in `CLAUDE.md`,
  `README.md`, and the vendored skill.

---

## Troubleshooting bootstrap issues

| Symptom | Fix |
|---|---|
| `pip install` fails on Pillow | Install Pillow's system deps: `brew install libjpeg zlib` (macOS) or `apt-get install libjpeg-dev zlib1g-dev` (Linux). |
| `rsvg-convert: command not found` | Re-run the `librsvg` install for your OS (see Prerequisites). |
| `auth_only.py` can't open browser | Run on a desktop machine; SSH-only environments need a manual flow (set `flow.run_local_server(port=0, open_browser=False)` and copy the printed URL). |
| Google API 403 / `insufficient_scope` | Delete `token.json` and re-run `auth_only.py` to re-consent with the right scopes. |
| Skill not triggering in Claude Code | Verify `~/.claude/skills/tce-unit-builder/SKILL.md` exists (symlink or copy). Restart Claude Code to re-scan skills. |
| `import pipeline` fails | You're not in the project root, or the venv isn't active. `cd` to the repo root and `source venv/bin/activate`. |
| Drive 403 on `build_unit_deck` | The OAuth user doesn't have Editor access to the shared TCE folder. Get access from the project owner. |
| Status table shows everything `complete` | The programme is done. Nothing to generate. Verify by inspecting `unit_plan.json`. |

---

## Reference

- [README](../README.md) — system overview, repo layout, agent setup notes.
- [CLAUDE.md](../CLAUDE.md) — runbook Claude reads at session start.
- [AUTOMATED_RUN_PROMPT.md](../AUTOMATED_RUN_PROMPT.md) — copy-paste prompt for fully
  autonomous runs.
- [.claude/skills/tce-unit-builder/SKILL.md](../.claude/skills/tce-unit-builder/SKILL.md) —
  the vendored skill that drives autonomous runs.
- [assets/rubric_product_assessment.md](../assets/rubric_product_assessment.md) — the gold
  standard every unit must clear (≥17/20).
