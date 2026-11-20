# Sensors

Sensors turn the physical arena into structured data streams that the rest of the rover can reason about. This subsystem owns the drivers, physical mounts and calibration for the cameras, LiDAR and inertial sensors, feeding images and point clouds to [Perception](perception.md), IMU data, images and scans to [Localisation](localisation.md), and compressed H.264 video to [Comms](comms.md). Wheel encoders sit on the drive motors and enter the system through [Teleop and rover control](teleop-and-control.md).

## Requirements

- Publish every reading with an accurate timestamp, a known coordinate frame and an honest estimate of its uncertainty.
- Overlap sensor views around the rover so the cameras cover the ground close to the chassis where the LiDAR can't see.
- Publish matching topics and coordinate frames in simulation and on the physical rover, so autonomy code runs identically on both.
- Exclude all compass and magnetometer data from every node.

## Hardware

- Two Luxonis OAK-D Pro cameras (front and rear): active stereo depth, colour video, hardware H.264 video encoding and an onboard IMU.
- One Ouster OS1-128 LiDAR: 360-degree 3D point cloud, surface reflectivity and a built-in 6-axis IMU.
- Hall-effect quadrature encoders mounted on the wheel motors (read by the Teensy).

## Competition rules

- [Not allowed](../rules.md#not-allowed): no GPS, no compasses, no ultrasonic proximity sensors and no touch sensors.
- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): lasers must be unmodified and Class I, Class II or below 5 mW, with manufacturer eye-safety documentation brought to inspection. Under the organisers' 4 November email, sensing the arena walls as obstacles is expected to be allowed in the final 2027 rulebook as long as no arena dimensions are hard-coded.
- [Before we compete](../rules.md#before-we-compete): the stowed rover must fit inside 150 cm × 75 cm × 75 cm at the start, including the height of every mounted sensor.
- [Scoring](../rules.md#scoring): each arena camera used costs 60 points, so the rover's own cameras give the operator's view.

## Timestamp, frame and covariance

A raw distance or pixel on its own is nearly useless to a moving rover. Every sensor message has to carry three pieces of metadata alongside its data:

The **timestamp** records the exact instant the sensor captured the measurement. Because the rover drives and turns while messages travel over USB or Ethernet, pairing a scan with a timestamp even half a second late places a rock or beacon in the wrong spot on the arena floor.

The **frame** identifies where the sensor sits on the chassis and which way it points. The URDF robot model stores the physical offset from `base_link` to every camera lens, IMU and LiDAR origin (see [Simulation](simulation.md)). If a camera is mounted 5 cm to the left of where the URDF says it is, every depth point and AprilTag pose carries that same 5 cm offset.

The **covariance** states how wrong a measurement is likely to be. Fusion filters such as an extended Kalman filter use covariance to weight competing readings ([Localisation](localisation.md) works through the exact maths). If a noisy sensor claims tiny covariance, one bad frame can drag the rover's estimated position metres off course.

## Active and passive stereo on sand

A standard stereo camera works like human eyes: it finds a distinctive patch of pixels in the left image, searches for the matching patch in the right image, and calculates depth from how far the patch shifted sideways. That works cleanly on brick walls, rocks or patterned carpets.

Bare arena sand breaks standard passive stereo because one patch of flat sand looks identical to the patch ten centimetres beside it. Without distinct visual texture, the matcher gives up and leaves large blank holes in the depth map. The OAK-D Pro avoids this with **active stereo**: an onboard infrared projector casts a crisp dot pattern across the sand ahead of the rover. Even on featureless sand, the stereo matcher locks onto those dots and recovers dense close-range depth. Because projected dots fade over distance and bright ambient light, active stereo shines in the near field within a few metres of the rover.

## The Ouster field of view and its blind zone

The Ouster OS1-128 Rev 7 spans a vertical field of view of 42.4 degrees, from +21.2 degrees above horizontal to -21.2 degrees beneath it ([Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf); older Ouster revisions listed 45 degrees, so confirm the revision stamped on your unit).

When you mount the LiDAR level on top of the rover, its lowest laser beam angles down at 21.2 degrees. That beam doesn't touch level ground directly beside the wheels; it strikes the sand some distance out:

```text
nearest level-ground hit = LiDAR height / tan(21.2 degrees)
```

At a mount height of 0.60 m, the nearest ground return lands about 1.55 m from the sensor. Closer than 1.55 m, the LiDAR shoots straight over the sand and can't see a low rock or crater rim. Raising the sensor pushes that ring farther out, and the 75 cm starting height cap limits how high you can mount it anyway.

The rover's own deck makes placement even more critical. In the June 2026 CAD model, sitting the Ouster 0.30 m back from the front edge of a flat top deck lets the deck block the lower beams, pushing the first ground return out to roughly 6 m ahead and hiding the ground behind the rover altogether while putting the top of the LiDAR over the 0.75 m limit. Moving the mount close to the front edge, tilting the sensor slightly, or raising it on a deployable mast after start are the main mechanical options, and the front and rear OAK-D Pro cameras cover the near ground beneath the LiDAR ring.

## Quality of service for sensors

Suppose a camera publishes 30 depth frames every second and Wi-Fi or CPU load briefly stalls a subscriber. If the transport holds onto old frames and insists on resending every dropped packet, your obstacle detector ends up processing stale frames from two seconds ago while the rover keeps rolling forward.

In ROS 2 Jazzy, **quality of service (QoS)** profiles control how topics handle delivery and buffering. The standard sensor data profile uses best-effort reliability (drop lost samples instead of stalling to resend them) and a short queue depth of 5, keeping only the newest frames. A queue depth of 1 discards every frame except the most recent.

There is one common trap: if a publisher uses best-effort reliability and a subscriber demands reliable delivery, ROS 2 refuses to connect them and often prints no error at all. Whenever a sensor topic looks silent, compare both ends with:

```bash
ros2 topic info --verbose /topic_name
```

## Compass data

The rules ban compasses completely, and judges ask you to demonstrate how any onboard magnetometer is disabled or stripped. Check the exact hardware inside each sensor you rely on:

- The Ouster OS1-128 contains a 6-axis IMU (gyroscope and accelerometer only) with no magnetometer, which makes explaining compass compliance to the judges straightforward.
- Luxonis OAK-D Pro cameras commonly carry a 9-axis BNO086 IMU that includes a magnetometer (some revisions carry a 6-axis BMI270). Always inspect the IMU reported by each camera unit, and if you read an OAK IMU, subscribe only to raw gyroscope and accelerometer data or the magnetometer-free game rotation vector.

## Open questions

1. Where will the Ouster mount on the revised chassis so it clears the deck, sees the near ground and stays inside the 75 cm starting height?
2. How much of the Ouster's and front camera's fields of view does the bucket ladder block in stowed and lowered positions?
3. Which IMU feeds localisation: the Ouster's 6-axis IMU or an OAK-D Pro IMU?
4. What camera resolutions, frame rates and LiDAR scan rates can the Jetson process in 25 W mode?
5. How does the team measure and verify the physical transform from `base_link` to every sensor on the assembled rover?

## Further reading

- [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [Ouster OS1 Rev 7 datasheet, version 3p1](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf)
- [ouster-ros](https://github.com/ouster-lidar/ouster-ros)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
