# Contributing

## Planning in Linear

We plan the work in the [UK Lunabotics 2027](https://linear.app/kjdotio/project/uk-lunabotics-2027-ce646930b227) project in Linear. Its [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) document explains the workstreams, milestones and two-week sprints, so read that before you pick up an issue.

Each issue says what the result is and how you'll know it's done. How you get there is up to you. The links in an issue are somewhere to start, so read the docs for our versions, look at how other teams solved the same problem, try things in the sim, and come to your own conclusions. Write down what you chose and why, either in the issue or in your pull request. Everything gets reviewed, so you can change your mind later. If you get stuck, ask in Discord.

Anyone can add issues. Break your own work into sub-issues as you plan it. If you find work that belongs to someone else, put it in **Backlog** with a "done when" and tell them. Move an issue to **In Progress** when you start and to **Done** when its "done when" is met.

## Pull requests

1. Create a branch from `main`.
2. Keep each pull request to one feature or one fix.
3. Run `colcon build` and `colcon test` in the dev VM.
4. Open the pull request and fill in the two headings in the template.
5. Get one approval from someone who didn't write the change.
6. Merge it yourself with **Squash and merge**.

Admins can push small doc fixes straight to `main`.

The description says what changes and why, and how you tested it. Put `Fixes INX-123` on its own line to link the Linear issue. If the change affects how the rover moves, or how it talks to the Teensy, the sensors or mission control, say what someone needs to check before the next run on the rover. Keep it short enough that a reviewer reads all of it.

## Commit messages

Squash and merge turns the pull request title and description into the commit on `main`, so they follow the same rules as any commit message.

The title is a short command that says what changes, such as `Stop the drive motors when Teensy messages stop`. Start it with a capital letter, keep it under about 50 characters, and leave off the full stop. Titles like `Fix bug`, `Update code` or `Phase 1` don't tell anyone anything.

After a blank line, explain why you made the change. The diff already shows how, so spend the words on the problem, what you decided, and anything a reviewer or a future reader needs, such as test results or a link to the issue. Chris Beams' [How to write a Git commit message](https://cbea.ms/git-commit/) and Google's guide to [change descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) explain the reasoning.

## Using AI

You can use AI tools. How you use them is up to you.

You're responsible for every line you submit. You must be able to explain what your code does and why it works. If you write tests, you must be able to explain what they check. Reviewers can ask about any line.

## Research tools

Agents and people use these MCP servers. Neither needs an account.

| Use it for | Tool | MCP URL |
|---|---|---|
| Library and API docs | Context7 | `https://mcp.context7.com/mcp` |
| Forums, issues, release notes, datasheets | Exa | `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa` |

Name the version in every question: Jazzy, Harmonic or JetPack 7.2.1. Exa allows about 50 calls a day for each network address, so fetch several pages in one call when you can.

The pull request rules follow the [ROS 2 Jazzy developer guide](https://docs.ros.org/en/jazzy/The-ROS2-Project/Contributing/Developer-Guide.html). The writing in this guide and in our docs follows the [Google developer documentation style guide](https://developers.google.com/style), with British spelling.
