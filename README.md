# 🎩✨ RoutineButler

## ℹ️ Overview

**RoutineButler** is an application designed to run in "kiosk-style" on a Raspberry Pi 🥧 connected to an LCD touchscreen interface 📺 and an electro-mechanically operated lockbox 📦. The app's primary purpose is to manage and notify users about daily routines 🏋️‍♂️, rewarding them with incentives (such as unlocking the lockbox) upon successful completion.

Here is a picture of my current setup which I am actively using as my morning and evening alarm clock:

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## 🏃👞 Running Kiosk-Style "On Boot" on a RaspberryPi

To run RoutineButler automatically on boot, I am using `systemd`, a service manager for Linux systems that provides a way to manage background processes (including running them on boot).

Here are the steps I took to set things up:

1. **Systemd Service File**: Create a systemd service file named `/etc/systemd/system/routine-butler.service` with the following contents:

    ```bash
    [Unit]
    Description=Routine Butler Python App
    After=network.target  # specifies that the service should start after the network is available

    [Service]
    User=raspberry  # user to run the service as
    WorkingDirectory=/home/raspberry/routine-butler  # path to the repo
    Environment=DISPLAY=:0  # display number (0 is used since my setup has only one display)
    Environment=PULSE_SERVER=/run/user/1000/pulse/native  # number is user-specific... 1000 is the common, default user-value
    ExecStart=bash startup.sh  # script in the repo that runs necessary commands to start the app on Raspberry Pi
    Restart=on-failure  # restart the service if it fails

    [Install]
    WantedBy=multi-user.target  # specifies that the service will be enabled during the multi-user system boot process
    ```

2. **Enable the Service**: After creating the service file, enable it using the following command:

    ```bash
    sudo systemctl enable routine-butler.service
    ```

**Hint**: To check the status and logs of the service, use `sudo systemctl status routine-butler.service` and `sudo journalctl -u routine-butler.service`, respectively.
