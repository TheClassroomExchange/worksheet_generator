# Canadian Classroom Exchange — Content Generation

## Folder structure

```
canadian_classroom_exchange/
├── .env.example                             # Copy to .env and add your keys
├── requirements.txt                         # pip install -r requirements.txt
├── canadian_classroom_content_batches.xlsx  # Content spec — PM edits this
│
├── scripts/
│   └── generate_units.py                    # Main generation script
│
├── generated_units/                         # Script writes output here
│   ├── batch_1/
│   ├── batch_2/
│   └── batch_3/
│
└── docs/
    ├── ENGINEER_README.md                   # Setup + usage guide
    └── PM_REVIEW_GUIDE.md                   # PM review checklist
```

## Quick start

```bash
# 1. Open this folder in VS Code

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env — add your Anthropic API key

# 5. Dry run first (zero API calls, zero cost)
python scripts/generate_units.py --batch 1 --dry-run

# 6. Run Batch 1 — 5 pilot units (~$0.40 CAD in API cost)
python scripts/generate_units.py --batch 1

# 7. Share the generated_units/batch_1/ folder with your PM for review
```

## Batch commands

```bash
# Test cheaply — first 2 units only
python scripts/generate_units.py --batch 1 --limit 2

# Full batch runs
python scripts/generate_units.py --batch 1   # 5 units
python scripts/generate_units.py --batch 2   # 15 units
python scripts/generate_units.py --batch 3   # 30 units

# Partial batch 3 run (5 at a time)
python scripts/generate_units.py --batch 3 --limit 5
```

## How the workflow runs

```
PM fills spreadsheet (grade + strand + notes)
        ↓
Engineer runs: python scripts/generate_units.py --batch 1 --limit 2
        ↓
Markdown files appear in generated_units/batch_1/
Spreadsheet status auto-updates to "generated"
        ↓
PM reviews .md files in Google Docs
PM updates spreadsheet: "approved" or "needs_regen" + feedback
        ↓
Engineer reruns for any needs_regen rows
        ↓
All approved → run Batch 2
```

## See docs/ for full setup and review guides.
