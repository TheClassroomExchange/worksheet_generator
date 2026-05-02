# Ontario curriculum reference

Local mirror of Ontario MOE curriculum expectations, used by the worksheet
generator to validate that blueprint stage outputs cite real expectation codes.

## Coverage (Phase 1)

| File | Curriculum | Grades | Year | Rows |
|---|---|---|---|---|
| `math.json` | Elementary Mathematics | 1, 2, 3 | 2020 | 159 |
| `kindergarten.json` | Kindergarten Framework — all 4 frames (math is integrated, not a standalone strand) | K | 2026 | 127 |

286 expectations total (49 overall + 225 specific + the 12 K overall).

Out of scope today (deferred):
- Elementary English Language (not in the source CMS — only French exists there)
- Elementary Science & Technology (G1-3, 2022)
- Elementary Social Studies (G1-3, 2023)

The fetcher (`pipeline/curriculum_fetch.py`) covers all of these via the same API
walk; just add target tuples and rerun.

## Source

Officially published Ontario MOE curriculum, served by a public Kontent.ai
delivery API behind www.dcp.edu.gov.on.ca. No authentication required. The
project ID is exposed in the SPA's bundle. Crown copyright; freely
reproducible for educational use.

API base: `https://ws.api.dcp.edu.gov.on.ca/content/api/items`

Provenance for each fetched course is recorded in `sources.json`.

## Schema

Each row in `expectations`:

```jsonc
{
  "grade": "1",                  // "K" | "1" | "2" | "3"
  "subject": "math",             // "math" | "kindergarten"
  "curriculum_year": 2020,
  "strand_code": "B",            // letter (G1-3) or frame letter (K)
  "strand_name": "Number",
  "strand_note": "...",          // intro paragraph for the strand
  "code": "B1.1",                // canonical expectation code
  "title": "Whole Numbers",      // short label (may be empty for some K rows)
  "text": "read and represent whole numbers up to and including 50…",
  "expectation_type": "specific",   // "overall" | "specific"
  "parent_overall_code": "B1",      // (specific only)
  "source_codename": "math___grade_1___b1_1"  // for traceability back to CMS
}
```

## How to use

```python
from pipeline import curriculum

# Lookup
row = curriculum.get("Grade 1", "B1.1")
print(row["text"])

# Validate a blueprint's codes (this is what consistency_check does)
unknown = curriculum.validate_codes("Grade 1", ["B1.1", "Z9.9"])
# -> ["Z9.9"]

# Browse a grade/strand
codes = curriculum.list_codes("Grade 1", strand_code="C")
```

`pipeline/schemas.py::consistency_check` calls `validate_codes` automatically
after every blueprint stage completes.

## Refresh

The data is small (286 rows) and the underlying curriculum is revised on multi-
year cycles, so refreshes are manual. To re-fetch:

```bash
./venv/bin/python -m pipeline.curriculum_fetch
```

Raw API responses are saved to `curriculum/raw/` for re-parsing without re-
hitting the API.
