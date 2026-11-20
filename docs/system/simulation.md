# Robot model and simulation

Building and debugging autonomy on an 80 kg rover with heavy motors is slow and risky: every test needs floor space, charged batteries and someone standing beside the E-stop. The simulation (sim) runs a virtual model of INNEX-1 inside a virtual Moon Yard arena in Gazebo Harmonic, letting you test command paths, coordinate frames, perception, localisation and navigation on a laptop before hardware is assembled or while the physical rover is in pieces.

The sim takes `/cmd_vel` commands from [Teleop and rover control](teleop-and-control.md) and publishes odometry, transforms, joint states, simulated time (`/clock`) and simulated sensor streams to [Perception](perception.md) and [Localisation](localisation.md). Concrete launch commands, topic lists, arena coordinates and zone dimensions live in the package READMEs:

- [innex_sim](../../src/innex_sim/README.md): the Moon Yard world, launch arguments, topics, arena frame and zone layout.
- [innex_description](../../src/innex_description/README.md): the robot model and its coordinate frames.

## Requirements

- Stand in for the physical rover so software work continues when hardware is unavailable or at another site.
- Publish matching ROS 2 topics and coordinate frames above the drive bridge so autonomy code written in simulation runs unchanged on the rover.
- Store the rover's dimensions, masses and sensor frame offsets in one shared robot model.
- Run close to real speed, with a real-time factor near 1.

## Competition rules

- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): simulation tests hold arena dimensions to spawn rocks and check bounds, while rover autonomy packages must never hard-code arena dimensions. Under the 4 November email clarification, sensing the arena walls is expected to be allowed in the final 2027 rulebook.
- [The arena](../rules.md#the-arena): the simulated Moon Yard matches the competition's 7.9 m × 4.4 m interior dimensions and zone layout.
- [The run](../rules.md#the-run): because judges randomise starting position and cardinal heading before each run, the sim accepts `x`, `y` and `yaw` launch arguments to test arbitrary start poses.

## Why the sim helps, and where it stops matching the rover

A bug in Gazebo costs two minutes to reproduce and reset; the same bug on the real rover costs an afternoon of lab setup. You can drive the simulated rover into a boulder a hundred times to tune a recovery behaviour without bending a single bracket.

That benefit holds only where the sim and the real rover speak the same interface. If you rename a topic or move a sensor frame in one, update the other so autonomy code never forks into "sim code" and "rover code". At the same time, Gazebo deliberately leaves out two realities of the physical rover:

- Sand and wheel slip: Gazebo does not simulate loose regolith digging physics or realistic skid-steer sinkage on sand. Running a dig or dump sequence in sim confirms that commands and state transitions fire in order, never how much sand the bucket ladder lifts. Wheel odometry also drifts far less in sim than on real sand, so any localisation filter tuned in sim still needs real sand tuning.
- The drive bridge and stop timeout: Gazebo's `DiffDrive` plugin replaces the rover's Jetson drive bridge, speed limits and Teensy path, and it has no command timeout. If a publisher stops sending `/cmd_vel`, the simulated rover keeps rolling at its last commanded velocity forever. Hardware stop layers and watchdog timeouts must therefore be verified on the bench and on blocks until simulation aligns with the drive bridge.

## The robot model (URDF and xacro)

To describe the rover's physical geometry in software, ROS 2 uses an XML format called **URDF** (Unified Robot Description Format). A URDF breaks the robot into rigid parts called **links** (chassis, wheels, camera housings, LiDAR) connected by **joints** (such as continuous rotating wheel axles). Each link carries mass, collision shape and visual geometry, and each sensor link fixes where that sensor sits relative to `base_link`.

Writing raw XML by hand gets repetitive quickly, so the repo writes the model in **xacro**, a macro language that expands into URDF using variables and reusable parts (like defining one wheel macro and instantiating it four times).

Both Gazebo and the real rover load the exact same URDF. On the Jetson, `robot_state_publisher` reads it and broadcasts the static transforms between `base_link` and every sensor. That means the model starts with rough June 2026 CAD dimensions and estimated masses so software can run early, and physical measurements from the assembled rover must replace every estimate before trusting calibration on hardware.

## Real-time factor

The **real-time factor (RTF)** compares how fast simulated time ticks against the clock on your wall. An RTF of `1.0` means one simulated second takes one real second. An RTF of `0.5` means Gazebo needs two real seconds to simulate one second of rover motion.

A low RTF quietly breaks timing tests. ROS 2 nodes using simulated time (`/clock`) slow down together with Gazebo, whereas anything tied to wall-clock time (your hands on the gamepad, network delays or a stopwatch) keeps running at full speed. At an RTF of `0.5`, a stop that takes `0.5 s` of simulated time takes a full `1.0 s` on your watch. Simulated cameras and 3D LiDAR cost the most compute because Gazebo renders the arena from each sensor's viewpoint on every tick, so check RTF whenever you enable another sensor on a laptop VM.

## Open questions

1. How closely does the simulated skid-steer turning model match the real rover once chassis mass and wheel geometry are measured?
2. Can simulation wrap or bridge the rover's actual drive bridge so stop timeouts match hardware?
3. How does simulation mock digging and dumping load feedback without modelling loose sand?
4. Can a typical team laptop VM run Gazebo with the Ouster LiDAR and both OAK-D Pro cameras enabled at an RTF of 0.9 or above?

## Further reading

- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html)
- [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
