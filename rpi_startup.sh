#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

## Change directory to the routine-butler repository
navigate_to_routine_butler_repository() {
  cd /home/raspberry/routine-butler
}

if not navigate_to_routine_butler_repository; then
  echo "Error: Failed to navigate to the /home/raspberry/routine-butler."
  exit 1
fi

echo "Running rpi_startup.sh from the routine-butler repository directory."

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
set_system_volume() {
  echo "Attempting to set volume..."
  amixer set PCM -- 60%
}

if ! set_system_volume; then
  echo "Error: Failed to set the volume with 'amixer set PCM -- 60%' command."
fi

## Start RoutineButler
start_routine_butler_process() {
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
}

echo "Spawning RoutineButler process..."
nohup start_routine_butler_process > start_routine_butler_process.log 2>&1 &

## Start Chromium in kiosk mode
echo "Spawning Chromium process..."
nohup chromium-browser --kiosk http://127.0.0.1:8080 > chromium.log 2>&1 &

