# Perception

Perception finds what is around the rover and where the rover cannot drive. It reads data from [Sensors](sensors.md) and finds obstacles, craters and the berm. [Navigation and mission](navigation-and-mission.md) uses the result.

## Requirements

- Find positive obstacles: rocks, and anything else that sticks up from the sand.
- Find negative obstacles: craters, and any other drop in the ground.
- Remove returns from the arena walls before any autonomy software sees them.
- Measure the berm, if the team decides the rover needs to.
- Separate unknown space from a confirmed hazard.

## Inputs and outputs

Perception takes point clouds and images from [Sensors](sensors.md). It sends hazards to [Navigation and mission](navigation-and-mission.md). The hazards might arrive as a cost map, as a list of objects, or in another form. The format is an open question.

Perception does not estimate the rover's pose. [Localisation](localisation.md) does that. Perception needs the pose to place what it sees on the arena floor.

## Rules

- [Navigation and sensing](../rules.md#navigation-and-sensing): the walls cannot be used for mapping, navigation or collision avoidance. You must prove this to the judges.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel, the judges set the obstacles so that the rover must detect them, map them and plan a route.
- [Autonomy penalties](../rules.md#autonomy-penalties): touching a rock or driving over a crater in the obstacle zone costs points.
- [During the run](../rules.md#during-the-run): do not push obstacles in the obstacle zone, and do not fill its craters.
- [The arena](../rules.md#the-arena): rocks are about 30 to 40 cm across. Craters are no more than about 40 to 50 cm deep or wide.

## Rocks and craters

Rocks are easier to find. A rock is a cluster of points that stands above the ground. A sensor sees it from a distance, and its shape stands out against flat sand. Software can fit a ground surface and mark whatever sits well above it.

Craters are harder. A crater shows up as a gap in the points. From low on the rover, the near rim hides the floor behind it, so the sensor sees the rim and then nothing. A missing return can mean a crater, a shadow, a dark patch, or a sensor that cannot see that far. Software must tell these apart. An error in either direction costs points. Missing a crater means driving into it. Marking flat sand as a crater blocks a route that was safe.

Distance makes this harder. From far away, the viewing angle is shallow, so the rim hides most of the floor. Close to the rover, the LiDAR sees no ground at all. [Sensors](sensors.md#the-ouster-field-of-view-and-its-blind-zone) explains why. The cameras must cover the near field.

## Unknown space and confirmed hazards

Space the rover has not seen is unknown. It is not free. A planner that treats unknown space as free drives into things it never saw. A planner that treats it as blocked cannot move. Perception labels each part of the area as free, hazard or unknown. The planner decides how much risk to accept in each part.

Hazards need short-lived memory. A rock the rover passed two seconds ago is still there, even though no sensor sees it. A hazard remembered for too long causes the opposite problem. A noisy detection then blocks a good route for the rest of the run. How long to remember a hazard is an open question.

## Crop boxes, masks and keepout zones

Three tools sound alike, but they do different jobs.

- A crop box removes 3D points that fall inside or outside a box. Use it to cut away points from the wall region.
- An image mask blanks part of a camera image before a detector reads it.
- A keepout zone is a constraint for the planner. It marks where the rover must not drive. A keepout zone must never serve as a landmark for localisation, because that would use the walls to find the rover's position.

## Wall returns

A LiDAR scan from the middle of the arena includes the walls. The software must remove those returns before any autonomy consumer sees them. The team must also show the judges how it does this. A filter that removes the points, together with a clear description of where the filter sits in the data flow, makes that demonstration possible.

## Open questions

1. Which sensor detects craters, and at what range: the Ouster, the OAK-D depth, or both?
2. How do crater detections reach the planner?
3. How are wall returns removed, and how do we show the judges that nothing uses them?
4. How long does the rover remember a hazard that it can no longer see?
5. Can the Ouster measure the berm before and after a dump?

## Further reading

- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
