# Sensors

This page answers what each sensor measures, where it sits and what it publishes. Sensors turn the physical world into data. [Perception](perception.md) and [Localisation](localisation.md) interpret that data. See [System design](../system-design.md) for where they sit in the whole rover.

## What it must do

- Publish every measurement with a timestamp, a coordinate frame and an honest estimate of its accuracy.
- Cover the area around the rover, near and far, with enough overlap that one sensor's blind spot is another's view.
- Publish the same topics and frames in the sim and on the rover, so code written against one runs on the other.
- Leave out compass data.

## Inputs and outputs

The sensors take nothing from other subsystems. They give images and point clouds to [Perception](perception.md), inertial measurement unit (IMU) data and images to [Localisation](localisation.md), and compressed video to [Comms and mission control](comms.md). The wheel encoders belong to [Teleop and rover control](teleop-and-control.md), which gives their counts to Localisation.

## Rules that apply

- [Not allowed](../rules.md#not-allowed): no GPS, and no compass. If an IMU has a compass, you must show the judges how you turn it off or remove its data.
- [Navigation and sensing](../rules.md#navigation-and-sensing): you must prove that autonomy sensing doesn't use the walls. Lasers must be unmodified, and Class I, Class II or below 5 mW.
- [Size and mass](../rules.md#size-and-mass): the rover must fit in 150 cm by 75 cm by 75 cm at the start, so sensor height counts.
- [Scoring](../rules.md#scoring): arena cameras cost points, so the rover's own cameras give the operator's view.

## Hardware

- Two Luxonis OAK-D Pro cameras, front and rear: active stereo depth, colour video, on-camera H.264 encoding and a built-in IMU.
- Ouster OS1-128 LiDAR: 360 degree 3D point cloud and reflectivity, with a built-in IMU.
- Hall-effect quadrature encoders on the four wheel motors.

## Nodes, topics and messages

A node is a running program, such as "read the camera" or "turn encoder counts into odometry". A topic is a named stream of data that nodes publish and subscribe to. A message is one item on that stream, and its type fixes the fields inside it. A camera driver is a node that publishes images on a topic, and a perception node subscribes to that topic. Neither node needs to know about the other.

## Timestamp, frame and covariance

Every measurement needs three things. The timestamp says when the sensor took the measurement, so software can line it up with other data. A late or wrong timestamp makes a moving rover look as if it jumped. The frame says where the sensor was and which way it pointed, so the point 2 m ahead of a camera becomes a point on the ground. The Unified Robot Description Format file ([URDF](simulation.md)) holds the position of each sensor frame relative to `base_link`.

Covariance is the honest estimate of how wrong the measurement might be. A filter uses it to decide how much to trust one sensor against another. A sensor that claims to be exact gets trusted too much, and one noisy reading then pulls the estimate away from the truth.

## Active and passive stereo on sand

A stereo camera finds depth by matching a patch of the left image to the same patch in the right image. Sand is flat, uniform and low in texture, so a passive stereo camera finds few matches and returns holes. The OAK-D Pro is an active stereo camera. It projects a dot pattern onto the scene, which gives the matcher texture to follow even on bare sand. Active stereo has a limited range, so it suits the near field.

## The Ouster field of view and its blind zone

The OS1-128 sees a vertical field of view of plus or minus 21.2 degrees, 360 degrees around. If you mount it level, the lowest beam points 21.2 degrees below the horizon. The beam reaches level ground only at some distance from the rover:

```text
nearest level-ground hit = LiDAR height / tan(21.2 degrees)
```

At a height of 0.6 m, the nearest hit is about 1.55 m away. Closer to the rover than that, the LiDAR sees no ground at all, so a crater or a low rock in that zone is invisible to it. The cameras cover this near field. A higher mount makes the blind zone larger, and the starting size limit caps how high you can mount it.

## Quality of service for sensors

Sensor data arrives at a steady rate, and an old frame has no value once a newer one exists. Sensor topics use a best effort quality of service (QoS) setting that keeps only the newest sample. If a publisher and a subscriber use settings that don't match, ROS 2 (Robot Operating System 2) delivers nothing and usually reports nothing. When a topic shows up in `ros2 topic list` but a node receives no messages, compare the QoS of both ends with `ros2 topic info --verbose`.

## Compass data

The OAK-D IMU includes a magnetometer, which measures magnetic heading like a compass. The rules ban compasses. Use only the gyroscope and accelerometer, and make sure no software reads the magnetometer or a heading derived from it.

## Open questions

1. Where does each sensor mount, and does the Ouster keep the rover inside the 75 cm starting height?
2. How much of the Ouster's view and the front camera's view does the bucket ladder block?
3. Which IMU feeds localisation: a camera's or the Ouster's?
4. What resolutions and rates can the Jetson process in 25 W mode?
5. How do we measure and check each sensor's transform from `base_link`?

## Read more

- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Ouster OS1 datasheet](https://data.ouster.io/downloads/datasheets/datasheet-rev7p1-v3p2-os1.pdf)
- [ouster-ros](https://github.com/ouster-lidar/ouster-ros)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
