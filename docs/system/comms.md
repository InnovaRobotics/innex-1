# Comms and mission control

This page answers how the operator sees and drives the rover over the link. It covers the router, the connection between the laptop and the Jetson, and what the operator sees in mission control. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Carry the operator's commands from the laptop to the Jetson.
- Carry video and telemetry from the rover back to the laptop.
- Keep the average data rate at or below 4,000 kbps over a whole run.
- Let ROS 2 (Robot Operating System 2) on the laptop and on the Jetson find each other and keep talking.
- Let the rover stop when the link goes quiet, and let the operator see that it has.
- Pass the comm check.

## Inputs and outputs

Operator commands travel from the laptop to [Teleop and rover control](teleop-and-control.md). Video comes from the cameras described in [Sensors](sensors.md). Telemetry comes from the rest of the rover, including [Navigation and mission](navigation-and-mission.md).

Nothing in this subsystem makes driving decisions. It carries messages, and the other subsystems decide what to send.

## Rules that apply

- [Communications](../rules.md#communications): dual-band router, assigned service set identifier (SSID, the network name), broadcast SSID, WPA2 or WPA3, and an average of 4,000 kbps or less with no peak limit.
- [Comm check](../rules.md#comm-check): 15 minutes on Wi-Fi channel 1. You must show every wireless part, control the robot wirelessly and turn off the router's 2.4 GHz band.
- [Mission control](../rules.md#mission-control): you can use only data and video from the robot and the arena camera monitors.
- [Hands-free rules](../rules.md#hands-free-rules): during an autonomous attempt, you can watch telemetry but you can't send commands, orientation data or obstacle locations.
- [Scoring](../rules.md#scoring): each arena camera you use costs points, so rover video carries the operator's view.
- [Undefined in v1.0](../rules.md#undefined-in-v10): the rulebook leaves comms inside the arena and between the arena and mission control as "TBD".

## Hardware

- Mission control laptop: reads the gamepad and runs Foxglove.
- Router: dual-band Wi-Fi between mission control and the rover.
- Jetson Orin Nano Super: the rover end of the link. See [jetson.md](../jetson.md).
- Two OAK-D Pro cameras: encode video on the camera.

## The 4,000 kbps budget

The rules limit the average rate over a run, not the peak, so short bursts above 4,000 kbps are allowed. A long burst can still delay command messages on a busy link. Three things use the budget:

- Video. Video is usually the largest user, and two cameras double it.
- Telemetry and visualisation: status, pose, and any map or point cloud preview the dashboard shows. A raw point cloud is far too large to send. One scan from a 128 beam LiDAR holds tens of thousands of points, and scans repeat several times each second.
- Discovery traffic. ROS 2 machines announce themselves and search for each other, and this chatter grows with every node and topic on the link.

Raw images and point clouds never cross the link. They stay on the Jetson, where the software uses them. The operator sees compressed video instead. The OAK-D Pro cameras encode H.264 video on the camera, so the Jetson doesn't spend its own processing power on it.

Someone must measure the average rate over a full run, because a short test can miss a slow rise in traffic.

## DDS discovery across machines

ROS 2 uses a middleware called DDS (Data Distribution Service). When two nodes start, DDS finds them through multicast announcements on the local network. Multicast works well on a wired network and badly on Wi-Fi, where routers often drop or throttle it. The symptom is that topics appear and disappear, or that a topic published on one machine doesn't show up on the other.

Two fixes are common: give each machine a fixed address and list the other machine's address as a discovery peer, or choose a different middleware such as `rmw_zenoh`. The Jazzy tutorial on [improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html) covers the first. Another Lunabotics team found that their link stopped dropping once the Jetson had a fixed address and the peer list was clean. See [their pull request](https://github.com/jsmith-exe/lunabotics/pull/98).

## The comm check

The comm check is short and has a fixed procedure, so you can rehearse it. While you wait in the queue, you can set your equipment to channel 1, but you must keep all wireless equipment off until your check starts. At the station, show the judges every wireless part, control the rover from the laptop, and turn off 2.4 GHz on the router. If you use Bluetooth or another non-Wi-Fi radio, bring printed datasheets. If the check takes more than 15 minutes, the team is disqualified.

## What the operator can use

In mission control, the operator can use only data and video that come from the robot, plus the arena camera monitors for awareness. Arena team members can't tell mission control about rocks, craters or other conditions. This means the dashboard has to show everything the operator needs to drive and to judge the state of a dig or a dump.

## Open questions

1. Does operator video go through ROS and Foxglove, or through a separate video stream?
2. Which topics cross the link, and at what rates?
3. Do we use tuned DDS discovery settings or `rmw_zenoh`?
4. How do we measure average link use over a full 20-minute run?
5. Where does the router sit, and does the rover need its own client bridge? The rules leave arena comms undefined.
6. What does the operator dashboard show during teleop and during a hands-free attempt?

## Read more

- [foxglove_bridge](https://index.ros.org/p/foxglove_bridge/)
- [Foxglove Image panel](https://docs.foxglove.dev/docs/visualization/panels/image)
- [Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
- [QPL debugging notes for their link](https://github.com/jsmith-exe/lunabotics/blob/main/qpl_ws/DnR.md)
- [QPL rover_cameras package](https://github.com/jsmith-exe/lunabotics/tree/main/qpl_ws/src/rover_cameras)
- [Iowa State net-adapter](https://github.com/Cardinal-Space-Mining/lance-2026/tree/main/net-adapter)
