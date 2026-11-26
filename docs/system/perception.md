# Perception

Before navigation can choose a safe path across the obstacle zone, software has to turn 3D point clouds and stereo depth frames into a map of where the rover's six wheels can and cannot drive. Perception reads scans and depth images from [Sensors](sensors.md), detects boulders, craters and the surrounding pit walls, and publishes those hazards to [Navigation and mission](navigation-and-mission.md).

Perception does not estimate where the rover sits in the arena; [Localisation](localisation.md) provides the pose, and perception uses that pose to place each detected rock or crater onto the arena map instead of leaving it in a moving camera frame.

## Boulders and craters

Sensor rays interact differently with a 35 cm boulder than with a 45 cm crater:

```text
  Sensor on rover
       *  \  \  \________________________
           \  \       (empty shadow)     \
            \  \____                      \____
  ___________\ /    \_____________________/    \______
              Boulder                     Crater
           (dense cluster)            (missing returns)
```

A boulder rises above the level sand, so rays strike its front face from several metres away and return a dense cluster of elevated 3D points. Obstacles that rise above ground level are called **positive obstacles**. Detecting them is direct: fit a local ground plane or elevation grid to the surrounding sand and mark point clusters standing above a height threshold.

A crater works in the opposite way. Because the cameras (0.70 m high) and LiDAR (0.94 m high) view the floor at a shallow angle, the near lip of a crater blocks the line of sight to its interior. Instead of returning recessed floor points, the sensor records flat sand, the near rim, and then an empty region with no returns. Drops below ground level are called **negative obstacles**.

Missing returns on sand have more than one possible cause: a 45 cm crater, the geometric shadow behind a boulder, a dark patch absorbing infrared light, or ground beyond the active-stereo projector's range. Misclassifying in either direction carries a cost: missing a real crater incurs a 30-point penalty if a wheel enters it, while marking every empty gap as a crater blocks valid routes across flat sand.

Viewing distance changes which sensor sees each hazard. Far ahead of the rover, LiDAR scan rings spread apart on the floor and meet the sand at shallow angles. Within 2.42 m of the central Ouster mount, the lowest LiDAR ring passes above flat ground altogether (see [Sensors](sensors.md#lidar-field-of-view)). Pairing the Ouster for mid-range boulders and walls with downward-pitched front and rear OAK-D Pro depth cameras for near-field craters covers both ranges.

## Occupancy and memory

Suppose a boulder two metres ahead hides the patch of sand behind it. Treating every unobserved cell as clear ground routes the rover straight into hidden craters sitting in the boulder's shadow. Treating every unobserved cell as an impassable obstacle leaves the rover surrounded by blocked cells and unable to move forward.

Perception resolves this by keeping three distinct states for each cell on the arena floor: **free** (sensor rays confirmed flat, passable sand), **hazard** (a confirmed boulder, crater or wall) and **unknown** (unobserved so far). That separation lets the planner prefer confirmed free cells while advancing cautiously up to the edge of unknown areas as the sensors uncover more of the pit.

Detected hazards also require bounded memory. Once a boulder passes beside the middle axle, neither the front camera nor the rear camera sees it, and it sits inside the LiDAR's near-field dead zone; clearing detections immediately causes the rear wheels to clip the boulder during a turn. Keeping every detection indefinitely causes the reverse failure, where a single cloud of dust thrown up while digging blocks a clear lane for the rest of the run. Decaying obstacle confidence when fresh rays pass cleanly through the volume clears temporary dust while preserving nearby rocks.

## Spatial filters

Three filtering tools act at different stages of perception and planning:

- A **crop box** removes 3D points falling inside or outside a fixed volume in the rover's body frame, such as removing depth returns off INNEX-1's 15 cm overhanging bucket ladder so software never mistakes the ladder for a boulder ahead of the chassis.
- An **image mask** blanks fixed 2D pixel regions in a camera frame before stereo matching or tag detection runs, hiding a bracket at the edge of the lens.
- A **keepout zone** is a planner-level polygon marking areas off limits on the map. Because competition rules forbid hard-coding the arena's 7.9 m × 4.4 m dimensions into autonomy software, static rectangular keepout fences cannot represent the pit walls; wall positions must come from live sensor returns.

## Arena walls

Any 360-degree Ouster scan inside the Moon Yard detects the surrounding wooden pit walls. Under the provisional 4 November organiser email clarification, mapping live wall returns as obstacles for autonomy and navigation is expected to be allowed in the final 2027 rulebook, provided no arena dimensions are hard-coded.

Keeping wall point handling in one dedicated stage of the point-cloud pipeline allows wall returns to pass directly into the hazard map under the expected 2027 rules, or switch cleanly to a filter if the final rulebook restricts them, while making the sensing pipeline clear to demonstrate during pre-run inspection.

## Rules and constraints

- Detect positive obstacles (30 to 40 cm boulders) and negative obstacles (craters up to 40 to 50 cm wide or deep), keeping `free`, `hazard` and `unknown` states distinct ([The arena](../rules.md#the-arena), [Autonomy penalties](../rules.md#autonomy-penalties)).
- Map arena boundaries from live sensor returns without hard-coding pit dimensions, and keep the pipeline modular so wall handling can be demonstrated at inspection ([Navigation and sensing](../rules.md#navigation-and-sensing), [Organiser clarifications](../rules.md#organiser-clarifications-provisional)).
- Do not push boulders or fill craters inside the obstacle zone ([During the run](../rules.md#during-the-run)).

## Further reading

- [Sensors](sensors.md) and [`innex_sim` README](../../src/innex_sim/README.md)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) and [DepthAI v3](https://docs.luxonis.com/software-v3/depthai/)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
