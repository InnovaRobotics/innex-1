# Review guidance

INNEX-1 is a lunar excavation rover for UK Lunabotics. The software runs ROS 2 Jazzy on Ubuntu 24.04. The Jetson runs JetPack 7.2.1. The firmware runs on a Teensy 4.1 and builds with PlatformIO. This code moves heavy motors. Review what the code does. Do not review how it looks.

Your comments help a person decide. Your comments do not approve or block a pull request.

## Scope

- Review only the lines that the pull request adds or changes. Do not report problems in code that it does not touch.
- Check the change against what the description says it does.
- Report a problem only when you are sure it is real. A false finding is worse than a missed one.
- Cite a rule for each Blocking or Warning finding. The rules are in this file, [AGENTS.md](AGENTS.md), [docs/safety.md](docs/safety.md), [docs/jetson.md](docs/jetson.md) and [docs/rules.md](docs/rules.md).

Do not report:

- Style, naming or formatting, unless it hides a defect.
- Refactors that a fix does not need.
- Features that the pull request does not claim to add.
- Wording in docs. Report only wrong facts, broken commands and broken links.

## Severity

Use these definitions exactly:

- Blocking: unsafe motion, a break of the competition rules, a failed build or test, a crash, or a committed credential.
- Warning: the code works but is risky. For example, an interface mismatch, or motion code with no test.
- Nit: anything that no rule covers. Post a nit only if it helps the author learn.

## Rules

### Safety

1. Each path that commands a motor or actuator stops the output when commands stop arriving.
2. Do not remove or lengthen an existing command timeout.
3. Commands are absolute setpoints, such as a velocity or a position.
4. Only one node or task commands each motor or actuator.
5. On a fault, stop the output. Do not hold the last value.
6. A change to a current limit, duty-cycle limit or speed limit needs a reason in the description.

### Competition rules

7. Do not use the arena walls for mapping, localisation, navigation or collision avoidance.
8. Do not use compass data. The OAK-D's IMU has a magnetometer. Use only its gyro and accelerometer data, or its game rotation vector.
9. Do not send raw images or point clouds to mission control. The link must average 4,000 kbps or less.
10. Do not send commands or orientation data to the rover during a hands-free autonomy attempt.

### ROS 2

11. Use Jazzy APIs and Gazebo Harmonic (`gz`). Flag Humble-only APIs, `ign` commands, and Gazebo Classic or Fortress names.
12. Use SI units and the frame names in REP 103 and REP 105 (`map`, `odom`, `base_link`). Both ends of a topic must agree on the message type, units and frame.
13. Command topics must not queue old commands. An old command must never arrive late.
14. Put IP addresses, host names and device paths in parameter files, not in code.

### Firmware

15. Do not use `delay()` or blocking reads in the control loop. Do not allocate memory after `setup()`.
16. A change to the serial protocol must update the Teensy side and the Jetson side in the same pull request.

### Evidence and secrets

17. The description must say what the author tested. A claim about rover behaviour needs evidence: a bag, a log or a photo.
18. Do not commit credentials, private network addresses or personal details.

## How to write each finding

Write for a first-year student who can program but is new to robotics. The author should learn something from each comment.

Use this order:

1. What goes wrong on the rover, in one plain sentence.
2. Why it happens, with the file and line.
3. How to fix it. Add a short code example if it helps.
4. Which rule it breaks, with a link to the rule in this repository.

Also:

- Use short sentences and everyday words.
- Explain each technical term and acronym the first time you use it.
- Put one problem in each comment.
- Start each comment with its severity.
- If you are not sure, say so, and say how to check.
- Link outside documentation only if you checked it. Otherwise, name the documentation and say that it needs checking.
- Be direct and kind. Do not praise the change, and do not pad the comment.

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
