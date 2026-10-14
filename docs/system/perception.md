# Perception

This page answers what is around the rover, and where it can't drive. Perception reads the data from [Sensors](sensors.md) and finds the obstacles, craters and berm. [Navigation and mission](navigation-and-mission.md) uses the result. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Find positive obstacles: rocks and anything else that sticks up from the sand.
- Find negative obstacles: craters and any other drop in the ground.
- Remove returns from the arena walls before any autonomy software sees them.
- Measure the berm, if the team decides the rover needs to.
- Tell the difference between unknown space and a confirmed hazard.

## Inputs and outputs

Perception takes point clouds and images from [Sensors](sensors.md). It gives hazards to [Navigation and mission](navigation-and-mission.md). The hazards might arrive as a map of cells that the rover must avoid, as a list of objects, or in another form. How they arrive is an open question.

Perception doesn't estimate the rover's pose. [Localisation](localisation.md) does that, and perception needs the pose to place what it sees on the arena floor.

## Rules that apply

- [Navigation and sensing](../rules.md#navigation-and-sensing): you can't use the walls for mapping, navigation or collision avoidance, and you must prove it to the judges.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel, the judges set the obstacles so that the rover must detect them, map them and plan a route.
- [Autonomy penalties](../rules.md#autonomy-penalties): touching a rock or driving over a crater in the obstacle zone costs points.
- [During the run](../rules.md#during-the-run): the rover must not push obstacles in the obstacle zone or fill its craters.
- [Arena](../rules.md#arena): rocks are about 30 cm to 40 cm across, and craters are no more than about 40 cm to 50 cm deep or wide.

## Rocks are the easier half

A rock is a cluster of points that stands above the ground. A sensor sees it from a distance, and its shape gives a clear signal against the flat sand around it. Software can find it by fitting a ground surface and marking whatever sits well above that surface.

## Craters are the harder half

A crater is an absence of points. From low on the rover, the near rim of a crater hides the floor behind it, so the sensor sees the rim and then nothing. A missing return has several possible causes: a crater, a shadow, a dark patch, or a sensor that couldn't see that far. Software must separate these from a crater, and a mistake in either direction costs points. Missing a crater means driving into it. Marking flat sand as a crater blocks a route that was safe.

Distance makes this worse in two ways. From far away, the viewing angle is shallow and the rim hides most of the floor. Close to the rover, the LiDAR (light detection and ranging) sensor sees no ground at all, as [Sensors](sensors.md#the-ouster-field-of-view-and-its-blind-zone) explains, so the cameras must cover the near field.

## Unknown space and confirmed hazards

Space the rover hasn't seen is unknown, not free. A planner that treats unknown space as free drives into things it never saw. A planner that treats it as blocked can't move at all. Perception must label each part of the area as free, hazard or unknown, and the planner decides how much risk it accepts in each.

Hazards need short-lived memory. A rock the rover passed 2 seconds ago is still there, even though no sensor sees it. Remembering a hazard for too long causes the opposite problem, because a noisy detection then blocks a good route for the rest of the run. How long to remember is an open question.

## Crop boxes, masks and keepout zones

Three tools sound alike and do different jobs.

- A crop box removes 3D points that fall inside or outside a box. You can use one to cut away the points that come from the wall region.
- An image mask blanks part of a camera image before a detector reads it.
- A keepout zone is a constraint for the planner. It tells the planner where the rover must not drive. A keepout zone must never act as a landmark for localisation, because that would use the walls to find the rover's position.

## Wall returns

The rules forbid using the walls for mapping, navigation and collision avoidance. A LiDAR scan from the middle of the arena includes the wall, so the software must remove those returns before any autonomy consumer sees them. The team must also be able to show the judges how it does this, in a way that proves nothing downstream uses the wall data. A filter that removes the points and a clear description of where it sits in the data flow make that demonstration possible.

## Open questions

1. Which sensor detects craters, at which range: the Ouster, the OAK-D depth, or both?
2. How do crater detections reach the planner?
3. How are wall returns removed, and how do we show the judges that nothing uses them?
4. How long does the rover remember a hazard it can no longer see?
5. Can the Ouster measure the berm before and after a dump?

## Read more

- [Ouster OS1 datasheet](https://data.ouster.io/downloads/datasheets/datasheet-rev7p1-v3p2-os1.pdf)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
