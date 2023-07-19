#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

REPO_DIR_PATH="/home/raspberry/routine-butler"
VENV_DIR_PATH="/home/raspberry/routine-butler/venv"

## Change directory to the routine-butler repository
navigate_to_routine_butler_repository() {
  cd "$REPO_DIR_PATH"
}

if not navigate_to_routine_butler_repository; then
  echo "Error: Failed to navigate to '$REPO_DIR_PATH'"
  exit 1
fi

## Check and activate the virtual environment
if [ ! -d "$VENV_DIR_PATH" ]; then
  echo "Error: Virtual environment directory '$VENV_DIR_PATH' not found."
  exit 1
fi

echo "Activating virtual environment..."
source "$VENV_DIR_PATH/bin/activate"


## Attempt to git pull latest version
echo "Updating with the latest version..."
git_status=$(git status --porcelain)
if [ -n "$git_status" ]; then
  echo "Warning: Local changes exist. Please commit or discard changes before running 'git pull'."
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
run_routine_butler() {
  echo "Attempting to run RoutineButler in single-user mode..."
  python3 run.py --single-user
}

if ! run_routine_butler; then
  echo "Error: RoutineButler failed to start. Attempting to install dependencies..."
  pip3 install -r requirements.txt
  echo "Re-attempting to start RoutineButler in single-user mode..."
  if ! run_routine_butler; then
    echo "Error: Failed to start RoutineButler even after installing dependencies."
    exit 1
  fi
fi