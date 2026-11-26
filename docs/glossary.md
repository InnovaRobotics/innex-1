# Glossary

## Action
<!-- subtitle: Goal, feedback and result interface | aliases: actions -->

A ROS 2 interface for a long-running task, such as a dump sequence. A client sends a goal, receives progress feedback while the task runs, gets a final result when it finishes, and can cancel the goal partway through. See [ROS 2 Jazzy actions](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Actions.html).

## AprilTag
<!-- subtitle: Square visual fiducial marker | aliases: AprilTags -->

A square black-and-white visual marker that camera software detects to report the marker's ID and 3D pose relative to the lens. The arena beacon can carry AprilTags on its face alongside LiDAR reflectors. See [Localisation](system/localisation.md) and the [AprilTag library](https://github.com/AprilRobotics/apriltag).

## Berm
<!-- subtitle: Construction target pile | aliases: regolith -->

The pile of sand the rover builds inside the construction target area (about 1.5 m by 0.9 m). The rulebook refers to the sand as "regolith". See [Scoring](rules.md#scoring).

## BLDC motor
<!-- subtitle: Brushless direct current motor | aliases: BLDC -->

A brushless direct current motor. Because an electronic controller must energise its coils in sequence, you cannot drive it with a plain brushed motor driver. INNEX-1 uses a 24 V geared BLDC motor on the bucket ladder. See [Teleop and rover control](system/teleop-and-control.md).

## Bridge
<!-- subtitle: Protocol and format translator -->

Software that translates messages between two systems with different protocols or formats. In simulation, `ros_gz_bridge` connects Gazebo Harmonic and ROS 2; on the rover, [`innex_drive_bridge`](../src/innex_drive_bridge/README.md) translates `/cmd_vel` into 18-byte USB serial frames for the Teensy, and `foxglove_bridge` streams allow-listed ROS 2 topics (such as `/oak_front/video` and `/oak_rear/video` from [`innex_video`](../src/innex_video/README.md)) to Foxglove over a WebSocket. See [`ros_gz_bridge`](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md) and [`foxglove_bridge`](https://index.ros.org/p/foxglove_bridge/).

## Costmap
<!-- subtitle: 2D traversability penalty grid | aliases: costmaps -->

A 2D grid overlaid on the arena floor where every cell stores a numerical cost for driving across it. Planners search the costmap to find a low-cost route around boulders, craters and walls. See [Navigation and mission](system/navigation-and-mission.md) and [Nav2 documentation](https://docs.nav2.org/).

## Covariance
<!-- subtitle: Measurement uncertainty matrix | aliases: covariances, variance -->

A matrix describing how uncertain a multi-variable measurement or pose estimate is, and how errors in one variable (such as heading) couple into another (such as sideways position). State-estimation filters use covariance to weight competing sensors. See [Localisation](system/localisation.md) and [Sensors](system/sensors.md).

## DDS
<!-- subtitle: Data Distribution Service -->

Data Distribution Service, the underlying middleware ROS 2 uses for node discovery and message transport. Default UDP multicast discovery frequently fails over Wi-Fi, so wireless links use static peers or an alternative middleware such as `rmw_zenoh`. See [Comms](system/comms.md), [ROS 2 discovery concepts](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Discovery.html) and [`rmw_zenoh`](https://github.com/ros2/rmw_zenoh).

## EKF
<!-- subtitle: Extended Kalman filter | aliases: extended Kalman filter, Kalman filter -->

Extended Kalman filter, a state-estimation algorithm that projects motion forward using a curved (non-linear) motion model and incorporates incoming sensor readings weighted by their covariances. See [Localisation](system/localisation.md) and [Nav2 `robot_localization` setup](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/).

## Encoder
<!-- subtitle: Hall-effect quadrature rotation sensor | aliases: encoders, quadrature encoder, quadrature encoders -->

A sensor that tracks wheel or motor rotation. INNEX-1's wheel motors carry Hall-effect quadrature encoders whose two pulse channels sit a quarter cycle apart so the Teensy can read both speed and direction. See [Teleop and rover control](system/teleop-and-control.md).

## E-stop
<!-- subtitle: Latching hardware emergency cut-off -->

Emergency stop, a latching red hardware button required by the rules. One push halts all motion, disconnects batteries from all controllers and isolates active subsystems, and resetting the button must never restart motion automatically. See [E-stop](rules.md#e-stop).

## Fiducial
<!-- subtitle: Calibrated reference marker | aliases: fiducials -->

A physical marker with known geometry that a sensor detects to compute pose. AprilTags are visual fiducials for cameras; retroreflective strips work as fiducials for a LiDAR. See [Localisation](system/localisation.md).

## Frame
<!-- subtitle: 3D coordinate system | aliases: coordinate frame, coordinate frames -->

A 3D coordinate system attached to a physical object or place, such as the arena (`map`), continuous local motion (`odom`), the rover body (`base_link`) or a camera lens. Every spatial measurement needs a frame to have meaning. See [System design](system-design.md#frames) and [REP 105](https://www.ros.org/reps/rep-0105.html).

## Hands-free
<!-- subtitle: Unassisted autonomous operation -->

The state during an autonomy attempt in which nobody in mission control touches any laptop, gamepad or control, and no commands, orientation data or obstacle positions are sent to the rover. See [Hands-free rules](rules.md#hands-free-rules).

## ICP
<!-- subtitle: Iterative closest point | aliases: iterative closest point -->

Iterative closest point, an algorithm that aligns two 3D point clouds by repeatedly shifting and rotating one scan until its surfaces match the other. LiDAR odometry uses ICP variants to track rover motion against rigid features such as the arena walls. See [Localisation](system/localisation.md).

## IMU
<!-- subtitle: Inertial measurement unit | aliases: IMUs, gyroscope -->

Inertial measurement unit, a sensor containing a gyroscope (measuring rotation rate) and an accelerometer (measuring linear acceleration). Some IMUs also contain a magnetometer (compass), which the competition bans. See [Sensors](system/sensors.md).

## Launch file
<!-- subtitle: Multi-node startup configuration | aliases: launch files -->

An XML, Python or YAML file that starts a group of ROS 2 nodes and their parameters in one command, such as `moon_yard.launch.xml` starting Gazebo, the watchdog, the bridge and the rover model. See [ROS 2 Jazzy launch concepts](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Launch.html).

## LiDAR
<!-- subtitle: Light detection and ranging -->

Light detection and ranging, a sensor that fires laser pulses and times their reflections to measure 3D distances. INNEX-1 carries an Ouster OS1-128. See [Sensors](system/sensors.md) and the [Ouster OS1 Rev 7 datasheet](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p1-os1.pdf).

## LiDAR odometry
<!-- subtitle: Scan-matching motion estimation -->

Estimating rover motion by matching consecutive 3D LiDAR scans against each other (for example via ICP). Because rigid walls do not slip when tyres spin in sand, LiDAR odometry tracks motion across the arena without relying on wheel traction. See [Localisation](system/localisation.md).

## Message
<!-- subtitle: Typed ROS 2 data structure -->

One typed unit of data published on a ROS 2 topic. For example, `geometry_msgs/msg/TwistStamped` carries linear and angular velocities alongside a timestamp and coordinate frame. See [ROS 2 Jazzy interfaces](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Interfaces.html).

## Mux
<!-- subtitle: Command source multiplexer | aliases: multiplexer, command multiplexer -->

Multiplexer, software that arbitrates between several command sources and forwards only one at a time. An onboard command mux between teleop and autonomy passes commands from only one source to each motor and gives operator stop highest priority. See [Teleop and rover control](system/teleop-and-control.md) and [`twist_mux`](https://index.ros.org/p/twist_mux/).

## Node
<!-- subtitle: Single-purpose ROS 2 process -->

A running ROS 2 process responsible for one focused job, such as reading a camera or running a route planner. Nodes communicate over topics, services and actions. See [ROS 2 Jazzy nodes](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Nodes.html).

## Odometry
<!-- subtitle: Incremental motion integration | aliases: wheel odometry -->

An estimate of how far and in what direction the rover has moved, computed by summing successive small motions (from wheel encoders, a gyroscope or consecutive LiDAR scans). Because small errors accumulate, odometry drifts over time until corrected by a fixed landmark. See [Localisation](system/localisation.md).

## Point cloud
<!-- subtitle: 3D surface sample set | aliases: point clouds -->

A collection of 3D coordinates measured on surfaces around the rover. Both the Ouster LiDAR and the OAK-D Pro stereo cameras produce point clouds. See [Perception](system/perception.md) and [OAK-D Pro specifications](https://docs.luxonis.com/hardware/products/OAK-D%20Pro).

## Pose
<!-- subtitle: 3D position and orientation -->

The rover's position (`x`, `y`, `z`) and orientation (heading, roll and pitch) expressed in a specific coordinate frame. See [Localisation](system/localisation.md).

## QoS
<!-- subtitle: Quality of service | aliases: quality of service -->

Quality of service, per-topic ROS 2 settings governing reliability, history depth and durability. Incompatible QoS profiles between a publisher and subscriber silently prevent messages from connecting. See [Sensors](system/sensors.md#quality-of-service) and [ROS 2 Jazzy QoS settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html).

## Real-time factor
<!-- subtitle: Simulation speed ratio | aliases: RTF -->

The ratio of simulated time to wall-clock time in Gazebo. A value of `1.0` matches real time; `0.5` runs at half real speed. See [Simulation](system/simulation.md#real-time-factor) and [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/).

## REP 103 and REP 105
<!-- subtitle: ROS coordinate conventions | aliases: REP 103, REP 105 -->

ROS Enhancement Proposals that establish coordinate conventions. REP 103 specifies SI units and body axes (x forward, y left, z up); REP 105 specifies the standard `map`, `odom` and `base_link` frame chain. See [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html).

## Setpoint
<!-- subtitle: Absolute controller target | aliases: setpoints -->

An absolute target value sent to a controller, such as a wheel angular velocity in mrad/s or an actuator position, instead of a relative increment from the previous value. See [Teleop and rover control](system/teleop-and-control.md).

## Skid steer
<!-- subtitle: Differential six-wheel steering | aliases: skid-steer -->

A six-wheel drivetrain with no steering linkages that turns by driving its left and right sides at different speeds, dragging front and rear tyres sideways across the ground. See [Teleop and rover control](system/teleop-and-control.md).

## Teleop
<!-- subtitle: Remote gamepad operation | aliases: teleoperation -->

Teleoperation, driving the rover remotely from mission control with a gamepad. See [Teleop and rover control](system/teleop-and-control.md).

## TF
<!-- subtitle: ROS 2 transform library (tf2) | aliases: tf2 -->

The ROS 2 transform library (`tf2`), which maintains the tree of coordinate frames and converts points, poses and velocities between any two connected frames. See [Localisation](system/localisation.md) and [ROS 2 Jazzy tf2 concepts](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Tf2.html).

## Topic
<!-- subtitle: Named publish-subscribe stream -->

A named publish-subscribe stream of ROS 2 messages, such as `/cmd_vel` for velocity commands. See [ROS 2 Jazzy topics](https://docs.ros.org/en/jazzy/Concepts/Basic/About-Topics.html).

## URDF and xacro
<!-- subtitle: Unified Robot Description Format | aliases: URDF, xacro -->

URDF (Unified Robot Description Format) is an XML file describing the rover's links, joints, masses and sensor frames. Xacro is a macro language that expands into URDF so parts and dimensions stay reusable. See [Simulation](system/simulation.md) and [ROS 2 Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html).

## Watchdog
<!-- subtitle: Safety deadline timer | aliases: watchdogs -->

A timer expecting regular input that triggers a safe fallback (stopping all motor outputs) whenever input stops arriving within its deadline. Simulation (`cmd_vel_watchdog`, 500 ms), the Jetson drive bridge (`innex_drive_bridge`, 500 ms) and the Teensy (`teensy_drive`, 250 ms) each enforce independent watchdogs. See [Teleop and rover control](system/teleop-and-control.md#stop-at-three-layers).
