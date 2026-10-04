# Review guidance

INNEX-1 is a lunar excavation rover for UK Lunabotics. The software is ROS 2 Jazzy on Ubuntu 24.04 and a Jetson on JetPack 7.2.1. The firmware runs on a Teensy 4.1 and is built with PlatformIO. This code moves heavy motors. Review what the code does, not how it looks.

Your comments help a person decide. They don't approve or block a pull request.

## Scope

- Review only the lines that the pull request adds or changes. Don't report problems in code that it doesn't touch.
- Check the change against what the description says it does.
- A false finding is worse than a missed one. Report a problem only when you're confident that it's real.
- Cite a rule for each Blocking or Warning finding. The rules are in this file, `AGENTS.md`, `CONTRIBUTING.md`, `docs/safety.md` and `docs/rules.md`.

Don't report:

- Style, naming or formatting, unless it hides a defect.
- Refactors that a fix doesn't need.
- Features that the pull request doesn't claim to add.
- Wording in docs. Report only wrong facts, broken commands and broken links.

## Severity

Use these definitions exactly:

- Blocking: unsafe motion, a break of the competition rules, a failed build or test, a crash, or a committed credential.
- Warning: the code works but is risky. For example, an interface mismatch, or motion code with no test.
- Nit: anything that no rule covers. Post a nit only if it helps the author learn.

## Rules

### Safety

1. Each path that commands a motor or actuator must stop the output when commands stop arriving.
2. Don't remove or lengthen an existing command timeout.
3. Commands must be absolute setpoints, such as a velocity or a position.
4. Only one node or task can command each motor or actuator.
5. On a fault, stop the output. Don't hold the last value.
6. A change to a current limit, duty-cycle limit or speed limit needs a reason in the description.

### Competition rules

7. Don't use the arena walls or structure for mapping, localisation, navigation or collision avoidance.
8. Don't use compass data. The OAK-D's IMU has a magnetometer. Use only its gyro and accelerometer data or its game rotation vector.
9. Don't send raw images or point clouds to mission control. The link must average 4,000 kbps or less.
10. Don't send commands or orientation data to the rover during a hands-free autonomy attempt.

### ROS 2

11. Use Jazzy APIs and Gazebo Harmonic (`gz`). Flag Humble-only APIs, `ign` commands, and Gazebo Classic or Fortress names.
12. Use SI units and the frame names in REP 103 and REP 105 (`map`, `odom`, `base_link`). Both ends of a topic must agree on the message type, units and frame.
13. Command topics must not queue old commands. An old command must never arrive late.
14. Put IP addresses, host names and device paths in parameter files, not in code.

### Firmware

15. Don't use `delay()` or blocking reads in the control loop. Don't allocate memory after `setup()`.
16. A change to the serial protocol must update the Teensy side and the Jetson side in the same pull request.

### Evidence and secrets

17. The description must say what the author tested. A claim about rover behaviour needs evidence: a bag, a log or a photo.
18. Don't commit credentials, private network addresses or personal details.

## How to write each finding

Write for a first-year student who can program but is new to robotics. The author should learn something from every comment.

Use this order:

1. What goes wrong on the rover, in one plain sentence.
2. Why it happens, with the file and line.
3. How to fix it. Add a short code example if it helps.
4. Which rule it breaks, with a link to the rule in this repository.

- Use short sentences and everyday words.
- Explain each technical term and each acronym the first time that you use it.
- Put one problem in each comment.
- Start each comment with its severity.
- If you aren't sure, say so, and say how to check.
- Link outside documentation only if you checked it. Otherwise, name the documentation and say that it needs checking.
- Be direct and kind. Don't praise the change or pad the comment.

Example of a bad finding:

> QoS durability/reliability mismatch on /cmd_vel; RELIABLE+KEEP_ALL induces stale-command latency under packet loss.

Example of a good finding:

> Blocking. If the Wi-Fi drops for a second, the rover can act on old drive commands after the link comes back.
>
> `teleop.py` line 42 publishes commands with a queue that keeps every message. When the link recovers, the rover receives the queued commands in order and drives on out-of-date input.
>
> Fix: keep only the newest command, for example `QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)`.
>
> Rule: ROS 2 rule 13 in `REVIEW.md`.
