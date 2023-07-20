#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

echo "Adjusting system volume to 60%..."
amixer set PCM -- 60%

echo "Attempting git pull..."
git pull

echo "Activating virtual environment..."
source venv/bin/activate

echo "Attempting to run RoutineButler in single-user mode..."
python3 run.py --single-user &

echo "Waiting for RoutineButler to start..."
sleep 8

echo "Starting Chromium in kiosk mode..."

xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

chromium-browser --noerrdialogs --disable-infobars --kiosk http://127.0.0.1:8080