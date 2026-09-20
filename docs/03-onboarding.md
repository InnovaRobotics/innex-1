# Onboarding: a development machine in 30 minutes

Goal: open this repository in the dev container and run `ros2 doctor`. If this takes longer than 30 minutes, the fault is in this document. Fix the document.

You need: a GitHub account in the `InnovaRobotics` organisation, Git, and VS Code with the Dev Containers extension. You do not need to install ROS on your host.

## 1. Get an Ubuntu 22.04 environment

Pick your host.

### Apple Silicon Mac (M1, M2, M3, M4)

Use VMware Fusion Pro. It is free for all use. The guest is Ubuntu 22.04 **arm64**, the same architecture as the Jetson.

1. Download and install VMware Fusion Pro 13.6 or later from Broadcom (free account required).
2. Download **Ubuntu Server 22.04.5 LTS arm64** ISO. Canonical does not publish a 22.04 arm64 desktop ISO; the server ISO plus the desktop package is the supported route. Use 22.04.2 or later; earlier ISOs do not boot in Fusion.
3. Create a new VM from the ISO. Settings: 6 processor cores, 8 GB RAM (leave 8 GB for macOS on a 16 GB machine), 60 GB disk, USB controller set to USB 3.1.
4. Install Ubuntu Server. Create your user. Enable OpenSSH server when asked.
5. In the VM, install the desktop and VMware tools:

   ```bash
   sudo apt update
   sudo apt install -y 'ubuntu-desktop^' open-vm-tools open-vm-tools-desktop
   sudo apt install -y linux-generic-hwe-22.04
   sudo reboot
   ```

   The HWE kernel (6.x) is required for 3D acceleration. Mesa 23.2 from `jammy-updates` already meets the requirement.
6. In Fusion: Virtual Machine > Settings > Display > tick **Accelerate 3D Graphics**. Reboot the VM.
7. Verify: `glxinfo -B` shows vendor `VMware, Inc.` and `OpenGL version string: 4.3`. If it shows `llvmpipe`, the HWE kernel is not active.
8. Install Docker Engine inside the VM (official `docs.docker.com/engine/install/ubuntu`), then `sudo usermod -aG docker $USER` and log out and in.

Known Gazebo Fortress behaviour in VMs: if the window is black or crashes, try `export OGRE_RTT_MODE=Copy`, then `ign gazebo --render-engine ogre`, then `export LIBGL_ALWAYS_SOFTWARE=1` as a last resort. RViz works with 3D on; for point clouds use the "Flat Squares" style, not "Points".

USB passthrough (Teensy, OAK-D): Virtual Machine > USB & Bluetooth > connect the device to the VM. macOS may ask for permission the first time.

### Windows 10/11

Use WSL2 with WSLg.

1. PowerShell as Administrator: `wsl --install -d Ubuntu-22.04`. Reboot. Create your user.
2. Install Docker Desktop for Windows with the WSL2 backend, and enable integration with the `Ubuntu-22.04` distro.
3. GUI apps work through WSLg with GPU acceleration. Gazebo Fortress may need `export LIBGL_ALWAYS_SOFTWARE=1`; Garden and later do not.
4. USB devices (Teensy, OAK-D) need `usbipd-win`: `winget install usbipd`, then `usbipd list`, `usbipd bind --busid <id>`, `usbipd attach --wsl --busid <id>`. Re-attach after every replug.

### Linux

Ubuntu 22.04 or 24.04 natively. Install Docker Engine. Done.

## 2. Clone and open

```bash
git clone git@github.com:InnovaRobotics/innex-1.git
cd innex-1
code .
```

VS Code: "Reopen in Container". The first build takes 5 to 15 minutes; later opens take seconds. Or pull the prebuilt image first: `docker pull ghcr.io/innovarobotics/innex-1-dev:latest`.

## 3. Smoke test

Inside the container terminal:

```bash
ros2 doctor
ros2 run demo_nodes_cpp talker &
ros2 run demo_nodes_py listener
```

You should see messages. `Ctrl-C` and `kill %1`.

## 4. Tools on the host (not in the container)

- **Foxglove** desktop app. Free account. Layouts are committed under `ops/foxglove/` when they exist.
- **Tailscale** for access to the Jetson and the bench. Ask KJ for an invite.
- **Linear** for tasks. Ask for an invite to team INX. Branch names are `inx-123-short-description`.
- **Bitwarden** shared collection for router, Wi-Fi and account credentials. Never put these in the repo or Discord.

## 5. First contribution

1. Pick a Linear issue labelled `good first issue`.
2. Branch from `main`. Make the change. `pre-commit run --all-files`.
3. Open a PR using the template. Cite evidence.
4. Someone else merges. Nobody merges their own PR.

## Time budget

| Step | Minutes |
|---|---|
| VM or WSL install | 15 |
| Docker | 5 |
| Clone and container build | 10 (first time) |
| Smoke test | 1 |
