# Localisation

This page answers where the rover is in the arena. It combines wheel motion, inertial data and the one fixed landmark the rules allow into one estimate of the rover's position and heading, called its pose. [Navigation and mission](navigation-and-mission.md) and [Perception](perception.md) use that pose. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Give a pose that doesn't jump, so the controllers and the planner see smooth motion.
- Correct the slow drift of that pose against something fixed in the arena.
- Work from a random start position and heading.
- Use no global positioning system (GPS) data, no compass data and no arena walls.
- Say how uncertain the pose is.

## Inputs and outputs

Localisation takes wheel encoder counts from [Teleop and rover control](teleop-and-control.md), and inertial measurement unit (IMU) data, camera images and LiDAR (light detection and ranging) point clouds from [Sensors](sensors.md). It gives the rover's pose to [Navigation and mission](navigation-and-mission.md), and to [Perception](perception.md), which needs the pose to place what it sees on the arena floor.

## Rules that apply

- [Not allowed](../rules.md#not-allowed): no GPS and no compass. An IMU's compass data must be turned off or removed.
- [Navigation and sensing](../rules.md#navigation-and-sensing): you can mount a beacon or fiducial on the frame near the start zone, and you can't use the walls.
- [Competition run](../rules.md#competition-run): the judges choose the start position and direction at random, immediately before the run.
- [Autonomy conditions](../rules.md#autonomy-conditions): for travel and full autonomy, you can drive only inside the start zone to localise.
- [Hands-free rules](../rules.md#hands-free-rules): you can't send orientation data to the rover during an autonomous attempt.

## Odom and map

The Robot Operating System (ROS) convention uses two frames for the rover's pose, described in [REP 105](https://www.ros.org/reps/rep-0105.html). The `odom` frame is smooth and continuous but drifts over time. It suits short-range control, because the pose never jumps. The `map` frame stays fixed to the arena, but it can jump when a correction arrives. It suits planning a route across the arena.

The frames form a chain: `map` to `odom` to `base_link`. In the transform (TF) tree, each frame has exactly one parent. If two nodes both published a transform from `map` to `base_link`, a lookup would give two answers, and the answer would change from one message to the next. One node therefore owns each link in the chain. The drift correction goes into the link between `map` and `odom`, so `base_link` motion in `odom` stays smooth.

## Wheel odometry on sand

Wheel odometry adds up wheel rotation into distance. On sand the wheels slip, so the rover moves less than the wheels say. A skid-steer rover turns by dragging its wheels sideways, so the error is largest in turns. The error grows with every metre the rover drives, and nothing inside the odometry can detect it.

## The IMU gives heading change

A gyroscope measures how fast the rover rotates. Adding that up gives how far the heading has changed since the start, which is the most useful thing the IMU gives, because it doesn't care about wheel slip. The gyroscope also drifts slowly. An IMU can't tell you the rover's heading in the arena frame. A compass could, and the rules ban it. A heading change is therefore always relative to the starting heading.

## The beacon is the one fixed landmark

Everything above drifts. To correct it, the rover needs something fixed whose position in the arena is known. The rules allow one: a beacon or fiducial on the frame near the start zone, facing the construction zone. A fiducial is a marker that software can detect and measure a pose from. An AprilTag is one kind. The beacon is the only fixed landmark the rules allow, so global corrections are rare. They happen when the rover sees the beacon, and between sightings the rover relies on odometry.

## The start zone

At the start, the rover doesn't know where it is or which way it faces, because the judges pick both at random. The rules let you drive inside the start zone to localise, so the rover can move until it finds the beacon and fixes its pose. The team has to solve how it does this from a random heading. A beacon that faces the construction zone can't be seen from every heading, and the rover might need to turn to find it.

## How localisation fails

- Wheel slip: odometry says the rover moved, and it didn't.
- One noisy detection, trusted too much: the pose jumps to a wrong place, and the planner follows it there.
- Bad timestamps: a measurement lines up with the wrong moment, and the filter blames the wrong motion.
- Bad calibration: a sensor's measured position on the rover differs from its position in the model, so every measurement carries the same error.

A fusion filter, such as an extended Kalman filter (EKF), weighs each source by its covariance and combines them. It still depends on honest covariances and good calibration. Whether the first autonomy tasks need a filter at all is an open question.

## Open questions

1. Does the beacon carry an AprilTag, retroreflective markers, or both?
2. Where exactly is the beacon frame, and how big can the beacon be?
3. How far does wheel odometry drift on sand over one crossing, and in a turn?
4. Do the first autonomy targets need a fused estimate, such as an EKF, or is odometry plus the beacon enough?
5. How does the rover find the beacon from a random start heading, and can the rear camera help?
6. Is LiDAR odometry worth its processing cost on the Jetson?

## Read more

- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
- [AprilTag library](https://github.com/AprilRobotics/apriltag)
- [apriltag_ros](https://index.ros.org/p/apriltag_ros/)
- [DepthAI AprilTag node](https://docs.luxonis.com/software-v3/depthai/depthai-components/nodes/april_tag/)
- [How many pixels an AprilTag needs](https://www.chiefdelphi.com/t/pixels-for-apriltag-detection/424609)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
