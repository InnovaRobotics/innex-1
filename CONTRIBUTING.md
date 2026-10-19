# Contributing

## Plan work in Linear

The 2027 work is planned in the [UK Lunabotics 2027](https://linear.app/kjdotio/project/uk-lunabotics-2027-ce646930b227) project in Linear. Read [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) before you pick an issue. It explains the workstreams, the milestones and the two-week sprints.

Each issue says what the result is and how you know it is done. You decide how to reach the result. Write down what you chose and why, in the issue or in your pull request. Everything gets reviewed, so you can change your mind later.

Anyone can add issues. Break your work into sub-issues as you plan it. If you find work that belongs to someone else, put it in Backlog with a "done when", and tell the owner. Move an issue to In Progress when you start. Move it to Done when its "done when" is met.

## Branches

Name each branch after its issue. Use the branch name that Linear suggests, or use `inx-<number>-<short-description>`. Use lowercase letters and hyphens.

## Pull requests

1. Create a branch from `main`.
2. Keep each pull request to one feature or one fix.
3. Run `colcon build` and `colcon test` on the Ubuntu machine.
4. Open the pull request. Fill in both headings of the template.
5. Get one approval from someone who did not write the change.
6. Merge with **Squash and merge**.

Make every change through a pull request. Do not push to `main`. [AGENTS.md](AGENTS.md) applies the same rule to AI agents.

In the description, put `Fixes INX-123` on its own line to link the Linear issue. Say what changes and why. Say how you tested it. If the change affects how the rover moves, how it talks to the Teensy, the sensors or mission control, say what someone must check before the next run on the rover. Keep the description short enough that a reviewer reads all of it.

## Commit messages

Squash and merge turns the pull request title and description into the commit on `main`. So the title and the description follow the rules for commit messages.

The title is a short command that says what changes. For example: `Stop the drive motors when Teensy messages stop`. Start with a capital letter. Keep the title under about 50 characters. Do not end it with a full stop. Titles such as `Fix bug`, `Update code` or `Phase 1` tell a reader nothing.

After a blank line, explain why you made the change. The diff already shows how. Spend your words on the problem, your decision, and anything a reviewer or a future reader needs. That includes test results and a link to the issue.

Two guides explain the reasoning: Chris Beams' [How to write a Git commit message](https://cbea.ms/git-commit/), and Google's guide to [change descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html).

## Using AI

You can use AI tools. You decide how you use them.

You are responsible for every line you submit. You must be able to explain what your code does and why it works. If you write tests, you must be able to explain what they check. Reviewers can ask about any line.

## Research tools

Agents and people use these MCP servers. Neither needs an account.

| Use it for | Tool | MCP URL |
|---|---|---|
| Library and API docs | Context7 | `https://mcp.context7.com/mcp` |
| Forums, issues, release notes, datasheets | Exa | `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa` |

Name the version in every question. For example: Jazzy, Harmonic or JetPack 7.2.1. Exa has usage limits, so put several questions in one search.

## Style

We write docs to the [Google developer documentation style guide](https://developers.google.com/style), with British spelling. The pull request rules follow the [ROS 2 Jazzy developer guide](https://docs.ros.org/en/jazzy/The-ROS2-Project/Contributing/Developer-Guide.html).
