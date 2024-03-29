import os
from enum import StrEnum
from functools import partial
from typing import Type

from routine_butler.utils.cloud_storage_bucket import (
    CloudStorageBucket,
    GoogleDriveFolder,
)
from routine_butler.utils.dataframe_like import DataframeLike, GoogleSheet
from routine_butler.utils.google.g_suite_credentials_manager import (
    G_Suite_Credentials_Manager,
)

MAIN_SERVER_PORT: int = 8080
TEMP_EXTRA_SERVER_PORT: int = 8081

# Paths

CURRENT_DIR_PATH: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR_PATH: str = os.path.dirname(CURRENT_DIR_PATH)

TEST_DB_PATH = os.path.join(PROJECT_DIR_PATH, "test_db.sqlite")
DB_PATH = os.path.join(PROJECT_DIR_PATH, "db.sqlite")
LOG_FILE_PATH = os.path.join(PROJECT_DIR_PATH, "app.log")

PATH_TO_ASSETS = os.path.join(CURRENT_DIR_PATH, "assets")

ROUTINE_SVG_PATH = os.path.join(PATH_TO_ASSETS, "routine-icon.svg")
PROGRAM_SVG_PATH = os.path.join(PATH_TO_ASSETS, "program-icon.svg")
REWARD_SVG_PATH = os.path.join(PATH_TO_ASSETS, "reward-icon.svg")
APP_LOGO_SVG_PATH = os.path.join(PATH_TO_ASSETS, "app-logo.svg")
CURLY_BRACKET_SVG_PATH = os.path.join(PATH_TO_ASSETS, "curly-bracket.svg")
ALARM_WAV_PATH = os.path.join(PATH_TO_ASSETS, "alarm_sound.wav")

PLUGINS_DIR_PATH = os.path.join(CURRENT_DIR_PATH, "plugins")
PLUGINS_IMPORT_STR = "routine_butler.plugins.{module}"

# Page paths


class PagePath(StrEnum):
    HOME = "/"
    DO_ROUTINE = "/do-routine"
    SET_ROUTINES = "/configure-routines"
    SET_PROGRAMS = "/configure-programs"
    LOGIN = "/login"
    RING = "/ring"
    YOUTUBE = "/youtube"
    ORATED_ENTRY = "/orated-entry"


# Playback rates for YouTube videos


class PlaybackRate(StrEnum):
    PLAYBACK_RATE_NORMAL = "1.0"
    PLAYBACK_RATE_125_PERCENT = "1.25"
    PLAYBACK_RATE_150_PERCENT = "1.5"
    PLAYBACK_RATE_175_PERCENT = "1.75"
    PLAYBACK_RATE_200_PERCENT = "2.0"


# G Suite credentials manager

G_SUITE_CREDENTIALS_PATH = os.path.join(
    PROJECT_DIR_PATH, "google_credentials.json"
)
G_SUITE_CREDENTIALS_MANAGER = G_Suite_Credentials_Manager(
    G_SUITE_CREDENTIALS_PATH,
    MAIN_SERVER_PORT,
    TEMP_EXTRA_SERVER_PORT,
    PagePath.DO_ROUTINE,
)

G_DRIVE_STORAGE_FOLDER_NAME = "Routine Butler"

# Globally-used CloudStorageBucket object

STORAGE_BUCKET: CloudStorageBucket = GoogleDriveFolder(
    G_DRIVE_STORAGE_FOLDER_NAME, G_SUITE_CREDENTIALS_MANAGER
)

# Folder within the root of storage bucket where flashcard sheets are stored

FLASHCARDS_FOLDER_NAME = "flashcards"

# Folder within the root of storage bucket where YouTubeVideo sheets are stored

YOUTUBE_VIDEO_FOLDER_NAME = "youtube_video"


# Folder within the root of storage bucket where DB backups are stored

DB_BACKUP_FOLDER_NAME = "db_backups"


# Gloablly-used DataframeLike type
# NOTE: partial is used here to maintain the consistency of the constructor interface
# since GoogleSheet uniquely requires root_folder_name and credentials_manager args

DATAFRAME_LIKE: Type[DataframeLike] = partial(
    GoogleSheet,
    root_folder_name=G_DRIVE_STORAGE_FOLDER_NAME,
    credentials_manager=G_SUITE_CREDENTIALS_MANAGER,
)

# Database

TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"
DB_URL = f"sqlite:///{DB_PATH}"
TEST_USER_USERNAME = "test"
SINGLE_USER_MODE_USERNAME = "CVxaUwC0Lkg7znaOMtwQP"

# Time Constants

CONSTANT_RING_INTERVAL = 1  # Time between noises for "constant" ringing
PERIODIC_RING_INTERVAL = 60  # Time between noises for "periodic" ringing

N_SECONDS_BW_RING_CHECKS = 1  # Check every n secs for alarm that should ring
N_SECONDS_BW_HOURLY_TASK_CHECKS = 5 * 60  # Check every n secs if new hour

BINDING_REFRESH_INTERVAL_SECONDS = 0.3  # Higher is more cpu friendly
THROTTLE_SECONDS = 0.7  # For event handlers that would otherwise be spammed


class _time_estimation:
    READING_SPEED_CHARS_PER_SECOND = 16
    CHECK_WAIT_SECOND_MULTIPLIER = 1.5


TIME_ESTIMATION = _time_estimation()


PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW = [
    PagePath.DO_ROUTINE,
    PagePath.RING,
    PagePath.LOGIN,
    PagePath.YOUTUBE,
    PagePath.ORATED_ENTRY,
]


class ICON_STRS:  # Quasar material icons
    add = "add"
    delete = "delete"
    play = "play_arrow"
    save = "save"
    down_arrow = "arrow_downward"
    up_arrow = "arrow_upward"
    alarm = "alarm"
    dark_mode = "dark_mode"
    light_mode = "light_mode"
    g_suite = "add_to_drive"
    loading = "pending"
    check = "check"
    pause = "pause"


class CLR_CODES:
    primary = "#2a5cbf"
    secondary = "#5c85d6"
    accent = "#2399cf"
    positive = "#23cf59"
    negative = "#cf2342"
    info = "#85d2ed"
    warning = "#d6dd54"


def visualize_icons_and_colors():
    """A quick script to visualize all the icons and colors in the above objects"""
    from nicegui import ui

    def get_values(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith("__")]

    with ui.row().classes("place-content-center"):
        for icon in get_values(ICON_STRS):
            ui.icon(icon)
    with ui.row().classes("place-content-center"):
        for color in get_values(CLR_CODES):
            ui.card().style(f"background-color: {color};")
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    visualize_icons_and_colors()
