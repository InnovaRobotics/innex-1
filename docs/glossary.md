# Glossary

These terms appear in the [system design](system-design.md) pages. Each entry gives the general meaning and, where it helps, how it applies to INNEX-1.

## Action

A ROS 2 (Robot Operating System 2) interface for a task that takes time, such as a dump sequence. The client sends a goal, receives progress feedback while the task runs, and gets a result at the end. The client can also cancel the goal.

## AprilTag

A square black and white marker that software can detect in a camera image. The detector reports the marker's ID and its pose relative to the camera. A beacon on the arena frame might carry one. See [Localisation](system/localisation.md).

## BLDC motor

A brushless direct current motor. It has no brushes, so a controller must switch the current in its coils in the right order. The bucket ladder uses a 24 V geared BLDC motor, so you can't drive it like a brushed motor. See [Teleop and rover control](system/teleop-and-control.md).

## Bridge

Software that passes data between two systems that don't share a format. On INNEX-1, `ros_gz_bridge` passes messages between Gazebo and ROS 2 in the sim. On the rover, a node on the Jetson passes `/cmd_vel` to the Teensy over USB serial.

## Costmap

A grid map in which each cell holds a cost for driving through it. A planner uses it to find a cheap route that avoids hazards. See [Navigation and mission](system/navigation-and-mission.md).

## Covariance

A measure of how uncertain a measurement is. A small covariance says the sensor is precise. A filter uses covariance to decide how much to trust each sensor. See [Sensors](system/sensors.md).

## DDS

Data Distribution Service, the middleware that ROS 2 uses to find other nodes and send messages between them. DDS discovery over Wi-Fi can fail, which affects the link between the laptop and the Jetson. See [Comms and mission control](system/comms.md).

## EKF

Extended Kalman filter. An algorithm that combines several noisy measurements into one estimate, and tracks how uncertain the estimate is. Localisation might use one to fuse wheel odometry, the IMU and beacon detections.

## Encoder

A sensor on a motor or wheel that counts rotation. The INNEX-1 wheel motors have Hall-effect quadrature encoders, which give two pulse trains a quarter cycle apart, so a counter can tell the direction of rotation. The Teensy counts the pulses.

## E-stop

Emergency stop. A latching red button that stops all motion and disconnects the batteries from all controllers. The rules require one. See [E-stop](rules.md#e-stop).

## Fiducial

A marker placed in the world so that a sensor can find it and measure a pose from it. An AprilTag is a fiducial for cameras. Retroreflective markers are fiducials for a LiDAR.

## Frame

A coordinate system attached to something, such as the rover, a sensor or the arena. A measurement is only meaningful with its frame. The main frames are `map`, `odom` and `base_link`. See [System design](system-design.md#frames).

## IMU

Inertial measurement unit. A sensor that measures rotation rate with a gyroscope and acceleration with an accelerometer, and sometimes magnetic field with a magnetometer. The rules ban compass data, so INNEX-1 uses only the gyroscope and accelerometer.

## Launch file

A file that starts a group of ROS 2 nodes with their settings in one command. For example, `moon_yard.launch.py` starts the sim, the bridge and the rover model.

## LiDAR

Light detection and ranging. A sensor that fires laser pulses and measures how long they take to return, which gives distances in many directions. The Ouster OS1-128 is the rover's LiDAR.

## Message

One item of data sent on a topic. Its type fixes the fields it holds. For example, `geometry_msgs/msg/TwistStamped` holds a velocity with a timestamp and a frame.

## Mux

Multiplexer. Software that has several sources of commands and passes one of them on. A mux between the gamepad and the autonomy software means only one source commands a wheel at a time.

## Node

A running program in ROS 2 that does one job, such as reading a sensor or converting commands. Nodes talk to each other through topics, services and actions.

## Odometry

An estimate of how far and in which direction something has moved, found by adding up small motions. Wheel odometry adds up wheel rotation. It drifts because the wheels slip.

## Point cloud

A set of 3D points that a sensor measured on the surfaces around it. A LiDAR and a depth camera both produce them.

## QoS

Quality of service. A set of options on a ROS 2 topic that controls how messages are delivered, such as whether to keep old messages. A publisher and a subscriber with settings that don't match might exchange no messages. See [Sensors](system/sensors.md).

## Real-time factor

How fast simulated time runs compared with the clock on the wall. 1 means the same speed. See [Robot model and simulation](system/simulation.md).

## REP 103 and REP 105

ROS Enhancement Proposals that set conventions. [REP 103](https://www.ros.org/reps/rep-0103.html) sets units and axis directions: x forward, y left and z up. [REP 105](https://www.ros.org/reps/rep-0105.html) sets frame names and which frame is the parent of which.

## Setpoint

A target value that a controller works to reach, such as a wheel velocity or an actuator position. INNEX-1 commands motors with absolute setpoints.

## Skid steer

A way to steer by driving the wheels on the left and right sides at different speeds, with no steering mechanism. The wheels drag sideways in a turn, so the rover slips.

## TF

The ROS 2 transform library. It keeps the position and orientation of each frame relative to its parent, and lets a node convert a point from one frame to another. See [Localisation](system/localisation.md).

## Topic

A named stream of messages. Nodes publish to a topic and subscribe to it. `/cmd_vel` is the topic for velocity commands.

## URDF and xacro

URDF, the Unified Robot Description Format, is an XML description of a robot's links, joints, masses and sensors. Xacro is a macro language that expands into URDF, so you can reuse parts and use variables. See [Robot model and simulation](system/simulation.md).

## Watchdog

A timer that expects regular input and acts when the input stops. The Jetson bridge and the Teensy each use one to stop the motors when commands stop. See [Teleop and rover control](system/teleop-and-control.md).
