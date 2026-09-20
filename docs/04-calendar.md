# Season calendar 2026-27

Status: provisional. The organisers have not published 2027 dates (uklunabotics.co.uk still shows the 2026 schedule as of 2026-09-20). The competition dates below are the 2026 pattern shifted by one year. Replace them the day the 2027 schedule appears.

Rule of the calendar: if a hardware gate slips, the autonomy scope shrinks. The dates do not move.

## Organiser milestones (2026 pattern, projected)

| When (projected) | Milestone | 2026 actual | Owner |
|---|---|---|---|
| Early Oct 2026 | Registration opens; 2027 rulebook published | 7 Oct 2025 | KJ |
| Mid Nov 2026 | Registration deadline: Statement of Support + Project Management Plan | 14 Nov 2025 | KJ + faculty advisor |
| Dec 2026 | Registration confirmed | Dec 2025 | - |
| Jan 2027 | System Design Review (SDR) document | 13 Jan 2026 | Whole team |
| Feb 2027 | Organiser check-in with teams | Feb 2026 | KJ |
| Mar-Apr 2027 | Critical Design Review (CDR) document | Mar-Apr 2026 | Whole team |
| ~May 2027 | Proof-of-life video due (rover operating) | ~May 2026 | Software + mechanical |
| Jun 2027 | Competition, The Open University, Milton Keynes (comm check, inspection, two runs) | 15-17 Jun 2026 | Whole team |

The Project Management Plan is the first deliverable and is due about eight weeks from now. Its content is this calendar plus the team, budget and risk register.

The US guidebook for 2027 (NASA) has already fixed: guidebook 3 Sep 2026, PMP 29 Sep 2026, PDR report 20 Nov 2026, selections 14 Dec 2026, then Robot Data Report and Proof of Life in early 2027. The UK organisers follow the US model with a one-to-two month lag, so treat the US dates as an early warning.

## Hardware and software gates (ours)

| Date | Gate | Pass criterion | If missed |
|---|---|---|---|
| 2026-10-15 | Interface contract v1 | Pin map YAML, serial protocol spec, E-stop and power-meter diagram agreed with electrical | Firmware work continues against 2026 pin map; contract becomes the blocker for bench |
| 2026-10-31 | Bench built | Teensy + one Sabertooth + one motor + E-stop on a board; motor spins from a laptop | Bench is the first thing done in November |
| 2026-11-30 | Teleop stack on bench | Pad -> ROS -> serial -> Teensy -> motor; watchdog stops motor on cable pull; bag recorded | Tier 2-3 macros pushed right |
| 2026-12-15 | Dev environment proven | Both team members build and run the container; CI green on amd64 and arm64 | - |
| 2027-01-31 | Rover drives under teleop | Both cameras streaming under 2,500 kbps; all four motors; E-stop test; bag recorded | Travel automation (Tier 4) dropped from the plan |
| 2027-02-28 | First sand session | One full excavate-dump cycle by hand in sand; slip and sinkage observed; bag recorded | Tier 4 dropped; Tier 2-3 at risk |
| 2027-02-28 | Comm check rehearsal | Bandwidth measured at the router under 4,000 kbps; 2.4 GHz disable script works | - |
| 2027-03-31 | Excavation and dump macros | Single-button sequences with position sensing, demonstrated in sand | Tier 2-3 dropped; teleop-only plan |
| 2027-04-15 | Hardware freeze | Aluminium mounts fitted; any later mechanical change requires a re-test | - |
| 2027-04-30 | Loaded sand test and transport test | Rover driven hard with a full hopper; loaded into and out of the van; nothing broke | Fix and repeat before proof of life |
| 2027-05-15 | Proof-of-life video | Full cycle on video, from the operator's screen only | - |
| 2027-05-31 | Two timed rehearsals | Two 20-minute runs from a cold start with a 10-minute setup; inspection packet complete | - |
| Competition week | Nothing new | No code changes after Monday except a documented fix with a bag | - |

Tier 4 (travel automation) work is allowed only after the 2027-02-28 gates are passed, and only on recorded sand bags first.

## Recurring

- Weekly: 30-minute sync; update Linear; post the week's session logs in `#rover-log`.
- After every hardware session: a session log issue and a bag in OneDrive.
- Monthly: re-check this calendar against the organiser site; update `docs/02-facts.md`.

## Availability

KJ: third year; availability to be entered per term. Teammate: to be entered. Exam periods block hardware sessions; plan gates around them, not through them.
