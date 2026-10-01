# UK Lunabotics rules

This is a summary of the UK Lunabotics 2026 Rule Book, v1.0, dated 18 May 2026. Where this page and the rulebook differ, the rulebook is correct.

The organisers publish documents at [uklunabotics.co.uk](http://uklunabotics.co.uk/).

## Scoring

Each team gets two competition runs. The final score is the sum of both runs.

| Category | How it's scored |
|---|---|
| Inspections | You must pass the vehicle inspection and the comm check before your first run. If you fail either, the robot can't enter the arena. |
| Berm productivity, normalised for mass | Berm volume in the target area, per minute of run, per kg of robot mass |
| Berm productivity, normalised for energy | Berm volume in the target area, per minute of run, per Wh of energy used |
| Bandwidth use | Arena cameras used during the run: 0 cameras scores 120, 1 camera scores 60, 2 cameras score 0 |
| Autonomy | Up to 600 points. See [Autonomy](#autonomy). |

The judges scan the arena before and after each run to measure the berm volume. Only volume inside the target area counts. The target area is about 1.5 m × 0.9 m. The berm can have any shape, height or number of piles.

The rulebook gives an example run with 77,551 cm³ of berm, a 66 kg robot and 36 Wh of energy:

| Category | Actual | Points |
|---|---|---|
| Berm, mass | 77,551 cm³ / 15 min / 66 kg = 78.33 | 344.6 |
| Berm, energy | 77,551 cm³ / 15 min / 36 Wh = 143.6 | 215.4 |
| Bandwidth | 1 camera | 60 |
| Autonomy | Excavation | 75 |
| Total | | 695 |

In the example, mass points are 4.4 × the actual value and energy points are 1.5 × the actual value. The rulebook doesn't state these factors outside the example. The example divides by 15 minutes, although runs are 20 minutes.

## Autonomy

| Task | Points | What the robot must do hands-free |
|---|---|---|
| Excavation | 75 | Dig and collect a visible amount of sand in the excavation zone |
| Dump | 50 | Enter the construction zone and put a visible amount of sand on the berm |
| Travel | 250 | Cross the obstacle zone from the starting zone into the excavation zone |
| Full autonomy, one cycle | 450 | Start zone to excavation, dig, return, dump |
| Full autonomy | 600 | The whole run, with at least two full cycles and a berm that scores |

- Excavation, dump and travel points add together, up to 375. They can happen on separate passes within a run.
- You can't combine excavation, dump or travel points with either full autonomy score.
- The Caterpillar Autonomy Award goes to the highest autonomy score over both runs. Berm points break a tie.

### Autonomy conditions

- For excavation, go hands-free before the robot touches the sand. Lift the digging mechanism out of the sand before you take control again.
- For dump, you can cross the obstacle zone by remote control. Go hands-free before the robot enters the construction zone.
- For travel and both full autonomy tasks, you can drive only inside the starting zone to localise. Go hands-free in the starting zone.
- Full autonomy, one cycle and full autonomy must start at the beginning of the run.
- For travel, the judges set the obstacles so that the robot must detect them, map them and plan a route. Don't use a "point and traverse" approach.

### Autonomy penalties

| Task | Contact with a rock, or driving over a crater, in the obstacle zone | Other |
|---|---|---|
| Travel | 30 points, once | 50 points if the attempt comes after you crossed the obstacle zone by remote control |
| Full autonomy, one cycle | 30 points each time, up to 90 | |
| Full autonomy | 30 points each time, up to 90 | |

In the excavation zone, the robot can move rocks and fill craters.

### Hands-free rules

1. Announce each attempt to the mission control judge before it starts, and make eye contact.
2. Announce when the attempt starts and when it ends.
3. Don't touch any equipment until you announce that the attempt is complete or has failed.
4. If the attempt fails, announce the failure before you take manual control.

If nobody tells the judge before an attempt, the attempt scores zero. If anyone touches equipment during an attempt, the attempt scores zero. You can move the arena cameras during an attempt.

During autonomy, you can watch telemetry. You can't send commands, orientation data or obstacle locations to the robot.

## Robot

### Size and mass

- The robot must fit inside 150 cm × 75 cm × 75 cm at the start. You choose which axis is which.
- After the start, the robot can extend up to 175 cm higher, to 250 cm above the sand.
- The maximum mass is 80 kg. Lower mass scores higher.
- The mass includes the radio equipment on the robot and the navigation beacon.
- The mass doesn't include equipment in mission control.
- If you use more than one robot, the limits apply to all the robots together.

### Required

- Four lifting points, marked and safe for hands. Teams carry the robot with one person per 20 kg.
- Three arrows: one for length, one for width, and one for the forward direction. The judges use the forward arrow to set the random start direction.
- An E-stop and an energy logger. See [E-stop](#e-stop) and [Energy logging](#energy-logging).

### Not allowed

- GPS, or IMUs with built-in GPS
- Compasses. If an IMU has a compass, you must show the judges how you turn it off or remove its data.
- Ultrasonic proximity sensors
- Touch sensors used to find or avoid obstacles
- Pneumatic or foam-filled tyres, and open-cell or closed-cell foam
- Hydraulics
- Anything that changes the physical or chemical properties of the sand
- Projectiles, ordnance or far-reaching mechanisms. Parts that extend within the size limits are allowed.
- Any process that doesn't work off-world. For example, cleaning dust from a lens must use a method that works on the Moon.

### Allowed

- Pneumatics, if all the gas is stored on the robot
- Li-ion, NiCd, sealed lead-acid and NiMH batteries
- Composites, rubber and plastic parts
- Fan-cooled electronics and brushed motors
- IMUs, and infrared, proximity and Hall effect sensors
- Honeycomb structures, if the edges are sealed or not sharp enough to cut
- More than one robot, if the team controls all parts at all times
- Earth-environment resources, such as oxygen or water, if the system is designed for the Moon and the resources count towards the robot's mass

Parts don't need to be space-qualified.

### Who builds it

Students must do all the design, building and operation. Outside companies can make parts from students' designs, for example laser cutting, 3D printing, CNC machining or PCB fabrication.

## E-stop

- One unmodified, off-the-shelf, red E-stop button on each robot. Without one, the robot is disqualified.
- At least 40 mm in diameter, at the highest practical point, and reachable without extra steps
- One push must stop all motion and disconnect the batteries from all controllers.
- The button must latch. Resetting it must not restart the robot. Restarting needs a separate, deliberate command.
- A control signal to a relay is allowed, if the relay stays open to keep the robot disabled.
- An onboard computer can stay on only if it has its own battery that doesn't go through the E-stop.
- Disabling the E-stop without permission from the staff disqualifies the robot.

## Energy logging

- An off-the-shelf electronic data logger must record the energy used in each run. The rulebook gives the PZEM-051 as an example.
- Put the logger at the highest practical point, where the judges can see it.
- Wire the logger between the battery and the E-stop, so its reading survives an E-stop.
- A judge reads the logger straight after the run.
- If the logger is wired wrong, you lose 30 points from the energy score. If it's wired wrong and the E-stop is used, you might score zero.
- If the robot has an onboard laptop, you must log its power use with a hardware monitor, such as HWiNFO.

## Batteries

1. Stay with batteries while they charge.
2. Unplug chargers overnight.
3. Store and carry lithium batteries in containers designed for them.
4. Store batteries upright, not touching each other.
5. Inspect a dropped battery for damage, and replace it if needed.
6. Don't store a battery that's hot after charging.
7. If a battery stays hot, take it outside if you can, and tell the event staff.
8. If there's fire or smoke, set off the fire alarm and call 999 or 112 from a safe place.

## Navigation and sensing

- The robot can't use the arena walls for mapping, navigation or collision avoidance.
- You must explain to the judges how your autonomy sensing works and prove it doesn't use the walls. If you don't, you're disqualified from the competition.
- You can mount a beacon or fiducial on the frame provided near the starting zone, facing the construction zone.
- You can fix it with tape, clamps or rods pushed into the sand. Screws and other fasteners that need holes aren't allowed.
- Attach the beacon during setup and remove it after the run.
- The beacon must have its own power, and its mass counts towards the 80 kg limit.
- Lasers must be unmodified, and Class I, Class II or below 5 mW. Bring the manufacturer's eye-safety documentation.

## Communications

1. Use a dual-band IEEE 802.11 router with 2.4 GHz and 5 GHz. You must be able to turn off 2.4 GHz.
2. Use the SSID you get at check-in, and transmit only on it.
3. Broadcast the SSID. Hidden networks aren't allowed.
4. Use WPA2 or WPA3 encryption.
5. Set 2.4 GHz channel width to 20 MHz.
6. Keep to Ofcom power limits. Don't add amplifiers. Amplifiers disqualify the team.
7. Keep the link to an average of 4,000 kbps or less. There's no peak limit.

- Bluetooth is allowed at Class 2 or 3, up to 2.5 mW EIRP. Class 1 isn't allowed.
- 2.4 GHz Zigbee and IEEE 802.15.4 aren't allowed.
- 5 GHz Wi-Fi and other unlicensed bands, such as 900 MHz, are allowed. The organisers don't monitor them for interference, and interference on them isn't grounds for a protest or rematch.

### Comm check

You must pass a comm check before you compete. You get 15 minutes at the check station, on Wi-Fi channel 1. While you're in the queue, you can set your equipment to channel 1, but then turn all wireless equipment off until your check starts.

During the check, you must:

1. Show the judges every wireless part on the robot.
2. Connect to the robot and control it wirelessly.
3. Turn off the router's 2.4 GHz band.

If you use Bluetooth or another non-Wi-Fi radio, bring printed datasheets that show the part number, frequency and power level. The datasheet must show that Bluetooth parts aren't Class 1.

If you don't finish the check in 15 minutes, you're disqualified from the competition.

### Comms in the RoboPits

- Turn off 2.4 GHz or power down wireless equipment.
- Use 5 GHz or an Ethernet cable.
- To test on 2.4 GHz, get permission from the Pit Boss first. Tests are short and only on channel 11.

## Competition run

| Stage | Time |
|---|---|
| Place the robot and set up | Up to 10 minutes |
| Run | 20 minutes |
| Remove the robot | 5 minutes |

1. The judges inspect the robot before each run. You can't change it between inspection and the run.
2. The judges choose the starting position and direction at random, just before the run.
3. The robot can't be anchored to the sand before the run starts.
4. If the robot doesn't move within 5 minutes of the timer starting, the run ends.
5. When the timer ends, stop. If the robot is in an autonomous task, send a command that stops it. It can finish a dump that has already started.
6. Keep the connection to the robot until the judge says you can disconnect. The robot might need to move or unload before removal.

### During the run

- Cross the obstacle zone to reach the excavation zone.
- Dig berm material only in the excavation zone. The robot can start digging when any part of it enters the excavation zone.
- The robot can start building when any part of it enters the construction zone.
- Don't push or move obstacles in the obstacle zone, and don't fill its craters.
- In the construction zone, you can push obstacles only to the side of the arena.
- Don't move obstacles into the excavation zone.
- Obstacles moved from the excavation zone into the target area count towards the berm.
- Stay inside the arena. Hitting the wall costs points, and ramming it can disqualify the run.
- Don't use the walls or any other part of the arena structure for operations.
- The robot can't push into the sand with more force than its own weight.
- The robot can split into parts. Unplanned breakage doesn't count against you.

### Ending a run early

If the robot can't continue, tell the mission control judge that you're ending the run. Examples:

- Loss of communication
- Loss of movement, or only occasional movement, for 5 minutes
- Loss of digging or unloading
- Loss of the whole robot

If you don't end the run within a reasonable time, the judges can end it. Wasting time, for example driving without purpose, can cost points. If a fix takes a long time, such as a full reset, tell the judge.

## Mission control

- Up to 4 team members, who enter together. No faculty or advisors.
- Bring only equipment you need to run the robot. Other laptops, phones and smart devices aren't allowed.
- Bring all the spares you need. You can't go back for forgotten items.
- No outside communication until the run ends, except the radio the judges give you during setup.
- Return the radio at the end of setup.
- Settle all rule questions before you enter mission control. The judges don't answer questions during the run.
- Use only data and video from the robot and the arena camera monitors. Use the monitors only for situational awareness.
- Don't connect to any equipment until setup starts.
- Arena team members can't tell mission control about obstacles, craters or other arena conditions.
- You can use the arena cameras during setup at no cost.
- Take all your equipment with you when you leave.

Breaking the intent of a rule counts as breaking the rule. Raise disputes with the Mission Control Director.

## Arena

- The inside of the arena is about 7.9 m × 4.4 m.
- Sand is about 21.5 cm deep in the travel and building areas, and 51.5 cm deep in the excavation area.
- Boulders are about 30 cm to 40 cm across, placed at random before each round. Some can be in the excavation zone.
- Craters are no more than about 40 cm to 50 cm deep or wide.
- The arena diagram shows Camera 1, Camera 2 and a pan and zoom camera.

### Arena access

- Only the active team can enter the arena: up to 4 people to place and remove the robot, and up to 4 in mission control.
- No faculty or advisors.
- Hosts fit masks the day before the competition. The arena team puts on PPE in the RoboPits staging area.
- Leave phones, cameras and tablets at the Arena Chief's station.
- Follow the Arena Chief's instructions, and approach the arena only when told to.
- After the run, vacuum sand off the robot at the cleaning station.

## RoboPits

- Each team gets space in a 15 m × 10 m marquee with a UK mains power strip.
- There's no internet. General Wi-Fi might be available, but bring your own mobile data.
- A marshal takes each team and its robot to the arena.

## Undefined in v1.0

- Comms rules inside the arena: "TBD"
- Comms between the arena and mission control: "TBD"
- The number of arena cameras available to mission control: "two [TBC]"
- RoboPits check-in procedures: listed in the contents, but missing from the document
