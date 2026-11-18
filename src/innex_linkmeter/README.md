# innex_linkmeter

Show, live, how many kbps each topic sends over the Wi-Fi link to mission control. The rules allow an average of 4,000 kbps over a run, with no peak limit. See [Communications](../../docs/rules.md#communications).

## Run

Build and source the workspace. With the sim running, start the meter with the sim topics:

```bash
ros2 run innex_linkmeter link_meter --ros-args \
  --params-file $(ros2 pkg prefix innex_linkmeter)/share/innex_linkmeter/config/sim.yaml
```

To measure other topics, set `topics`:

```bash
ros2 run innex_linkmeter link_meter --ros-args -p topics:='[/oak_front/rgb/image_raw, /odom]'
```

Once a second, the node prints each topic's kbps over the last second, the total, and the average since the node started. A topic shows `waiting` until something publishes on it. When the average goes over `limit_kbps`, the last line turns red.

## Parameters

| Parameter | Default | What it does |
|---|---|---|
| `topics` | none, you must set it | The topics to measure. Match it to `foxglove_bridge`'s `topic_whitelist`. |
| `limit_kbps` | `3600.0` | The average above which the meter warns. 3,600 leaves 10% spare under the 4,000 kbps rule. |

## Topics it publishes

| Topic | Type | What it holds |
|---|---|---|
| `/link/kbps` | `std_msgs/Float32` | The total over the last second |
| `/link/average_kbps` | `std_msgs/Float32` | The average since the node started |

Plot both in Foxglove's [Plot panel](https://docs.foxglove.dev/docs/visualization/panels/plot).

## What it measures

The node subscribes with `raw=True`, so each message arrives as its serialised bytes and is not deserialised. It counts the length of those bytes, as `ros2 topic bw` does, and uses the same sensor-data QoS. 1 kbps is 1,000 bits per second. `ros2 topic bw` reports bytes, so divide the meter's kbps by 8 to compare them.

This is what ROS sends, not what the router sees. Wi-Fi and network overhead add a little on top. The router measurement is part of INX-147.
