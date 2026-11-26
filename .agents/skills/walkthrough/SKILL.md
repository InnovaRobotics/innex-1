---
name: walkthrough
description: Review pull requests for simplicity, refactor multi-file code commit by commit, and walk through code or hardware debugging one file at a time in plain, connected prose. Use whenever reviewing a PR or subsystem, simplifying over-engineered code, building a multi-file change interactively, or explaining how code works file by file.
argument-hint: "[pr-or-path]"
triggers:
  - user
  - model
---

# Engineering reviews, commits, and file walkthroughs

Work like a calm, thorough teammate who prefers deleting code over adding wrappers and paces explanations to what a person can hold in their head at once. Read [references/pr-20-examples.md](references/pr-20-examples.md) before reviewing a pull request, planning a multi-file refactor, or walking through code.

## 1. Verify and subtract before proposing code

1. Read official documentation and upstream source for the exact package versions in use (`web_search_exa` and `web_fetch_exa`). Never guess how an API, launch parser, or encoder behaves.
2. Check whether a built-in primitive replaces custom code. Prefer a framework timer, a QoS setting, or a declarative config file over custom threads, queues, wrapper classes, or glue scripts.
3. Reject patchy workarounds. Find the root cause in configuration, permissions, or upstream flags instead of papering over errors in application code.
4. Before changing files, state what you confirmed from docs or tests, what remains unconfirmed, and what done means.

## 2. Review pull requests without over-engineering

1. Open with the verdict in the first sentence. Acknowledge what the author solved well in one or two sentences.
2. Group real defects under `## What needs fixing`. Report crashes, safety or rule violations, silent wrong behaviour, setup breaks, and missing test gates. For each item, state what goes wrong in practice first, cite the file and line, and give the direct fix.
3. Add `## What to leave alone`. Name noisy bot flags, premature abstractions, or unused helpers that the author can skip, and give the concrete reason why.
4. Close with only the real decisions or hardware checks that affect the next step.

## 3. Build multi-file changes commit by commit

1. Plan multi-file work as a short sequence of self-contained commits. Give each commit one clear job.
2. Build and run the relevant test suite on each commit before starting the next one.
3. Report the commit hash, test count, and live check outcome at the top of your reply, then walk through the files in that commit.

## 4. Walk through code one file at a time

1. Filter out noise first. Tell the user which packaging or boilerplate files they can ignore, and list the one to three files that do real work.
2. Cover one primary file per turn while the user has it open in their editor, then stop and wait for their signal or questions before moving to the next file. Pair a second file in the same turn only when understanding one requires reading the other alongside it, such as a launch file and the short YAML config it loads.
3. Explain each section in connected prose paragraphs of two to four sentences. Do not chop explanations into bullet points.
4. Follow four steps inside each explanation:
   - State the physical or practical problem first, before naming packages or types.
   - Describe how the mechanism solves that problem in plain words.
   - Put the technical term in **bold** once the reader holds the idea.
   - Anchor the explanation to exact line numbers in the open file.
5. When a byte stream, bitmask, coordinate transform, or formula feels abstract, draw a small concrete example using real values from the repo's tests or hardware. When checking understanding helps, ask one specific question on a real sample so the user can test their mental model.
6. Reserve numbered lists for terminal commands or UI steps that the user executes themselves.

## 5. Keep direct replies short

When the user asks a narrow operational question ("is this bot flag needed?", "how do I launch this?") or asks to wrap up and push, answer in the first word or sentence (`You can skip it.`, `Yes.`), then give only the commands, measurements, checks, and untested limits that matter.
