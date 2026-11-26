# Approved interaction examples (PR #20 session)

These excerpts come from the PR #20 review session (`innex_video` and `innex_sim`) and show the team standard for agent reviews and file walkthroughs.

## 1. Filtering boilerplate and pacing one file at a time

Notice how this reply strips away packaging files, lists the three files that matter, opens only the first 37-line file, builds from the 4,000 kbps Wi-Fi constraint to **keyframe**, **NAL units**, and **Annex B** before naming line numbers, and stops at the end of that single file:

> Inside `src/innex_video`, you can ignore all the ROS packaging boilerplate (`package.xml`, `setup.py`, `setup.cfg`, and `resource/`). Only three files do real work:
>
> 1. `src/innex_video/innex_video/video_messages.py` wraps raw video bytes into the ROS message Foxglove expects.
> 2. `src/innex_video/innex_video/video_relay.py` opens one OAK-D Pro camera and publishes its video stream.
> 3. `src/innex_video/launch/video.launch.xml` starts the front and rear camera nodes alongside Foxglove Bridge.
>
> Open `src/innex_video/innex_video/video_messages.py` first in VS Code. It is 37 lines long, and we will stop after this one file before touching the next.
>
> ### File 1: `video_messages.py`
>
> Start with why we compress video at all. If a camera sent a full grid of raw colour pixels fifteen times every second, one stream would blow straight past our 4,000 kbps competition Wi-Fi limit. H.264 shrinks that traffic by sending one complete picture once per second, and then for the next fourteen frames sending only the patches that moved since the frame before. That complete once-per-second picture is called a **keyframe**.
>
> Picture what happens when the rover is running in the arena and you open Foxglove on the mission control laptop ten seconds in. If the first message Foxglove receives is one of those "only what moved" frames, it has no starting picture to apply the movement to, so the screen stays blank until the next keyframe arrives. Even when that keyframe arrives, Foxglove still cannot decode the pixels unless the frame also carries the stream's setup rules, such as the image width, height, and colour layout.
>
> Because one video frame carries those setup rules and pixel slices bundled together in a single byte string, H.264 divides the byte string into small labelled packets called **NAL units** (Network Abstraction Layer units). In the byte stream format Foxglove reads, called **Annex B**, each chunk starts with a fixed marker of zeros followed by a `1` (`\x00\x00\x01` or `\x00\x00\x00\x01`). The single byte right after that marker holds a five-bit label (`data[index] & 0x1f`) telling the decoder what kind of chunk follows: `7` and `8` are the setup headers (SPS and PPS), and `5` is a keyframe's image data (IDR).
>
> That is all `nal_types(data)` on lines 6 to 26 does. It walks across a frame's bytes, spots each `\x00\x00\x01` or `\x00\x00\x00\x01` marker, and collects those five-bit type numbers into a Python set. Our unit tests use it to check that keyframes contain `{5, 7, 8}`, proving Foxglove can tune into a live stream within one second.
>
> Have a read through `video_messages.py` in VS Code. Ask about any line that feels unclear, or say when you are ready for file two (`video_relay.py`).

## 2. Turning an abstract byte format into a concrete visual

When a teammate asked how the `\x00` and `\x01` markers relate to the chunk type, the reply drew the literal bytes from the unit test, showed the binary mask on one real byte, and ended with a single check question on a packet captured from the team's OAK-D Pro camera:

> You are close, with one small twist on what `\x00` and `\x01` are doing. The `\x00\x00\x00\x01` bytes are grouped together as a single divider (like a fence post between chunks), and the byte that tells you "I am a setup rule" or "I am a pixel slice" is the byte right after `\x01`.
>
> Here is the keyframe byte string from `test_video_messages.py` broken apart so you can see each piece:
>
> ```text
> 00 00 00 01   67   42 00 1e    00 00 01   68   ce 06 e2    00 00 00 01   65   88 84
> ^^^^^^^^^^^   ^^   ^^^^^^^^    ^^^^^^^^   ^^   ^^^^^^^^    ^^^^^^^^^^^   ^^   ^^^^^
>   divider    label  payload     divider  label  payload      divider    label payload
> ```
>
> Look at why line 26 writes `data[index] & 0x1f` instead of reading `67` directly. One byte holds eight bits, and H.264 uses the first three bits of that label byte for network priority flags while packing the chunk's type number into the last five bits. In binary, `0x67` is `0110 0111`. Masking with `& 0x1f` (`0001 1111` in binary) zeroes out the first three bits and keeps the last five (`00111`), which equals `7` (SPS).
>
> To test your mental model on a real chunk from your OAK-D Pro earlier: every frame from your camera began with `\x00\x00\x00\x01\x09\xf0`. Which byte in there is the label byte, and what NAL type number does `& 0x1f` pull out of it?

## 3. Pairing two files when one explanation depends on the other

When `video.launch.xml` loaded `config/camera_ids.yaml` by node name, both files belonged in the same turn so the YAML section matching made sense straight away:

> Open file three in VS Code: `src/innex_video/launch/video.launch.xml` (alongside `src/innex_video/config/camera_ids.yaml` if you want to glance at the 10-line config it loads). This is the last file in Commit 1, and it is 32 lines long.
>
> Lines 10 to 22 start two separate copies of `video_relay` from file two, naming one `front_video_relay` and the other `rear_video_relay`. Because ROS 2 matches sections inside a YAML file by node name, `<param from="$(var camera_config)" />` feeds the `front_video_relay:` block of `camera_ids.yaml` to the front node and the `rear_video_relay:` block to the rear node.

## 4. Dismissing over-engineered review noise in four words

When an automated review flagged a hypothetical half-configured YAML state, the reply gave the verdict in sentence one and explained the real operating states in three sentences:

> You can skip it. Devin Review marked four of its earlier flags as resolved on this push, leaving one yellow warning on `video.launch.xml`.
>
> That warning pictures someone writing a serial number under `rear_video_relay` in `camera_ids.yaml`, leaving `front_video_relay` blank at the same time, and plugging in only the rear camera. In practice you have two real states: bench testing with both IDs blank, or rover bring-up with both `front` and `rear` IDs filled in together. Nobody needs a half-filled `camera_ids.yaml`.
