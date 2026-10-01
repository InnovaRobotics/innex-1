# Jetson

The rover's computer is a Jetson Orin Nano Super Developer Kit. It runs JetPack 7.2.1 (Jetson Linux R39.2.1, Ubuntu 24.04) without a desktop. You use it over SSH.

## Rules

- Deploy a known commit to the Jetson. Don't edit code or install packages on it.
- Keep it in 25 W mode. Don't select MAXN SUPER (`nvpmodel -m 2`).
- Don't upgrade or unhold `nvidia-l4t-*` packages.
- Don't install firmware capsules.

## Shut down

1. Run `ssh innex-1 sudo poweroff`.
2. Wait 20 seconds.
3. Unplug the power.

## Get access

You need an SSH key on GitHub and a Tailscale account.

1. If you don't have an SSH key on GitHub, create one with `ssh-keygen -t ed25519`.
2. Add the `.pub` file to **GitHub** > **Settings** > **SSH and GPG keys**.
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

    ```
    ssh innex-1
    ```

The Jetson accepts SSH keys only. It doesn't accept passwords.

### Add or remove a key

To add a key from GitHub, a lead runs:

```
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
- The `wifi-reconnect.timer` service checks the Wi-Fi every minute. If the Wi-Fi has disconnected, it connects to a saved network.
- To turn off Wi-Fi, first stop the timer with `sudo systemctl stop wifi-reconnect.timer`.
- On eduroam, Tailscale sends traffic through a relay. The relay is fast enough for SSH, but too slow for video.

### Troubleshooting

| Problem | Fix |
|---|---|
| `ssh innex-1-usb` times out while a UTM VM runs | UTM has taken the USB device. In the VM's USB menu, clear **Linux for Tegra**. Or run `utmctl usb disconnect 0955:7020`. |
| SSH warns that the host key changed | Check the new key with a lead. Then run `ssh-keygen -R innex-1`. |
| Tailscale shows the Jetson as offline | Connect over USB-C. Check the Wi-Fi with `nmcli device status`. |
