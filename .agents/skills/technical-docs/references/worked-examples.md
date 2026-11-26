# Worked examples from `docs/system/localisation.md`

Read this file before drafting or rewriting a conceptual subsystem doc. Each example pairs the original choppy INNEX-1 text with the rewritten passage and notes which writing practices did the work.

## Example 1: Explaining architecture (`map` to `odom` to `base_link`)

### Before

> REP 105 defines two frames for the pose. The `odom` frame is smooth and continuous, but it drifts over time. It suits short-range control, because the pose never jumps. The `map` frame stays fixed to the arena, but it can jump when a correction arrives. It suits route planning across the arena.
>
> The frames form a chain: `map` to `odom` to `base_link`. In the transform (TF) tree, each frame has exactly one parent. If two nodes both published a transform from `map` to `base_link`, a lookup would return two answers. So each link in the chain has one owner. The drift correction goes into the link between `map` and `odom`. Motion of `base_link` in `odom` stays smooth.

What failed: eleven short sentences of nearly identical length; opens with a spec acronym (`REP 105`) before stating the problem; never shows what breaks when a single frame jumps mid-turn.

### After

> Once you combine continuous odometry (from wheels, IMU and LiDAR) with discrete beacon fixes, an architectural problem turns up. Suppose you keep one coordinate system for the whole arena and publish the rover's pose in it. Imagine the rover drives 3 metres across the obstacle zone, accumulating 25 cm of sideways drift along the way. Halfway around a rock, the camera catches sight of the beacon, and your localisation node snaps the estimated position 25 cm to the right in one tick.
>
> To the motion controller steering around that rock, the rover appeared to teleport 25 cm sideways. The controller reacts to the sudden error by jerking the wheels, which can swing the rover into the rock it was avoiding. If you avoid jumps by ignoring the beacon instead, the rover drives smoothly, except the route planner thinks the berm sits 40 cm away from its real spot.
>
> You need both behaviours at once: smooth, continuous motion for short-range control, and arena-fixed accuracy for route planning. [REP 105](https://www.ros.org/reps/rep-0105.html) solves this by placing two fixed coordinate frames above the rover's body frame, `base_link`, in a chain. The following diagram shows how the three frames connect and where each update lands.
>
> ```mermaid
> flowchart LR
>     map["map<br/>anchored to the arena"] -->|"beacon fix (can jump)"| odom["odom<br/>local origin"]
>     odom -->|"wheel + IMU + LiDAR odometry (smooth, drifts slowly)"| base["base_link<br/>on the rover"]
> ```
>
> Look at the two links in the chain. The link from `odom` to `base_link` tracks continuous motion from the wheels, IMU and LiDAR odometry. It can drift slightly over time, but it never jumps, so short-range controllers read `base_link` in `odom` and steer without sudden jerks. The link from `map` to `odom` absorbs every discrete correction from the beacon. Whenever a beacon sighting reveals 25 cm of accumulated drift, localisation shifts the `map` to `odom` transform by 25 cm. That puts the rover back in the right spot on the arena map for the route planner, while `base_link` keeps moving smoothly inside `odom`.
>
> In ROS 2, the transform library (**TF**) enforces one strict rule: every frame has one parent. If an odometry node and a beacon node both tried to publish a direct transform from `map` to `base_link`, any node asking for the rover's pose would receive two conflicting answers. Putting `odom` in the middle gives every link a single owner.

What changed:
- Lets the single-frame instinct fail physically (controller jerks into a rock) and shows the opposite failure (berm 40 cm off) before introducing REP 105.
- Adds a Mermaid chain and explicitly tells the reader which link to inspect instead of dropping an unreferenced diagram.
- Explains the TF single-parent constraint as the final piece locking the chain together.

## Example 2: Explaining LiDAR odometry (ICP) with arena walls

### Before

The original `localisation.md` assumed arena walls were banned and mentioned LiDAR odometry only as one open question:

> 6. Is LiDAR odometry worth its processing cost on the Jetson?

What failed: carried forward an outdated no-walls assumption after the organisers' 4 November email clarification, and dropped the term "LiDAR odometry" without explaining how scan matching works or how it fits alongside wheel odometry and the beacon.

### After

> Wheel odometry and the gyroscope both degrade when the rover digs, climbs over loose sand or twists in place. Sensing the arena walls with the Ouster OS1-128 LiDAR changes what localisation can do across the whole pit.
>
> Imagine printing two transparent copies of the LiDAR's top-down scan: one captured a tenth of a second ago, and one captured at this instant. Because the rover moved slightly between scans, the dots along the arena walls shifted by a few centimetres. If you slide and rotate the second sheet until its wall lines sit right on top of the first sheet's wall lines, the amount you had to move the sheet equals the rover's motion between those two moments. Matching consecutive point clouds like this is called **LiDAR odometry**, and software typically solves the alignment with an algorithm such as **iterative closest point (ICP)**.
>
> This works well on sand for a simple reason: the laser beams bounce off rigid arena walls that never slip, even while the rover's tyres spin in place. It also respects the rule against hard-coded arena dimensions. The software never stores the pit's 7.9 m by 4.4 m size in code; it compares each live scan against the scans it built moments earlier.
>
> LiDAR odometry still leaves two geometric gaps. First, tiny alignment errors add up over long drives, so the pose can still drift over time. Second, a live scan of a rectangular pit only tells you how far you moved from where you started, and a rectangle looks identical if you rotate it 180 degrees. Without an external landmark, the LiDAR can't tell which end of the pit is the excavation zone. Running point-cloud matching also uses real CPU time, so any LiDAR odometry package has to fit inside the Jetson's 25 W power mode.

What changed:
- Opens with a concrete physical analogy (two overlapping transparent top-down scans) and names **LiDAR odometry** and **iterative closest point (ICP)** only after the reader pictures the motion.
- Explains *why* it beats wheel slip (rigid walls) and *why* it obeys the no-hard-coding rule (compares live scans against recent scans, never stored pit dimensions).
- Names its real limits honestly (gradual drift, 180-degree rectangle symmetry, 25 W CPU budget), setting up the next section on why the beacon still anchors the arena frame.

## Example 3: Explaining a Kalman filter and EKF from scratch

### Before

> A fusion filter, such as an extended Kalman filter (EKF), weighs each source by its covariance and combines them. The filter still depends on honest covariances and good calibration. Whether the first autonomy tasks need a filter at all is an open question.

What failed: compresses covariance, Kalman gain, predict-and-update and linearisation into two opaque sentences; leaves a newcomer with no idea how weighting works or why an *extended* filter is needed.

### After

> Your first instinct might be to split the difference. Suppose the rover drove straight down the arena. Wheel odometry says `x = 2.00 m`, and a beacon sighting (or a LiDAR match) says `x = 1.60 m`. Taking the midpoint puts you at `1.80 m`.
>
> That average assumes both numbers deserve equal trust, which isn't true on sand. After two metres of driving with wheel slip, wheel odometry could be off by 30 cm either way. A crisp close-range beacon sighting might be accurate to around 10 cm. Giving a sloppy wheel guess the same vote as a sharp measurement pulls your estimate 20 cm away from the stronger source.
>
> To weight each source fairly, every sensor has to report both its reading and how spread out its errors tend to be. Statistics captures that spread by squaring the typical error to produce the **variance**. Using the numbers from that example:
>
> - Wheel odometry has a typical error of `0.30 m`, so its variance is `0.30 * 0.30 = 0.09 m^2`.
> - The beacon sighting has a typical error of `0.10 m`, so its variance is `0.10 * 0.10 = 0.01 m^2`.
>
> Because squaring grows fast, three times the error becomes nine times the variance. On a real rover, you track several numbers at once (x, y, heading and velocities), so those variances sit in a grid called a **covariance** matrix.
>
> With both variances in hand, you want a blending weight between 0 and 1 that says how far to step from the prediction towards the measurement. Dividing the prediction variance by the total variance gives that exact ratio:
>
> ```text
> weight = prediction variance / (prediction variance + measurement variance)
> ```
>
> Plug in our wheel prediction (`2.00 m`, variance `0.09`) and the beacon sighting (`1.60 m`, variance `0.01`):
>
> ```text
> weight = 0.09 / (0.09 + 0.01) = 0.90
> updated position = 2.00 + 0.90 * (1.60 - 2.00) = 1.64 m
> ```
>
> Check both extremes to verify that the formula makes sense. If the measurement had zero error (variance `0`), the weight would equal `0.09 / 0.09 = 1`, and you'd take `1.60 m` outright. If the measurement had far more noise (say variance `9.0`), the weight would drop to `0.09 / 9.09`, under 1 per cent, and you'd stay close to the prediction. The combined estimate also has a slightly smaller variance (`0.009 m^2`) than either input alone.
>
> That blending weight is called the **Kalman gain** (written `K` in textbooks, alongside `P` for the state covariance and `R` for the measurement covariance). A **Kalman filter** runs this calculation in a repeating **predict** and **update** cycle. A plain Kalman filter assumes every step is a straight-line relationship, where doubling an input doubles the output. Rover motion stops being linear as soon as you turn: driving forward by distance `d` at heading angle `theta` changes `x` by `d * cos(theta)` and `y` by `d * sin(theta)`, and sines and cosines curve. An **extended Kalman filter (EKF)** handles those curves by approximating them with a straight tangent line at the rover's pose on each tick, then running the same predict-and-update maths.

What changed:
- Lets the plain average (`1.80 m`) fail on unequal sensor noise before introducing **variance** and **covariance**.
- Uses plain English equations (`prediction variance / (prediction variance + measurement variance)`) before attaching textbook symbols (`K`, `P`, `R`).
- Checks both extremes (`0` and `9.0`) and computes the exact combined variance (`0.009 m^2`) so the reader builds trust in the maths.
- Explains "extended" through `d * cos(theta)` and `d * sin(theta)` curving, connecting straight to ROS 2 Jazzy's `robot_localization` (`ekf_node`).
