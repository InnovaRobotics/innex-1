# Repository instructions for agents

Use British English.

## Source of truth, in order

1. `docs/02-facts.md` (hardware, versions, rulebook version).
2. Interface contracts and pin maps under `contracts/` when they exist.
3. `docs/01-decisions.md`.
4. Package READMEs under `src/*/README.md` when they exist.
5. The 2026 repository (`KJdotIO/innex1-rover`) as historical reference only. Do not copy code from it without a decision-log entry.

If two sources disagree, stop and report the disagreement. Do not pick one silently.

## Hard rules

- Do not flash firmware.
- Do not enable motors or publish velocity commands to a live rover.
- Do not merge pull requests.
- Do not connect to the Jetson or any rover hardware.
- Do not write credentials, tokens, Wi-Fi keys or passwords anywhere.
- Do not add a dependency without stating the version and the reason in the pull request.
- Do not add or remove code comments unless asked.

## Conventions

- ROS 2 Humble, Ubuntu 22.04, Python 3.10, C++17.
- Typed ROS messages only. No `std_msgs/*MultiArray` for commands or telemetry.
- Commands are absolute setpoints. Never deltas.
- Every actuator has exactly one owning node.
- Every launch file is started by the single supervised launcher.
- Every derived requirement cites the rulebook version and clause.
- Prose for procedures follows Simplified Technical English: one instruction per sentence, active voice, one term per meaning.

## Skills

Load the relevant skill from `skills/*/SKILL.md` before ROS 2, bring-up, perception, testing, security, Docker or web-bridge work. See `skills/README.md`.

## Review focus

Report only: broken builds, runtime failures, unsafe robot behaviour, ROS interface or TF contract mismatches, launch/config/deployment breakage, stale upstream API assumptions, missing tests for risky behaviour, or divergence from `docs/`. Do not comment on style, naming or formatting; pre-commit owns those.
