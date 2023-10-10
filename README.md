# 🎩✨ RoutineButler

## ℹ️ Overview

**RoutineButler** is an application designed to run in "kiosk-style" on a Raspberry Pi 🥧 connected to an LCD touchscreen interface 📺 and an electro-mechanically operated lockbox 📦. The app's primary purpose is to manage and notify users about daily routines 🏋️‍♂️, rewarding them with incentives (such as unlocking the lockbox) upon successful completion.

Here is a picture of my current setup which I am actively using as my morning and evening alarm clock:

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## 🏃👞 Setup Instructions

### 1. Flash Raspberry Pi OS

Flash the latest version of **32-bit** [Raspberry Pi OS Lite](https://www.raspberrypi.org/software/operating-systems/) onto an SD card and boot up the Raspberry Pi.

### 2. Make sure system is up-to-date

After configuring the Raspberry Pi with language, timezone, and internet, make sure the system is up-to-date with:

```bash
sudo apt update
sudo apt upgrade
```

### 2. Clone Repo

Clone the repo with:

```bash
git clone https://github.com/sonnygeorge/routine-butler.git
```

### 3. Change the system's python version to 3.11

Use [this](https://github.com/tvdsluijs/sh-python-installer) tool to change the system's python version to 3.11.

```bash
wget -qO - https://raw.githubusercontent.com/tvdsluijs/sh-python-installer/main/python.sh | sudo bash -s 3.11.0
```

## Run on boot

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
