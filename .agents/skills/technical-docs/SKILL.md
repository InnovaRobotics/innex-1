---
name: technical-docs
description: Write and rewrite clear, accessible, human-sounding technical documentation for the INNEX-1 rover project, including subsystem explainers, architecture overviews, glossaries, rules summaries and internal engineering reviews (SDR/PDR). Use whenever drafting, updating or rewriting docs in docs/ or docs/system/, explaining robotics or software concepts (such as localisation, LiDAR odometry, Kalman filters, TF frames, perception, navigation, comms or simulation), or improving choppy, jargon-heavy or AI-sounding technical prose. Not for command-heavy setup guides, safety checklists, CLI runbooks or code comments.
argument-hint: "[file-or-topic]"
triggers:
  - user
  - model
---

# Technical documentation writing

Write technical docs that a first-year student who can program, and is new to robotics, understands on the first read without losing engineering accuracy. Build each explanation from concrete intuition and verified facts, so natural prose replaces both choppy fact-lists and synthetic AI phrasing.

## Pick the right register first

Match the voice to the document before drafting a word:

- Subsystem explainers and overviews (`docs/system/*.md`, `docs/system-design.md`): second person ("you"), natural contractions ("don't", "can't", "it's"), conversational and direct.
- Internal engineering reviews and baselines (SDR, PDR, design specs): third person ("the rover", "the operator", "the team"), present tense, active voice, no contractions, exact engineering values (`500 ms`, `4,000 kbps`, `25 W`), `shall` reserved for requirement tables only, reference documents listed once instead of bracketed `[RD1]` tags, and at most one requirement ID per paragraph.
- Reference pages (`docs/rules.md`, `docs/glossary.md`): plain, complete British English sentences with all existing heading anchors preserved.
- Out of scope: leave command-heavy setup guides (`docs/setup-*.md`), hardware runbooks (`docs/jetson.md`) and safety checklists (`docs/safety.md`) terse and procedural.

## How to explain technical ideas

Apply six learning-science principles in every conceptual section. Read [references/research-basis.md](references/research-basis.md) if you need the underlying citations or want to adapt a choice.

1. Start from what the reader knows. Open an unfamiliar topic with a physical picture (counting footsteps in a dark room for odometry; sliding two transparent top-down scans until wall dots align for LiDAR scan matching) before introducing formulas or packages.
2. Use the idea before you name it. Explain the mechanism in plain words first, then put the technical term in **bold** once the reader holds the concept ("Adding up small motions over time like this is called **odometry**").
3. Let the natural wrong instinct fail first, then repair it. Where a newcomer is likely to guess wrong (keeping one arena frame instead of `map` and `odom`, or taking a 50/50 average of two unequal sensors), walk into that mistake with real rover numbers, show how it breaks, and introduce the real mechanism as the fix.
4. Check claims with concrete numbers and extreme cases. After giving a formula, plug in realistic rover figures and test both ends (such as variance `0` and huge variance `9.0` for Kalman gain) so the reader can verify why the formula behaves sensibly.
5. Keep high cohesion. Put one idea in each paragraph (two to four sentences) and join every paragraph to the last with plain causal words ("because", "so", "therefore", "when"). Prefer connected prose paragraphs over bullet lists; use bullets only for genuinely parallel items such as requirements, rules or hardware parts.
6. Point at diagrams instead of repeating them. Introduce each Mermaid diagram with the question it answers, then direct the reader to the exact link or loop to inspect.

## Write well instead of patching AI tells

AI prose sounds synthetic because models default to staging importance, repeating rhythm by rule and padding ordinary claims. Prevent those habits while drafting:

- State the fact directly. Cut `not X, but Y`, `it's not X, it's Y` and `X rather than Y` contrasts unless correcting a real belief the reader holds. Cut throat-clearing openers (`Here's the thing`, `Let's dive in`), one-line summary closers and dramatic fragments.
- Choose punctuation deliberately. Never use em dashes, en dashes or spaced double hyphens (` -- `) in prose; use a comma, full stop, colon or parentheses so the clause relationship stays explicit.
- Vary sentence length and drop forced triads. Mix short and medium sentences, keep real two-item or four-item lists instead of padding to three, and avoid bold-label bullet dumps (`- **Label:** ...`).
- Use plain British English and timeless wording. Use British spelling (`localisation`, `metres`, `tyres`, `towards`, `behaviour`, `colour`). Avoid `should` (use `must`, `can` or `might`), `simply`, `easy`, `just`, `please note`, `let's`, `very`, `ensure`, `serves as`, exclamation marks and curly quotes. Avoid time-anchored words (`now`, `currently`, `new`, `existing`, `soon`, `yet`, `eventually`) and directional document references (`above`, `below` for page position).

## Worked before/after example

This short extract comes from the rewrite of `docs/system/localisation.md`. Read [references/worked-examples.md](references/worked-examples.md) before drafting a full subsystem doc; it contains the complete before/after transformations for the REP 105 frame split, LiDAR odometry (ICP) with arena walls and the Kalman filter walkthrough.

**Before (choppy, jargon-first, no mental model):**

> REP 105 defines two frames for the pose. The `odom` frame is smooth and continuous, but it drifts over time. It suits short-range control, because the pose never jumps. The `map` frame stays fixed to the arena, but it can jump when a correction arrives. It suits route planning across the arena.
>
> A fusion filter, such as an extended Kalman filter (EKF), weighs each source by its covariance and combines them. The filter still depends on honest covariances and good calibration.

**After (wrong instinct first, concrete numbers, plain terms before names):**

> Suppose you keep one coordinate system for the whole arena and publish the rover's pose in it. Imagine the rover drives 3 metres across the obstacle zone, accumulating 25 cm of sideways drift along the way. Halfway around a rock, the camera catches sight of the beacon, and your localisation node snaps the estimated position 25 cm to the right in one tick.
>
> To the motion controller steering around that rock, the rover appeared to teleport 25 cm sideways. The controller reacts to the sudden error by jerking the wheels, which can swing the rover into the rock it was avoiding. If you avoid jumps by ignoring the beacon instead, the rover drives smoothly, except the route planner thinks the berm sits 40 cm away from its real spot.
>
> You need both behaviours at once: smooth, continuous motion for short-range control, and arena-fixed accuracy for route planning. REP 105 solves this by placing two fixed coordinate frames above the rover's body frame, `base_link`, in a chain.

Why this works: the original defines `odom` and `map` before the reader feels why one frame breaks. The rewrite walks straight into the single-frame failure on a concrete rock avoidance manoeuvre, making the two-frame chain feel inevitable before naming REP 105.

## Workflow

Follow these five steps on every documentation task:

1. Verify facts first. Read the current doc, related repo READMEs, `docs/rules.md` (including provisional organiser clarifications) and official docs for the exact project stack (Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, JetPack 7.2.1). Check incoming links and heading anchors with `grep` before renaming headings. Never invent measurements or carry forward stale rules.
2. Outline in learner order. List the concepts from concrete problem to mechanism, pick the physical analogy and wrong instinct for each hard idea, and decide where a small Mermaid diagram earns its space.
3. Draft top to bottom. Keep all valid requirements, rule links, inputs/outputs, open questions and further reading links. Label provisional or calculated statements honestly.
4. Audit the prose. Read [references/audit-checklist.md](references/audit-checklist.md) and run its pattern and link checks on every file you edited. Fix every hit instead of ignoring "minor" tells.
5. Preserve scope. Change prose and diagrams cleanly without breaking code blocks, commands, topic names, URLs or unrelated files.
