# Competition rules

These are the competition rules that affect our software and operations. Two rulebooks apply:

- The UK Lunabotics 2026 Rule Book, v1.0, dated 18 May 2026. Most of this page follows it.
- The UK Lunabotics 2027 draft rule book, v0.1, dated 3 October 2026. It is based on the 2026 rules and is subject to change. The final rulebook will be published at [uklunabotics.co.uk](https://uklunabotics.co.uk/). [Differences in the 2027 draft](#differences-in-the-2027-draft) lists the changes that matter to us.

Where this page and the rulebook differ, the rulebook is correct.

## Before we compete

We must pass two inspections before our first run. Neither is optional. A rover that does not pass cannot enter the arena.

- The mechanical inspection covers size, mass, lifting points, arrows, the E-stop and the energy logger.
- The communications check is described in [Comm check](#comm-check).

## Not allowed

- GPS, or IMUs with built-in GPS.
- Compasses. If an IMU has a compass, we must show the judges how we turn it off or remove its data.
- Ultrasonic proximity sensors.
- Touch sensors used to find or avoid obstacles.

## Scoring

| Category | How it is scored |
|---|---|
| Inspections | Pass the vehicle inspection and the comm check before the first run. |
| Berm volume, normalised for mass | Berm volume in the target area, per minute of run, per kg of rover mass. |
| Berm volume, normalised for energy | Berm volume in the target area, per minute of run, per Wh of energy used. |
| Bandwidth use | Arena cameras used during the run: 0 cameras scores 120, 1 camera scores 60, 2 cameras score 0. |
| Autonomy | Up to 600 points. See [Autonomy](#autonomy). |

The judges scan the arena before and after each run. Only berm inside the target area counts. The target area is about 1.5 m × 0.9 m. The berm can have any shape, height or number of piles.

Each team has two runs. The final score adds the two runs together.

The rulebook's example divides by 15 minutes. A run lasts 20 minutes. The example scoring sheet in the 2027 draft uses multipliers of 4.4 for mass and 1.5 for energy. The rulebook does not give these formulas outside the example. Check the final rulebook before we rely on them.

## Autonomy

| Task | Points | What the rover must do hands-free |
|---|---|---|
| Excavation | 75 | Dig and collect a visible amount of sand in the excavation zone |
| Dump | 50 | Enter the construction zone and put a visible amount of sand on the berm |
| Travel | 250 | Cross the obstacle zone from the starting zone into the excavation zone |
| Full autonomy, one cycle | 450 | Start zone to excavation, dig, return, dump |
| Full autonomy | 600 | The whole run, with at least two full cycles and a berm that scores |

- Excavation, dump and travel points add together, up to 375. They can happen on separate passes within a run.
- Excavation, dump and travel points cannot combine with either full autonomy score.
- The Caterpillar Autonomy Award goes to the highest autonomy score over both runs in the 2026 rulebook. The 2027 draft uses the sum of both runs. Berm points break a tie.

### Autonomy conditions

- For excavation, go hands-free before the rover touches the sand. Lift the digging mechanism out of the sand before taking control again.
- For dump, we can cross the obstacle zone by remote control. Go hands-free before the rover enters the construction zone.
- For travel and both full autonomy tasks, we can drive only inside the starting zone to localise. Go hands-free in the starting zone.
- Full autonomy, one cycle, and full autonomy must start at the beginning of the run.
- For travel, the judges set the obstacles so that the rover must detect them, map them and plan a route. A "point and traverse" approach is not allowed.

### Autonomy penalties

| Task | Contact with a rock, or driving over a crater, in the obstacle zone | Other |
|---|---|---|
| Travel | 30 points, once | 50 points if the attempt comes after we crossed the obstacle zone by remote control |
| Full autonomy, one cycle | 30 points each time, up to 90 | |
| Full autonomy | 30 points each time, up to 90 | |

In the excavation zone, the rover can move rocks and fill craters.

### Hands-free rules

1. Announce each attempt to the mission control judge before it starts. Make eye contact.
2. Announce when the attempt starts and when it ends.
3. Do not touch any equipment until we announce that the attempt is complete or has failed.
4. If the attempt fails, announce the failure before taking manual control.

If nobody tells the judge before an attempt, the attempt scores zero. If anyone touches equipment during an attempt, the attempt scores zero. We can move the arena cameras during an attempt.

During autonomy, we can watch telemetry. We cannot send commands, orientation data or obstacle locations to the rover.

## Navigation and sensing

- The rover cannot use the arena walls for mapping, navigation or collision avoidance. Touch sensors that brush a wall are not allowed either.
- We must explain to the judges how our autonomy sensing works, and prove that it does not use the walls. Otherwise we are disqualified.
- We can mount a beacon or fiducial on the frame near the starting zone, facing the construction zone.
- We fix the beacon with tape, clamps or rods pushed into the sand. Screws and other fasteners that need holes are not allowed.
- We attach the beacon during setup and remove it after the run.
- The beacon must have its own power. Its mass counts towards the 80 kg limit.
- Lasers must be unmodified, and Class I, Class II or below 5 mW. We must bring the manufacturer's eye-safety documentation.

## Communications

1. Use a dual-band IEEE 802.11 router with 2.4 GHz and 5 GHz. We must be able to turn off 2.4 GHz.
2. Use the SSID we get at check-in. Transmit only on it.
3. Broadcast the SSID. Hidden networks are not allowed.
4. Use WPA2 or WPA3 encryption.
5. Set the 2.4 GHz channel width to 20 MHz.
6. Keep to Ofcom power limits. Do not add amplifiers. Amplifiers disqualify the team.
7. Keep the link to an average of 4,000 kbps or less. There is no peak limit.

- Bluetooth is allowed at Class 2 or 3, up to 2.5 mW EIRP. Class 1 is not allowed.
- 2.4 GHz Zigbee and IEEE 802.15.4 are not allowed.
- 5 GHz Wi-Fi and other unlicensed bands, such as 900 MHz, are allowed. The organisers do not monitor them for interference. Interference on them is not grounds for a protest or rematch.

### Comm check

We must pass a comm check before we compete. We get 15 minutes at the check station, on Wi-Fi channel 1. In the queue, we can set our equipment to channel 1. Then we turn all wireless equipment off until the check starts.

During the check, we must:

1. Show the judges every wireless part on the rover.
2. Connect to the rover and control it wirelessly.
3. Turn off the router's 2.4 GHz band.

If we use Bluetooth or another non-Wi-Fi radio, we bring printed datasheets. They must show the part number, frequency and power level. They must show that Bluetooth parts are not Class 1.

If we do not finish the check in 15 minutes, we are disqualified.

### RoboPits comms

- Turn off 2.4 GHz, or power down wireless equipment.
- Use 5 GHz or an Ethernet cable.
- To test on 2.4 GHz, get permission from the Pit Boss first. Tests are short, and only on channel 11.

## The run

| Stage | Time |
|---|---|
| Place the rover and set up | Up to 10 minutes |
| Run | 20 minutes |
| Remove the rover | 5 minutes |

1. The judges inspect the rover before each run. We cannot change it between inspection and the run.
2. The judges choose the starting position and direction at random, just before the run.
3. The rover cannot be anchored to the sand before the run starts.
4. If the rover does not move within 5 minutes of the timer starting, the run ends.
5. When the timer ends, stop. If the rover is in an autonomous task, send a command that stops it. It can finish a dump that has already started.
6. Keep the connection to the rover until the judge says we can disconnect. The rover might need to move or unload before it is removed.

### During the run

- Cross the obstacle zone to reach the excavation zone.
- Dig berm material only in the excavation zone. The rover can start digging when any part of it enters the excavation zone.
- The rover can start building when any part of it enters the construction zone.
- Do not push or move obstacles in the obstacle zone. Do not fill its craters.
- In the construction zone, we can push obstacles only to the side of the arena.
- Do not move obstacles into the excavation zone.
- Obstacles moved from the excavation zone into the target area count towards the berm.
- Stay inside the arena. Hitting the wall costs points. Ramming it can disqualify the run.
- Do not use the walls or any other part of the arena structure for operations.
- The rover cannot push into the sand with more force than its own weight.

### Ending a run early

If the rover cannot continue, tell the mission control judge that we are ending the run. Examples include loss of communication, loss of movement (or only occasional movement) for 5 minutes, loss of digging or unloading, and loss of the whole rover.

If we do not end the run within a reasonable time, the judges can end it. Wasting time, for example by driving without purpose, can cost points. If a fix takes a long time, such as a full reset, tell the judge.

## E-stop

- The rover needs one unmodified, off-the-shelf, red E-stop button. Without one, it is disqualified.
- One push must stop all motion. It must disconnect the batteries from all controllers, and isolate the batteries from the other active subsystems.
- The button must latch. Resetting it must not restart the rover. A separate, deliberate command restarts it.
- A control signal to a relay is allowed, if the relay stays open to keep the rover disabled.
- An onboard computer can stay on only if it has its own battery. That battery must not go through the E-stop.
- Disabling the E-stop without permission from the staff disqualifies the rover.

## Mission control

- Up to four team members enter together. No faculty or advisors.
- Bring only the equipment needed to run the rover. Other laptops, phones and smart devices are not allowed.
- No outside communication until the run ends, except the radio the judges give us during setup.
- Settle all rule questions before entering mission control. The judges do not answer questions during the run.
- Use only data and video from the rover and the arena camera monitors. Use the monitors only for situational awareness.
- Do not connect to any equipment until setup starts.
- Arena team members cannot tell mission control about obstacles, craters or other arena conditions.
- We can use the arena cameras during setup at no cost.

## The arena

- The inside of the arena is about 7.9 m × 4.4 m.
- Boulders are about 30 to 40 cm across. The judges place them at random before each round. Some can be in the excavation zone.
- Craters are no more than about 40 to 50 cm deep or wide.

## Undefined in v1.0

The 2026 rulebook leaves these points undefined or "TBD":

- The comms rules inside the arena.
- The comms rules between the arena and mission control.
- The number of arena cameras available to mission control, which it gives as "two [TBC]".

The 2027 draft defines some of these in its communications section. This page does not summarise that section yet.

## Differences in the 2027 draft

These changes in the 2027 draft (v0.1, 3 October 2026) matter to us:

- The Caterpillar Autonomy Award uses the sum of autonomy scores from both runs.
- The E-stop must also isolate the batteries from the other active subsystems.
- The hands-free rule names laptops and game controllers. Nobody in mission control may use them during an attempt.
- Teams may not update the autonomy program to add or upload obstacle locations.
- Teams must explain how they interact with the telemetry system before each run. The judge checks that they send no commands.
- The autonomy point values are 50, 75, 125, 250, 300, 375, 450 and 600.
