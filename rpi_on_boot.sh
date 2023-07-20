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
chromium-browser http://127.0.0.1:8080

# Use xdotool to send F11 key to Chromium, which will trigger full-screen mode
DISPLAY=:0 xdotool key F11