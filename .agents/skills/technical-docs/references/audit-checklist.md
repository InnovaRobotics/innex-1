# Pre-delivery prose and link audit checklist

Read this file during Step 4 of the workflow, after drafting a doc and before finishing.

## 1. Structural AI-tell check

Read the draft aloud from top to bottom and remove these patterns:

- Staging contrasts: `not X, but Y`, `not just X, but Y`, `it's not X, it's Y`, `X rather than Y`, or the same contrast split across two sentences ("This does not mean X. It means Y."). Keep a negation only when it corrects a real misconception the reader holds.
- One-line summary closers and dramatic fragments: a short sentence at the end of a paragraph or section that restates the point instead of adding a fact.
- Staged openers: `Here's the thing`, `Let's dive in`, `Now let's look at`, `At its core`, `What really matters`.
- Forced triads: three parallel nouns or examples where two carry the full meaning.
- Bold-label bullet lists: `- **Wheel slip:** ...`. Turn explanations into cohesive prose paragraphs; keep bullets unbolded and only for real parallel items.
- Overused filler and inflation: `crucial`, `pivotal`, `robust` (figurative), `landscape`, `interplay`, `delve`, `underscore`, `highlight`, `additionally`, `actually`, `key` (adjective), `valuable`, `ensure`, `serves as`, `functions as`, `stands as`, `very`.
- Shallow `-ing` riders: `..., ensuring that...`, `..., highlighting the...`, `..., reflecting...`.
- Repeated heading: a first sentence that merely restates the heading right above it.
- Chatbot residue: greetings, praise or closing offers ("Let me know if...").

## 2. Project style and British English check

- British spelling throughout: `localisation`, `metres`, `centimetres`, `tyres`, `towards`, `behaviour`, `colour`, `normalised`, `maximises`, `practise` (verb) / `practice` (noun).
- Punctuation: zero em dashes, en dashes or spaced double hyphens (` -- `) in prose; straight quotes (`"` and `'`), never curly quotes; no exclamation marks.
- Banned phrasing: no `should` (use `must`, `can` or `might`), `simply`, `easy`, `just`, `please note`, `let's`, `in order to`, `it is important that`, `with respect to`.
- Timeless wording: avoid `now`, `currently`, `new`, `existing`, `soon`, `yet`, `eventually` when describing system behaviour.
- Accessible wording: avoid `above` and `below` for document position (use `earlier`, `preceding` or `the following diagram`; physical geometry like `below horizontal` is fine). Avoid figurative ableist metaphors (such as "wakes up blind" or "blind spot" when "dead zone" or "no knowledge of its coordinates" is clearer).
- Register discipline for internal engineering reviews (SDR/PDR): third person only (no `you`, `we`, `our`), no contractions, `shall` in requirement tables only, no `[RD1]` bracket tags in prose, at most one requirement ID per paragraph.

## 3. Factual and technical check

- Match the exact stack: Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic (`gz`), Python 3.12, JetPack 7.2.1 (R39.2.1). Reject Humble, Fortress or JetPack 6 answers unless verified for Jazzy/Harmonic.
- Check provisional organiser clarifications against `docs/rules.md` and mark email-only clarifications as provisional until the final 2027 rulebook confirms them.
- Verify every worked number and arithmetic step by hand.
- Keep all valid requirements, inputs/outputs, rule links, open questions and further reading links when rewriting an existing doc.

## 4. Automated style and link verification script

Run this check from the repository root on the files you edited (adjust `files` as needed):

```python
import os, re

files = ["docs/system/localisation.md"]

BAD_RE = re.compile(
    r"(—|–| -- |\bshould\b|\bsimply\b|\beasy\b|\bjust\b|\bplease note\b|\blet's\b|"
    r"\bnow\b|\bcurrently\b|\bnew\b|\bexisting\b|\byet\b|\beventually\b|\bactually\b|"
    r"\bensure|\bserves as\b|\bfunctions as\b|\brather than\b|\bvery\b|\bnot only\b|\bnot just\b|"
    r"\btoward\b|\bmeter\b|\bmeters\b|\bbehavior\b|\bcolor\b|\btire\b|\btires\b|!|“|”|‘|’)",
    re.I,
)

for f in files:
    for idx, line in enumerate(open(f), 1):
        clean = re.sub(r"https?://\S+", "", line)
        for m in BAD_RE.finditer(clean):
            print(f"STYLE {f}:{idx}: [{m.group(0)}] {line.strip()}")

def slugify(h):
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", h.strip().lower()))

anchors = {}
for f in files:
    text = open(f).read()
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        target = m.group(2)
        if target.startswith(("http", "mailto:")):
            continue
        rel, anc = target.split("#", 1) if "#" in target else (target, None)
        dest = os.path.normpath(os.path.join(os.path.dirname(f), rel)) if rel else f
        if not os.path.exists(dest):
            print(f"BROKEN FILE {f}: {target}")
        elif anc:
            if dest not in anchors:
                anchors[dest] = {
                    slugify(h.group(1))
                    for line in open(dest)
                    for h in [re.match(r"^#+\s+(.*)$", line)]
                    if h
                }
            if anc not in anchors[dest]:
                print(f"BROKEN ANCHOR {f}: {target}")
```

For an internal engineering review (third-person SDR/PDR register), also scan prose outside requirement tables for `\b(you|we|our)\b`, `n't\b`, `\[RD\d+\]` and `\bshall\b`.
