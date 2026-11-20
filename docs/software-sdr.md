# INNEX-1 software system design review

## 1. Introduction

This document defines the architecture of the INNEX-1 rover software for UK Lunabotics 2027. It is the baseline input for the team's system design review (SDR), which NASA NPR 7123.1D Table G-5 calls a system definition review. The review asks the software, electrical and mechanical teams to accept or correct the requirements, confirm the architecture and interfaces, and agree on the review gate at which each open item closes. The team holds this review before the preliminary design review (PDR) due by 29 January 2027.

The scope covers all software on the rover's computers and the mission control laptop, plus the interfaces between software and the electrical and mechanical subsystems. Chassis design, excavation mechanics and battery wiring sit outside this document except at those interfaces. Technical terms are defined in the [Glossary](glossary.md).

**Table 1. Reference documents**

| ID | Reference document |
| --- | --- |
| RD1 | [UK Lunabotics 2027 Rule Book, draft v0.1](https://uklunabotics.co.uk/Lunabotics/UKLunabotics2027_RuleBook_DRAFT_v0.1.pdf) |
| RD2 | [UK Lunabotics 2027 Challenge Overview and Registration Requirements, v2.0](https://uklunabotics.co.uk/Lunabotics/UKLunabotics2027_OverviewAndRegistration_v2.0_23_09_2026.pdf) |
| RD3 | [NASA NPR 7123.1D, Appendix G, Table G-5](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7123_001D_&page_name=AppendixG) |
| RD4 | Organiser email clarification (James Cole, UK Lunabotics, 4 November 2026; provisional until the final rulebook) |

## 2. Use case

Figure 1 shows the Moon Yard arena and one excavation cycle. The arena interior is approximately 7.9 m long and 4.4 m wide. Before a run starts, the team places the rover in the start zone and mounts a beacon on the arena frame near that corner, facing the construction zone. The judges pick a random position inside the start zone and spin a direction wheel so the rover's forward arrow points north, east, south or west. Operators sit in mission control outside the arena and plan to run without arena cameras, relying on the rover's own cameras alone.

*[Figure 1. The arena and one cycle of a run. Zone positions are approximate.]*

A run lasts up to 20 minutes, and the team ends the run when it chooses. In each cycle, the rover crosses the obstacle zone around random boulders and craters (1), lowers its bucket ladder in the excavation zone to collect sand (2), returns to the construction zone (3), and dumps the sand onto the berm target area (4). At the end of the run, the judges scan the berm and score its volume against rover mass and energy used.

Software develops in three overlapping stages. Stage 1 runs on the real rover and puts all four steps under gamepad remote control. Stages 2 and 3 begin in simulation and on a hard floor while hardware matures. Stage 2 automates digging and dumping (steps 2 and 4). Stage 3 automates obstacle traversal (steps 1 and 3) and ends with one full autonomous cycle. Before an autonomous traverse or full-cycle attempt, the operator can drive the rover inside the start zone by remote control to lock down its pose, then announce hands-free and leave all controls untouched.

## 3. Competition score

Every system trade depends on what the competition rewards. The judges score each run in four parts, and the final score adds both runs together.

**Table 2. Scoring breakdown**

| Part | Points |
| --- | --- |
| Berm, normalised for mass | 4.4 × V / (T × m) |
| Berm, normalised for energy | 1.5 × V / (T × E) |
| Arena cameras | 120 for no cameras, 60 for one, 0 for two (example values) |
| Autonomy | Excavation 75, dump 50, traverse 250; one full cycle 450; full run 600 |

Here `V` is berm volume inside the target area in cm3, `T` is run time in minutes, `m` is rover mass in kg, and `E` is energy used in Wh. The organisers have stated by email that `T` is the time the run took when the team ends it, and that each autonomy task is scored independently so a failure in one stage does not erase earlier credit. The final rulebook can change both rules.

Because the mass score tracks volume per minute and the energy score also divides by total energy, running longer at a steady pace reduces energy points as energy accumulates. The system therefore favours a large load per cycle, short cycle times, low mass and low onboard power. In the rulebook example, autonomy points in one run exceed berm points.

## 4. System-level requirements

Tables 3 to 5 define the software requirements, their sources and the earliest development stage in which each applies. Mass, stowed envelope and E-stop hardware requirements belong to the mechanical and electrical teams; cross-team dependencies appear in Table 7.

**Table 3. Functional requirements**

| ID | Requirement | Source | Stage |
| --- | --- | --- | --- |
| F1 | The operator shall be able to drive the rover, operate the bucket ladder and dump sand from mission control with a gamepad. | Team | 1 |
| F2 | The rover shall send video and telemetry to mission control. The operator shall be able to perform F1 using this data alone, without arena cameras. | Mission Operations 2 and 3 | 1 |
| F3 | The rover shall stop all motion when the operator releases the enable button, when the link fails, or when an onboard computer stops sending commands. | Team | 1 |
| F4 | After an E-stop reset, the rover shall not move until the operator sends a separate start command. | E-STOP Button 6 | 1 |
| F5 | The operator shall be able to stop all rover activity with one command at the end of a run. | Mission Conclusion 1 | 1 |
| F6 | Each motor and each actuator shall accept commands from only one source at a time. | Team | 2 |
| F7 | The rover shall lower the bucket ladder, collect sand and raise the bucket ladder with no operator input. | Autonomous Operations 1 | 2 |
| F8 | The rover shall determine its position and heading in the arena from any valid starting position and heading. | Construction Protocol 4, Autonomous Operations 2 | 2 |
| F9 | The rover shall align with the berm target area and dump sand inside it with no operator input. | Autonomous Operations 2 | 2 |
| F10 | During an autonomous step, mission control software shall display telemetry and shall send no commands, orientation data or obstacle positions to the rover. | Autonomy Rules 1, 2, 5 and 6 | 2 |
| F11a | The rover shall detect boulders of 30 to 40 cm, craters up to 40 to 50 cm, and the arena walls using its onboard sensors. | Autonomous Operations 3, RD4 | 3 |
| F11b | The rover shall plan and follow a route around detected hazards with no operator input. | Autonomous Operations 3 | 3 |
| F12 | The rover shall complete one full cycle (traverse, dig, traverse, dump) with no operator input. | Autonomous Operations 4 | 3 |
| F13 | During an autonomous step, the rover shall report the step state (running, complete or failed) and shall end a failed step with no operator input. | Mission Operations 3 | 2 |
| F14 | The rover shall not touch the arena walls and shall stay inside the arena. During an autonomous step, it shall detect the walls with its sensors. | Robotic Operations 3, RD4 | 1 (teleop), 3 (autonomy) |

**Table 4. Performance requirements**

| ID | Requirement | Source | Stage |
| --- | --- | --- | --- |
| P1 | The average data rate of the link shall be 4,000 kbps or less during a run. | Communication System Requirements 14 | 1 |
| P2 | The command to the motor controllers shall reach zero 600 ms or less after the last valid command arrives. (Proposal) | Team | 1 |
| P3 | The software shall be ready to drive the rover before the end of the 10-minute setup period. | Construction Protocol 3 | 1 |
| P4 | The team shall connect to the rover and control it wirelessly within 15 minutes at the comm check. | Comm Check 3 and 6 | 1 |
| P5 | During an autonomous traverse, the rover shall not touch a boulder and shall not drive across a crater. | Autonomous Operations 3 | 3 |
| P6 | At the berm target area, the position error shall be 0.2 m or less and the heading error 5 degrees or less. (Proposal) | Construction Points 2 | 2 |

**Table 5. Non-functional requirements**

| ID | Requirement | Source | Stage |
| --- | --- | --- | --- |
| N1 | The software shall not use GPS or compass data. If an IMU contains a magnetometer, the software shall not read it. | Navigation Protocol 2, 3 and 7 | 1 |
| N2 | The rover shall not use touch sensors or ultrasonic proximity sensors. | Robot Requirements 13 and 18 | 1 |
| N3 | The link shall use the assigned SSID with WPA2 or WPA3 encryption. The 2.4 GHz channel shall be 20 MHz wide. | Communication System Requirements 2 to 7 | 1 |
| N4 | Rover software above the drive bridge shall run unchanged in simulation and on the rover, using identical topics and coordinate frames. | Team | 1 |
| N5 | Software running on the rover shall not contain the arena dimensions as fixed values. | RD4 | 2 |

## 5. Functional architecture

Figure 2 shows the software functions and data flow. Two functions run on the mission control laptop, and the rest run onboard the rover. Commands cross the link to the rover; compressed video and telemetry return to mission control.

*[Figure 2. Functional architecture of the INNEX-1 software.]*

In stage 1, gamepad input on the laptop turns stick and trigger movements into velocity and mechanism commands while the operator holds the enable button (F1). On the rover, a command selector passes commands from one active source to motion control and gives an operator stop command priority over every source. Motion control turns the velocity command into left and right wheel speeds, drives the bucket ladder and dump actuators, enforces the stop timeouts in section 9.2, and holds all outputs disabled after an E-stop reset until a separate start command arrives.

Sensing reads the two stereo cameras, the 3D LiDAR and the inertial measurement units (IMUs). Each camera compresses its video in hardware so the onboard computer spends no CPU cycles on video encoding. Only compressed video and allow-listed telemetry cross the wireless link to the operator display, while raw LiDAR point clouds remain onboard to stay within the 4,000 kbps limit (P1).

Stages 2 and 3 add three onboard autonomy functions. Pose estimation computes the rover's position and heading (its **pose**) from wheel motion, gyroscope rates, LiDAR scans and beacon sightings without GPS or compass data (F8). Hazard detection reads camera depth and LiDAR returns to locate boulders, craters and arena walls. Mission and route planning plots a route around those hazards and runs the dig and dump sequences, feeding commands into the same command selector used for teleoperation. During any autonomous step, the mission control display stays read-only and sends no commands.

In simulation, Gazebo models the rover body, sensors, motors and actuators. Its built-in drive plugin also replaces the rover's velocity-to-wheel-speed conversion, speed limits and wheel odometry, with no command timeout. Aligning simulation with the rover drive bridge is tracked under open item O4.

## 6. Architecture trade-offs

The primary architectural decision is how the rover localises across the arena. Four PDR-level package choices (video codec, network transport, drive controller framework and command selector) are summarised in section 6.2 and compared in detail in Appendix A.

### 6.1 Localisation sources

Localisation must produce smooth motion for local steering while remaining accurate across the 7.9 m pit without storing fixed arena dimensions. The organisers have stated by email that sensing and mapping the pit walls for autonomy and navigation is expected to be allowed, provided the rover does not hard-code arena dimensions; the final rulebook will confirm this. Table 6 compares the four localisation sources supported by the hardware.

**Table 6. Localisation source trade-off**

| Source | What it provides | Where it fails | Status |
| --- | --- | --- | --- |
| Wheel odometry and gyroscope | Smooth short-term motion between fixes | Unbounded drift; large wheel slip in turns and digging | Planned |
| Beacon viewed by a camera | Absolute pose fix in the arena frame | Unreadable from the excavation zone, about 6.6 m away at 71 degrees off the beacon face (calculated) | Planned |
| Beacon viewed by the LiDAR | Absolute pose fix across wider angles | Needs retroreflective strips on the beacon face; untested | Candidate |
| LiDAR odometry using the walls | Continuous low-drift motion across the whole pit | Allowed by email clarification only; Jetson load unmeasured | Candidate, provisional |

The baseline design runs on wheel-plus-gyro odometry and camera beacon fixes alone, adding LiDAR beacon detection and wall-based LiDAR odometry if the final rulebook and Jetson power budget permit (O6).

### 6.2 PDR-level choices

Four subsystem choices have fixed requirements at SDR while leaving package selection for PDR (Appendix A):

- Operator video: onboard camera H.264 encoding sets bitrate directly in kbps without loading the Jetson (selected).
- Link transport: a WebSocket bridge with a topic allow-list carries video and read-only telemetry to mission control (selected); ROS 2 gamepad transport over Wi-Fi remains open between static peers and Zenoh (O3).
- Drive control: motion control computes wheel setpoints, enforces the stop timeout and reports wheel odometry; choosing between a custom node and `ros2_control` stays open (O4).
- Command selector: an onboard arbiter switches between teleop and autonomy for both wheels and mechanisms, with operator stop always taking priority; choosing between extending `twist_mux` and a single mode node stays open (O5).

## 7. Physical architecture and interfaces

Figure 3 shows the computers, sensors and physical links. The mission control laptop reads the gamepad and runs the operator display. The organisers have stated by email that the arena provides mains power and an Ethernet cable in one corner for the team's router, linking it directly to mission control; the final rulebook will confirm this. Under that layout, the router sits in the arena corner and the rover carries a Wi-Fi client radio only.

*[Figure 3. The computers, sensors and physical connections.]*

On the rover, a Jetson Orin Nano Super runs ROS 2 Jazzy and all high-level software. A Teensy 4.1 connects over USB serial and handles the timing-critical hardware loop: signalling motor controllers, counting wheel encoder pulses and disabling outputs when serial messages stop. Two OAK-D Pro cameras (front and rear) connect over USB, and an Ouster OS1-128 LiDAR connects over Ethernet.

Table 7 defines the system interfaces, including five cross-team hardware dependencies (I10 to I14) that software requires from electrical and mechanical.

**Table 7. System interfaces**

| ID | Interface | Between | Description | Needed for |
| --- | --- | --- | --- | --- |
| I1 | Wireless link | Laptop, router and Jetson | Ethernet from laptop to corner router, Wi-Fi to rover client; commands to rover, video and telemetry back, averaging 4,000 kbps or less | F1, F2, P1 |
| I2 | Velocity command | Gamepad or mission planning, and command selector | Linear and angular velocity command in the rover body frame | F1, F6, F11b |
| I3 | Operator video | Jetson and laptop | One compressed H.264 stream per camera through the telemetry bridge | F2, P1 |
| I4 | Telemetry | Jetson and laptop | Read-only status, pose and diagnostics restricted to an allow-list | F2, F10, F13 |
| I5 | Drive and mechanism serial | Jetson and Teensy | Wheel and actuator setpoints to Teensy; encoder counts and Teensy state (armed, fault, E-stop) back to Jetson | F1, F3, F4, F8 |
| I6 | Camera data | OAK-D Pro cameras and Jetson | Colour images, stereo depth, IMU data and encoded H.264 streams over USB | F2, F8, F11a |
| I7 | LiDAR data | Ouster OS1-128 and Jetson | 3D point clouds, reflectivity and 6-axis IMU data over Ethernet | F8, F11a, F14 |
| I8 | Motor signals | Teensy and motor controllers | Control signals for drive, ladder and dump controllers; electrical selects the signal format | F1, F3, F7, F9 |
| I9 | Coordinate frames | All rover software | Three frames: arena map, continuous odometry and rover body. Pose estimation supplies map to odometry; ownership of odometry to body is open under O6. | F8, F11a, F11b |
| I10 | E-stop state | Electrical and Teensy | Signal showing that the E-stop disconnected motor power | F4 |
| I11 | Mechanism feedback | Electrical, mechanical and Teensy | End stops or position feedback for ladder, bed and door, plus fill or motor-current feedback | F7, F9 |
| I12 | Sensor and antenna mounts | Mechanical and software | Unobstructed forward LiDAR ground view within the 0.75 m height limit, plus Wi-Fi antennas outside the carbon-fibre body | F11a, P5, I1 |
| I13 | Compute power | Electrical and software | Power supply for Jetson, LiDAR and cameras, wired so energy logging measures their draw | Section 9.4 |
| I14 | Rover geometry data | Mechanical and software | Measured wheel radius, track width, chassis mass, beacon mass and sensor offsets | N4, F8 |

## 8. Subsystems

Table 8 maps the seven software subsystems to Figure 2.

**Table 8. Software subsystems**

| Subsystem | Functions from Figure 2 |
| --- | --- |
| Teleop and rover control | Gamepad input, command selector, motion control |
| Comms and mission control | Video and telemetry bridge, operator display |
| Sensors | Sensor drivers and ingestion |
| Localisation | Pose estimation |
| Perception | Hazard detection |
| Navigation and mission | Mission and route planning |
| Simulation | Virtual arena, rover model and simulated sensors |

### 8.1 Teleop and rover control

A gamepad node on the laptop publishes velocity and mechanism commands only while the operator holds the enable button, capped at 0.25 m/s linear speed and 0.4 rad/s turn rate (F1). The Jetson drive bridge turns velocity commands into left and right wheel setpoints and acts only on the latest command so delayed packets cannot replay stale motion. The Teensy drives the motor controllers, counts encoder pulses and enforces actuator end stops.

Section 9.2 sets the three stop layers. For mechanism automation, the proposed split has the Teensy enforce hardware end stops and actuator safety limits while the mission function on the Jetson sequences the dump steps (door open, bed raise, hold, bed lower, door close). That split and the command selector design close under O4 and O5.

### 8.2 Comms and mission control

The laptop connects to the corner router by Ethernet, and the rover connects over Wi-Fi under the competition encryption and channel rules (N3). A WebSocket bridge on the Jetson sends both H.264 camera streams and allow-listed telemetry to the Foxglove display, which shows video, wheel odometry, command selector state, step state and Teensy health. Disabling client publish on the bridge keeps the display read-only during hands-free autonomy (F10).

### 8.3 Sensors

The rover carries front and rear OAK-D Pro active stereo cameras, an Ouster OS1-128 LiDAR and wheel motor encoders. Each camera projects an infrared dot pattern to recover close-range depth on bare sand. The Ouster delivers a 360-degree point cloud and surface reflectivity, with its lowest beam angled 21.2 degrees below horizontal.

In the June 2026 CAD model, the LiDAR sits on a flat deck 0.30 m behind the front edge and 0.70 m ahead of the rear edge. That mount puts the sensor top above the 0.75 m limit, and the deck hides the ground for about 6 m ahead and across the entire rear (calculated). Resolving mount geometry closes under O1 and I12. To respect the compass ban, software reads only gyroscope and accelerometer outputs; the Ouster's 6-axis IMU has no magnetometer, whereas OAK-D Pro units can carry a 9-axis IMU whose magnetometer must stay excluded (N1).

### 8.4 Localisation

Localisation tracks the rover's pose across the arena without GPS, compasses or fixed arena dimensions (F8). Wheel **odometry** drifts rapidly on loose sand because skid-steer turns drag the tyres sideways. A gyroscope measures rotation rate independent of wheel slip, though it drifts slowly and has no arena heading reference.

To anchor the arena frame, the rover detects a beacon mounted near the start zone, facing the construction zone. All markers sit on one face, letting AprilTag visual **fiducials** for the cameras share the surface with retroreflective strips for the LiDAR. Because the judges set the start heading to north, east, south or west, the operator turns the rover inside the start zone by remote control until a sensor detects the beacon before starting autonomy.

Under the organisers' email clarification, sensing the pit walls for localisation and navigation is expected to be allowed in the final rulebook. Matching consecutive LiDAR scans against the sensed walls tracks motion continuously across the whole arena without hard-coding pit dimensions, covering the excavation zone where the beacon sits 6.6 m away at a 71-degree angle to the camera. Two fixed coordinate frames separate smooth steering from global corrections: a continuous odometry frame for local motion control, and an arena map frame that absorbs discrete beacon updates. Fusion design closes under O6 and beacon design under O8.

### 8.5 Perception

Perception classifies ground around the rover into free space, confirmed hazards and unknown space so navigation avoids boulders and craters (F11a). Boulders rise above the sand plane; craters appear as gaps hidden behind their near rim. Keeping unknown space distinct from free space prevents the planner from treating an occluded gap as safe ground, while front and rear camera depth fills the LiDAR near field. Under the email clarification, sensed walls enter the hazard map directly from live sensor returns. Choosing the detection method and map representation (a 2D **costmap** or elevation grid) closes under O10.

### 8.6 Navigation and mission

Navigation plots and tracks a collision-free path around hazards detected during that run (F11b). The mission function sequences the excavation cycle, checks sensor and pose health before starting an autonomous attempt, reports step state (running, complete or failed), and stops safely after bounded retries on failure (F13).

Because the bucket ladder sits at the front and the dump bed empties at the rear, the rover approaches excavation forwards and approaches the berm either in reverse or after turning round (O2). Dump approaches also consult hazard data because obstacles can sit inside the construction zone. Holding zone goals without fixed arena dimensions closes under O9.

### 8.7 Simulation

Gazebo Harmonic models the Moon Yard arena, rover geometry and sensors so teams can test autonomy before hardware is ready. Simulation and rover share one URDF model and matching topics and frames above the drive bridge (N4). Because Gazebo does not model loose sand physics and its drive plugin has no command timeout, digging performance, slip and stop timing are verified on hardware.

**Table 9. Allocation of requirements to subsystems**

| Subsystem | Requirements |
| --- | --- |
| Teleop and rover control | F1, F3, F4, F5, F6, P2 |
| Comms and mission control | F2, F10, P1, P3, P4, N3 |
| Sensors | N1, N2 |
| Localisation | F8, P6 |
| Perception | F11a |
| Navigation and mission | F7, F9, F11b, F12, F13, F14, P5, N5 |
| Simulation | N4 |

## 9. Budgets

Budgets come from datasheets and calculations. Tests in section 10 replace estimates with hardware measurements.

### 9.1 Link data rate

The competition caps average link traffic at 4,000 kbps (P1). Table 10 budgets two 864 × 480 H.264 streams, telemetry and commands, keeping 1,300 kbps of margin for motion bursts.

**Table 10. Link bandwidth budget**

| Traffic | Direction | Allocation (kbps) |
| --- | --- | --- |
| Front camera H.264 video | Rover to laptop | 1,000 |
| Rear camera H.264 video | Rover to laptop | 1,000 |
| Allow-listed telemetry | Rover to laptop | 500 |
| Gamepad commands and discovery | Both | 200 |
| Margin | Both | 1,300 |
| Total | | 4,000 |

### 9.2 Stop time

Each layer that can fail stops the rover independently (F3). Table 11 gives the three stop layers.

**Table 11. Stop layers**

| Layer | Trigger | Action | Time to act |
| --- | --- | --- | --- |
| Gamepad node (laptop) | Enable button released | Sends zero velocity command | Next publish cycle |
| Drive bridge (Jetson) | No command for 500 ms | Sends zero setpoints to Teensy | 500 ms |
| Teensy 4.1 | No valid serial message for 250 ms | Disables all motor and actuator outputs | 250 ms |

Because serial transit and controller ramp follow the 500 ms bridge timeout, proposed requirement P2 targets 600 ms or less to zero motor controller command. Neither timeout can be lengthened. At 0.25 m/s, the rover travels about 15 cm during 600 ms before braking begins (calculated); physical stopping distance is measured on the floor test.

### 9.3 Computer load

The Jetson Orin Nano Super has 8 GB of shared CPU and GPU memory and runs in 25 W mode. Full-stack load has not been measured. The team benchmarks each autonomy candidate on the Jetson in 25 W mode before selecting localisation and perception packages.

### 9.4 Power and energy of the computer and sensors

Onboard compute power counts towards the energy score, and the rulebook requires it to be measurable. Table 12 lists datasheet power in watts and upper-bound 20-minute energy; motors sit in the electrical budget.

**Table 12. Power and energy of the computer and sensors**

| Part | Power (W) | Upper-bound energy in 20 min (Wh) | Source |
| --- | --- | --- | --- |
| Jetson Orin Nano Super (25 W mode) | 25 | 8.3 | [NVIDIA Jetson Orin Nano Super](https://www.nvidia.com/en-gb/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/) |
| Ouster OS1-128 (running) | 14 to 20 | 4.7 to 6.7 | [Ouster OS1 Rev 7 datasheet](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p2-os1.pdf) |
| Ouster OS1-128 (standby) | 5 | 1.7 | [Ouster OS1 Rev 7 datasheet](https://data.ouster.io/downloads/datasheets/datasheet-rev7-v3p2-os1.pdf) |
| Two OAK-D Pro cameras | 15 (7.5 each) | 5.0 | [Luxonis OAK-D Pro](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) |
| Total (all running) | 54 to 60 | 18.0 to 20.0 | |

In the rulebook example, an entire rover used 36 Wh. At maximum draw over 20 minutes, computers and sensors alone use 18.0 to 20.0 Wh, making compute power and run duration major drivers of the energy score. Putting the LiDAR into standby cuts its draw to 5 W.

### 9.5 Cycle time

Straight-line crossings cover about 5.7 m from start to excavation and 5.4 m from excavation to construction. At 0.25 m/s, crossings take at least 23 s and 22 s before turns and obstacle detours. Dig duration, dump duration and load per cycle remain unmeasured; together with mass and power, they determine the berm score and optimal run length.

## 10. Test plan

Verification progresses across six stages, adding one physical layer at a time so faults isolate cleanly.

**Table 13. Test stages**

| Stage | Setup | What it verifies |
| --- | --- | --- |
| T1 Unit and CI | Automated build and tests on each pull request | Nodes build and pass unit checks |
| T2 Simulation | Gazebo Moon Yard with rover and sensor model | Autonomy stack, frames, localisation and planning above the drive bridge |
| T3 Bench | Jetson and Teensy on USB with no motors | Serial link, timeouts and command selector switching |
| T4 Blocks | Rover on blocks with wheels off the ground | Motor and actuator directions, end stops, E-stop reset interlock and stop layers |
| T5 Floor | Rover on a walled floor with boxes, driven from mission control | Camera-only driving, link rate, stop distance, comm check, wall localisation and boulder avoidance |
| T6 Sand | Rover on sand with competition-sized boulders and craters | Digging, dumping, wheel slip, localisation accuracy and crater detection |

**Table 14. Verification of requirements**

| ID | Method | Stages | Pass check |
| --- | --- | --- | --- |
| F1 | Demonstration | T4, T5 | Operator drives, digs and dumps with the gamepad. |
| F2 | Demonstration | T5 | Operator completes a cycle with no direct view and no arena cameras. |
| F3 | Test | T3, T4 | Outputs stop on enable release, link loss and bridge halt. |
| F4 | Test | T4 | After E-stop reset, no motor moves until the separate start command. |
| F5 | Test | T4 | One stop command halts all motors and actuators. |
| F6 | Test | T2, T3 | With two active sources, only the selected source reaches motion control. |
| F7 | Demonstration | T6 | Rover completes a dig sequence with no operator input. |
| F8 | Test | T2, T5, T6 | Pose error stays within bounds from multiple start poses and cardinal headings. |
| F9 | Demonstration | T6 | Rover aligns with and dumps into the berm target area with no operator input. |
| F10 | Inspection and test | T2, T5 | Selector ignores operator motion commands during autonomy; link capture shows none sent. |
| F11a | Test | T2, T5, T6 | Perception detects boulders (30 to 40 cm), craters (40 to 50 cm) and walls. |
| F11b | Test | T2, T5, T6 | Planner generates and follows a safe route around hazards. |
| F12 | Demonstration | T2, T6 | Rover completes one full traverse-dig-traverse-dump cycle autonomously. |
| F13 | Test | T2, T5 | Telemetry reports step state; autonomy halts itself on injected failure. |
| F14 | Test | T5, T6 | Rover stays inside arena without touching walls, sensing walls during autonomy. |
| P1 | Test | T5 | Average link rate over 20 minutes is 4,000 kbps or less. |
| P2 | Test | T3, T4 | Time from last valid command to zero motor controller command is 600 ms or less (proposal). |
| P3 | Test | T5 | Software is ready to drive within 10 minutes of power-on. |
| P4 | Demonstration | T5 | Practice comm check finishes in 15 minutes or less. |
| P5 | Test | T2, T5, T6 | Rover touches no boulder and enters no crater across repeated traverses. |
| P6 | Test | T5, T6 | Pose at berm target area is within 0.2 m and 5 degrees (proposal). |
| N1 | Inspection | T1 | Code and configuration read no GPS, compass or magnetometer data. |
| N2 | Inspection | T1 | Sensor list includes no touch or ultrasonic sensors. |
| N3 | Inspection | T5 | Router and client use WPA2 or WPA3 and a 20 MHz 2.4 GHz channel. |
| N4 | Inspection | T1, T2 | Rover and simulator share launch files, topics and frames above the drive bridge. |
| N5 | Inspection | T1 | Rover autonomy packages contain no fixed arena dimensions. |

## 11. Open items

Table 15 tracks unresolved architecture decisions and when each closes.

**Table 15. Open items**

| ID | Open item | Closes at |
| --- | --- | --- |
| O1 | LiDAR mount position clearing the chassis within the 0.75 m height limit | PDR |
| O2 | Return traverse direction: reverse to berm, or turn round | PDR |
| O3 | ROS 2 transport for gamepad commands over Wi-Fi (static peers or Zenoh) | PDR |
| O4 | Drive controller (`ros2_control` or custom node) and aligning simulation with drive bridge | PDR |
| O5 | Command selector implementation and mode transitions | PDR |
| O6 | Localisation fusion method and odometry-to-body transform ownership | PDR |
| O7 | E-stop restart interlock: electrical, software or both | PDR |
| O8 | Beacon marker design (AprilTags, retroreflectors or both) and dimensions | PDR |
| O9 | Holding zone goals without fixed arena dimensions | When organisers confirm |
| O10 | Hazard detection method, costmap format and route planner | CDR |

## 12. Risks

**Table 16. Risks**

| ID | Risk | Effect | Mitigation |
| --- | --- | --- | --- |
| R1 | Rover hardware arrives late. | Little time remains for floor and sand tests. | Test in simulation and on the bench first (T2, T3); agree a floor-test date with mechanical and electrical. |
| R2 | Simulator does not model loose sand. | Digging, dumping and slip wait until T6. | Run early ladder trials in a sand box and schedule full sand tests early. |
| R3 | Final rulebook changes requirements. | Design or interfaces must change. | Trace Tables 3 to 5 to rulebook sections and audit each release. |
| R4 | Final rulebook changes arena comms layout. | Router placement or radio setup changes. | Keep network settings in parameter files and rehearse the comm check (P4). |
| R5 | Jetson saturates in 25 W mode with full autonomy running. | Pose lags or hazards are missed. | Benchmark each subsystem in 25 W mode before package selection; keep point clouds onboard. |
| R6 | Default ROS 2 multicast discovery fails over Wi-Fi. | Mission control drops connection or topics. | Use WebSocket bridge for video and telemetry; test static peers and Zenoh on the router (O3). |
| R7 | Camera cannot read beacon from excavation zone. | Pose drifts without a far-end fix. | Evaluate wall-based LiDAR odometry and LiDAR retroreflectors on the beacon (O6, O8). |
| R8 | LiDAR misses low rocks or crater rims near the rover. | Rover hits a rock or enters a crater (P5). | Use front and rear OAK-D Pro depth for the near field; test with competition-sized hazards (T6). |
| R9 | Organiser answers on walls and time divisor exist only in email. | Localisation or run strategy changes if the final rulebook disagrees. | Keep the no-walls localisation baseline working (Table 6); confirm at the 2 December information day. |
| R10 | CAD LiDAR mount hides 6 m ahead and all rear ground, and exceeds 0.75 m. | Hazard detection fails P5 and inspection fails. | Resolve mount geometry with mechanical before PDR (O1, I12). |
| R11 | No sand test venue is ready. | Excavation, slip and craters stay untested. | Test ladder in a sand box; test localisation and boulders on a walled floor with boxes (T5). |
| R12 | Interface knowledge sits with one person. | Cross-subsystem work stalls if that person is unavailable. | Keep interfaces in Table 7, assign each to one of its two subsystems, and peer-review changes. |

## 13. Schedule

Table 17 lists competition milestones, including the 2 December information day where provisional clarifications are confirmed.

**Table 17. Competition dates**

| Date | Event |
| --- | --- |
| Wed 2 December 2026 | Competition information day |
| By Fri 29 January 2027 | Preliminary design review (PDR) |
| By Fri 12 March 2027 | Critical design review (CDR) |
| Fri 19 March 2027 | Down-selection to 8 teams |
| By Fri 14 May 2027 | Proof of Life video (driving, moving material and E-stop) |
| By Fri 21 May 2027 | Competition places confirmed |
| Tue 6 July 2027 | Arrival |
| Wed 7 to Thu 8 July 2027 | Competition at The Open University |

Because the overview document describes the Proof of Life video showing the rover moving material as well as driving and stopping on the E-stop, remote-control digging and dumping must work before 14 May 2027. Table 18 lists the five software capability milestones.

**Table 18. Software milestones**

| Milestone | Stage | Test stages | Needed for |
| --- | --- | --- | --- |
| Drive simulated rover from mission control | 1 | T1, T2 | Validate command path before hardware assembly |
| Drive real rover from mission control | 1 | T3 to T5 | Proof of Life video, 14 May 2027 |
| Dig and dump by remote control | 1 | T4, T6 | Proof of Life video, 14 May 2027, and manual cycles |
| Autonomous dig and dump | 2 | T2, T6 | Partial autonomy points (125 points) |
| Full autonomous cycle | 3 | T2, T5, T6 | Traverse and full-cycle points (250 to 600 points) |

## Appendix A. Design options for the PDR

The following four trade tables record candidate packages and protocols evaluated ahead of PDR selection.

### A.1 Operator video

The OAK-D Pro encodes H.264, H.265 and MJPEG in hardware ([Luxonis VideoEncoder](https://docs.luxonis.com/software/depthai-components/nodes/video_encoder)).

**Table A1. Options for operator video**

| Option | Data rate | Display in Foxglove |
| --- | --- | --- |
| Raw images | About 330,000 kbps at 1280 × 720, 30 fps | Supported |
| MJPEG, encoded on camera | Quality-controlled, not fixed kbps; compresses each frame alone | Supported |
| H.264, encoded on camera | Controlled directly in kbps | Supported |
| H.265, encoded on camera | Controlled directly in kbps | Depends on laptop hardware and codecs |

The team selects onboard H.264 for direct bitrate control, broad laptop playback and zero Jetson encoding load.

### A.2 Link transport

Default ROS 2 discovery relies on UDP multicast ([ROS 2 discovery settings](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)), which Wi-Fi routers often drop.

**Table A2. Options for link transport**

| Option | Discovery | Traffic crossing link | Notes |
| --- | --- | --- | --- |
| DDS, default | UDP multicast on subnet | Discovery plus subscribed topics | No setup |
| DDS, static peers | Explicit peer IP addresses | Same as default DDS | Set via environment variables |
| [rmw_zenoh](https://github.com/ros2/rmw_zenoh) | Routers over TCP; no multicast | Same as DDS, without multicast floods | Jazzy binaries exist; non-Tier-1; all hosts must match |
| [foxglove_bridge](https://github.com/foxglove/foxglove-sdk/blob/main/ros/src/foxglove_bridge/README.md) | Single WebSocket to rover | Allow-listed topics only | Display laptop needs no ROS 2 install |

The team selects `foxglove_bridge` for video and read-only telemetry. Gamepad transport remains open between static DDS peers and `rmw_zenoh` (O3).

### A.3 Drive control

**Table A3. Options for drive control**

| Option | Velocity to wheel speeds | Command-loss stop | Wheel odometry | Team effort |
| --- | --- | --- | --- | --- |
| [ros2_control](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html) (`diff_drive_controller`) | Built in | Built in (0.5 s default) | Built in, with odometry-to-body transform | Custom C++ hardware interface for Teensy serial |
| Standalone ROS 2 node | Written by team | Written by team | Written by team | Single self-contained node |

The initial bridge is a standalone node; final selection closes at PDR (O4).

### A.4 Command selector

**Table A4. Options for command selector**

| Option | Velocity commands | Mechanism commands | Stop command | Team effort |
| --- | --- | --- | --- | --- |
| [twist_mux](https://github.com/ros-teleop/twist_mux) | Priority selection with timeouts | Not handled | Lock topic blocks lower priorities | Config plus separate mechanism arbiter |
| Custom mode node | Switched with mechanisms by one state | Switched with velocity by one state | Handled in state machine | Written and tested by team |

Running the selector onboard keeps autonomous commands off Wi-Fi and preserves arbitration during link dropouts. Because `twist_mux` does not arbitrate mechanism commands, the team writes mechanism selection either way. Final choice closes at PDR (O5).
