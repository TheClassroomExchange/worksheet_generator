# PM Review Guide — The Classroom Exchange

## Your job in two sentences
You review the markdown file for **curriculum accuracy and classroom usability**.
You do NOT review design, images, or formatting — those come in Week 2.

---

## What to open
Each generated unit produces two files in the `generated_units/batch_X/` folder:

| File | What it is | Do you need it? |
|---|---|---|
| `unit_theme_name.md` | **The one you review** — full readable unit | YES |
| `unit_theme_name.json` | Raw data for the script | No — ignore |

Open the `.md` file in Google Docs (File → Open → Upload) or any markdown viewer.

---

## Review checklist (per unit — target 30 min max)

### Curriculum accuracy
- [ ] Learning intention matches the curriculum code listed at the top
- [ ] Success criteria are grade-appropriate (not too easy, not too hard)
- [ ] Canadian context is used throughout (Canadian coins, Canadian animals, Canadian places)
- [ ] No US references snuck in (no "pennies" for coins, no "Common Core", no US state names)
- [ ] The strand focus is maintained across all 7 lessons (doesn't drift into a different strand)

### Classroom usability
- [ ] Teacher scripts are written in full — no vague "[discuss]" gaps
- [ ] Timing feels realistic for the grade (K lessons shouldn't run 60 min)
- [ ] Materials list is realistic (no items a typical Ontario classroom wouldn't have)
- [ ] Exit tickets are specific and observable

### Worksheet quality
- [ ] Instructions are written at the right reading level for the grade
- [ ] Image placeholders have clear descriptions (the image gen script needs these)
- [ ] Answer key is included and correct
- [ ] Response types match the task (circling, drawing, writing — appropriate for grade)

### Assessment suite
- [ ] Rubric criteria match the learning goals
- [ ] Level 3 is the "expected" bar — not too high, not too low
- [ ] Summative task is achievable in the time stated

### Red flags — mark `needs_regen` immediately if:
- [ ] A3.5 (Indigenous perspectives) unit — needs extra scrutiny for accuracy and sensitivity
- [ ] Curriculum code cited doesn't match the content taught
- [ ] Grade 3 content that references EQAO — check question formats are correct style
- [ ] Any content that could be culturally insensitive

---

## How to give feedback

**If the unit is good → approved:**
1. Open `canadian_classroom_content_batches.xlsx`
2. Find the row, change Status to `approved`
3. Leave a short PM comment if you want to note anything for Week 2 images

**If it needs a fix → needs_regen:**
1. Change Status to `needs_regen`
2. Write your specific feedback in PM Comments column — be precise:
   - ❌ "The math is wrong" (too vague)
   - ✅ "Lesson 3 says 2 quarters = 75¢ — should be 50¢. Also needs a dime activity."
3. The engineer reruns the script for that row only — your comment gets injected into the prompt

**If it needs a small edit you can do yourself:**
- Just edit the `.md` file directly and mark `approved`
- Note what you changed in PM Comments

---

## What `[IMAGE_PLACEHOLDER]` blocks mean

You will see blocks like this throughout the worksheets:

```image-placeholder
id: L1_P1_IMG1
description: B&W line art coloring-book style, Canadian nickel (5-cent coin) showing beaver on reverse, 80x80px, clean outlines
placement: left of question text
```

**Ignore these in Week 1.** They are instructions for the image generation script in Week 2.
Your only job is to check the *description* makes sense for the activity.
If a placeholder says "image of a US penny" — flag it. Otherwise, move on.

---

## Batch review targets

| Batch | Units | Target completion |
|---|---|---|
| Batch 1 — Pilot | 5 | 2–3 days after generation |
| Batch 2 — Stress test | 15 | 5–7 days after generation |
| Batch 3 — Scale | 30 | Rolling — approve as you go |

**Don't review all of Batch 1 before giving feedback.** Review unit 1, give feedback,
let the engineer adjust the prompt if needed, then review unit 2. Early feedback
improves all subsequent units.
