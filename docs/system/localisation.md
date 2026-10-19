# Localisation

Localisation finds where the rover is in the arena. It combines wheel motion, inertial data and the one fixed landmark that the rules allow. The result is the rover's pose: its position and heading. [Navigation and mission](navigation-and-mission.md) and [Perception](perception.md) use the pose.

## Requirements

- Give a pose that does not jump, so that controllers and planners see smooth motion.
- Correct the slow drift of the pose against something fixed in the arena.
- Work from a random start position and heading.
- Use no GPS data, no compass data and no arena walls.
- State how uncertain the pose is.

## Inputs and outputs

Localisation takes wheel encoder counts from [Teleop and rover control](teleop-and-control.md). It takes IMU data, camera images and LiDAR point clouds from [Sensors](sensors.md). It gives the pose to [Navigation and mission](navigation-and-mission.md) and to [Perception](perception.md).

## Rules

- [Not allowed](../rules.md#not-allowed): no GPS and no compass. If an IMU has a compass, its data must be switched off or removed.
- [Navigation and sensing](../rules.md#navigation-and-sensing): you can mount a beacon or fiducial on the frame near the start zone. You cannot use the walls.
- [The run](../rules.md#the-run): the judges choose the start position and direction at random, just before the run.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel and full autonomy, you can drive only inside the start zone to localise.
- [Hands-free rules](../rules.md#hands-free-rules): do not send orientation data to the rover during an autonomous attempt.

## The odom and map frames

REP 105 defines two frames for the pose. The `odom` frame is smooth and continuous, but it drifts over time. It suits short-range control, because the pose never jumps. The `map` frame stays fixed to the arena, but it can jump when a correction arrives. It suits route planning across the arena.

The frames form a chain: `map` to `odom` to `base_link`. In the transform (TF) tree, each frame has exactly one parent. If two nodes both published a transform from `map` to `base_link`, a lookup would return two answers. So each link in the chain has one owner. The drift correction goes into the link between `map` and `odom`. Motion of `base_link` in `odom` stays smooth.

## Wheel odometry on sand

Wheel odometry adds up wheel rotation into distance. On sand, the wheels slip, so the rover moves less than the wheels say. A skid-steer rover turns by dragging its wheels sideways, so the error is largest in turns. The error grows with every metre the rover drives. Odometry cannot detect it.

## The IMU gives heading change

A gyroscope measures how fast the rover rotates. Adding those rates up gives the change in heading since the start. This is the most useful thing the IMU gives, because it does not depend on wheel slip. The gyroscope drifts slowly. The IMU cannot give the heading in the arena frame. A compass could, but the rules ban compasses. A heading change is therefore always relative to the starting heading.

## The beacon is the one fixed landmark

Everything above drifts. To correct the drift, the rover needs something fixed, with a known position in the arena. The rules allow one landmark: a beacon or fiducial on the frame near the start zone, facing the construction zone. A fiducial is a marker that software can detect to measure a pose. An AprilTag is one kind.

The beacon is the only fixed landmark, so corrections are rare. They happen when the rover sees the beacon. Between sightings, the rover relies on odometry.

## The start zone

At the start, the rover does not know where it is or which way it faces. The judges choose both at random. The rules let the rover drive inside the start zone to localise. The rover must move until it finds the beacon and fixes its pose. The team must solve how to do this from a random heading. A beacon that faces the construction zone cannot be seen from every heading, so the rover may need to turn to find it.

## How localisation fails

- Wheel slip: odometry says the rover moved, and it did not.
- One noisy detection, trusted too much: the pose jumps to a wrong place, and the planner follows it.
- Bad timestamps: a measurement lines up with the wrong moment, and the filter blames the wrong motion.
- Bad calibration: a sensor's measured position on the rover differs from its position in the model. Every measurement then carries the same error.

A fusion filter, such as an extended Kalman filter (EKF), weighs each source by its covariance and combines them. The filter still depends on honest covariances and good calibration. Whether the first autonomy tasks need a filter at all is an open question.

## Open questions

1. Does the beacon carry an AprilTag, retroreflective markers, or both?
2. Where exactly is the beacon frame, and how big can the beacon be?
3. How far does wheel odometry drift on sand over one crossing, and in a turn?
4. Do the first autonomy targets need a fused estimate, such as an EKF, or are odometry and the beacon enough?
5. How does the rover find the beacon from a random start heading? Can the rear camera help?
6. Is LiDAR odometry worth its processing cost on the Jetson?

## Further reading

- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
- [AprilTag library](https://github.com/AprilRobotics/apriltag)
- [apriltag_ros](https://index.ros.org/p/apriltag_ros/)
- [DepthAI AprilTag node](https://docs.luxonis.com/software-v3/depthai/depthai-components/nodes/april_tag/)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
