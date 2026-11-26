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

   For the router's network, also add `innex-1-lan`. See [Networking](#networking).
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

Use the first route that works. The first two routes need no internet and no account.

| Host | Route | Use it |
|---|---|---|
| `innex-1-usb` | USB-C cable to the Jetson (192.168.55.1) | At the bench, or when the Jetson has no network |
| `innex-1-lan` | The rover router's network (192.168.8.10) | At the competition, and when your laptop is on the rover router |
| `innex-1` | Tailscale | From anywhere, when the Jetson has internet |

Add the new host to `~/.ssh/config`:

```
Host innex-1-lan
  HostName 192.168.8.10
  User innex-1
```

- Do not make scripts or launch files depend on Tailscale. The competition has no internet, so Tailscale is offline there.
- The rover router has no internet. When the Jetson is on the router's Wi-Fi, Tailscale shows it as offline. This is normal. Use `innex-1-usb` or `innex-1-lan`.
- The Jetson connects to the saved Wi-Fi network with the highest priority that is in range. The rover router has priority 10. Other saved networks have priority 0, as fallbacks.
- To add a network, run `sudo nmtui` on the Jetson.
- Wi-Fi power saving is off.
- The `wifi-reconnect.timer` service checks the Wi-Fi every minute. If the Wi-Fi has disconnected, the service connects to a saved network.
- To turn off Wi-Fi, stop the timer first: `sudo systemctl stop wifi-reconnect.timer`.
- On eduroam, Tailscale sends traffic through a relay. The relay is fast enough for SSH, but too slow for video.

## Bluetooth

Bluetooth is off. The `bluetooth` service is disabled, and `rfkill` blocks the radio. The rules allow only Class 2 and Class 3 Bluetooth, so ask a lead before you use it.

To turn Bluetooth on:

```bash
sudo rfkill unblock bluetooth
sudo systemctl enable --now bluetooth
```

## Rover router

The rover router is a GL.iNet GL-A1300. Its address is 192.168.8.1.

| Setting | Value |
|---|---|
| 5 GHz | Channel 36, 40 MHz, WPA2-PSK |
| 2.4 GHz | Channel 1, 20 MHz, WPA2-PSK |
| Guest networks | Off |
| LAN | 192.168.8.1/24. DHCP from 192.168.8.100 to 192.168.8.249. |
| Jetson, Wi-Fi | 192.168.8.10 (reserved) |
| Jetson, Ethernet | 192.168.8.11 (reserved) |

The router has no internet connection.

To open the admin page from your laptop, make an SSH tunnel through the Jetson:

```bash
ssh -N -L 8088:192.168.8.1:80 innex-1-usb
```

Then open `http://localhost:8088`. Ask a lead for the admin password. Do not write it in this repository, in Discord or in prompts.

Before the competition:

1. Change the SSID to the one the organisers assign. The rules require that SSID, and it must be visible.
2. Keep the 2.4 GHz width at 20 MHz.
3. Change the Wi-Fi password and the admin password.
4. Check that you can turn off the 2.4 GHz band. The comm check tests this. See [Rules](rules.md).

If the Jetson is on the router's Ethernet port and on its Wi-Fi at the same time, pings and routing can fail. Use one link at a time.

## Shut down

1. Run `ssh innex-1 sudo poweroff`.
2. Wait 20 seconds.
3. Unplug the power.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ssh innex-1-usb` times out while a UTM VM runs | UTM has taken the USB device. In the VM's USB menu, clear **Linux for Tegra**. Or run `utmctl usb disconnect 0955:7020`. |
| SSH warns that the host key changed | Check the new key with a lead. Then run `ssh-keygen -R innex-1`. |
| Tailscale shows the Jetson as offline | If the Jetson is on the rover router, this is normal. Connect with `innex-1-lan` or `innex-1-usb`. Otherwise, connect over USB-C and check the Wi-Fi with `nmcli device status`. |
