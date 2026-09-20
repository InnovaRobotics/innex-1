# Current facts

The one-page table of what is true today. Update it when a fact changes. If a document elsewhere disagrees with this table, this table wins and the other document is wrong.

Last verified: 2026-09-20.

## Competition

| Fact | Value | Source |
|---|---|---|
| Rulebook in force | UK Lunabotics RuleBook 2026 v1.0 | `/Documents/UKLunabotics RuleBook 2026 v1.0.pdf` (local) |
| 2027 rulebook | Not published | Organisers, TBC |
| Arena | ~7.9 m x 4.4 m; sand 21.5 cm (traverse, construction), 51.5 cm (excavation) | Rulebook, Arena Composition |
| Obstacles | Boulders 30-40 cm; craters up to 40-50 cm wide | Rulebook, Arena Composition |
| Run | 20 min; 10 min setup; 5 min removal; must move within 5 min | Rulebook, Mission Control |
| Envelope / mass | 150 x 75 x 75 cm; 80 kg max; 4 lifting points | Rulebook, Robot Requirements |
| Bandwidth | 4,000 kbps average; assigned SSID only; 2.4 GHz at 20 MHz | Rulebook, Communications |
| Arena cameras | 0 = 120 pts, 1 = 60, 2 = 0 | Rulebook, Construction Points |
| Autonomy points | Excavation 75; Dump 50; Travel 250; Full 450 / 600 | Rulebook, Autonomous Operations |
| Walls | May not be used for sensing, mapping or navigation | Rulebook, Autonomy Rules 3-4 |
| Fiducials | Allowed on the frame by the start zone only; mass counts | Rulebook, Robotic Operations 7 |
| E-stop | One COTS red button >= 40 mm, latching, isolates batteries from controllers; separate compute battery outside E-stop path allowed | Rulebook, E-STOP 1-7 |
| Power meter | Between battery and E-stop; 30-pt penalty otherwise | Rulebook, Power Meters 2 |
| Lens cleaning | Must be a Moon-plausible process (no canned air) | Rulebook, Battery Protocol 8 |

## Rover hardware (as competed June 2026; mechanical model not yet received)

| Item | Value | Source |
|---|---|---|
| Chassis | ~45 kg skid steer, carbon-fibre body; bucket ladder excavation; rear hopper with sliding door and tipping | 2026 repo docs; team |
| Drive motors | 4 x Gimson GR-WM4-V3, 24 V worm gear ~64:1, 37 rpm no-load, self-locking, 40% duty at rated load, IP30 | `gr-wm4-v3-drivetrain-motor.md` (2026) |
| Encoders | Quadrature Hall (SS460S), 12 PPR motor shaft, ~720/rev output; VCC red, GND black, A white, B yellow; 3.3 V supply | same |
| Drive controllers | 2 x Sabertooth 2x32, packet serial 9600 baud, address 128; Teensy `Serial1` pin 1 (left), `Serial7` pin 29 (right) | `sabertooth-2x32.md`, session 2026-06-06 |
| Actuators | 2 x Cytron MDD10A (PWM + DIR); 2 x 50 mm (Tru Components), 2 x 250 mm (DCHouse, via 12 V buck); no position feedback | `cytron-mdd10a.md`, session 2026-06-06 |
| Excavation motor | 57BLR50 BLDC via BLD-510B: SV PWM pin 6, F/R pin 13, EN pin 14, PG pin 31, ALM pin 32; EN polarity depends on driver version | `bld-510b-bldc-controller.md` |
| Microcontroller | Teensy 4.1, USB serial 115200 to Jetson | 2026 firmware |
| Compute | Jetson Orin Nano Super Developer Kit, 8 GB, JetPack 6.x (exact version TBC) | team |
| Cameras | 2 x Luxonis OAK-D Pro (USB, RVC2, IR dot projector, BNO086 IMU, on-device H.264) | Luxonis docs |
| LiDAR | Ouster OS1-128 (Rev 7 class; firmware TBC). 42.4 deg vertical FOV; 14-20 W; 5 W standby; ICM-20948 IMU 100 Hz | Ouster datasheet Rev7 |
| Router | GL.iNet GL-A1300 (Wi-Fi 5, 2x2, 867 Mbps 5 GHz, OpenWrt) | GL.iNet datasheet |
| Batteries | 6S 22.2 V 8,000 mAh (motive); 4S 14.8 V 5,000 mAh (compute) | Electrical CDR 2026 |
| Motor mounts | 3D-printed mounts failed in June 2026; aluminium replacements planned | Public post-competition report |

## Software versions

| Item | Value |
|---|---|
| OS | Ubuntu 22.04 (Jammy) |
| ROS 2 | Humble (EOL May 2027) |
| RMW | `rmw_cyclonedds_cpp` |
| ROS_DOMAIN_ID | 27 |
| Python / C++ | 3.10 / C++17 |
| Simulation | Gazebo Fortress (kinematic stand-in only) |
| Firmware toolchain | PlatformIO, Arduino framework for Teensy |
| Dev image | `ghcr.io/innovarobotics/innex-1-dev` |

## People

| Role | Who |
|---|---|
| Software lead, org owner | KJ (@KJdotIO) |
| Firmware and hardware bridge | Electrical -> software teammate (GitHub handle TBC) |
| Mechanical / electrical contacts | TBC |

## Unknowns to resolve

- Jetson JetPack exact version (`cat /etc/nv_tegra_release`).
- Ouster firmware version and standby wake time.
- Whether the drive motors are on the same mounts and wiring as June 2026.
- Hopper volume and bucket-ladder excavation rate.
- Whether excavation and deposition are on opposite ends of the rover (assumed yes).
- Teammate GitHub / Linear / Discord handles.
