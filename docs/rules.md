# Competition rules

This page summarises the UK Lunabotics rules that shape INNEX-1's software, sensing and run operations. Three sources apply:

- The UK Lunabotics 2026 Rule Book, v1.0, dated 18 May 2026, which forms the baseline for most sections here.
- The UK Lunabotics 2027 draft rule book, v0.1, dated 3 October 2026, which builds on the 2026 rules and remains subject to revision until the final rulebook appears on [uklunabotics.co.uk](https://uklunabotics.co.uk/). [Differences in the 2027 draft](#differences-in-the-2027-draft) lists the changes that matter to the team.
- An email clarification from the organisers (James Cole, UK Lunabotics, 4 November 2026), summarised in [Organiser clarifications](#organiser-clarifications-provisional). Treat those answers as provisional until the final 2027 rulebook publishes them.

Whenever this page and an official rulebook disagree, the rulebook wins.

## Before we compete

The rover must pass two inspections before its first run. A rover that fails either inspection cannot enter the arena.

- Mechanical inspection checks stowed size (150 cm × 75 cm × 75 cm at the start), mass (80 kg maximum including the beacon and onboard radio), lifting points, forward orientation arrows, the E-stop and the energy logger.
- Communications inspection follows the 15-minute procedure in [Comm check](#comm-check).

## Not allowed

The rules ban four categories of sensing hardware on the rover:

- GPS receivers, including IMUs with built-in GPS.
- Compasses of any kind. If an IMU includes a magnetometer, you must demonstrate to the judges how software switches it off or strips its data.
- Ultrasonic proximity sensors.
- Touch sensors used to detect or avoid obstacles or walls.

## Scoring

After passing pre-run inspections, the judges score each run across four point categories, then add both runs together for the final competition score.

| Category | How it is scored |
| --- | --- |
| Inspections | Pass vehicle inspection and the comm check before the first run |
| Berm volume, normalised for mass | Berm volume inside the target area, per minute of run, per kg of rover mass |
| Berm volume, normalised for energy | Berm volume inside the target area, per minute of run, per Wh of energy used |
| Bandwidth use | Arena cameras used during the run: 0 cameras scores 120, 1 camera scores 60, 2 cameras score 0 (example values) |
| Autonomy | Up to 600 points; see [Autonomy](#autonomy) |

The judges scan the arena before and after each run. Only sand deposited inside the target area (about 1.5 m × 0.9 m) counts towards berm volume, regardless of pile shape or height.

In the 2027 draft scoring example, the multipliers are 4.4 for mass and 1.5 for energy, and the example divides by 15 minutes even though the maximum run length is 20 minutes. The rulebook does not state those multipliers outside the example, so confirm them against the final rulebook before building strategy around exact point totals. Under the 4 November email clarification, the time divisor is the actual duration of the run when the team tells the judge it has finished.

## Autonomy

| Task | Points | What the rover must do hands-free |
| --- | --- | --- |
| Excavation | 75 | Dig and collect a visible amount of sand in the excavation zone |
| Dump | 50 | Enter the construction zone and deposit a visible amount of sand on the berm |
| Travel | 250 | Cross the obstacle zone from the start zone into the excavation zone |
| Full autonomy, one cycle | 450 | Start zone to excavation, dig, return across the obstacle zone, dump |
| Full autonomy | 600 | Complete at least two full cycles with a scoring berm |

Excavation, dump and travel points add together up to 375 and can happen on separate passes during a run. They do not stack with either full autonomy score. Under the 2026 rules, the Caterpillar Autonomy Award went to the highest single-run autonomy score; the 2027 draft sums both runs instead, with berm points breaking ties.

### Autonomy conditions

- For excavation, go hands-free before the digging mechanism touches the sand, and lift it completely clear of the sand before resuming manual control.
- For dump, you can cross the obstacle zone by remote control, then go hands-free before the rover enters the construction zone.
- For travel and both full autonomy tasks, you can drive by remote control only inside the start zone to localise, then go hands-free before leaving the start zone.
- Full autonomy (one cycle) and full autonomy must begin at the start of the run.
- For travel, the judges arrange obstacles so the rover has to sense them, map them and plan a route. A pre-programmed "point and traverse" path is forbidden.

### Autonomy penalties

| Task | Contact with a boulder, or driving over a crater, in the obstacle zone | Other |
| --- | --- | --- |
| Travel | 30 points, once | 50 points if attempted after crossing the obstacle zone by remote control |
| Full autonomy, one cycle | 30 points each time, up to 90 | |
| Full autonomy | 30 points each time, up to 90 | |

Inside the excavation zone, the rover can move boulders and fill craters without penalty.

### Hands-free rules

Every autonomous attempt follows the same strict protocol with the mission control judge:

1. Announce the attempt to the mission control judge before starting and make eye contact.
2. Announce clearly when the hands-free attempt starts and when it ends.
3. Touch no laptops, gamepads or controls until you announce that the attempt has succeeded or failed.
4. If an attempt fails, announce the failure before taking manual control.

Starting without notifying the judge, or touching controls mid-attempt, scores zero for that attempt. Operators can still adjust the arena camera views (if used) and passively monitor telemetry, provided nobody sends commands, orientation data or obstacle locations to the rover.

## Navigation and sensing

- In the 2026 rulebook and 2027 draft v0.1, the arena walls cannot be used for mapping, autonomous navigation or collision avoidance, and touch sensors that brush a wall are banned. The 4 November organiser email states that mapping the walls as obstacles for autonomy and navigation is expected to be allowed in the final 2027 rulebook, while hard-coding the arena's dimensions into navigation software stays forbidden. See [Organiser clarifications](#organiser-clarifications-provisional).
- You must explain to the inspection judges how your autonomy sensing works, and prove it complies with the sensing rules. Failing to disclose how sensing works disqualifies the team.
- You can mount one beacon or fiducial on the designated frame near the start zone, facing the construction zone. All markers or devices must sit on that single face.
- Attach the beacon with tape, clamps or rods pushed into the sand; screws or fasteners that make holes in the arena frame are forbidden. Mount it during setup and remove it during the removal window.
- The beacon must carry its own power if active, and its mass counts towards the 80 kg rover limit.
- Lasers must be unmodified and Class I, Class II or below 5 mW. Bring manufacturer eye-safety datasheets to inspection.

## Communications

1. Use a dual-band IEEE 802.11 router (2.4 GHz and 5 GHz) whose 2.4 GHz radio can be turned off.
2. Transmit only on the SSID assigned at check-in, and broadcast it (hidden networks are forbidden).
3. Encrypt the network with WPA2 or WPA3.
4. Set the 2.4 GHz channel width to 20 MHz.
5. Stay within Ofcom transmit power limits. External amplifiers disqualify the team.
6. Keep the average data rate over a run to 4,000 kbps or less. Short peaks above 4,000 kbps are allowed.

Bluetooth is allowed at Class 2 or Class 3 (up to 2.5 mW EIRP); Class 1 is banned. 2.4 GHz Zigbee and IEEE 802.15.4 are banned. 5 GHz Wi-Fi and other unlicensed bands such as 900 MHz are allowed, though organisers do not monitor them for interference and interference is not grounds for a rematch.

### Comm check

Every team passes a timed communications inspection before competing. While waiting in the queue, set equipment to Wi-Fi channel 1 and keep all wireless radios powered off until your slot starts. Inside the 15-minute window:

1. Show the judges every wireless component on the rover.
2. Connect from the laptop and control the rover wirelessly.
3. Switch off the router's 2.4 GHz band on demand.

Bring printed datasheets showing part number, frequency and output power for any Bluetooth or non-Wi-Fi radio. Exceeding 15 minutes disqualifies the team.

### RoboPits comms

- Turn off 2.4 GHz Wi-Fi in the pits, or power down wireless gear.
- Use 5 GHz Wi-Fi or an Ethernet cable for pit work.
- Ask the Pit Boss for permission before any brief 2.4 GHz test, and run it on channel 11 only.

## The run

| Stage | Time |
| --- | --- |
| Place the rover and set up | Up to 10 minutes |
| Run | Up to 20 minutes |
| Remove the rover | 5 minutes |

1. Judges inspect the rover before each run; no changes are allowed between inspection and the run.
2. Right before the timer starts, judges choose a random starting position inside the start zone and spin a direction wheel to point the rover's forward arrow north, east, south or west.
3. The rover cannot be anchored into the sand before the timer starts.
4. If the rover fails to move within 5 minutes of the run starting, the run ends.
5. When the timer expires (or the team ends the run), stop immediately. Send a stop command if an autonomous task is active; a dump already underway can finish.
6. Keep the wireless link up until the judge clears you to disconnect, in case the rover needs to move or unload before removal.

### During the run

- Cross the obstacle zone to reach the excavation zone. Digging can start as soon as any part of the rover enters the excavation zone, and berm building can start once any part enters the construction zone.
- Do not push boulders or fill craters inside the obstacle zone.
- Inside the construction zone, you can push obstacles only towards the side of the arena, never into the excavation zone.
- Rocks carried from the excavation zone onto the target area count towards berm volume.
- Stay inside the arena. Touching a wall incurs a penalty, and ramming a wall can disqualify the run.
- Do not lean against or use the arena walls or structure to perform mechanical operations.
- Do not push into the sand with more downward force than the rover's own weight.

### Ending a run early

Tell the mission control judge if the rover can no longer continue, for example after lost communications, no meaningful movement for 5 minutes, or a broken digging or dumping mechanism. Judges can also end a run if a team stalls or drives without purpose. If a recovery or reboot will take time, inform the judge.

## E-stop

- The rover must carry one unmodified, off-the-shelf red E-stop button at the highest practical point, at least 40 mm across.
- One push must stop all motion, disconnect the batteries from all motor controllers and isolate the batteries from other active subsystems.
- The button must latch mechanically. Resetting it must not restart the rover; a separate, deliberate command must re-enable motion.
- Switching power through a relay is allowed if the relay stays open until explicitly re-armed.
- An onboard computer can stay powered during an E-stop only if it runs from its own separate battery outside the E-stop circuit.
- Disabling the E-stop without staff permission disqualifies the rover.

## Mission control

- Up to four team members enter mission control together, with no faculty or advisors.
- Bring only equipment required to operate the rover; phones, spare laptops and smart devices stay outside.
- No outside communication is allowed during the run, aside from the organiser radio during setup.
- Settle all rule questions before entering mission control; judges do not answer rule queries during a run.
- Operate using only rover data, rover video and the arena camera monitors (for situational awareness only). Arena team members cannot relay obstacle locations or conditions to mission control.
- Do not connect to rover equipment until the setup timer begins. Using the arena cameras during setup carries no score penalty.

## The arena

- Interior dimensions are about 7.9 m × 4.4 m.
- Boulders are about 30 to 40 cm across and placed at random before each round; some can sit inside the excavation zone.
- Craters are up to about 40 to 50 cm deep or wide.

## Undefined in v1.0

The 2026 rulebook left three communications details marked "TBD":

- Wireless rules inside the arena.
- Link layout between the arena and mission control.
- Number of arena cameras available in mission control ("two [TBC]").

The 2027 draft and the 4 November organiser email fill in several of those details.

## Differences in the 2027 draft

Main changes in the UK Lunabotics 2027 draft rule book (v0.1, 3 October 2026):

- The Caterpillar Autonomy Award sums autonomy scores across both runs instead of taking the best single run.
- The E-stop must isolate the batteries from all other active subsystems in addition to motor controllers.
- Hands-free rules name laptops and game controllers explicitly; nobody in mission control may touch them during an autonomous attempt.
- Teams cannot alter or upload obstacle locations to the autonomy program.
- Before each run, teams must explain how they interact with telemetry so the judge can confirm no commands are sent.
- Autonomy point tiers are 50, 75, 125, 250, 300, 375, 450 and 600.

## Organiser clarifications (provisional)

On 4 November 2026, James Cole (UK Lunabotics) answered five team questions by email. Treat these points as provisional until the final 2027 rulebook confirms them:

- Walls and localisation: mapping the pit walls as obstacles for autonomy and navigation is expected to be allowed, while hard-coding the arena's dimensions into the navigation system is forbidden. Colliding with the pit walls remains forbidden, and the arena chief can stop a run if a collision looks likely.
- Communications layout: arena comms follow the US rulebook layout, with a mains power socket and an Ethernet cable in one corner feeding from the team-supplied router to mission control. The router sits in the arena corner and the rover carries a Wi-Fi client radio only.
- Beacon frame: official dimensions will be published later. Any number of markers or devices can sit on the beacon as long as all occupy one face (a flat surface).
- Independent autonomy scoring: autonomy tasks are classified independently so a failure in one stage does not erase credit earned in other tasks, with full points awarded once all steps succeed.
- Run time divisor: the time `T` in the berm scoring formulas is the actual duration of the run when the team tells the judge it has finished.
