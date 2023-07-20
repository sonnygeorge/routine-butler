#!/bin/bash
# chains the necessary commands for running RoutineButler on a Raspberry Pi

REPO_DIR_PATH="/home/raspberry/routine-butler"
VENV_DIR_PATH="/home/raspberry/routine-butler/venv"
PYTHON_SCRIPT_PATH="/home/raspberry/routine-butler/run.py"

# # Set up environment variables
# export DISPLAY=:0
# export PULSE_SERVER=/run/user/1000/pulse/native

# ## Change directory to the routine-butler repository
# navigate_to_routine_butler_repository() {
#   cd "$REPO_DIR_PATH"
# }

# if not navigate_to_routine_butler_repository; then  # FIXME: remove
#   echo "Error: Failed to navigate to '$REPO_DIR_PATH'"
#   exit 1
# fi

## Check and activate the virtual environment
if [ ! -d "$VENV_DIR_PATH" ]; then
  echo "Error: Virtual environment directory '$VENV_DIR_PATH' not found."
  exit 1
fi

echo "Activating virtual environment..."
source "$VENV_DIR_PATH/bin/activate"

# ## Attempt to git pull latest version of RoutineButler
# echo "Updating with the latest version of RoutineButler..."
# git_status=$(git -C "$REPO_DIR_PATH" status --porcelain)
# if [ -n "$git_status" ]; then
#   echo "Warning: Local changes exist. Please commit or discard changes before running 'git pull'."
# fi

# git -C "$REPO_DIR_PATH" pull

# ## Set RPi volume
# set_system_volume() {
#   echo "Attempting to set volume..."
#   amixer set PCM -- 60%
# }

# if ! set_system_volume; then
#   echo "Error: Failed to set the volume with 'amixer set PCM -- 60%' command."
# fi

echo "Attempting to run RoutineButler in single-user mode..."
python3 "$PYTHON_SCRIPT_PATH" --single-user &

sleep 5

# Start Chromium in kiosk mode
chromium-browser --kiosk http://127.0.0.1:8080

# ## Start RoutineButler
# run_routine_butler() {
#   echo "Attempting to run RoutineButler in single-user mode..."
#   python3 "$PYTHON_SCRIPT_PATH" --single-user
# }

# if ! run_routine_butler; then
#   echo "Error: RoutineButler failed to start. Attempting to install dependencies..."
#   pip3 install -r requirements.txt  # FIXME: absolute path
#   echo "Re-attempting to start RoutineButler in single-user mode..."
#   if ! run_routine_butler; then
#     echo "Error: Failed to start RoutineButler even after installing dependencies."
#     exit 1
#   fi
# fi