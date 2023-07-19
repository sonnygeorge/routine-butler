#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

# Get the current working directory's name
current_dir=$(basename "$PWD")
echo "Current directory: $current_dir"

echo "Running rpi_startup.sh from '$current_dir' dir"

# Check if the current directory's name is "mydir"
if [ "$current_dir" != "routine-butler" ]; then
  echo "Error: This startup script must run from the routine_butler directory."
  exit 1
fi

echo "Updating with latest version..."
git pull

echo "Setting volume..."
amixer set PCM -- 60%

echo "Starting RoutineButler in single-user mode..."
python3 run.py --single-user

echo "Opening chromium in kiosk mode..."
chromium-browser --kiosk http://127.0.0.1:8080