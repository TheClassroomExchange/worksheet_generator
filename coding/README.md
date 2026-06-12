# Coding Worksheets — K–3 Pipeline (planning)

Design docs for adapting this `worksheet_generator` pipeline (today: K-3 Ontario
**Math** → Google Slides) to generate **original, Ontario-aligned K–G3 coding
worksheets** as branded **PDFs**, organized grade → subject → topic in Google
Drive, with **original kawaii mascot SVGs**.

> Status: **planned, not yet built.** Source corpus (`Coding Resources-Kassandra`)
> is two companies' copyrighted curriculum + MIT Scratch cards — we mirror
> *structure only* and generate original content. Never clone verbatim or reuse
> their mascot/art.

## Contents
- **[PLAN.md](PLAN.md)** — full adaptation plan: source review, output structure, pipeline reuse/change/build map, stages, gates, pilot (Grade 3 · Block Coding).
- **[HANDOFF.md](HANDOFF.md)** — resume-here summary: decisions, Drive IDs, next steps, gotchas.
- **[rubrics/](rubrics/)** — per-grade content rubrics (become `assets/rubric_coding_<grade>.md` at build time; `pipeline/rubric.py` selects by grade):
  - `rubric_coding_K.md`, `rubric_coding_G1.md`, `rubric_coding_G2.md`, `rubric_coding_G3.md`
  - 5 criteria × L1–L4 = /20; **pass ≥15 AND Criterion 2 (concept correctness) ≥ L3** (hard gate, tied to the code-runs gate).

## Subjects per grade (final)
| Grade | Subjects |
|---|---|
| K | Unplugged Computational Thinking · Sequencing & Algorithms · Intro Block Coding |
| G1 | Block Coding (Sequential Events) · Unplugged Sequencing & Algorithms · Intro Debugging |
| G2 | Block Coding (Concurrent Events) · Events & Parallel Scripts · Debugging & Reading Code |
| G3 | Block Coding (incl. loops) · Intro Python Turtle · Debugging |
