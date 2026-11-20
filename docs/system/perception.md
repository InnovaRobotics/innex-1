# Perception

Before navigation can choose a safe lane across the obstacle zone, the rover has to turn raw camera images and laser returns into a clear picture of where it can and can't drive. Perception reads point clouds and depth images from [Sensors](sensors.md), locates boulders, craters and arena walls, and hands those hazards to [Navigation and mission](navigation-and-mission.md).

Perception doesn't estimate where the rover is in the arena; [Localisation](localisation.md) owns the pose. Perception takes that pose so it can place each rock or crater at the right spot on the arena floor instead of only knowing where the hazard sat relative to the camera a split second ago. Whether hazards reach navigation as a 2D costmap, an elevation grid or an object list remains an open design choice.

## Requirements

- Detect positive obstacles: boulders (about 30 to 40 cm across) and anything else rising above the sand.
- Detect negative obstacles: craters (up to 40 to 50 cm wide or deep) and any sudden drop in the ground.
- Detect the arena walls from live sensor returns so navigation keeps the rover inside the pit without hard-coded arena bounds.
- Keep unknown space distinct from confirmed free space and confirmed hazards.
- Measure the berm before and after a dump, if the team decides the mission needs volume feedback.

## Competition rules

- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): the 2027 draft rulebook forbids using arena walls, while the organisers' 4 November email states that mapping the walls as obstacles for autonomy and navigation is expected to be allowed in the final rulebook, provided you don't hard-code the arena's dimensions. Keep the sensor pipeline modular so a wall filter can be enabled if the final rulebook reverts.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel autonomy, judges place boulders and craters so the rover must sense them, map them and plan around them live.
- [Autonomy penalties](../rules.md#autonomy-penalties): touching a boulder or driving over a crater in the obstacle zone costs 30 points per incident.
- [During the run](../rules.md#during-the-run): do not push boulders or fill craters inside the obstacle zone.
- [The arena](../rules.md#the-arena): boulders are roughly 30 to 40 cm across, and craters are up to 40 to 50 cm deep or wide.

## Why craters are much harder to see than boulders

Walk through what a laser or stereo camera sees when you point it across sandy ground. A boulder sticks up above the flat sand, so beams hit its front face from several metres away and return a tight cluster of elevated points. Objects that rise above the ground like this are called **positive obstacles**. Detecting them is direct: fit a smooth ground surface to the nearby sand and flag any cluster of points sitting well above it.

A crater works in the opposite way. Because the sensor sits low on the rover, the near lip of a crater blocks the sensor's line of sight to the floor inside the hole. Instead of returning a neat bowl of deep points, the sensor sees flat sand, then the lip, and then an empty gap with no returns at all. Drops in the ground like this are called **negative obstacles**.

That gap creates an awkward ambiguity. A missing return can mean a 45 cm crater waiting to trap a wheel, a shadow behind a rock, a dark patch that absorbed the light, or ground sitting beyond the sensor's useful range. Guessing wrong in either direction hurts you: ignoring a real gap sends the rover into a crater for a 30-point penalty, while treating every empty gap as a crater walls off safe routes across flat sand.

Viewing angle makes distance matter too. Farther from the rover, laser beams skim the sand at a shallow angle, so the near rim hides almost the whole crater and neighbouring LiDAR scan rings spread far apart on the ground. Close to the rover, the Ouster's lowest beam overshoots the floor altogether ([Sensors](sensors.md#the-ouster-field-of-view-and-its-blind-zone) works out the exact dead zone). That's why perception pairs the LiDAR for mid-range scanning with front and rear OAK-D Pro depth cameras covering the near field.

## Unknown space, confirmed hazards and memory

Suppose a sensor hasn't seen the patch of sand behind a boulder. Your first instinct might be to mark every spot without a detected obstacle as clear to drive through. If you do that, the planner happily routes the rover straight through uninspected craters hidden behind rocks.

The opposite extreme fails too. If you mark every unseen cell as blocked, the rover can't drive forward into areas its sensors haven't reached. Perception solves this by keeping three separate labels for every patch of ground: **free** (the sensor saw flat, traversable sand), **hazard** (a confirmed boulder, crater or wall) and **unknown** (unobserved so far). That lets the planner decide how cautiously to treat unknown space as the rover moves and fills in the map.

Hazards also need short-lived memory. A boulder that passed beside the front wheel two seconds ago hasn't vanished even though the front camera no longer sees it, so forgetting hazards immediately causes the rover to clip obstacles while turning. Keeping every detection forever causes the reverse problem: a single burst of dust or a stray noisy return blocks a clean lane for the rest of the run. Tuning how long a hazard decays without fresh sightings is an open question.

## Crop boxes, image masks and keepout zones

Three perception and mapping tools sound similar in conversation, even though they act at completely different stages of the pipeline:

- A **crop box** deletes 3D points falling inside or outside a chosen volume in space (for example, stripping points that hit the rover's own bucket ladder so the rover doesn't mistake itself for a boulder).
- An **image mask** blanks out fixed pixels in a 2D camera frame before a depth matcher or detector runs (for example, hiding a bracket at the edge of the lens).
- A **keepout zone** is a map-level constraint given to the planner to mark areas the rover must avoid driving into. Because the rules forbid hard-coding arena dimensions into autonomy software, you can't draw a static keepout box from the rulebook's 7.9 m by 4.4 m size to represent the walls; walls have to enter the map from live sensor returns.

## Handling the arena walls

A 360-degree Ouster scan from anywhere in the Moon Yard picks up the surrounding pit walls clearly. Under the organisers' 4 November email clarification, mapping those live wall returns as obstacles for autonomy and navigation is expected to be allowed in the final 2027 rulebook, as long as the rover never relies on hard-coded arena dimensions.

Because that clarification is provisional until the final rulebook is published, keeping wall handling isolated in one clean stage of the point-cloud pipeline gives you a clean fallback: walls flow straight into the hazard map under the expected 2027 rules, or pass through a dedicated filter if the final rulebook restricts wall returns. Either way, you can point straight to that stage during inspection and show the judges how every point is handled.

## Open questions

1. At what range does each sensor (Ouster LiDAR versus front and rear OAK-D Pro depth) reliably detect 40 to 50 cm craters without excessive false positives?
2. What data representation carries hazards from perception to navigation: a 2D costmap, an elevation grid (such as `grid_map`) or a custom obstacle list?
3. How long does the hazard map remember an obstacle once it leaves the sensor field of view?
4. How does perception filter out dust plumes kicked up during digging and turning?
5. Can the Ouster measure berm growth before and after a dump accurately enough to be useful?

## Further reading

- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
