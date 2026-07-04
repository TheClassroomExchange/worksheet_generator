# Standing quality gates (language pipeline)

`language/quality_gates.py` promotes the rules that were previously enforced only by
one-off remediation sweeps (`reveal_fix` / `dedup_fix` / `tg_fix` / `face_fix`) into the
**durable build path**. `run_quality_gates(unit_dir, content, grade, pdf)` is called by
`language_build.build_unit` after `fit_render` (needs the rendered PDF). Any violation
**raises `QualityGateError`** — a bad build cannot pass. This is what stops a fresh
rebuild (or a new subject) from silently reintroducing the 8 rounds of fixes.

## The gates
| Gate | Fails when | Source of truth |
|---|---|---|
| **G1 kid-safe** | a blocked word appears in any student-facing token | `kidsafe_blocklist.json` (`blocked` + context `allow`) |
| **G2 distinct** | a reading sheet repeats a picture or grapheme example word beyond allowance | `allow_repeats.json` (per-grapheme, inventory-limited) |
| **G3 image-in-sentence** | a picture word does not appear in its own sentence (stem-tolerant) | — |
| **G4 face/object** | an image word is classified neither animate nor inanimate (would render silently faceless) | `image_words.json` (`animate` / `inanimate`) |
| **G5 teacher-guide** | the answer key is blank (`—`) or drifts from `derive_teacher_guide`, or the step-3 verb mismatches | `gen_content.derive_teacher_guide` |
| **G6 page-count** | the combined PDF is > 2 pages | — |

## Correct-by-construction (generator side)
- `gen_content._clean_reading_rows` — `gen_word_building` picks the first N **distinct,
  valid** rows (skips a duplicate/mismatched picture) instead of a blind `[:3]`.
- `phonics_images._is_animate` — RAISES on an unclassified word (no silent faceless);
  `_ai` uses `concrete_prompts.json` for abstract/homograph words (photo/foil/nail/...).

## Run the catalogue control
```
cd ~/Desktop/TCE/wg-language
python3 -m language.quality_gates            # scan every canonical unit (expect 0 failures)
python3 -m language.quality_gates <unit_dir> # one unit
```
A new image word or a new inventory-limited grapheme requires a one-line addition to the
matching JSON (the gate tells you which). The gates found 2 real residual defects on the
"finished" catalogue on day one (a leftover `skull` in source, a robot-picture-on-music
mismatch) — treat a failure as a real defect first, a calibration second.
