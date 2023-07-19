#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

repo_dir_path="/home/raspberry/routine-butler"
venv_dir_path="/home/raspberry/routine-butler/venv"
run_python_script_path="python3 run.py --single-user"


## Check and activate the virtual environment
if [ ! -d "$venv_dir_path" ]; then
  echo "Error: Virtual environment directory '$venv_dir_path' not found."
  exit 1
fi

echo "Activating virtual environment..."
source "$venv_dir/bin/activate"

## Change directory to the routine-butler repository
navigate_to_routine_butler_repository() {
  cd "$repo_dir_path"
}

if not navigate_to_routine_butler_repository; then
  echo "Error: Failed to navigate to '$repo_dir_path'"
  exit 1
fi

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
  python3 "$run_python_script_path" --single-user
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