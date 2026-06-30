# Language (Phonics/Morphology) Worksheet Rubric — Grade 3

**Ontario reference:** Language (2023), **Strand B — Foundations of Language**, OE
**B2 Language Foundations for Reading and Writing** (G3: B2.1 *consolidated* phonics —
monosyllabic & multisyllabic; B2.2 orthographic; **B2.3 morphology — meanings of words
and morphemes: bases, prefixes, suffixes**; B2.5 reading fluency). Cite the
grade-correct **B2.x** code (verbatim from `curriculum/language.json`).

**Concept scope (G3 — extends the K–2 program):** one target per sheet across
`phonics_scope.json` orders 107+ — **morphology & multisyllabic decoding**: suffixes
(-s/-es, -ing, -ed, -er/-est, -ly/-y/-ful), prefixes (un-, re-, pre-, dis-, mis-),
syllable types (closed/open, compounds), contractions. Type = **Word-Building &
Sentences** (build base+affix → read decodable sentences). Standard layout.

## Scoring model
5 criteria, each **L1–L4 (1–4 pts)** → **/20**. Walk each checklist top-down; stop at
the highest level where *every* item is met.
> **PUBLISH GATE (all grades, enforced by `pipeline/language_rubric.py`): total ≥ 19/20
> AND C2 ≥ L3 AND C3 = L4 AND C5 = L4.** Only droppable point: C1 or C4 → L3.

### C1 — Ontario Strand-B Alignment
- **L1:** Names a skill but the task doesn't exercise it.
- **L2:** Task touches the skill; link to B2 implied, not stated.
- **L3:** Task clearly exercises one B2 skill (esp. B2.3 morphology); the teacher guide cites the specific B2.x code.
- **L4:** All of L3 **and** the verbatim B2 text + a plain "In plain terms:" gloss.

### C2 — Decodability & Phonetic/Morphological Accuracy *(HARD GATE — must be ≥ L3)*
- **L1:** A base or affixed word uses a grapheme not yet taught, or an affix changes a base spelling incorrectly (e.g. wrong doubling/drop-e).
- **L2:** Decodable, but the target morpheme is barely present or spelling-change rule is inconsistent.
- **L3:** `decodability_run.json` passes (bases decodable from cumulative graphemes; affixes/heart words allowed); the target morpheme is genuinely exercised; any spelling change (double final consonant / drop silent e / y→i) is applied correctly and stated in the key.
- **L4:** All of L3 **and** base→affixed meaning shift is made explicit; multisyllabic examples included; natural sentences.

### C3 — Structured-Phonics/Morphology Pedagogy & Grade Fit *(HARD GATE — = L4)*
- **L1:** Overloads multiple morphemes or sentences too dense for G3.
- **L2:** Mostly G3-appropriate but one item assumes an untaught base/affix.
- **L3:** Exactly one new morpheme/syllable target + cumulative review; explicit build step (base + affix → word) then read in context.
- **L4:** All of L3 **and** a meaning/word-sort stretch + an easier entry; consolidated-phonics fluency in the sentences.

### C4 — Clarity, Layout & Template Fidelity
- **L1:** Cluttered; unclear tasks.
- **L2:** Followable but visual flow inconsistent.
- **L3:** Clear build-table + boxed sentences + pictures matching the Drive design family; images aligned.
- **L4:** All of L3 **and** clean word-building grid; no near-empty page (`page_fill_ok`).

### C5 — Teacher Guide Completeness *(HARD GATE — = L4)*
- **L1:** Objective only.
- **L2:** Objective + steps, no answer key / facilitation script.
- **L3:** Plain-language objective, materials, step-by-step script, answer key (with spelling-change rules), B2 code cited.
- **L4:** All of L3 **and** make-it-easier / make-it-harder + a 1-line "look-for" success indicator; no teacher jargon (T1 lint clean).

## Remediation mapping
- C1/C2 fail → re-author `content.json` + re-run decodability gate.
- C3/C4 fail → re-author worksheet body.
- C5 fail → re-author teacher guide section only.
