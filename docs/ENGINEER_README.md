# Unit Generation Script — Engineer Setup Guide

## What this does
Reads the content spec spreadsheet, calls Claude API to generate full 7-lesson units,
saves markdown + JSON files, and updates the spreadsheet status automatically.

## Setup (one time)

```bash
# 1. Install dependencies
pip install anthropic openpyxl

# 2. Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Make sure the spreadsheet is in the same folder as the script
ls canadian_classroom_content_batches.xlsx  # should exist
```

## Running a batch

```bash
# Always do a dry run first — no API calls, just shows what would run
python generate_units.py --batch 1 --dry-run

# Run Batch 1 (all 5 pending units)
python generate_units.py --batch 1

# Run just the first 2 units of Batch 1 (good for initial testing)
python generate_units.py --batch 1 --limit 2

# Run Batch 2 after Batch 1 is approved
python generate_units.py --batch 2

# Run just 5 units from Batch 3 at a time
python generate_units.py --batch 3 --limit 5
```

## Output structure

```
generated_units/
├── batch_1/
│   ├── our_classroom_market.md        ← PM reviews this
│   ├── our_classroom_market.json      ← raw data, ignore for now
│   ├── counting_to_twenty_bears.md
│   └── ...
├── batch_2/
│   └── ...
└── batch_3/
    └── ...
```

## What happens to the spreadsheet

The script automatically updates:
- **Status** column: `pending` → `generated` (or `needs_regen` if it failed)
- **PM Comments** column: adds filename + suggested price from the generated unit

Your PM then updates Status to `approved` or `needs_regen` with their feedback.

## Rerunning a failed or rejected unit

1. PM marks row as `needs_regen` and adds specific feedback in PM Comments
2. Temporarily change status back to `pending` in the spreadsheet
3. Add the PM feedback to the `notes` column of that row
4. Run: `python generate_units.py --batch 1 --limit 1`
   (it picks up the first pending row)

## Cost estimate

| Run | Units | Est. API cost |
|---|---|---|
| Batch 1 | 5 | ~$0.40 CAD |
| Batch 2 | 15 | ~$1.20 CAD |
| Batch 3 | 30 | ~$2.40 CAD |
| All 50 | 50 | ~$4.00 CAD |

## Adjusting the prompt

If Batch 1 output quality needs tuning, edit the `build_prompt()` function
in `generate_units.py`. Specifically:

- **Too much variance in lesson length?** Add to prompt: "Each lesson must be exactly 45 minutes."
- **Missing Canadian context?** Add: "Every example must use a Canadian setting, person, or object."
- **Worksheets too hard/easy?** Add grade-specific calibration notes.
- **PM keeps rejecting a strand?** Add the PM's feedback as an explicit constraint.

## Connecting to the marketplace pipeline (Week 2+)

The `.json` files are already structured for Agent 2 (Listing Automation).
The `marketplace_metadata` block maps directly to your Supabase `educational_resources` table.
The `image_placeholders` blocks in each worksheet will feed the image generation script.
