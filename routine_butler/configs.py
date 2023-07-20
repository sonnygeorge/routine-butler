import os
from enum import StrEnum

CURRENT_DIR_PATH: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR_PATH: str = os.path.dirname(CURRENT_DIR_PATH)

TEST_DB_PATH = os.path.join(PROJECT_DIR_PATH, "test_db.sqlite")
DB_PATH = os.path.join(PROJECT_DIR_PATH, "db.sqlite")
LOG_FILE_PATH = os.path.join(PROJECT_DIR_PATH, "app.log")
ROUTINE_SVG_PATH = os.path.join(CURRENT_DIR_PATH, "assets/routine-icon.svg")
PROGRAM_SVG_PATH = os.path.join(CURRENT_DIR_PATH, "assets/program-icon.svg")
REWARD_SVG_PATH = os.path.join(CURRENT_DIR_PATH, "assets/reward-icon.svg")
APP_LOGO_SVG_PATH = os.path.join(CURRENT_DIR_PATH, "assets/app-logo.svg")
ALARM_WAV_PATH = os.path.join(CURRENT_DIR_PATH, "assets/alarm_sound.wav")

PLUGINS_DIR_PATH = os.path.join(CURRENT_DIR_PATH, "plugins")
PLUGINS_IMPORT_STR = "routine_butler.plugins.{module}"

GDRIVE_FOLDER_NAME = "Routine Butler"
GDRIVE_CREDENTIALS_PATH = os.path.join(
    CURRENT_DIR_PATH, "gdrive_credentials.json"
)

TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"
DB_URL = f"sqlite:///{DB_PATH}"
TEST_USER_USERNAME = "test"
SINGLE_USER_MODE_USERNAME = "CVxaUwC0Lkg7znaOMtwQP"

CONSTANT_RING_INTERVAL = 1  # Time between noises for "constant" ringing
PERIODIC_RING_INTERVAL = 60  # Time between noises for "periodic" ringing

N_SECONDS_BW_RING_CHECKS = 1  # Check every n secs for alarm that should ring

BINDING_REFRESH_INTERVAL_SECONDS = 0.3  # Higher is more cpu friendly
THROTTLE_SECONDS = 0.7  # For event handlers that would otherwise be spammed


class PagePath(StrEnum):
    HOME = "/"
    DO_ROUTINE = "/do-routine"
    SET_ROUTINES = "/configure-routines"
    SET_PROGRAMS = "/configure-programs"
    LOGIN = "/login"
    RING = "/ring"


PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW = [
    PagePath.DO_ROUTINE,
    PagePath.RING,
    PagePath.LOGIN,
]


class ICON_STRS:  # Quasar material icons
    add = "add"
    delete = "cancel"
    play = "play_arrow"
    save = "save"
    down_arrow = "arrow_downward"
    up_arrow = "arrow_upward"
    alarm = "alarm"
    dark_mode = "dark_mode"
    light_mode = "light_mode"
    # Maybe use some of these later?
    # app = "token"
    # settings = "settings"
    # config = "settings_input_component"
    # sidebar = "menu"
    # add_alarm = "alarm_add"
    # gdrive = "add_to_drive"
    # lock = "lock_outline"
    # unlock = "lock_open"
    # start = "not_started"
    # person = "accessibility_new"
    # panels = "dashboard"
    # check = "done"


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
