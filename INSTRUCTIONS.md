# CLAUDE CODE — Batch Unit Generation Instructions

## What this project does
Generates full 7-lesson Ontario curriculum-aligned educational units using the Claude API.
Reads a content spec from the Excel spreadsheet, generates markdown + JSON files per unit,
and updates the spreadsheet status automatically.

---

## Step 1 — Environment setup

```bash
cd canadian_classroom_exchange
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Step 2 — Dry run (always do this first, zero cost)

```bash
python scripts/generate_units.py --batch 1 --dry-run
```

Expected output:
```
[1/5] Kindergarten · Mathematics · B. Number (Counting & Quantity)
  [DRY RUN] Would generate: Counting to Twenty: Bears & Blocks ...
[2/5] Grade 1 · Mathematics · F. Financial Literacy
  [DRY RUN] Would generate: Our Classroom Market: Canadian Coins ...
...
Done. Success: 0 | Failed: 0
```

If you see this — the spreadsheet is being read correctly. Proceed to Step 3.

---

## Step 3 — Run Batch 1 (5 pilot units)

```bash
python scripts/generate_units.py --batch 1
```

- Takes ~3–5 minutes
- Costs ~$0.40 CAD in API calls
- Outputs markdown + JSON files to: `generated_units/batch_1/`
- Auto-updates spreadsheet status to `generated`

---

## Step 4 — Run Batch 2 (after PM approves Batch 1)

```bash
python scripts/generate_units.py --batch 2
```

- 15 units, ~$1.20 CAD, ~12–15 minutes

---

## Step 5 — Run Batch 3 (after PM approves Batch 2)

```bash
# Run in chunks of 10 to allow rolling PM review
python scripts/generate_units.py --batch 3 --limit 10
python scripts/generate_units.py --batch 3 --limit 10
python scripts/generate_units.py --batch 3 --limit 10
```

- 30 units total, ~$2.40 CAD

---

## How to rerun a rejected unit

When PM marks a row `needs_regen` in the spreadsheet:

1. Copy PM's feedback from the PM Comments column into the Notes column of that row
2. Change the Status cell back to `pending`
3. Run the batch again — script only picks up `pending` rows:
   ```bash
   python scripts/generate_units.py --batch 1
   ```

---

## Output files per unit

Each generated unit produces two files in `generated_units/batch_X/`:

| File | Purpose |
|---|---|
| `unit_theme_name.md` | Human-readable — PM reviews this in Google Docs |
| `unit_theme_name.json` | Machine-readable — feeds into marketplace pipeline later |

---

## Spreadsheet status values

The script reads and writes the `Status` column automatically:

| Status | Meaning | Set by |
|---|---|---|
| `pending` | Ready to generate | PM / Engineer |
| `generated` | Script ran successfully | Script (auto) |
| `pm_review` | PM actively reviewing | PM |
| `approved` | Good to go — ready for image layer | PM |
| `needs_regen` | Rejected — needs a new generation | PM |

---

## Batch summary

| Batch | Sheet name | Units | Est. cost | Est. time |
|---|---|---|---|---|
| 1 | Batch 1 — Pilot | 5 | $0.40 CAD | 4 min |
| 2 | Batch 2 — Stress Test | 15 | $1.20 CAD | 15 min |
| 3 | Batch 3 — Scale | 30 | $2.40 CAD | 30 min |

---

## Folder structure

```
canadian_classroom_exchange/
├── INSTRUCTIONS.md                          ← you are here
├── .env.example                             → copy to .env, add API key
├── .env                                     (you create this — gitignored)
├── requirements.txt
├── canadian_classroom_content_batches.xlsx  ← PM edits this
│
├── scripts/
│   └── generate_units.py                    ← the generation script
│
├── generated_units/                         ← script writes here
│   ├── batch_1/
│   ├── batch_2/
│   └── batch_3/
│
└── docs/
    ├── ENGINEER_README.md                   ← full technical reference
    └── PM_REVIEW_GUIDE.md                   ← PM's review checklist
```

---

## Common issues

**"No pending rows found"**
→ The Status column in the spreadsheet has no `pending` values in that batch sheet.
→ Check you're on the right sheet tab and the Status column (column L) says `pending`.

**JSON parse error in output**
→ Claude occasionally returns malformed JSON under load.
→ The script marks it `needs_regen` automatically. Just rerun.

**API rate limit error**
→ Add `--limit 5` to run fewer units per session with a gap in between.

**Spreadsheet not found**
→ Make sure you're running from inside the `canadian_classroom_exchange/` folder,
   or adjust `EXCEL_PATH` at the top of `generate_units.py` to the full path.
