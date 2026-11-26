# Research and style sources behind this skill

Read this file only when you need to explain or adapt why a writing rule exists.

## Learning-science basis

- Conversational style (personalisation principle): Ginns, P., Martin, A. J. and Marsh, H. W. (2013), "Designing instructional text in a conversational style: a meta-analysis", *Educational Psychology Review* (https://doi.org/10.1007/s10648-013-9228-0); Mayer, R. E. (2005), *Cambridge Handbook of Multimedia Learning* (https://doi.org/10.1017/cbo9780511816819.014). Second-person, natural wording improves transfer over stiff formal prose in explainers.
- Explicit links between ideas (text cohesion): McNamara, D. S., Kintsch, E., Songer, N. B. and Kintsch, W. (1996), "Are good texts always better?", *Cognition and Instruction*, 14(1) (https://doi.org/10.1207/s1532690xci1401_1); O'Reilly, T. and McNamara, D. S. (2007), "Reversing the reverse cohesion effect", *Discourse Processes*, 43(2) (https://doi.org/10.1207/s15326950dp4302_2). Readers new to a domain learn far more when causal links are stated explicitly instead of left as gaps between terse sentences.
- Effective instructional explanations: Wittwer, J. and Renkl, A. (2008), "Why instructional explanations often do not work", *Educational Psychologist*, 43(1), 49 to 64 (https://doi.org/10.1080/00461520701756420). Explanations succeed when anchored to prior knowledge and focused on underlying principles instead of bare rules.
- Concrete before abstract (concreteness fading): Fyfe, E. R., McNeil, N. M., Son, J. Y. and Goldstone, R. L. (2014), "Concreteness fading in mathematics and science instruction: a systematic review", *Educational Psychology Review* (https://doi.org/10.1007/s10648-014-9249-3). Start with concrete numbers and physical objects, then attach formal names and symbols.
- Coherence and diagrams with text: Cromley, J. G. and Chen, R. (2025), "A meta-analysis of Richard Mayer's multimedia learning research", *Educational Research Review* (https://doi.org/10.1016/j.edurev.2025.100730). Cutting decorative detail and pairing concise diagrams with text that directs attention yields consistent learning gains.

## Editorial and AI-writing sources

- Google developer documentation style guide (https://developers.google.com/style): tone, timeless documentation, sentence-case headings, active voice, word list and inclusive phrasing, adapted to British English per INNEX-1 `CONTRIBUTING.md`.
- Wikipedia's "Signs of AI writing" (https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing): structural and stylistic tells (staging contrasts, one-line closers, forced triads, dashes as universal connectors, inflation and formatting-by-rule).

## Skill authoring sources

- Devin CLI skills documentation (`extensibility/skills/overview.mdx` and `extensibility/skills/creating-skills.mdx`): frontmatter schema (`name`, `description`, `argument-hint`, `triggers`), directory layout (`.devin/skills/<name>/SKILL.md`, `~/.config/devin/skills/<name>/SKILL.md`), and inline vs subagent permissions.
- Agent Skills open specification (https://agentskills.io/specification) and best-practices guide (https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/best-practices.mdx): progressive disclosure (metadata, concise `SKILL.md` under 500 lines, on-demand `references/` one level deep), omitting facts agents already know, and matching specificity to task fragility.
- Anthropic reference skills (`anthropics/skills`: `skill-creator` and `doc-coauthoring`) and local Devin skills (`~/.config/devin/skills/humanizer`, `animate`, `pick-ui-library`, `~/.claude/skills/teaching-prose`, `better-writing`): concrete trigger phrasing in `description` and explicit when-to-read pointers for reference files.
