# Robot model and simulation

This page answers how we test all of the other subsystems without the rover. The robot model describes the rover's shape and sensors, and the simulation (sim) runs that model in a virtual copy of the arena. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Stand in for the rover, so the team can test software before the rover exists or while it is unavailable.
- Publish the same topics and frames as the real rover, so code written against the sim runs on the rover.
- Hold the rover's dimensions, masses and sensor positions in one model.
- Run fast enough to test against, which means a real-time factor close to 1.

## Inputs and outputs

The sim takes velocity commands, as the real rover does, from [Teleop and rover control](teleop-and-control.md). It gives odometry, transforms, joint states and the clock back. The [`innex_sim` README](../../src/innex_sim/README.md#rover) lists the topics. When the model includes sensors, the sim gives their data to [Perception](perception.md) and [Localisation](localisation.md) through the same topics and frames as the real sensors.

## Rules that apply

- [Navigation and sensing](../rules.md#navigation-and-sensing): the sim's walls are geometry only, and autonomy must not use them.
- [Arena](../rules.md#arena): the world follows the arena size and the zone layout.
- [Competition run](../rules.md#competition-run): the judges randomise the start pose, and the sim lets you set the spawn pose with launch arguments.

## Where the details live

This page explains the ideas. The package READMEs hold the commands and the numbers:

- [`innex_sim`](../../src/innex_sim/README.md): the Moon Yard world, the launch file, the topics, the arena frame and the zones.
- [`innex_description`](../../src/innex_description/README.md): the robot model and its frames.

To build the workspace and run the sim for the first time, follow [ONBOARDING.md](../../ONBOARDING.md).

## What the sim is for

The sim lets you find mistakes before the rover can hurt anyone or anything. You can drive it, break it, reset it and run the same test a hundred times. A bug that appears in the sim costs a few minutes. The same bug on the rover costs a test session and needs someone at the emergency stop (E-stop). The sim also lets people work when the rover is in pieces or at another site.

The sim only helps if it matches the rover where your code can tell the difference. The sim and the real rover publish the same topics and frames. If you change a topic name or a frame in one, change it in the other.

## What the sim leaves out

Gazebo doesn't simulate sand usefully, so the sim leaves digging physics out. The sim also doesn't model realistic wheel slip on sand. Both limits matter for the other pages:

- A dig or a dump in the sim can show that the commands and the sequence work. It can't show how much sand the ladder lifts.
- Wheel odometry in the sim might drift less than on the real rover, so a localisation filter that works in the sim might still need tuning on the rover.

## The robot model

The robot model is a Unified Robot Description Format (URDF) file, written as xacro, which is a macro language that expands into URDF. It lists the rover's parts as links, such as the chassis and the wheels, and joins them with joints. Each link has a mass and a shape, and each sensor has a frame that fixes where it sits relative to `base_link`.

The sim and the real rover use the same URDF. On the rover, `robot_state_publisher` reads it and publishes the transforms between the frames, so a camera frame in the model is the camera frame on the rover. This is why sensor positions must come from measurements of the real rover.

The model starts rough: a box chassis, four wheels, and estimated masses. Measurements of the real rover replace the estimates. A rough model is enough to test the command path, the frames and the launch files, so you don't have to wait for exact numbers.

## Real-time factor

The real-time factor (RTF) is how fast simulated time runs compared with the clock on the wall. An RTF of 1 means the sim runs as fast as real life. An RTF of 0.5 means the sim takes 2 seconds to simulate 1 second.

A low RTF makes timing tests misleading. Nodes that use simulated time follow the sim's clock, but anything on the wall clock, such as the gamepad, the network or a person watching, runs at real speed. At an RTF of 0.5, a stop that takes 0.5 s of simulated time takes 1 s of real time. Sensors cost the most: a camera or a LiDAR (light detection and ranging) sensor renders the scene on each tick. Check the RTF each time you add a sensor.

## Walls

The sim's walls are geometry so that the rover stays in the arena and the physics works. The rules forbid using walls for mapping, navigation or collision avoidance. A rover that works in the sim because it uses the walls breaks the rules.

## Open questions

1. How closely does the sim's skid steer match the real rover once it's measured?
2. How does the sim stand in for digging and dumping without sand?
3. Can the sim run all the sensors at a real-time factor of 0.9 or above in a laptop virtual machine (VM)?

## Read more

- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html)
- [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
