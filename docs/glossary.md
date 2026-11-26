# Glossary

## Action

A ROS 2 interface for a long-running task, such as a dump sequence. A client sends a goal, receives progress feedback while the task runs, gets a final result when it finishes, and can cancel the goal partway through.

## AprilTag

A square black-and-white visual marker that camera software detects to report the marker's ID and 3D pose relative to the lens. The arena beacon can carry AprilTags on its face alongside LiDAR reflectors. See [Localisation](system/localisation.md).

## Berm

The pile of sand the rover builds inside the construction target area (about 1.5 m by 0.9 m). The rulebook refers to the sand as "regolith".

## BLDC motor

A brushless direct current motor. Because an electronic controller must energise its coils in sequence, you cannot drive it with a plain brushed motor driver. INNEX-1 uses a 24 V geared BLDC motor on the bucket ladder. See [Teleop and rover control](system/teleop-and-control.md).

## Bridge

Software that translates messages between two systems with different protocols or formats. In simulation, `ros_gz_bridge` connects Gazebo Harmonic and ROS 2; on the rover, [`innex_drive_bridge`](../src/innex_drive_bridge/README.md) translates `/cmd_vel` into `18`-byte USB serial frames for the Teensy, and `foxglove_bridge` streams allow-listed ROS 2 topics (such as `/oak_front/video` and `/oak_rear/video` from [`innex_video`](../src/innex_video/README.md)) to Foxglove over a WebSocket.

## Costmap

A 2D grid overlaid on the arena floor where every cell stores a numerical cost for driving across it. Planners search the costmap to find a low-cost route around boulders, craters and walls. See [Navigation and mission](system/navigation-and-mission.md).

## Covariance

A matrix describing how uncertain a multi-variable measurement or pose estimate is, and how errors in one variable (such as heading) couple into another (such as sideways position). Fusion filters use covariance to weight competing sensors. See [Localisation](system/localisation.md) and [Sensors](system/sensors.md).

## DDS

Data Distribution Service, the underlying middleware ROS 2 uses for node discovery and message transport. Default UDP multicast discovery frequently fails over Wi-Fi, so wireless links use static peers or an alternative middleware such as `rmw_zenoh`. See [Comms](system/comms.md).

## EKF

Extended Kalman filter, a state-estimation algorithm that predicts motion forward using a curved (non-linear) motion model and blends incoming sensor readings weighted by their covariances. See [Localisation](system/localisation.md).

## Encoder

A sensor that tracks wheel or motor rotation. INNEX-1's wheel motors carry Hall-effect quadrature encoders whose two pulse channels sit a quarter cycle apart so the Teensy can read both speed and direction. See [Teleop and rover control](system/teleop-and-control.md).

## E-stop

Emergency stop, a latching red hardware button required by the rules. One push halts all motion, disconnects batteries from all controllers and isolates active subsystems, and resetting the button must never restart motion automatically. See [E-stop](rules.md#e-stop).

## Fiducial

A physical marker with known geometry that a sensor detects to compute pose. AprilTags are visual fiducials for cameras; retroreflective strips work as fiducials for a LiDAR.

## Frame

A 3D coordinate system attached to a physical object or place, such as the arena (`map`), continuous local motion (`odom`), the rover body (`base_link`) or a camera lens. Every spatial measurement needs a frame to have meaning. See [System design](system-design.md#frames).

## Hands-free

The state during an autonomy attempt in which nobody in mission control touches any laptop, gamepad or control, and no commands, orientation data or obstacle positions are sent to the rover. See [Hands-free rules](rules.md#hands-free-rules).

## ICP

Iterative closest point, an algorithm that aligns two 3D point clouds by repeatedly shifting and rotating one scan until its surfaces match the other. LiDAR odometry uses ICP variants to track rover motion against rigid features such as the arena walls. See [Localisation](system/localisation.md).

## IMU

Inertial measurement unit, a sensor containing a gyroscope (measuring rotation rate) and an accelerometer (measuring linear acceleration). Some IMUs also contain a magnetometer (compass), which the competition bans. See [Sensors](system/sensors.md).

## Launch file

An XML, Python or YAML file that starts a group of ROS 2 nodes and their parameters in one command, such as `moon_yard.launch.xml` starting Gazebo, the watchdog, the bridge and the rover model.

## LiDAR

Light detection and ranging, a sensor that fires laser pulses and times their reflections to measure 3D distances. INNEX-1 carries an Ouster OS1-128.

## LiDAR odometry

Estimating rover motion by matching consecutive 3D LiDAR scans against each other (for example via ICP). Because rigid walls do not slip when tyres spin in sand, LiDAR odometry tracks motion across the arena without relying on wheel traction. See [Localisation](system/localisation.md).

## Message

One typed unit of data published on a ROS 2 topic. For example, `geometry_msgs/msg/TwistStamped` carries linear and angular velocities alongside a timestamp and coordinate frame.

## Mux

Multiplexer, software that arbitrates between several command sources and forwards only one at a time. An onboard command mux between teleop and autonomy passes commands from only one source to each motor and gives operator stop highest priority. See [Teleop and rover control](system/teleop-and-control.md).

## Node

A running ROS 2 process responsible for one focused job, such as reading a camera or running a route planner. Nodes communicate over topics, services and actions.

## Odometry

An estimate of how far and in what direction the rover has moved, computed by summing successive small motions (from wheel encoders, a gyroscope or consecutive LiDAR scans). Because small errors accumulate, odometry drifts over time until corrected by a fixed landmark. See [Localisation](system/localisation.md).

## Point cloud

A collection of 3D coordinates measured on surfaces around the rover. Both the Ouster LiDAR and the OAK-D Pro stereo cameras produce point clouds.

## Pose

The rover's position (`x`, `y`, `z`) and orientation (heading, roll and pitch) expressed in a specific coordinate frame. See [Localisation](system/localisation.md).

## QoS

Quality of service, per-topic ROS 2 settings governing reliability, history depth and durability. Incompatible QoS profiles between a publisher and subscriber silently prevent messages from connecting. See [Sensors](system/sensors.md#quality-of-service-for-sensors).

## Real-time factor

The ratio of simulated time to wall-clock time in Gazebo. A value of `1.0` matches real time; `0.5` runs at half real speed. See [Simulation](system/simulation.md#real-time-factor).

## REP 103 and REP 105

ROS Enhancement Proposals that establish coordinate conventions. REP 103 specifies SI units and body axes (x forward, y left, z up); REP 105 specifies the standard `map`, `odom` and `base_link` frame chain.

## Setpoint

An absolute target value sent to a controller, such as a wheel angular velocity in mrad/s or an actuator position, instead of a relative increment from the previous value.

## Skid steer

A six-wheel drivetrain with no steering linkages that turns by driving its left and right sides at different speeds, dragging front and rear tyres sideways across the ground.

## Teleop

Teleoperation, driving the rover remotely from mission control with a gamepad. See [Teleop and rover control](system/teleop-and-control.md).

## TF

The ROS 2 transform library (`tf2`), which maintains the tree of coordinate frames and converts points, poses and velocities between any two connected frames. See [Localisation](system/localisation.md).

## Topic

A named publish-subscribe stream of ROS 2 messages, such as `/cmd_vel` for velocity commands.

## URDF and xacro

URDF (Unified Robot Description Format) is an XML file describing the rover's links, joints, masses and sensor frames. Xacro is a macro language that expands into URDF so parts and dimensions stay reusable. See [Simulation](system/simulation.md).

## Watchdog

A timer expecting regular input that triggers a safe fallback (stopping all motor outputs) whenever input stops arriving within its deadline. Simulation (`cmd_vel_watchdog`, 500 ms), the Jetson drive bridge (`innex_drive_bridge`, 500 ms) and the Teensy (`teensy_drive`, 250 ms) each enforce independent watchdogs. See [Teleop and rover control](system/teleop-and-control.md#stop-at-three-layers).
