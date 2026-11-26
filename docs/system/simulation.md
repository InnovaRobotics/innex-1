# Robot model and simulation

Testing autonomy or control changes directly on a `58.5 kg` rover with six geared motors is slow and unforgiving: every run needs lab floor space, charged LiPo packs and a second person standing over the E-stop. The simulation (sim) runs a virtual copy of INNEX-1 inside a Gazebo Harmonic Moon Yard arena, letting you test launch files, coordinate frames, video, perception, localisation and route planning on a laptop in minutes while hardware is in pieces or at another site.

Both packages live on `main` today:

- [`innex_description`](../../src/innex_description/README.md) holds the six-wheel xacro/URDF robot model, sensor frames (`oak_front_frame`, `oak_rear_frame`, `os_sensor`) and Gazebo plugins.
- [`innex_sim`](../../src/innex_sim/README.md) holds the `7.9 m x 4.4 m` Moon Yard world, `moon_yard.launch.xml`, the `500 ms` `cmd_vel_watchdog` node, simulated H.264 camera relays (`video:=true`) and Ouster point-cloud bridging (`lidar:=true`).

## Where the sim matches the rover, and where it leaves physics out

Simulation only saves time when autonomy and teleop nodes cannot tell whether they are talking to Gazebo or to the Jetson. Above the drive bridge, both publish and subscribe to the same ROS 2 topics and REP 105 frames (`/cmd_vel`, `/odom`, `/tf`, `/joint_states`, `/ouster/points`, `/oak_front/video` and `/oak_rear/video`). Whenever you rename a topic or move a sensor mount in one place, update the other in the same pull request so software never splits into "sim code" and "rover code".

At the same time, Gazebo leaves out two physical realities that you still have to verify on hardware:

- Granular sand and digging loads: Gazebo models the arena floor, craters and rocks as rigid meshes instead of loose regolith. Running a dig or dump sequence in sim verifies state transitions and joint commands, never how much sand the bucket ladder collects or how deeply tyres sink while excavating.
- Real-sand slip and the Teensy serial link: Gazebo's wheels use dry Coulomb friction (`1.0` rolling, `0.5` sideways) instead of deformable sand, and `ros_gz_bridge` replaces the USB serial wire to the Teensy (`Layer 3`). Localisation filters tuned in sim still need real-sand covariance tuning, and Teensy watchdog behaviour still needs block testing on the bench.

## The robot model (URDF and xacro)

ROS 2 describes a robot's 3D geometry in an XML format called **URDF** (Unified Robot Description Format). A URDF breaks the rover into rigid bodies called **links** (chassis, six paddle wheels, front and rear cameras, LiDAR) joined together by **joints** (`continuous` rotating wheel axles and `fixed` sensor brackets). Each link carries visual shapes, simplified collision shapes (two boxes and six smooth cylinders so physics and raycasting stay fast) and mass/inertia properties. Because raw XML repeats itself across six identical wheels, `innex_description` writes the model in **xacro**, a macro language that expands variables and reusable macros into URDF at launch.

Gazebo and the physical rover share that exact same xacro file. On both, `robot_state_publisher` reads the generated URDF and broadcasts the `tf2` transforms from `base_link` (on the ground beneath the middle axle) out to every wheel and sensor lens. The model starts with dimensions from the November 2026 INNEX-2 Master CAD (`0.02`) and masses from the Mechanical Team SDR (`58.5 kg` empty including sensors); physical tape-measure and scale readings from the assembled rover must replace those numbers before relying on hardware calibration.

## The Gazebo drive plugin

Gazebo Harmonic's `DiffDrive` plugin drives all six wheels from left and right velocity commands, applying speed caps (`0.4 m/s` linear, `0.8 rad/s` angular) and acceleration ramps. Because turning a six-wheel chassis drags the front and rear tyres sideways across the ground, `DiffDrive` uses a calibrated effective wheel separation of `0.717 m` (wider than the `0.675 m` geometric track) so `/odom` heading matches the rover's actual turn rate in Gazebo.

Left on its own, `DiffDrive` has one hazardous quirk: it has no command timeout and keeps spinning at the last velocity forever if a publisher crashes. To match Layer 2 of the real rover ([Teleop and rover control](teleop-and-control.md#stop-at-three-layers)), `moon_yard.launch.xml` places `cmd_vel_watchdog` between `/cmd_vel` and Gazebo. It subscribes with best-effort QoS and depth `1`, forwards fresh commands to `/cmd_vel_watchdog/cmd_vel`, and publishes zero every `500 ms` on the wall clock whenever `/cmd_vel` goes silent. Always publish velocity commands to `/cmd_vel`, never straight to `/cmd_vel_watchdog/cmd_vel`. See [When commands stop](../../src/innex_sim/README.md#when-commands-stop).

## Real-time factor

The **real-time factor (RTF)** measures how fast Gazebo ticks compared with a stopwatch on your desk. An RTF of `1.0` means one simulated second takes one wall-clock second; an RTF of `0.5` means Gazebo needs two wall-clock seconds to compute one second of rover physics.

Low RTF values quietly distort timing experiments. Nodes launched with `use_sim_time:=true` follow Gazebo's `/clock` topic and slow down proportionally, whereas anything tied to the real world (your thumbs on the gamepad, `cmd_vel_watchdog`'s wall-clock timer or network latency) keeps running at wall speed. Rendering 3D GPU raycasts and camera frames costs the bulk of CPU/GPU time, which is why `moon_yard.launch.xml` leaves `video:=false` by default and exposes `lidar:=false` so software-rendered Mac VMs can test teleop or H.264 video at smooth frame rates while keeping `os_sensor` in the TF tree.

## Requirements and competition rules

Subsystem requirements:

- Stand in for the physical rover so software development and CI tests (`xvfb-run -a colcon test`) run without hardware.
- Match the real rover's ROS 2 topics and REP 103 / REP 105 frames above the drive bridge.
- Store chassis dimensions, masses and sensor extrinsics in one shared xacro model.
- Maintain a usable real-time factor on developer laptops, with launch flags to shed heavy sensor rendering when unneeded.

Applicable rules:

- [Navigation and sensing](../rules.md#navigation-and-sensing) and [Organiser clarifications](../rules.md#organiser-clarifications-provisional): simulation scripts and world files store the `7.9 m x 4.4 m` pit size to build meshes and verify bounds, while rover autonomy packages must never hard-code arena dimensions.
- [The arena](../rules.md#the-arena): `moon_yard` replicates the rulebook zone layout, approximate boulder/crater sizes and start-corner beacon frame.
- [The run](../rules.md#the-run): `moon_yard.launch.xml` accepts `x`, `y` and `yaw` arguments so tests exercise random starting positions and cardinal headings.

## Open questions

1. How closely does Gazebo's `0.717 m` effective skid-steer separation match the assembled six-wheel rover on hard floor and on sand?
2. How will `innex_sim` expose joints and mock load feedback for the bucket ladder and dump bed so Stage 2 autonomy sequences can be tested end-to-end without granular sand physics?
3. How will the central `23 cm` Ouster riser in `innex_description` stow or fold inside the `75 cm` pre-run inspection box on the physical chassis?

## Further reading

- [`innex_sim` README](../../src/innex_sim/README.md) and [`innex_description` README](../../src/innex_description/README.md)
- [Gazebo Harmonic sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [Jazzy URDF tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html) and [Jazzy launch tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [REP 103](https://www.ros.org/reps/rep-0103.html) and [REP 105](https://www.ros.org/reps/rep-0105.html)
