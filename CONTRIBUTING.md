# Contributing

## Linear

We plan the work in the [UK Lunabotics 2027](https://linear.app/kjdotio/project/uk-lunabotics-2027-ce646930b227) project. Read its [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) document first.

- Each workstream is one parent issue with one owner. Break it into sub-issues as you plan.
- Anyone can add issues. If you find work outside your workstream, put it in **Backlog** with a "done when", and tell whoever owns that area.
- Move an issue to **In Progress** when you start, and to **Done** when its "done when" is met.
- Mark dependencies with **blocked by**.
- Put `Fixes INX-123` in your pull request description, so the issue links to it.

The links in each issue are places to start, not the answer. Read the docs for our versions, look at what other teams did, try things in the sim, and come to your own conclusions. Write down what you decided and why, in the issue or in your pull request. Everything gets reviewed, so it's fine to try something and change it later. If you're stuck, ask in Discord.

## Pull requests

1. Create a branch from `main`.
2. Keep each pull request to one feature or one fix.
3. Before you open the pull request, run `colcon build` and `colcon test` in the dev VM.
4. In the description, say what you tested. If you tested on the rover, say so.
5. Get one approval from someone who didn't write the change.
6. After approval, the author merges with **Squash and merge**.

Admins can push small doc fixes straight to `main`.

## Commit and pull request messages

The pull request title and description become the commit on `main`.

- Write the first line as a short command that says what changes. For example: `Stop the drive motors when Teensy heartbeats stop`.
- Don't write titles like `Fix bug`, `Update code` or `Phase 1`.
- After a blank line, say why you made the change. Include what a reviewer needs: the problem, test results, and links to issues.

## Using AI

You can use AI tools. How you use them is up to you.

You're responsible for every line you submit. You must be able to explain what your code does and why it works. If you write tests, you must be able to explain what they check. Reviewers can ask about any line.

## Research tools

Agents and people use these MCP servers. Neither needs an account.

| Use it for | Tool | MCP URL |
|---|---|---|
| Library and API docs | Context7 | `https://mcp.context7.com/mcp` |
| Forums, issues, release notes, datasheets | Exa | `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa` |

- Name the version in every question: Jazzy, Harmonic or JetPack 7.2.1.
- Exa allows about 50 calls a day for each network address. To save calls, fetch several pages in one call.

This guide follows [Google's guide to change descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) and the [ROS 2 Jazzy developer guide](https://docs.ros.org/en/jazzy/The-ROS2-Project/Contributing/Developer-Guide.html).
