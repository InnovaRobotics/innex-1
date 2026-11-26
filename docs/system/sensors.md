# Sensors

Sensors turn the physical arena into timestamped data streams that the rest of the rover can act on. This subsystem owns the drivers, physical mounts and calibration for the cameras, LiDAR and inertial sensors, feeding images and point clouds to [Perception](perception.md), IMU readings, images and scans to [Localisation](localisation.md), and compressed H.264 video to [Comms](comms.md). Wheel encoders sit on the six drive motors and enter the software stack through [Teleop and rover control](teleop-and-control.md).

On `main` today, [`innex_description`](../../src/innex_description/README.md) defines the 3D frames for the front and rear OAK-D Pro cameras (`oak_front_frame`, `oak_rear_frame`, plus REP 103 optical frames) and the central Ouster OS1-128 (`os_sensor`). [`innex_video`](../../src/innex_video/README.md) streams hardware-encoded H.264 video from the OAK-D Pro cameras, and [`innex_sim`](../../src/innex_sim/README.md) publishes simulated camera video and `/ouster/points` in Gazebo Harmonic. Onboard depth/IMU publishing (`depthai` and `ouster-ros`) and Teensy encoder telemetry are planned for Stages 2 and 3.

## Timestamp, frame and covariance

A raw distance or pixel array on its own is unusable on a moving robot. Every sensor message needs three pieces of metadata attached to it.

The **timestamp** records the exact instant the sensor captured the physical scene. Suppose the rover turns at `0.4 rad/s` while a LiDAR scan takes `250 ms` to travel over Ethernet and get stamped on arrival instead of capture: that quarter-second delay rotates every boulder in the scan by nearly `6 degrees`, swinging a rock four metres away by `40 cm` on the map.

The **frame** states where the sensor sits on the chassis and which way its axes point. `robot_state_publisher` broadcasts those offsets from the shared xacro model (see [Simulation](simulation.md)). If the physical front camera bolts on `5 cm` to the left of its URDF coordinates, every AprilTag fix and depth point carries that permanent `5 cm` bias.

The **covariance** states how spread out the sensor's errors tend to be. State-estimation filters weight competing readings by their covariances ([Localisation](localisation.md) works through the arithmetic). If a noisy detector reports a tiny covariance, one bad frame drags the rover's estimated position off course.

## Active and passive stereo on sand

A stereo camera estimates depth the way human eyes do: it picks a distinctive patch of pixels in the left lens, finds the matching patch in the right lens, and computes distance from how far the patch shifted sideways between the two views. That works cleanly on textured rocks, arena walls or lab floors.

Flat, uniform sand breaks ordinary passive stereo because one patch of sand looks identical to the patch ten centimetres beside it. With nothing distinct to match, a passive stereo camera leaves empty holes across the floor. Each Luxonis OAK-D Pro solves this with **active stereo**: an infrared laser projector casts a dense dot texture onto the sand ahead of the rover. Even on featureless regolith, the stereo matcher locks onto those projected dots and recovers close-range depth. Because infrared dots dim with square-law distance and ambient arena lighting, active stereo excels within a few metres of the chassis.

## The Ouster field of view and its blind zone

The Ouster OS1-128 Rev 7 spans a vertical field of view of `42.4 degrees`, from `+21.2 degrees` above the horizon to `-21.2 degrees` below it ([Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf); older Ouster revisions listed `45 degrees`, so check the revision label on the unit).

When the LiDAR sits level above the rover, its lowest laser ring angles downward at `21.2 degrees`. Those beams overshoot the sand directly beside the wheels and first touch flat ground some distance out:

```text
nearest level-ground hit = LiDAR height / tan(21.2 degrees)
```

At a low mount height of `0.60 m`, the innermost scan ring hits flat sand about `1.55 m` from the sensor. Raising the sensor clears the rover's own bodywork at the cost of widening that uninspected ring.

You can see that exact trade-off in the November 2026 INNEX-2 robot model (`innex_1.urdf.xacro`). Placing the Ouster on a `23 cm` central riser (`0.94 m` sensor base, `0.998 m` top height) lifts its `-21.2 degree` bottom beam cleanly above both rounded cross-rails and camera housings across all `360 degrees` with zero self-hits, while pushing the nearest level-ground LiDAR hit out to roughly `2.42 m`. Inside that `2.42 m` ring, the front and rear OAK-D Pro cameras (`0.70 m` above ground, pitched `15 degrees` downward) cover the near sand. Because the pre-run mechanical inspection enforces a `75 cm` (`0.75 m`) stowed height limit, the `0.998 m` central riser must either fold down for inspection and deploy after the run starts, or move to a lower mount with a crop box stripping chassis self-returns.

## Quality of service for sensors

Suppose a camera publishes `15` or `30` depth frames per second and CPU load briefly stalls an obstacle detector. If the middleware buffers every missed frame and insists on resending dropped packets in order, the detector ends up processing stale images from two seconds ago while the rover keeps rolling towards a crater.

In ROS 2 Jazzy, **quality of service (QoS)** profiles govern how each topic balances reliability against freshness. The built-in sensor data profile uses best-effort reliability (drop lost packets instead of stalling to retransmit them) and a short queue depth of `5`, discarding older frames once five newer ones arrive.

One trap catches people out repeatedly: a best-effort publisher and a reliable subscriber are incompatible, so ROS 2 refuses to connect them and prints no error in many tools. Whenever a sensor topic stays silent, inspect both ends with:

```bash
ros2 topic info --verbose /topic_name
```

## Compass data

Competition rules forbid compasses of every kind, and inspection judges ask teams to demonstrate how any onboard magnetometer is disabled or stripped. Hardware selection keeps that demonstration clean:

- The Ouster OS1-128 contains a 6-axis IMU (3-axis gyroscope and 3-axis accelerometer) with no magnetometer hardware inside the housing, making it simple to verify at inspection.
- Luxonis OAK-D Pro units typically carry a 9-axis BNO086 IMU with a magnetometer (some hardware batches fit a 6-axis BMI270). Check the exact IMU reported by each camera, and if any node reads an OAK IMU, configure it to publish raw gyroscope/accelerometer readings or the magnetometer-free game rotation vector only.

## Requirements and competition rules

Subsystem requirements:

- Stamp every measurement with capture time, a calibrated URDF frame and an honest covariance.
- Overlap LiDAR and stereo camera coverage so near-field sand inside the LiDAR ring is never unobserved.
- Match topic names, message types and frame IDs between simulation and hardware.
- Exclude all magnetometer and compass data across every driver and node.

Applicable rules:

- [Not allowed](../rules.md#not-allowed): no GPS, no compasses, no ultrasonic sensors and no touch sensors.
- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): lasers must be unmodified and Class I, Class II or under `5 mW`, with printed eye-safety datasheets at inspection; live wall sensing is provisionally expected to be allowed in 2027 provided arena dimensions are never hard-coded.
- [Before we compete](../rules.md#before-we-compete): the rover must start inside a `150 cm x 75 cm x 75 cm` stowed envelope, including all sensor mounts.
- [Scoring](../rules.md#scoring): avoiding both arena cameras earns `120` points.

## Open questions

1. Does the `23 cm` central Ouster platform deploy after the start timer begins, or drop below `0.75 m` permanently with self-hit crop boxes?
2. How much of the front camera and Ouster fields of view does the bucket ladder occlude when stowed versus lowered into the sand?
3. Does localisation fuse the Ouster's 6-axis IMU alone, or add gyroscope readings from an OAK-D Pro?
4. What depth image resolution, frame rate and Ouster scan rate (`10 Hz` vs `20 Hz`) fit comfortably inside the Jetson's `25 W` power budget alongside autonomy?
5. What jig or calibration target verifies the physical transform from `base_link` to both cameras and the Ouster on the assembled chassis?

## Further reading

- [`innex_video` README](../../src/innex_video/README.md) and [`innex_description` README](../../src/innex_description/README.md)
- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) and [DepthAI v3](https://docs.luxonis.com/software-v3/depthai/)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf) and [ouster-ros](https://github.com/ouster-lidar/ouster-ros)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
