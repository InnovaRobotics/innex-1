# Perception

Before navigation can pick a safe corridor across the obstacle zone, the rover has to turn raw 3D point clouds and stereo depth frames into a map of where its six wheels can and cannot roll. Perception reads scans and depth images from [Sensors](sensors.md), detects boulders, craters and the surrounding pit walls, and publishes those hazards to [Navigation and mission](navigation-and-mission.md).

Perception is planned for Stage 3 and has no ROS package on `main` (simulated `/ouster/points` and camera feeds already run in [`innex_sim`](../../src/innex_sim/README.md) to support development). Perception does not estimate where the rover sits in the arena; [Localisation](localisation.md) owns the pose, and perception uses that pose to pin each detected rock or crater onto the arena floor instead of leaving it in a moving camera frame.

## Why craters are harder to detect than boulders

Compare what happens to sensor rays when they meet a `35 cm` boulder versus a `45 cm` crater, shown in side profile in the diagram:

```text
  Sensor on rover
       *  \  \  \________________________
           \  \       (empty shadow)     \
            \  \____                      \____
  ___________\ /    \_____________________/    \______
              Boulder                     Crater
           (dense cluster)            (missing returns)
```

Follow the two ray bundles from the sensor on the left. A boulder rises above the level sand, so rays strike its front face from several metres out and bounce back as a dense cluster of elevated 3D points. Obstacles sticking up above the ground like this are called **positive obstacles**. Finding them is direct: fit a local plane or height grid to the surrounding sand and flag clusters standing well above it.

A crater behaves in the opposite way. Because the cameras (`0.70 m` high) and LiDAR (`0.94 m` high) view the arena at a shallow grazing angle, the near lip of a crater blocks the line of sight to its floor. Instead of returning a neat bowl of recessed points, the sensor sees flat sand, the near lip, and then an empty gap where no points come back at all. Drops below ground level like this are called **negative obstacles**.

That empty gap is ambiguous on real sand. Missing returns can come from a `45 cm` crater waiting to trap a wheel, the geometric shadow behind a boulder, a dark or wet patch absorbing infrared light, or ground beyond the active-stereo projector's reach. Guessing wrong in either direction hurts the run: ignoring a real gap sends the rover into a crater for a `30`-point penalty, while flagging every empty patch as a crater walls off clean routes across flat sand.

Range sharpens that problem further. Far ahead of the rover, LiDAR rings spread apart on the floor and hit at shallow angles where even a `5 cm` ripple casts a long shadow. Inside `2.42 m` of the central Ouster riser, the LiDAR's lowest beam overshoots level sand completely (see [Sensors](sensors.md#the-ouster-field-of-view-and-its-blind-zone)). Pairing the Ouster for mid-range positive obstacles and pit walls with downward-pitched front and rear OAK-D Pro depth cameras for near-field craters covers both zones.

## Unknown space, confirmed hazards and memory

Picture the rover spawning in the start zone with a large boulder two metres ahead blocking its view of the sand behind it. A newcomer's first instinct is often to start with an empty map and mark only detected rocks as blocked. If you do that, every hidden crater sitting in a boulder's shadow looks like clean sand, and the planner routes straight into it.

Flipping the default fails equally fast: if every unobserved square counts as a lethal obstacle, the rover boxes itself in and refuses to move. Perception resolves this by maintaining three distinct states for every cell on the floor: **free** (rays confirmed flat, traversable sand), **hazard** (a confirmed boulder, crater or wall) and **unknown** (occluded or uninspected so far). That three-way split lets the planner prefer confirmed free sand while driving cautiously up to the edge of unknown regions to reveal what sits behind an obstacle.

Confirmed hazards also need bounded memory. Once a boulder passes alongside the middle axle, neither the front camera nor the rear camera sees it, and it sits inside the Ouster's near-field ring; forgetting it instantaneously causes the rover to swing its tail into the rock on the next turn. Remembering every single point forever causes the opposite failure: one clump of airborne dust during digging permanently blocks a valid lane. Decaying obstacle confidence over time when fresh rays pass cleanly through the same volume clears transient dust while preserving real rocks nearby.

## Crop boxes, image masks and keepout zones

Three spatial filters sound alike in conversation while acting on different stages of the pipeline:

- A **crop box** deletes 3D points inside or outside a fixed volume in the rover's body frame, such as stripping depth returns off INNEX-1's own `15 cm` protruding bucket ladder so perception never mistakes the ladder for a rock right in front of the bumper.
- An **image mask** zeroes out fixed 2D pixel regions in a camera frame before stereo matching or AprilTag detection runs, hiding a chassis strut at the corner of the lens.
- A **keepout zone** is a planner-level polygon marking areas off limits on the map. Because the rules forbid hard-coding the arena's `7.9 m x 4.4 m` dimensions into autonomy software, you cannot draw a static rectangular keepout fence for the pit walls; wall boundaries have to enter the map from live sensor returns.

## Handling the arena walls

Any `360`-degree Ouster scan inside the Moon Yard picks up the surrounding wooden pit walls cleanly. Under the provisional 4 November 2026 organiser email clarification, mapping those live wall returns as obstacles for autonomy and navigation is expected to be allowed in the final 2027 rulebook, provided no arena dimensions are hard-coded.

Because that answer remains provisional until the final rulebook is published, isolating wall points in one explicit stage of the point-cloud pipeline gives the team two advantages: wall returns feed straight into the hazard map under the expected 2027 rules, or switch cleanly to a filter if the final rulebook restricts them, and you can show inspection judges the exact node handling wall points in thirty seconds.

## Requirements and competition rules

Subsystem requirements:

- Detect positive obstacles (`30` to `40 cm` boulders and raised terrain) and negative obstacles (craters up to `40` to `50 cm` wide or deep).
- Detect arena walls from live sensor scans without hard-coding pit dimensions.
- Maintain separate `free`, `hazard` and `unknown` ground states with bounded temporal memory.
- Strip self-returns from the bucket ladder and chassis using body-frame crop boxes or masks.
- Measure berm growth before and after a dump if mission logic requires volume confirmation.

Applicable rules:

- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): no hard-coded arena dimensions; live wall mapping is provisionally expected to be allowed in 2027, and sensing pipelines must be explained to inspection judges.
- [Autonomy conditions](../rules.md#autonomy-conditions) and [Autonomy penalties](../rules.md#autonomy-penalties): obstacles are randomised so routes must be sensed live, and hitting a boulder or crater in the obstacle zone costs `30` points per incident.
- [During the run](../rules.md#during-the-run) and [The arena](../rules.md#the-arena): boulders (`30` to `40 cm`) and craters (`40` to `50 cm`) cannot be pushed or filled in the obstacle zone.

## Open questions

1. Out to what distance do the `15-degree` pitched OAK-D Pro cameras reliably separate `40` to `50 cm` craters from shallow sand shadows?
2. Which map structure passes hazards to navigation: a 2.5D elevation map (`grid_map`), Nav2's `voxel_layer` / `spatio_temporal_voxel_layer`, or a custom height-step detector feeding `Costmap2D`?
3. What decay time keeps passed boulders in memory through a turn without locking airborne digging dust into the map?
4. Can two static Ouster scans (before and after dumping) estimate deposited berm volume accurately enough to guide mission decisions?

## Further reading

- [Sensors](sensors.md) and [`innex_sim` README](../../src/innex_sim/README.md)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) and [DepthAI v3](https://docs.luxonis.com/software-v3/depthai/)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
