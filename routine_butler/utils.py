import array
import datetime
import importlib
import os
import platform
import subprocess
import wave
from typing import TYPE_CHECKING, Dict, Optional, Protocol, Tuple, Type

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.constants import ABS_PLUGINS_DIR_PATH, CLR_CODES, PagePath

if TYPE_CHECKING:
    from routine_butler.models.routine import Alarm, Routine
    from routine_butler.models.user import User
    from routine_butler.state import State


def apply_color_theme():
    ui.colors(
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )


def redirect_to_page(
    page_path: PagePath, n_seconds_before_redirect: float = 0.1
):
    def _redirect_to_page():
        ui.open(page_path)

    ui.timer(n_seconds_before_redirect, _redirect_to_page, once=True)


def redirect_if_user_is_none(user: "User"):
    if user is None:
        redirect_to_page(PagePath.LOGIN)


def move_up_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move - 1, list_.pop(idx_to_move))


def move_down_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move + 1, list_.pop(idx_to_move))


def snake_to_upper_camel(snake_case_str: str) -> str:
    return "".join(word.capitalize() for word in snake_case_str.split("_"))


class ProgramPlugin(Protocol):
    """Protocol for program types to implement"""

    def administer(self, on_complete: callable):
        ...

    def dict(self) -> dict:
        ...


def dynamically_get_plugins() -> Dict[str, Type[ProgramPlugin]]:
    """Dynamically loads all program types from the programs directory"""
    program_types = {}
    for file_name in os.listdir(ABS_PLUGINS_DIR_PATH):
        if not file_name.startswith("_") and file_name.endswith(".py"):
            module_name = file_name[:-3]
            module = importlib.import_module(
                f"routine_butler.plugins.{module_name}"
            )
            class_name = snake_to_upper_camel(module_name)
            program_types[class_name] = getattr(module, class_name)
    return program_types


# FIXME: make method of Alarm
def calculate_seconds_until_alarm(alarm: "Alarm") -> int:
    now = datetime.datetime.now()
    alarm_time = datetime.datetime.strptime(alarm.time, "%H:%M").time()
    alarm_datetime = datetime.datetime.combine(now.date(), alarm_time)
    return int((alarm_datetime - now).total_seconds())


SECONDS_IN_DAY = 24 * 60 * 60


def get_next_alarm(
    user: "User", engine: Engine
) -> Tuple[Optional["Alarm"], Optional["Routine"]]:
    next_alarm = None
    next_alarms_routine = None
    routines = user.get_routines(engine)
    min_seconds_remaining = SECONDS_IN_DAY  # no alarm is more than day away
    for routine in routines:
        for alarm in routine.alarms:
            if alarm.is_enabled:
                seconds_remaining = calculate_seconds_until_alarm(alarm)
                if seconds_remaining < 0:
                    seconds_remaining += SECONDS_IN_DAY
                if seconds_remaining < min_seconds_remaining:
                    min_seconds_remaining = seconds_remaining
                    next_alarm = alarm
                    next_alarms_routine = routine
    return next_alarm, next_alarms_routine


# FIXME: make method of Alarm
def should_ring(alarm: "Alarm") -> bool:
    seconds_until_alarm = calculate_seconds_until_alarm(alarm)
    return -60 < seconds_until_alarm <= 0  # if time passed w/in last minute


def check_for_alarm_to_ring(state: "State") -> None:
    if state.next_alarm is not None and should_ring(state.next_alarm):
        state.next_alarm.ring()


def create_new_wav_given_volume_multiplier(
    input_file, output_file, volume_multiplier
) -> None:
    with wave.open(input_file, "rb") as wav_in:
        params = wav_in.getparams()
        audio_data = array.array("h", wav_in.readframes(wav_in.getnframes()))

    # Apply the volume multiplier to each audio sample
    adjusted_data = array.array(
        "h", (int(sample * volume_multiplier) for sample in audio_data)
    )

    with wave.open(output_file, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(adjusted_data.tobytes())


def play_wav(file_path: str) -> None:
    system = platform.system()
    if system == "Windows":
        command = [
            "powershell",
            f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()",
        ]
    elif system == "Darwin":
        command = ["afplay", file_path]
    elif system == "Linux":
        command = ["aplay", file_path]
    else:
        raise NotImplementedError(f"Unsupported os: {system}")
    subprocess.run(command)


def play_wav_with_volume_adjustment(
    file_path: str, volume: float = 1.0
) -> None:
    if volume < 0.0 or volume > 1.0:
        raise ValueError("Volume must be between 0.0 and 1.0")
    if volume != 1.0:
        temp_path = os.path.splitext(file_path)[0] + "-volume-adjusted.wav"
        create_new_wav_given_volume_multiplier(file_path, temp_path, volume)
        play_wav(temp_path)
        os.remove(temp_path)
    else:
        play_wav(file_path)


# define and add custom log level for database events
DB_LOG_LVL = "DB EVENT"
logger.level(DB_LOG_LVL, no=33, color="<magenta>")

# define and add custom log level for hardware events
HW_LOG_LVL = "HW EVENT"
logger.level(HW_LOG_LVL, no=34, color="<yellow>")


# Don't forget to change the default keyboard to keyboard-lq1.xml
# stackoverflow.com/questions/70574505/how-to-change-the-default-matchbox-keyboard-layout


def open_keyboard():
    subprocess.Popen(["matchbox-keyboard"])


def close_keyboard():
    subprocess.run(["killall", "matchbox-keyboard"])
