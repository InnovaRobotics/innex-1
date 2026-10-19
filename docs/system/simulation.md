# Robot model and simulation

The simulation (sim) runs the rover model in a virtual copy of the arena. The team uses it to test the other subsystems before the rover exists, or while the rover is unavailable.

## Requirements

- Stand in for the rover, so the team can test software when the rover is in pieces or at another site.
- Publish the same topics and frames as the real rover, so code written for the sim runs on the rover.
- Hold the rover's dimensions, masses and sensor positions in one model.
- Run fast enough. The real-time factor should be close to 1.

## Inputs and outputs

The sim takes velocity commands from [Teleop and rover control](teleop-and-control.md), as the real rover does. It gives back odometry, transforms, joint states and the clock. The [innex_sim README](../../src/innex_sim/README.md#rover) lists the topics. When the model includes sensors, the sim gives their data to [Perception](perception.md) and [Localisation](localisation.md) on the same topics and frames as the real sensors.

## Rules

- [Navigation and sensing](../rules.md#navigation-and-sensing): the sim's walls are geometry only. Autonomy must not use them.
- [The arena](../rules.md#the-arena): the world follows the arena size and the zone layout.
- [The run](../rules.md#the-run): the judges choose the start pose at random. The sim sets the spawn pose with launch arguments.

## Where the details live

The package READMEs hold the commands and the numbers:

- [innex_sim](../../src/innex_sim/README.md): the Moon Yard world, the launch file, the topics, the arena frame and the zones.
- [innex_description](../../src/innex_description/README.md): the robot model and its frames.

## What the sim is for

The sim finds mistakes before the rover can hurt anyone or anything. You can drive it, break it, reset it, and run the same test a hundred times. A bug in the sim costs minutes. The same bug on the rover costs a test session, and it needs someone at the E-stop.

The sim helps only where it matches the rover. The sim and the rover publish the same topics and frames. If you change a topic name or a frame in one, change it in the other.

## What the sim leaves out

The sim does not model sand usefully, so it leaves out digging physics. It also does not model realistic wheel slip on sand. Both limits matter:

- A dig or a dump in the sim shows that the commands and the sequence work. It does not show how much sand the ladder lifts.
- Wheel odometry in the sim may drift less than on the real rover. A localisation filter that works in the sim may still need tuning on the rover.

## The robot model

The robot model is a URDF file written in xacro. URDF is the Unified Robot Description Format, an XML description. Xacro is a macro language that expands into URDF. The model lists the rover's parts as links, such as the chassis and the wheels. Joints connect the links. Each link has a mass and a shape. Each sensor has a frame that fixes where it sits relative to `base_link`.

The sim and the rover use the same URDF. On the rover, `robot_state_publisher` reads it and publishes the transforms between the frames. A camera frame in the model is the camera frame on the rover. So sensor positions must come from measurements of the real rover.

The model starts rough. It has a box chassis, four wheels and estimated masses. Measurements of the real rover replace the estimates. A rough model is enough to test the command path, the frames and the launch files, so you do not have to wait for exact numbers.

## The Gazebo drive plugin

Gazebo's `DiffDrive` plugin drives the four wheels as a skid steer. It has no command timeout. It keeps the last command until a new command arrives. The [innex_sim README](../../src/innex_sim/README.md#rover) gives the speed and acceleration limits.

## Real-time factor

The real-time factor (RTF) compares simulated time with wall-clock time. An RTF of 1 means the sim runs at real speed. An RTF of 0.5 means the sim takes two seconds to simulate one second.

A low RTF makes timing tests misleading. Nodes that use simulated time follow the sim clock. Anything on the wall clock, such as the gamepad, the network or a person watching, runs at real speed. At an RTF of 0.5, a stop that takes 0.5 s of simulated time takes 1 s of real time. Sensors cost the most, because a camera or a LiDAR renders the scene on each tick. Check the RTF each time you add a sensor.

## Open questions

1. How closely does the sim's skid steer match the real rover, once the real rover is measured?
2. How does the sim stand in for digging and dumping, without sand?
3. Can the sim run all the sensors at a real-time factor of 0.9 or above on a laptop virtual machine?

## Further reading

- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html)
- [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
