# Automated end-to-end run — Grade 1 Pattern Parade

This is the prompt to paste into a **fresh Claude Code session** to build the
Grade 1 Pattern Parade unit end-to-end with no human intervention. Use it to
validate the pipeline + skill + differentiation rules before scheduling cron
jobs for Grade 2 and Grade 3.

## How to use

1. Open a new Claude Code session in this project directory:
   `/Users/anthonnymonterroso/Documents/TheClassroomExchange/claude_code_handoff/worksheet_generator`
2. Paste the prompt below as the first message.
3. Walk away. Don't reply, don't intervene. Let the session run.
4. Come back when it's done (or when the session ends naturally).

---

## The prompt (copy-paste this)

```
Build the Grade 1 Pattern Parade unit end-to-end, fully automated, no
clarifying questions. Use the tce-unit-builder skill.

Critical rules for this run:
- Do NOT ask me any questions. Make every decision yourself based on the
  memory file (~/.claude/projects/-Users-anthonnymonterroso-Desktop-TCE-TCE/memory/project_worksheet_generator.md)
  and the canonical reference at generated_units/batch_1/k_patterns_pattern_parade/.
- Keep going until the unit is fully done (all 15 stages, composed images,
  Slides deck built, PDF exported, visually validated) OR until you hit a
  failure that the retry path cannot recover from.
- For every judgment call, briefly note the decision in your reply so I can
  review later. Do not pause for confirmation.
- This is the gap-finding run. Document anything that felt awkward, broken,
  or required guesswork.

Pipeline:
1. Resume work on g1_patterns_pattern_parade (already initialized in
   generated_units/batch_2/).
2. Generate all 15 stages following the K Pattern Parade reference for
   structure, but with Grade 1 content density (per the differentiation
   table in the memory file: ~400-char teacher scripts, 4 action steps,
   2-3 consolidation prompts).
3. Reuse Coco + Bea/Finn/Bibi/Moss + manipulatives M1-M6 + char_coco_puppet.
4. Use Grade 1 Ontario expectations C1.1-C1.4 (already loaded in input_row.json).
5. After all 15 stages: run compose_for_unit(), render_unit() to write
   unit.md, then build_unit_deck() to produce the Slides + validation PDF.
6. Render the PDF to PNGs and visually compare a sample of slides
   (cover, lesson 1, worksheet 1, rubric, certificate, marketplace) to the
   reference K unit. Note any visual issues.

End-of-run report:
At the end, produce a structured report:
1. Stages completed (list)
2. Stages failed (list with reason — should be 0 ideally)
3. Slides deck URL
4. Validation PDF path
5. Pixel-by-pixel issues observed during validation
6. Judgment calls you made (and the rationale for each)
7. Suggestions for improvements before scheduling cron jobs
8. Final status_table() output across all 3 batches

If you run out of session budget before completing, end cleanly:
- complete_stage() any in-progress stage that's done
- mark_failed() any in-progress stage that isn't ready (so it can be retried)
- Print status_table() so the next session can resume

Start by reading the memory file, then the skill at
~/.claude/skills/tce-unit-builder/SKILL.md, then begin work.
```

---

## What "fully automated" means

The new session should:
- ✅ Make all content decisions itself (lesson titles, teacher scripts,
  worksheet tasks, etc.) using the K unit as the structural template and the
  G1 curriculum expectations as the content guide.
- ✅ Execute every Bash and Write call without confirmation prompts (decline
  via decision-rule rather than ask).
- ✅ Run consistency_check after every stage and address any failures.
- ✅ Run compose + Slides build + PDF export at the end.
- ✅ Visually inspect a representative sample of the produced slides.
- ❌ Should NOT ask the user "should I proceed?", "what theme should I use?",
  "is this OK?". Every such question has an answer in the memory file.

## What you (the user) should look for in the report

When the session finishes, check:

1. **Did all 15 stages complete?** If any failed, the report tells you which
   one and why.
2. **Does the deck URL open and look reasonable?** The deck is the deliverable.
3. **Are the lesson plans noticeably different from K?** Grade 1 should have
   longer teacher scripts and more action steps (per the differentiation
   table). If the content reads identical to K, the differentiation isn't
   landing.
4. **Are there any judgment calls that you'd have made differently?** This
   tells you where the schema or skill needs tightening before cron jobs run
   unattended.
5. **Are there any visual issues** (text off slide, image clipped, font wrong,
   overflow)? These reveal layout-budget problems for the longer G1 content.

## After this validation run

If it worked well:
- Schedule cron jobs for Grade 2 and Grade 3 using the same prompt format
  (just swap the unit slug).

If there are gaps:
- Update the memory file and skill with the lessons learned.
- Update the K reference unit if needed.
- Fix any layout budget issues in `pipeline/slides.py`.
- Then schedule the cron jobs.
