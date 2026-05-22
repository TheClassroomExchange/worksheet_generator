"""Gate runners — the bridge between manifest stages and the agent skills.

Each runner:
1. Loads the relevant unit_dir files
2. Builds a prompt for the agent that points at the relevant skill
3. (In production) spawns an agent via the Agent tool and parses the response
4. Validates the response against the relevant Pydantic schema
5. Writes the verdict file to unit_dir/
6. Returns the parsed verdict object so callers can route remediation

In this module the agent-spawn is encapsulated by ``call_grader_agent``,
which is a placeholder that callers can override (e.g., the production
runner uses Claude's Agent tool; tests can stub it).

Pydantic schemas live in pipeline.schemas:
    PairRubricVerdict, OverallUnitVerdict, VisualInspectionVerdict
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .schemas import (
    PairRubricVerdict,
    OverallUnitVerdict,
    VisualInspectionVerdict,
)


PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = Path(__file__).parent / "skills"


# ── Prompt builders ──────────────────────────────────────────────────


def _read_skill(name: str) -> str:
    """Read pipeline/skills/<name>/SKILL.md verbatim."""
    p = SKILLS_DIR / name / "SKILL.md"
    if not p.exists():
        raise FileNotFoundError(f"Skill not found: {p}")
    return p.read_text(encoding="utf-8")


def build_pair_gate_prompt(unit_dir: Path, pair_n: int) -> str:
    """Build the prompt for the pair_rubric_grader agent."""
    bp = (unit_dir / "0_blueprint.json").read_text(encoding="utf-8")
    lp = (unit_dir / f"1_lesson_{pair_n:02d}.json").read_text(encoding="utf-8")
    ws = (unit_dir / f"2_worksheet_{pair_n:02d}.json").read_text(encoding="utf-8")
    ir_path = unit_dir / "input_row.json"
    ir = ir_path.read_text(encoding="utf-8") if ir_path.exists() else "{}"
    skill = _read_skill("pair_rubric_grader")

    return f"""You are the pair_rubric_grader agent for the TCE K-G3 curriculum
generator.

Read the SKILL document below carefully, then grade pair {pair_n} of unit
{unit_dir.name}. Inputs follow the SKILL. Emit ONE JSON object that
validates against pipeline.schemas.PairRubricVerdict (no prose outside
the JSON).

## SKILL document

{skill}

## Inputs

### blueprint (0_blueprint.json)
```json
{bp}
```

### lesson_{pair_n:02d} (1_lesson_{pair_n:02d}.json)
```json
{lp}
```

### worksheet_{pair_n:02d} (2_worksheet_{pair_n:02d}.json)
```json
{ws}
```

### input_row.json
```json
{ir}
```

## Output target path
Write your JSON verdict ONLY (no Markdown wrapper, no prose) to:
{unit_dir}/pair_{pair_n:02d}_verdict.json

When the JSON is written, end your response with the literal line
"DONE" so the caller knows you're finished.
"""


def build_overall_gate_prompt(unit_dir: Path) -> str:
    bp = (unit_dir / "0_blueprint.json").read_text(encoding="utf-8")
    lessons = []
    worksheets = []
    for i in range(1, 6):
        lp = unit_dir / f"1_lesson_{i:02d}.json"
        ws = unit_dir / f"2_worksheet_{i:02d}.json"
        if lp.exists():
            lessons.append(f"### lesson_{i:02d}\n```json\n{lp.read_text(encoding='utf-8')}\n```")
        if ws.exists():
            worksheets.append(f"### worksheet_{i:02d}\n```json\n{ws.read_text(encoding='utf-8')}\n```")
    pair_verdicts = []
    for i in range(1, 6):
        pv = unit_dir / f"pair_{i:02d}_verdict.json"
        if pv.exists():
            pair_verdicts.append(f"### pair_{i:02d}_verdict\n```json\n{pv.read_text(encoding='utf-8')}\n```")
    skill = _read_skill("overall_unit_grader")

    return f"""You are the overall_unit_grader agent for the TCE K-G3
curriculum generator.

Read the SKILL document below carefully, then grade the entire unit
{unit_dir.name}. All 5 pair gates have already passed (verdicts attached
for context). Emit ONE JSON object validating against
pipeline.schemas.OverallUnitVerdict. No prose outside the JSON.

## SKILL document

{skill}

## Inputs

### blueprint
```json
{bp}
```

{chr(10).join(lessons)}

{chr(10).join(worksheets)}

### Pair-gate verdicts (FYI)
{chr(10).join(pair_verdicts)}

## Output
Write the JSON verdict to: {unit_dir}/overall_unit_verdict.json
End your response with "DONE".
"""


def build_visual_inspection_prompt(unit_dir: Path, deck_url: str) -> str:
    bp_text = (unit_dir / "0_blueprint.json").read_text(encoding="utf-8")
    pdf = unit_dir / "validation_export.pdf"
    skill = _read_skill("visual_inspector")

    return f"""You are the visual_inspector agent for the TCE K-G3 curriculum
generator.

Read the SKILL document below carefully, then inspect every slide in
the deck PDF for unit {unit_dir.name}. Use the Read tool with the
``pages`` parameter to walk the PDF in chunks.

## SKILL document

{skill}

## Deck

- Live URL (for reference): {deck_url}
- Local PDF: {pdf}
- Blueprint context (so you know what characters and manipulatives to expect):

```json
{bp_text}
```

## Output
Write your VisualInspectionVerdict JSON to:
{unit_dir}/visual_inspection_verdict.json

End your response with "DONE".
"""


# ── Verdict loaders / validators ─────────────────────────────────────


def load_pair_verdict(unit_dir: Path, pair_n: int) -> PairRubricVerdict:
    p = unit_dir / f"pair_{pair_n:02d}_verdict.json"
    return PairRubricVerdict.model_validate_json(p.read_text(encoding="utf-8"))


def load_overall_verdict(unit_dir: Path) -> OverallUnitVerdict:
    p = unit_dir / "overall_unit_verdict.json"
    return OverallUnitVerdict.model_validate_json(p.read_text(encoding="utf-8"))


def load_visual_verdict(unit_dir: Path) -> VisualInspectionVerdict:
    p = unit_dir / "visual_inspection_verdict.json"
    return VisualInspectionVerdict.model_validate_json(p.read_text(encoding="utf-8"))


# ── Hooks for the orchestrator ───────────────────────────────────────


GraderAgent = Callable[[str], str]
"""Callable that takes a prompt and returns the agent's response.

In production this wraps the Agent tool. In tests / one-shot demos the
caller can stub it. Either way the runner doesn't care — it parses
whatever JSON file the agent wrote to disk.
"""


def run_pair_gate(unit_dir: Path, pair_n: int, agent: GraderAgent) -> PairRubricVerdict:
    """Spawn the pair_rubric_grader, write verdict, validate, return."""
    prompt = build_pair_gate_prompt(unit_dir, pair_n)
    _ = agent(prompt)
    return load_pair_verdict(unit_dir, pair_n)


def run_overall_gate(unit_dir: Path, agent: GraderAgent) -> OverallUnitVerdict:
    prompt = build_overall_gate_prompt(unit_dir)
    _ = agent(prompt)
    return load_overall_verdict(unit_dir)


def run_visual_inspection(unit_dir: Path, deck_url: str,
                           agent: GraderAgent) -> VisualInspectionVerdict:
    prompt = build_visual_inspection_prompt(unit_dir, deck_url)
    _ = agent(prompt)
    return load_visual_verdict(unit_dir)
