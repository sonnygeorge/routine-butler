#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

current_dir=$(basename "$PWD")
echo "Running rpi_startup.sh from current directory: '$current_dir'"

## Make sure the current directory's name is "routine-butler"
if [ "$current_dir" != "routine-butler" ]; then
  echo "Error: This startup script must run from the routine_butler directory."
  exit 1
fi

## Check and activate the virtual environment
venv_dir="venv"
if [ ! -d "$venv_dir" ]; then
  echo "Error: Virtual environment directory '$venv_dir' not found. Please create or verify the virtual environment."
  exit 1
fi

echo "Activating virtual environment..."
source "$venv_dir/bin/activate"

## Git pull latest version
echo "Updating with the latest version..."
git_status=$(git status --porcelain)
if [ -n "$git_status" ]; then
  echo "Error: Local changes exist. Please commit or discard changes before running 'git pull'."
  exit 1
fi

git pull

## Set RPi volume
# Function to set system volume
set_system_volume() {
  echo "Attempting to set volume..."
  amixer set PCM -- 60%
}

if ! set_system_volume; then
  echo "Error: Failed to set the volume with 'amixer set PCM -- 60%' command."
fi

## Start RoutineButler
# Function to execute run.py
start_routine_butler() {
  echo "Attempting to start RoutineButler in single-user mode..."
  python3 run.py --single-user
}

if ! start_routine_butler; then
  echo "Error: RoutineButler failed to start. Attempting to install dependencies..."
  pip3 install -r requirements.txt
  echo "Re-attempting to start RoutineButler in single-user mode..."
  if ! start_routine_butler; then
    echo "Error: Failed to start RoutineButler even after installing dependencies."
    exit 1
  fi
fi

## Open Chromium in kiosk mode
echo "Opening Chromium in kiosk mode..."
chromium-browser --kiosk http://127.0.0.1:8080
