# Jetson

The Jetson is the rover's computer. It is a Jetson Orin Nano Super Developer Kit running JetPack 7.2.1, which includes Jetson Linux (L4T) R39.2.1 and Ubuntu 24.04. You must use it over SSH.

## Rules

- Deploy a known commit to the Jetson. Do not edit code on it. Do not install packages on it.
- Keep the Jetson in 25 W mode. Do not select MAXN SUPER (`nvpmodel -m 2`).
- Do not upgrade or unhold `nvidia-l4t-*` packages.
- Do not install firmware capsules.

## Check the power mode

Run this command on the Jetson:

```bash
sudo nvpmodel -q
```

The default mode is 25 W, according to [NVIDIA's BSP setup guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/setup_bsp.html). If the output does not show 25 W, or shows MAXN SUPER, tell a lead.

## Get access

You need an SSH key on GitHub and a Tailscale account.

1. If you do not have an SSH key on GitHub, create one: `ssh-keygen -t ed25519`.
2. Add the `.pub` file in GitHub under **Settings** > **SSH and GPG keys**.
3. Send your GitHub username to a lead. The lead adds your key to the Jetson.
4. Create a free [Tailscale](https://tailscale.com) account.
5. Send your Tailscale email address to a lead. The lead shares the Jetson with you.
6. Add these hosts to `~/.ssh/config`:
   ```
   Host innex-1
     HostName innex-1
     User innex-1

   Host innex-1-usb
     HostName 192.168.55.1
     User innex-1
   ```
7. Connect:
   ```bash
   ssh innex-1
   ```

The Jetson accepts SSH keys only. It does not accept passwords.

## Add or remove a key

A lead adds a GitHub key with this command:

```bash
curl -fsSL https://github.com/USERNAME.keys | ssh innex-1 'cat >> ~/.ssh/authorized_keys'
```

To remove a key, delete its line from `~/.ssh/authorized_keys` on the Jetson.

## Networking

| Host | Route | Use it |
|---|---|---|
| `innex-1` | Tailscale, over Wi-Fi | From anywhere |
| `innex-1-usb` | USB-C cable to the Jetson | When the Jetson has no Wi-Fi, or Tailscale is down |

- The Jetson connects to any saved Wi-Fi network in range. To add a network, run `sudo nmtui` on the Jetson.
- Wi-Fi power saving is off.
- The `wifi-reconnect.timer` service checks the Wi-Fi every minute. If the Wi-Fi has disconnected, the service connects to a saved network.
- To turn off Wi-Fi, stop the timer first: `sudo systemctl stop wifi-reconnect.timer`.
- On eduroam, Tailscale sends traffic through a relay. The relay is fast enough for SSH, but too slow for video.

## Shut down

1. Run `ssh innex-1 sudo poweroff`.
2. Wait 20 seconds.
3. Unplug the power.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ssh innex-1-usb` times out while a UTM VM runs | UTM has taken the USB device. In the VM's USB menu, clear **Linux for Tegra**. Or run `utmctl usb disconnect 0955:7020`. |
| SSH warns that the host key changed | Check the new key with a lead. Then run `ssh-keygen -R innex-1`. |
| Tailscale shows the Jetson as offline | Connect over USB-C. Check the Wi-Fi with `nmcli device status`. |
