# RoutineButler

**RoutineButler** is an app that is designed to be run "kiosk-style" on a RaspberryPi 🥧 connected to:

- 📺 an LCD touchscreen interface
- 📦 an electro-mechanically operated lockbox

Its purpose is to alart and administer "routines" 🏋️‍♂️  to users in exchange for incentives (such as unlocking whatever they may have put in the lockbox).

Here is a picture of my current setup which I am actively using as my morning and evening alarm clock:

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## Running RoutineButler Kiosk-Style "On Boot" on a RaspberryPi

What is currently working for me is the following:

1. Creating a `/etc/xdg/autostart/routine_butler.desktop` file with the following contents:

    ```bash
    [Desktop Entry]
    Exec=chromium-browser --kiosk http://127.0.0.1:8080
    ```

2. Adding the following line to `/etc/rc.local` before the `exit 0` line:

    ```bash
    sudo /bin/bash /home/raspberry/routine_butler/rpi_on_boot.sh > /dev/null 2>&1 &
    ```

Hints:

- The `> /dev/null 2>&1 &` part is to make sure that the script runs in the background and does not block the boot process.
- Always use absolute file names in the invoked bash script.

## Experimental

```bash
[Unit]
Description=Routine Butler Python App
After=network.target

[Service]
User=raspberry
WorkingDirectory=/home/raspberry/routine-butler
Environment=DISPLAY=:0
Environment=PULSE_SERVER=/run/user/1000/pulse/native
ExecStart=/usr/bin/python3 run.py --single-user
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
