# Sensors

Sensors turn the physical world into data. [Perception](perception.md) and [Localisation](localisation.md) interpret that data.

## Requirements

- Publish every measurement with a timestamp, a frame and an honest estimate of its accuracy.
- Cover the area around the rover, near and far. Overlap the views, so that one sensor's blind spot is another sensor's view.
- Publish the same topics and frames in the sim and on the rover. Code written against one must run on the other.
- Do not use compass data.

## Inputs and outputs

Sensors take no input from other subsystems. They send images and point clouds to [Perception](perception.md). They send IMU data and images to [Localisation](localisation.md). They send compressed video to [Comms](comms.md). The wheel encoders belong to [Teleop and rover control](teleop-and-control.md), which sends their counts to localisation.

## Hardware

- Two Luxonis OAK-D Pro cameras, front and rear. Each has active stereo depth, colour video, on-camera H.264 encoding and a built-in IMU.
- An Ouster OS1-128 LiDAR. It gives a 360-degree 3D point cloud and reflectivity, with a built-in IMU.
- Hall-effect quadrature encoders on the four wheel motors.

## Rules

- [Not allowed](../rules.md#not-allowed): no GPS and no compass.
- [Navigation and sensing](../rules.md#navigation-and-sensing): you must prove that the autonomy sensors do not use the walls. Lasers must be unmodified, and Class I, Class II or below 5 mW.
- [Robot requirements](../rules.md#before-we-compete): the rover must fit in 150 cm × 75 cm × 75 cm at the start. Sensor height counts.
- [Scoring](../rules.md#scoring): arena cameras cost points. The rover's own cameras give the operator's view.

## Timestamp, frame and covariance

Each measurement needs three things.

- The timestamp says when the sensor took the measurement. A late or wrong timestamp makes a moving rover look as if it jumped.
- The frame says where the sensor is and which way it points. The URDF holds the position of each sensor frame relative to `base_link`. See [Simulation](simulation.md).
- The covariance is the honest estimate of how wrong the measurement might be. A filter uses it to decide how much to trust each sensor. A sensor that claims to be exact gets too much trust. One noisy reading then pulls the estimate away from the truth.

## Active and passive stereo on sand

A stereo camera finds depth by matching a patch in the left image to the same patch in the right image. Sand is flat, uniform and low in texture. A passive stereo camera finds few matches, so its depth map has holes. The OAK-D Pro is an active stereo camera. It projects a dot pattern onto the scene. The pattern gives the matcher texture to follow on bare sand. Active stereo has a limited range, so it suits the near field.

## The Ouster field of view and its blind zone

The Ouster OS1-128 has a vertical field of view of 42.4 degrees, from +21.2 to −21.2 degrees. That figure comes from the Rev 7 datasheet, [version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf). Older datasheets give 45 degrees, from +22.5 to −22.5. Check the revision that matches your sensor.

If you mount the sensor level, the lowest beam points 21.2 degrees below the horizon. The beam reaches level ground only at some distance from the rover:

```text
nearest level-ground hit = LiDAR height / tan(21.2 degrees)
```

At a height of 0.6 m, the nearest hit is about 1.55 m away. Closer than that, the LiDAR sees no ground. A crater or a low rock in that zone is invisible to it. The cameras cover this near field. A higher mount makes the blind zone larger, and the size limit caps how high you can mount the sensor.

## Quality of service for sensors

Sensor data arrives at a steady rate, and an old frame has little value once a newer one exists. In ROS 2 Jazzy, the sensor data profile uses best effort reliability and a queue depth of 5. Best effort means that lost samples are not resent. The queue keeps the five newest samples. A queue depth of 1 keeps only the newest sample.

If the publisher and the subscriber use settings that do not match, messages may not arrive. You may see no error. To compare the settings at both ends, run:

```bash
ros2 topic info --verbose /topic_name
```

## Compass data

The rules ban compasses. If an IMU has one, you must explain to the judges how you switch it off, or how you remove its data. Luxonis lists the OAK-D Pro IMU as a BNO086, a 9-axis IMU with a magnetometer. Check the IMU on each camera you use.

Use only the gyroscope and accelerometer data, or the game rotation vector. Make sure no software reads the magnetometer, or a heading derived from it.

## Open questions

1. Where does each sensor mount? Does the Ouster keep the rover inside the 75 cm starting height?
2. How much of the Ouster's view, and of the front camera's view, does the bucket ladder block?
3. Which IMU feeds localisation: a camera's IMU or the Ouster's?
4. What resolutions and rates can the Jetson process in 25 W mode?
5. How do we measure and check the transform of each sensor from `base_link`?

## Further reading

- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [ouster-ros](https://github.com/ouster-lidar/ouster-ros)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
