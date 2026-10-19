# Glossary

## Action

A ROS 2 interface for a task that takes time, such as a dump sequence. The client sends a goal, receives progress while the task runs, and gets a result at the end. The client can also cancel the goal.

## AprilTag

A square black and white marker that a camera can detect. The detector reports the marker's ID and its pose relative to the camera. The beacon may carry one. See [Localisation](system/localisation.md).

## Berm

The pile of sand that the rover builds in the target area, which is about 1.5 m by 0.9 m. The rulebook calls the sand "regolith".

## BLDC motor

A brushless direct current motor. A controller must switch the current in the coils in the right order, so you cannot drive it like a brushed motor. The bucket ladder uses one. See [Teleop and rover control](system/teleop-and-control.md).

## Bridge

Software that passes data between two systems with different formats. In the sim, `ros_gz_bridge` passes messages between Gazebo and ROS 2. On the rover, a node on the Jetson passes `/cmd_vel` to the Teensy over USB serial.

## Costmap

A grid in which each cell holds a cost for driving through it. A planner uses it to find a cheap route that avoids hazards. See [Navigation and mission](system/navigation-and-mission.md).

## Covariance

How uncertain a measurement is. A small covariance means the sensor is precise. A filter uses covariance to decide how much to trust each sensor. See [Sensors](system/sensors.md).

## DDS

Data Distribution Service. The middleware that ROS 2 uses to find nodes and send messages between them. Discovery can fail over Wi-Fi. See [Comms](system/comms.md).

## EKF

Extended Kalman filter. An algorithm that combines several noisy measurements into one estimate, and tracks how uncertain the estimate is.

## Encoder

A sensor that counts the rotation of a wheel or motor. The wheel motors have Hall-effect quadrature encoders. Their two pulse trains are a quarter cycle apart, so a counter can find the direction of rotation. The Teensy counts the pulses.

## E-stop

Emergency stop. A latching red button. One push stops all motion and disconnects the batteries from all controllers. The rules require one. See [E-stop](rules.md#e-stop).

## Fiducial

A marker in the world that a sensor can detect, so that it can measure a pose from the marker. An AprilTag is a fiducial for cameras. Retroreflective markers are fiducials for a LiDAR.

## Frame

A coordinate system attached to something, such as the rover, a sensor or the arena. A measurement needs its frame to have a meaning. The main frames are `map`, `odom` and `base_link`. See [System design](system-design.md#frames).

## Hands-free

The state in which nobody controls the rover during an autonomy attempt. The rules set when an attempt starts and ends. See [Hands-free rules](rules.md#hands-free-rules).

## IMU

Inertial measurement unit. A sensor that measures rotation rate with a gyroscope and acceleration with an accelerometer. Some also have a magnetometer. The rules ban compass data, so the rover uses only the gyroscope and accelerometer.

## Launch file

A file that starts a group of ROS 2 nodes with their settings, in one command. For example, `moon_yard.launch.py` starts the sim, the bridge and the rover model.

## LiDAR

Light detection and ranging. A sensor that fires laser pulses and measures how long they take to return. The rover's LiDAR is an Ouster OS1-128.

## Message

One item of data sent on a topic. Its type sets the fields it holds. For example, `geometry_msgs/msg/TwistStamped` holds a velocity with a timestamp and a frame.

## Mux

Multiplexer. Software that takes commands from several sources and passes one on. A mux between the gamepad and the autonomy software means one source at a time commands a wheel.

## Node

A running ROS 2 program that does one job, such as reading a sensor or converting commands. Nodes talk to each other through topics, services and actions.

## Odometry

An estimate of how far and in which direction something has moved, found by adding up small motions. Wheel odometry drifts because the wheels slip.

## Point cloud

A set of 3D points that a sensor measured on the surfaces around it. A LiDAR and a depth camera both produce one.

## QoS

Quality of service. Settings on a ROS 2 topic that control delivery, such as whether to keep old messages. A publisher and a subscriber with incompatible settings may exchange no messages. See [Sensors](system/sensors.md#quality-of-service-for-sensors).

## Real-time factor

How fast simulated time runs compared with the clock on the wall. A value of 1 means the same speed. See [Simulation](system/simulation.md#real-time-factor).

## REP 103 and REP 105

ROS Enhancement Proposals that set conventions. REP 103 sets units and axis directions: x forward, y left and z up. REP 105 sets frame names and which frame is the parent of which.

## Setpoint

A target value that a controller works to reach, such as a wheel velocity or an actuator position. The rover commands its motors with absolute setpoints.

## Skid steer

A way to steer by driving the wheels on each side at different speeds. There is no steering mechanism. The wheels drag sideways in a turn, so the rover slips.

## Teleop

Teleoperation. A person drives the rover by remote control. The term also names the subsystem that does this. See [Teleop and rover control](system/teleop-and-control.md).

## TF

The ROS 2 transform library. It keeps the position and orientation of each frame relative to its parent. It also converts points from one frame to another. See [Localisation](system/localisation.md).

## Topic

A named stream of messages. Nodes publish to a topic and subscribe to it. `/cmd_vel` is the topic for velocity commands.

## URDF and xacro

URDF, the Unified Robot Description Format, is an XML description of a robot's links, joints, masses and sensors. Xacro is a macro language that expands into URDF, so you can reuse parts and use variables. See [Simulation](system/simulation.md).

## Watchdog

A timer that expects regular input and acts when the input stops. The Jetson bridge and the Teensy each use one to stop the motors when commands stop.
