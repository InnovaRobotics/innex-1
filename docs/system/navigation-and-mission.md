# Navigation and mission

This page answers where the rover goes next, how it gets there, and what it does on arrival. Navigation turns a goal into a path and follows it. The mission decides which goal comes next and runs the dig and dump steps. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Turn a goal into a path that avoids the hazards, and follow that path.
- Replan when the picture around the rover changes.
- Start the dig sequence on arrival at the excavation zone, and the dump sequence on arrival at the berm.
- Check that the rover is ready before an attempt, and stop the attempt when it isn't.
- Retry a failed step a bounded number of times, then end the attempt safely.
- Keep the rover inside the arena without using the walls as landmarks.

## Inputs and outputs

Navigation and mission takes hazards from [Perception](perception.md) and the pose from [Localisation](localisation.md). It sends velocity commands on `/cmd_vel` and mechanism commands to [Teleop and rover control](teleop-and-control.md). It reports its progress as telemetry through [Comms and mission control](comms.md).

Navigation doesn't own hazard detection, global anchoring or mechanism control. Perception, localisation and the control subsystem own those. Keeping the boundaries clear lets you test each part alone.

## Rules that apply

- [Autonomy](../rules.md#autonomy): each task has a hands-free boundary, and the points depend on it.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel, the judges set the obstacles so the rover must detect them, map them and plan a route. A "point and traverse" approach isn't allowed.
- [Autonomy penalties](../rules.md#autonomy-penalties): contact with a rock, or driving over a crater, costs points.
- [Hands-free rules](../rules.md#hands-free-rules): you announce each attempt, and you can't send commands, orientation data or obstacle locations during it.
- [Navigation and sensing](../rules.md#navigation-and-sensing): no walls for mapping, navigation or collision avoidance.
- [During the run](../rules.md#during-the-run): stay inside the arena, and don't push obstacles or fill craters in the obstacle zone.

## The obstacle field is random

The judges place rocks and craters at random before each round, so the team can't record a route and replay it. The rules forbid a "point and traverse" approach for the same reason. The rover must find a route through the obstacles it detects in that run. A planner works from a map of what the sensors have seen so far, and it replans as the map fills in. A costmap is a common form of this map: a grid in which each cell holds a cost for driving there.

## Forward to dig, reverse to dump

The bucket ladder is at the front of the rover and the dump bed empties at the rear. The rover therefore approaches the excavation zone driving forward and approaches the berm in reverse, which avoids turning on the spot in loose sand. The planner and the controller must follow paths in both directions. A planner that assumes the rover always drives forward can't plan the reversing approach to the berm.

## The cycle

```mermaid
flowchart TD
    localise["Localise"] --> travel1["Travel to the excavation zone"]
    travel1 --> dig["Dig"]
    dig --> travel2["Travel to the construction zone"]
    travel2 --> dump["Dump"]
    dump --> decide{"Time and health allow another cycle?"}
    decide -->|yes| travel1
    decide -->|no| stop["Stop safely"]
```

Each step reports what happened, so the log explains why the mission continued, succeeded or stopped.

## Readiness checks

Before an attempt, the mission checks that the rover can do the job. Odometry is arriving, the transforms exist, the pose is certain enough and each sensor is publishing. A rover that starts with a hidden fault produces failures that look like planning bugs and take hours to trace. If a check fails, the mission doesn't start.

## Bounded recoveries

Things go wrong during a run: the rover gets stuck, a path is blocked, a detection flickers. A recovery is an action the rover takes to get out of such a state, such as backing up or turning on the spot. Recoveries must have limits, in the number of tries and in the time they take. Without limits, a rover can spend the whole run recovering. The mission ends an attempt that exceeds its limits and announces the failure, as the hands-free rules require.

## Where the hands-free boundary falls

Each autonomy task starts hands-free at a point the rules set:

- Excavation: before the rover touches the sand. You lift the digging mechanism out of the sand before you take control again.
- Dump: before the rover enters the construction zone. You can cross the obstacle zone by remote control.
- Travel and both full autonomy tasks: in the start zone. You can drive only inside the start zone to localise.

After that point, nobody can tell the rover where to go. The mission must already know its goal when the boundary arrives, or must be able to work it out from its own sensors. A goal in the arena frame depends on the pose from [Localisation](localisation.md).

## Open questions

1. Does autonomous excavation need navigation, or only the dig sequence?
2. Which planner and controller suit a skid-steer rover that drives forward to dig and reverses to dump?
3. How do we keep the planner inside the arena without using the walls as landmarks?
4. Does the mission run as a state machine or a behaviour tree?
5. How many retries does each step get before the attempt is declared failed?
6. How does the operator start an attempt and follow its progress without sending the rover anything?

## Read more

- [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Nav2, the common ROS 2 navigation framework](https://docs.nav2.org/)
- [Nav2 keepout zones tutorial](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_with_keepout_filter/navigation2_with_keepout_filter/)
