# RoutineButler

**RoutineButler** is an app that is designed to be run "kiosk-style" on a RaspberryPi 🥧 connected to:

- 📺 an LCD touchscreen interface
- 📦 an electro-mechanically operated lockbox

Its purpose is to alart and administer "routines" 🏋️‍♂️  to users in exchange for incentives (such as unlocking whatever they may have put in the lockbox).

Here is a picture of my current setup which I am actively using as my morning and evening alarm clock:

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## Running RoutineButler Kiosk-Style "On Boot" on a RaspberryPi

What is currently working for me is the following:

1. Adding the following systemd service file (`/etc/systemd/system/routine-butler.service`):

    ```bash
    [Unit]
    Description=Routine Butler Python App
    After=network.target

    [Service]
    User=raspberry
    WorkingDirectory=/home/raspberry/routine-butler  # path to the repo
    Environment=DISPLAY=:0
    Environment=PULSE_SERVER=/run/user/1000/pulse/native
    ExecStart=bash startup.sh
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

2. Enabling it with:

    ```bash
    sudo systemctl enable routine-butler.service
    ```

Hint: Check the status and logs of the service with:

```bash
sudo systemctl status routine-butler.service
```

and

```bash
sudo journalctl -u routine-butler.service
```
