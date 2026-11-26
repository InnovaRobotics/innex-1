# Robot model and simulation

Testing autonomy or control software directly on a 58.5 kg rover with six geared motors requires floor space, charged LiPo batteries and a second person standing beside the E-stop. The simulation (sim) runs a virtual model of INNEX-1 inside a Gazebo Harmonic Moon Yard arena, allowing launch files, coordinate frames, video streams, perception, localisation and route planning to be tested on a laptop when hardware is unavailable.

Two packages implement the model and virtual arena:

- [`innex_description`](../../src/innex_description/README.md) defines the six-wheel xacro/URDF robot model, sensor frames (`oak_front_frame`, `oak_rear_frame`, `os_sensor`) and Gazebo plugins.
- [`innex_sim`](../../src/innex_sim/README.md) defines the 7.9 m × 4.4 m Moon Yard world, `moon_yard.launch.xml`, the 500 ms `cmd_vel_watchdog` node, simulated H.264 camera relays (`video:=true`) and Ouster point-cloud bridging (`lidar:=true`).

## Sim-to-real boundary

Simulation saves testing time only when teleop and autonomy nodes use identical interfaces in Gazebo and on the Jetson. Above the drive bridge, both publish and subscribe to the same ROS 2 topics and REP 105 frames (`/cmd_vel`, `/odom`, `/tf`, `/joint_states`, `/ouster/points`, `/oak_front/video` and `/oak_rear/video`). Changing a topic name or moving a sensor mount requires updating both in the same pull request so code never diverges between simulation and hardware.

At the same time, Gazebo omits two physical effects that always require hardware verification:

- Granular sand and digging forces: Gazebo represents the arena floor, craters and boulders as rigid meshes instead of loose regolith. Running a dig or dump sequence in simulation verifies state transitions and joint commands, without modelling how much sand the bucket ladder collects or how deeply wheels sink while excavating.
- Loose-sand wheel slip and USB serial hardware: Gazebo wheels use dry Coulomb friction (1.0 rolling, 0.5 lateral) instead of deformable sand, and `ros_gz_bridge` replaces the USB serial link to the Teensy (Layer 3). State-estimation covariances tuned in simulation still need calibration on real sand, and Teensy hardware watchdogs still require bench testing on blocks.

## Robot model

ROS 2 describes 3D robot geometry in an XML format called **URDF** (Unified Robot Description Format). A URDF divides the rover into rigid parts called **links** (chassis, six paddle wheels, cameras, LiDAR) connected by **joints** (`continuous` wheel axles and `fixed` sensor mounts). Each link specifies visual geometry, simplified collision primitives (two boxes and six smooth cylinders to keep physics and raycasting fast) and mass/inertia properties. To avoid repeating XML across six wheels, `innex_description` writes the model in **xacro**, a macro language that expands parameters and macros into URDF at launch.

Gazebo and the physical rover load the same xacro file. On both, `robot_state_publisher` reads the generated URDF and broadcasts `tf2` transforms from `base_link` (on the ground directly beneath the middle axle) to every wheel and sensor optical frame. CAD dimensions and estimated masses in `innex_1.urdf.xacro` provide starting values that physical measurements of the assembled rover replace before hardware calibration.

## The Gazebo drive plugin

Gazebo Harmonic's `DiffDrive` plugin drives all six wheels from left and right velocity targets, enforcing speed limits (0.4 m/s linear, 0.8 rad/s angular) and acceleration limits. Because turning a six-wheel chassis drags the front and rear tyres sideways across the ground, `DiffDrive` uses a calibrated effective wheel separation of `0.717 m` (wider than the `0.675 m` geometric track) so `/odom` heading matches the simulated rover's true yaw rate.

On its own, `DiffDrive` has no command timeout and keeps turning at the last received velocity if a publisher exits. To match Layer 2 on the physical rover ([Teleop and rover control](teleop-and-control.md#stop-at-three-layers)), `moon_yard.launch.xml` places `cmd_vel_watchdog` ahead of Gazebo. It subscribes to `/cmd_vel` with best-effort QoS and depth 1, forwards fresh commands to `/cmd_vel_watchdog/cmd_vel`, and publishes zero every 500 ms on the wall clock whenever `/cmd_vel` goes quiet. Always publish velocity commands to `/cmd_vel`, never directly to `/cmd_vel_watchdog/cmd_vel`. See [When commands stop](../../src/innex_sim/README.md#when-commands-stop).

## Real-time factor

The **real-time factor (RTF)** is the ratio of simulated time to wall-clock time. An RTF of `1.0` means one simulated second takes one wall-clock second; an RTF of `0.5` means Gazebo takes two wall-clock seconds to compute one second of rover physics.

A low RTF affects timing measurements whenever simulated and wall clocks meet. Nodes configured with `use_sim_time:=true` follow Gazebo's `/clock` topic and slow down alongside the physics engine, whereas anything on the wall clock (operator stick inputs, `cmd_vel_watchdog` or network timeouts) runs at real speed. Rendering 3D LiDAR rays and camera images accounts for most simulation load, so `moon_yard.launch.xml` sets `video:=false` by default and provides `lidar:=false` to turn off heavy sensor raycasting on CPU-rendered virtual machines while preserving `os_sensor` in TF.

## Rules and constraints

- Publish identical ROS 2 topics and REP 103 / REP 105 frames above the drive bridge in simulation and on hardware, with headless CI verification (`xvfb-run -a colcon test`).
- Keep arena dimensions (`7.9 m × 4.4 m`) confined to simulation world generation and test assertions; rover autonomy packages must never hard-code arena dimensions ([Navigation and sensing](../rules.md#navigation-and-sensing), [Organiser clarifications](../rules.md#organiser-clarifications-provisional)).
- Support arbitrary starting positions and cardinal headings via `x`, `y` and `yaw` launch arguments ([The run](../rules.md#the-run)).

## Further reading

- [`innex_sim` README](../../src/innex_sim/README.md) and [`innex_description` README](../../src/innex_description/README.md)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html) and [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
