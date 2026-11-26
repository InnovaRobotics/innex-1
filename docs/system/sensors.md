# Sensors

Sensors convert the physical arena into timestamped measurements that the rest of the software can act on. This subsystem covers the drivers, physical mounts and calibration for the cameras, LiDAR and inertial sensors, supplying images and point clouds to [Perception](perception.md), IMU readings, images and scans to [Localisation](localisation.md), and hardware-compressed H.264 video to [Comms](comms.md). Wheel quadrature encoders sit on the six drive motors and enter the system through [Teleop and rover control](teleop-and-control.md).

[`innex_description`](../../src/innex_description/README.md) defines the 3D coordinate frames for the front and rear OAK-D Pro cameras (`oak_front_frame`, `oak_rear_frame`, plus REP 103 optical frames) and the central Ouster OS1-128 (`os_sensor`). [`innex_video`](../../src/innex_video/README.md) streams hardware-encoded H.264 video from the cameras, and [`innex_sim`](../../src/innex_sim/README.md) publishes matching simulated camera feeds and `/ouster/points` in Gazebo Harmonic.

## Measurement metadata

A raw distance or pixel array on its own is unusable on a moving rover. Every sensor message carries three pieces of metadata alongside its payload.

The **timestamp** records the instant the sensor captured the physical scene. Suppose the rover turns at 0.4 rad/s while a LiDAR scan takes 250 ms to travel over Ethernet and receives a timestamp on arrival instead of capture: that quarter-second delay rotates every boulder in the scan by nearly 6 degrees, shifting a rock four metres away by 40 cm on the map.

The **frame** specifies where the sensor sits on the chassis and which way its axes point. `robot_state_publisher` broadcasts those offsets from the shared xacro model (see [Simulation](simulation.md)). If the front camera mounts 5 cm to the left of its URDF coordinates, every AprilTag fix and depth point carries that constant 5 cm offset.

The **covariance** states the typical spread of the sensor's error. State-estimation filters weight competing readings by their covariances ([Localisation](localisation.md) shows the calculation). If a noisy detector reports an artificially small covariance, one poor frame pulls the estimated pose off course.

## Stereo depth on sand

A stereo camera measures depth by finding a distinctive patch of pixels in the left image, locating the matching patch in the right image, and calculating distance from how far the patch shifted sideways between the two lenses. That method works cleanly on textured boulders and wooden walls.

Uniform sand defeats ordinary passive stereo because one patch of flat sand looks identical to the patch ten centimetres beside it. With no distinct visual texture to match, passive stereo leaves empty gaps across the floor. Each Luxonis OAK-D Pro solves this with **active stereo**: an onboard infrared laser projector casts a dense pattern of dots onto the sand ahead of the rover. Even on featureless regolith, the stereo matcher pairs those projected dots across left and right images to recover dense depth. Because projected infrared dots dim with distance and ambient arena lighting, active stereo works best within a few metres of the chassis.

## LiDAR field of view

The Ouster OS1-128 Rev 7 spans a vertical field of view of 42.4 degrees, from +21.2 degrees above horizontal to -21.2 degrees below it ([Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf); older Ouster revisions span 45 degrees, so verify the hardware revision label on the sensor).

When the LiDAR mounts level above the rover, its lowest laser beam angles downward at 21.2 degrees. That beam passes above the sand directly beside the wheels and first meets flat ground at a horizontal distance set by mount height:

```text
nearest level-ground hit = LiDAR height / tan(21.2 degrees)
```

At a mount height of 0.60 m, the innermost ring meets flat ground about 1.55 m from the sensor. Raising the mount clears the rover's own bodywork at the cost of widening that uninspected near-field ring.

In `innex_1.urdf.xacro`, placing the Ouster on a 23 cm central riser (`0.94 m` sensor base, `0.998 m` top height) lifts its -21.2-degree bottom beam clear of the chassis cross-rails and camera housings across all 360 degrees with zero self-returns, placing the nearest level-ground LiDAR hit at roughly 2.42 m. Inside that 2.42 m ring, the front and rear OAK-D Pro cameras (`0.70 m` high, pitched 15 degrees downward) cover the near ground. Because mechanical inspection enforces a 75 cm (`0.75 m`) stowed height limit at the start of a run, a central riser above 0.75 m must fold down for inspection and deploy after the timer starts, or sit lower with body-frame crop boxes filtering chassis returns.

## Quality of service

Suppose a camera publishes 15 or 30 depth frames per second and CPU load briefly delays an obstacle detector. If the middleware buffers every missed frame and retransmits dropped packets in sequence, the detector processes two-second-old images while the rover rolls forward.

In ROS 2 Jazzy, **quality of service (QoS)** profiles control how each topic trades delivery guarantees against latency. The standard sensor data profile uses best-effort reliability (dropping lost packets instead of waiting for retransmissions) and a queue depth of 5, discarding older frames once five newer ones arrive.

One mismatch causes silent connection failures: a best-effort publisher and a reliable subscriber do not connect, and ROS 2 prints no error in many command-line tools. Whenever a sensor topic delivers zero messages, inspect both ends with:

```bash
ros2 topic info --verbose /topic_name
```

## Compass compliance

Competition rules ban compasses completely, and inspection judges require teams to demonstrate how any onboard magnetometer is disabled or excluded. Hardware selection keeps that check clear:

- The Ouster OS1-128 contains a 6-axis IMU (3-axis gyroscope and 3-axis accelerometer) with no magnetometer hardware inside, making compliance straightforward to show at inspection.
- Luxonis OAK-D Pro cameras commonly include a 9-axis BNO086 IMU with a magnetometer (some batches fit a 6-axis BMI270). Check the IMU model reported by each unit, and configure any OAK IMU driver to publish raw gyroscope/accelerometer channels or the magnetometer-free game rotation vector only.

## Rules and constraints

- Publish every reading with capture time, a calibrated URDF frame and an honest covariance, using identical topic names and frame IDs in simulation and on hardware.
- Overlap LiDAR and downward-pitched stereo camera views so near-field ground inside the LiDAR dead zone is covered, while starting inside the 150 cm × 75 cm × 75 cm stowed envelope ([Before we compete](../rules.md#before-we-compete)).
- Exclude all GPS, compass, ultrasonic and touch-sensor data, and bring printed Class I / Class II laser eye-safety datasheets to inspection ([Not allowed](../rules.md#not-allowed), [Navigation and sensing](../rules.md#navigation-and-sensing)).

## Further reading

- [`innex_video` README](../../src/innex_video/README.md) and [`innex_description` README](../../src/innex_description/README.md)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) and [DepthAI v3](https://docs.luxonis.com/software-v3/depthai/)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf) and [ouster-ros](https://github.com/ouster-lidar/ouster-ros)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
