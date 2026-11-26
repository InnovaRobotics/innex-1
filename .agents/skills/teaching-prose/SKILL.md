---
name: teaching-prose
description: Write teaching explanations as flowing, conversational prose that breaks a robotics or software topic down step by step, grounded in learning-science research. Use whenever a teammate asks you to teach, explain, or break down a concept, walk through how a subsystem works, or rewrite choppy notes so they are less rushed and use fewer bullet points. Not for terse reference sheets, code comments, or CLI runbooks.
---

# Teaching prose

Teammates learn best from prose that reads like a patient tutor talking to them: one idea at a time, every step joined to the last, nothing assumed, without rushing through walls of bullet points. Read `references/example-section.md` before you write to see every principle below working together. The evidence behind each principle is in `references/research.md`; cite it when you explain a choice.

## The principles, and why they work

**Talk to the reader.** Write in the second person ("you", "your"), with contractions and the occasional "we" or "let's". Conversational text produces deeper learning than formal text, probably because it makes the reader treat the page as a conversation and try harder to understand it (the personalisation principle).

**Start from what the reader already knows.** Open each topic with something familiar and concrete (a die, a box of fruit, an email inbox), and build the new idea on top of it. Explanations work when they connect to prior knowledge and fail when they float free of it.

**Use the idea before you name it.** Describe the thing in plain words first, then give it its technical name in bold. "Each of those possible results is called an **outcome**" lands better than "An outcome is…". The name then labels something the reader already understands.

**One idea per paragraph, and join every paragraph to the last.** Keep paragraphs to two to four sentences. Make the logical links explicit with words like "so", "because", "that's why", "now", "but". Readers who are new to a topic understand far more from text that spells out these links, because they can't yet fill the gaps themselves.

**Explain why a rule is true, not just what it says.** For each formula or rule, give the one or two sentences that make it feel inevitable. A rule that makes sense needs no memorising, and principles transfer to new problems where bare facts don't.

**Let the reader's first instinct go wrong, then fix it.** Where there is a natural mistake (just adding P(A) and P(B), putting the wrong thing on the bottom of a fraction), walk into it on purpose with a real example, show the absurd result, then show what went wrong. The formula comes last, as the repair. This is far more memorable than stating the formula and warning about the mistake.

**Check every claim with a concrete case.** After a worked result, verify it another way ("You can check this by listing the faces…"). This models self-checking and builds trust in the method.

**Point at pictures, don't duplicate them.** When there is a diagram, set it up with a question the picture answers ("The picture below shows what went wrong"), then talk the reader through what to look at in it. Text and diagram together beat either alone, but only if the text directs attention.

**Leave real thinking to the reader.** End with a short *Your turn* problem that asks them to do the key step themselves, ideally the step the section just taught (for example, "write down which faces are in both events before you touch the formula"). Explanations shouldn't replace the learner's own thinking.

**Cut anything that doesn't serve understanding.** No intros about what the section will cover, no recaps, no decorative facts. Extraneous material reliably lowers learning.

## Form

- Prose paragraphs, not bullet points. Use a list only for genuinely parallel items the reader will scan, such as a set of options, and even then consider a sentence first.
- Use `###` subheadings to split a section into stages of the argument, phrased as what the stage is about ("The fourth rule: 'or'").
- Put formulas in display blocks (in Claude Docs, a ```latex code block). Introduce each formula in the sentence before it and explain it in the sentences after.
- Tables are fine for data the reader looks things up in (a grid of outcomes, a joint-probability table). They aren't a substitute for explanation.
- Bold only the term being defined, at the moment it is defined.
- British English. Plain words. Sentences mostly under 25 words, with varied length.
- Stay true to the source material (slides, textbook). Supplement it to make it clearer, but don't contradict it or invent facts.

## Process

1. Read the source material for the section and list, for yourself, the ideas in the order a learner needs them.
2. For each idea, pick the concrete case you'll start from and the likely wrong instinct.
3. Write the section top to bottom in prose, following the principles above.
4. Reread it as a beginner. Wherever you'd ask "why?" or "where did that come from?", add the missing sentence. Wherever a sentence doesn't help, cut it.
5. Keep any existing diagrams and charts, and rewrite the text around them so it points at them.
