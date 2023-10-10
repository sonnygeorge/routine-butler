# 🎩✨ RoutineButler

## ℹ️ Overview

**RoutineButler** is an application designed to run in "kiosk-style" on a Raspberry Pi 🥧 connected to an LCD touchscreen interface 📺 and an electro-mechanically operated lockbox 📦. The app's primary purpose is to manage and notify users about daily routines 🏋️‍♂️, rewarding them with incentives (such as unlocking the lockbox) upon successful completion.

Here is a picture of my current setup which I am actively using as my morning and evening alarm clock:

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## 🏃 Setup Instructions

### 1. Flash Raspberry Pi OS

Flash the latest version of **32-bit** [Raspberry Pi OS Lite](https://www.raspberrypi.org/software/operating-systems/) onto an SD card and boot up the Raspberry Pi.

### 2. Make sure system is up-to-date

After configuring the Raspberry Pi with language, timezone, and internet, make sure the system is up-to-date with:

```bash
sudo apt update
sudo apt upgrade
```

### 3. Clone Repo

Clone the repo with:

```bash
git clone https://github.com/sonnygeorge/routine-butler.git
```

### 4. Change the system's python version to 3.11

Use [this](https://github.com/tvdsluijs/sh-python-installer) tool to change the system's python version to 3.11 with:

```bash
wget -qO - https://raw.githubusercontent.com/tvdsluijs/sh-python-installer/main/python.sh | sudo bash -s 3.11.0
```

### 5. Change audio output device

While the above command is running, use `sudo raspi-config` and configure the usb audio device as the output device.

Verify that this worked by opening a YouTube video and checking that the audio is playing through the correct device.

### 6. Install matchbox-keyboard

First, install matchbox-keyboard with:

```bash
sudo apt-get install matchbox-keyboard
```

### 7. Install emojis

Next, install emojis with:

```bash
sudo apt install fonts-noto-color-emoji
```

### 8. Install flac

Next, install flac with:

```bash
sudo apt-get install flac
```

### 8. Create venv and install dependencies

First, verify that the system's Python version is 3.11 with:

```bash
python --version
```

Then create a virtual environment and install dependencies with:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If `pyaudio` fails to install, try the following:

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### 9. Verify app's audio and keyboard functionality

First, verify that the app's audio is working by running (make sure venv is activated):

```bash
python test_audio_and_keyboard.py
```

### 10. Create a systemd service to run the app on startup and enable the service

In order to run the app on startup, we will create a systemd service file and enable it.

Create a systemd service file named `/etc/systemd/system/routine-butler.service` with:

```bash
sudo nano /etc/systemd/system/routine-butler.service
```

Copy and paste the following contents into the file:

```bash
[Unit]
Description=Routine Butler Python App
After=network.target

[Service]
User=raspberry
WorkingDirectory=/home/raspberry/routine-butler
Environment=DISPLAY=:0
Environment=PULSE_SERVER=/run/user/1000/pulse/native
ExecStart=bash startup.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

After creating the service file, enable it using the following command:

```bash
sudo systemctl enable routine-butler.service
```

**Hint**: To check the status and logs of the service, use `sudo systemctl status routine-butler.service` and `sudo journalctl -u routine-butler.service`, respectively.
