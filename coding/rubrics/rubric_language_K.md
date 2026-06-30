# Language (Phonics) Worksheet Rubric — Kindergarten

**Ontario reference:** The Kindergarten Program (2025), **Strand A — Foundations of
Language and Mathematics**, OE **A2 Foundations for Reading and Writing** (A2.1 name
letters; A2.2 letter formation; A2.3 isolate/blend/segment phonemes; A2.4 simple
grapheme–phoneme correspondences; A2.5 read/spell simple words; A2.6 read short
sentences). Cite the grade-correct **A2.x** code (verbatim from `curriculum/language.json`).

**Concept scope (K):** one grapheme–phoneme correspondence per sheet, single letters
through first digraphs/CVC (`phonics_scope.json` orders 1–33). Letter formation,
beginning-sound picture cue, sound boxes (say-it→map-it→write-it), simple CVC reading.
Early single-letter sheets DO NOT use decodable sentences. **K/G1 = roomy layout.**

## Scoring model
5 criteria, each **L1–L4 (1–4 pts)** → **/20**. Walk each checklist top-down; stop at
the highest level where *every* item is met.
> **PUBLISH GATE (all grades, enforced by `pipeline/language_rubric.py`): total ≥ 19/20
> AND C2 ≥ L3 AND C3 = L4 AND C5 = L4.** Only droppable point: C1 or C4 → L3.

### C1 — Ontario Strand-A Alignment
- **L1:** Names a skill but the task doesn't exercise it.
- **L2:** Task touches the skill; link to A2 implied, not stated.
- **L3:** Task clearly exercises one A2 skill; the teacher guide cites the specific A2.x code.
- **L4:** All of L3 **and** the verbatim A2 text + a plain "In plain terms:" gloss.

### C2 — Decodability & Phonetic Accuracy *(HARD GATE — must be ≥ L3)*
- **L1:** Any word/picture uses a sound not yet taught (decodability gate fails).
- **L2:** Decodable, but the target sound is barely present or a picture mismatches its word.
- **L3:** `decodability_run.json` passes (every word from taught graphemes + heart words); the target grapheme is genuinely exercised; every picture matches its word/sound.
- **L4:** All of L3 **and** the target sound appears in varied positions (initial/medial/final) appropriate to the lesson.

### C3 — Structured-Phonics Pedagogy & Grade Fit *(HARD GATE — = L4)*
- **L1:** Requires reading beyond range, too many items, or no picture support.
- **L2:** Mostly K-appropriate but one element assumes fluency/fine-motor beyond range.
- **L3:** One idea per page; picture-supported; large targets; explicit (model the sound), no unsupported reading; **roomy writing space honoured**.
- **L4:** All of L3 **and** I-do/we-do/you-do scaffold + an oral/movement option; review of a prior sound where the routine expects it.

### C4 — Clarity, Layout & Template Fidelity
- **L1:** Cluttered; unclear what the child does.
- **L2:** Followable but visual flow inconsistent or cramped.
- **L3:** Clear single task; strong left→right/top→down flow; matches the Drive template (formation lines / sound boxes / beginning-sound picture); images aligned to prompts.
- **L4:** All of L3 **and** a worked model the child then repeats; no near-empty page (`page_fill_ok`).

### C5 — Teacher Guide Completeness *(HARD GATE — = L4)*
- **L1:** Objective only.
- **L2:** Objective + steps, no answer key / facilitation script.
- **L3:** Plain-language objective, materials, step-by-step script, answer key, A2 code cited.
- **L4:** All of L3 **and** make-it-easier / make-it-harder + a 1-line "look-for" success indicator; no teacher jargon (T1 lint clean).

## Remediation mapping
- C1/C2 fail → re-author `content.json` + re-run decodability gate.
- C3/C4 fail → re-author worksheet body (reduce load / fix flow / add space).
- C5 fail → re-author teacher guide section only.
