# Language (Phonics) Worksheet Rubric — Grade 2

**Ontario reference:** Language (2023), **Strand B — Foundations of Language**, OE
**B2 Language Foundations for Reading and Writing** (G2: B2.1 phonics — monosyllabic
& multisyllabic incl. set-for-variability; B2.2 orthographic; B2.3 morphology; B2.5
reading fluency). Cite the grade-correct **B2.x** code (verbatim from
`curriculum/language.json`).

**Concept scope (G2):** one target per sheet across `phonics_scope.json` orders 86–106
(silent letters gn/gh, low-frequency vowel spellings au/aw/al/augh, ew/ui/ue,
air/are/ear, ei/ey/eigh/aigh/ea, ch=/k/, or/ar=/er/, schwa). Flagship type = **"I Can
Read Sentences"** + word-sort/spelling-choice word work. Standard (non-roomy) layout.

## Scoring model
5 criteria, each **L1–L4 (1–4 pts)** → **/20**. Walk each checklist top-down; stop at
the highest level where *every* item is met.
> **PUBLISH GATE (all grades, enforced by `pipeline/language_rubric.py`): total ≥ 19/20
> AND C2 ≥ L3 AND C3 = L4 AND C5 = L4.** Only droppable point: C1 or C4 → L3.

### C1 — Ontario Strand-B Alignment
- **L1:** Names a skill but the task doesn't exercise it.
- **L2:** Task touches the skill; link to B2 implied, not stated.
- **L3:** Task clearly exercises one B2 skill; the teacher guide cites the specific B2.x code.
- **L4:** All of L3 **and** the verbatim B2 text + a plain "In plain terms:" gloss.

### C2 — Decodability & Phonetic Accuracy *(HARD GATE — must be ≥ L3)*
- **L1:** Any word/picture uses a grapheme not yet taught (decodability gate fails).
- **L2:** Decodable, but the target spelling is barely present or a picture mismatches its sentence.
- **L3:** `decodability_run.json` passes; the target grapheme is genuinely exercised; pictures match; where the target is one of several spellings of a sound, the sheet stays on its assigned spelling.
- **L4:** All of L3 **and** contrasts the target spelling with a known same-sound spelling (set-for-variability), in natural sentences.

### C3 — Structured-Phonics Pedagogy & Grade Fit *(HARD GATE — = L4)*
- **L1:** Overloads new patterns or sentences too dense for G2.
- **L2:** Mostly G2-appropriate but one item assumes an untaught spelling.
- **L3:** Exactly one new target + cumulative review; sentences allow monosyllabic AND a multisyllabic example; explicit word-sort/spelling-choice step.
- **L4:** All of L3 **and** a fluency routine + stretch (own sentence / sort by spelling) and an easier entry.

### C4 — Clarity, Layout & Template Fidelity
- **L1:** Cluttered; unclear tasks.
- **L2:** Followable but visual flow inconsistent.
- **L3:** Clear tasks; matches the Drive template (tab, directions, boxed sentences + pictures, tracker); word-sort grid legible; images aligned.
- **L4:** All of L3 **and** clean spelling-choice/sort layout; no near-empty page (`page_fill_ok`).

### C5 — Teacher Guide Completeness *(HARD GATE — = L4)*
- **L1:** Objective only.
- **L2:** Objective + steps, no answer key / facilitation script.
- **L3:** Plain-language objective, materials, step-by-step script, answer key, B2 code cited.
- **L4:** All of L3 **and** make-it-easier / make-it-harder + a 1-line "look-for" success indicator; no teacher jargon (T1 lint clean).

## Remediation mapping
- C1/C2 fail → re-author `content.json` + re-run decodability gate.
- C3/C4 fail → re-author worksheet body.
- C5 fail → re-author teacher guide section only.
