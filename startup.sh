#!/bin/bash
# Commands for running RoutineButler on a Raspberry Pi

echo "Adjusting system volume to 84%..."
amixer set Master -- 85%

echo "Activating virtual environment..."
source venv/bin/activate

echo "Attempting to run RoutineButler in single-user mode..."
python3.11 run.py --single-user &

echo "Waiting for RoutineButler to start..."
sleep 15

echo "Starting Chromium in kiosk mode..."

# Stop the screensaver function & desktop environment from interfering w/ display
xset s noblank
xset s off
xset -dpms
# Remove the mouse cursor from the display
unclutter -idle 0.5 -root &

chromium-browser --noerrdialogs --disable-infobars --kiosk http://127.0.0.1:8080
