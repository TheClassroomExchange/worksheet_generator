# Language (Phonics) Worksheet Rubric — Grade 1

**Ontario reference:** Language (2023), **Strand B — Foundations of Language**, OE
**B2 Language Foundations for Reading and Writing** (B2.1 phonemic awareness; B2.2
alphabetic knowledge; B2.3 grapheme–phoneme correspondences; B2.4 phonics to read/
spell; B2.5 orthographic; B2.6 morphology; B2.8 reading fluency). Cite the
grade-correct **B2.x** code (verbatim from `curriculum/language.json`).

**Concept scope (G1):** one target per sheet across `phonics_scope.json` orders 34–85
(double consonants, -all/-oll/-ull, -nk, long vowels, VCe, vowel teams, soft c/g,
tch/dge, r-controlled, diphthongs, silent letters). Flagship type = **"I Can Read
Sentences"** (5 decodable sentences + pictures + 3× read tracker + highlight-the-pattern
word work). **G1 = roomy layout.**

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
- **L2:** Decodable, but the target pattern is barely present or a picture mismatches its sentence.
- **L3:** `decodability_run.json` passes (every word from taught graphemes + cumulative heart words); the target grapheme is genuinely exercised in every sentence; each picture matches its sentence.
- **L4:** All of L3 **and** the target appears in varied positions/word shapes; sentences are natural, not contrived word-lists.

### C3 — Structured-Phonics Pedagogy & Grade Fit *(HARD GATE — = L4)*
- **L1:** Sentences too long/complex, or no picture support, or mixes many new patterns.
- **L2:** Mostly G1-appropriate but one sentence overloads working memory.
- **L3:** Exactly one new target + cumulative review only; 5 short sentences; picture support; explicit highlight-the-pattern step; **roomy writing space honoured**.
- **L4:** All of L3 **and** read-3-times fluency routine + a stretch (write-your-own / sort) and an easier entry; follows the Drive "I Can Read Sentences" routine.

### C4 — Clarity, Layout & Template Fidelity
- **L1:** Cluttered; unclear what the child does.
- **L2:** Followable but visual flow inconsistent or cramped.
- **L3:** Clear tasks; matches the Drive template (corner tab w/ target, directions, 5 boxed sentences + pictures, 3× smiley tracker); images aligned to sentences.
- **L4:** All of L3 **and** a clean word-work strip; no near-empty page (`page_fill_ok`).

### C5 — Teacher Guide Completeness *(HARD GATE — = L4)*
- **L1:** Objective only.
- **L2:** Objective + steps, no answer key / facilitation script.
- **L3:** Plain-language objective, materials, step-by-step script, answer key (decodability notes), B2 code cited.
- **L4:** All of L3 **and** make-it-easier / make-it-harder + a 1-line "look-for" success indicator; no teacher jargon (T1 lint clean).

## Remediation mapping
- C1/C2 fail → re-author `content.json` + re-run decodability gate.
- C3/C4 fail → re-author worksheet body (shorten sentences / fix flow / add space).
- C5 fail → re-author teacher guide section only.
