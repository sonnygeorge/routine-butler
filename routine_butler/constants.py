import os
from enum import StrEnum

ABS_CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
ABS_ROUTINE_SVG_PATH = os.path.join(ABS_CURRENT_DIR, "assets/routine-icon.svg")
ABS_PROGRAM_SVG_PATH = os.path.join(ABS_CURRENT_DIR, "assets/program-icon.svg")
ABS_REWARD_SVG_PATH = os.path.join(ABS_CURRENT_DIR, "assets/reward-icon.svg")

ABS_PLUGINS_DIR_PATH = os.path.join(ABS_CURRENT_DIR, "plugins")

ABS_MP3_PATH = os.path.join(ABS_CURRENT_DIR, "assets/alarm_sound.mp3")

CONSTANT_RING_INTERVAL = 1
PERIODIC_RING_INTERVAL = 60


class PagePath(StrEnum):
    HOME = "/"
    DO_ROUTINE = "/do-routine"
    SET_ROUTINES = "/configure-routines"
    SET_PROGRAMS = "/configure-programs"
    LOGIN = "/login"
    RING = "/ring"


class ICON_STRS:  # Quasar material icons
    # currently using
    add = "add"
    delete = "cancel"
    play = "play_arrow"
    save = "save"
    down_arrow = "arrow_downward"
    up_arrow = "arrow_upward"
    alarm = "alarm"
    # ... maybe use some of these later?
    app = "token"
    settings = "settings"
    config = "settings_input_component"
    sidebar = "menu"
    add_alarm = "alarm_add"
    gdrive = "add_to_drive"
    lock = "lock_outline"
    unlock = "lock_open"
    start = "not_started"
    person = "accessibility_new"
    panels = "dashboard"
    check = "done"


class CLR_CODES:
    # old
    black = "#0a0908"
    dark_gray = "#22333b"
    gray = "#3c4858"
    beige = "#eae0d5"
    dark_green = "#3e5641"
    # currently using
    primary = "#2e5cb8"  # buttons
    secondary = "#5c85d6"  # header
    accent = "#2399cf"
    positive = "#23cf59"
    negative = "#cf2342"
    info = "#85d2ed"
    warning = "#d6dd54"


# for throttling events that would otherwise fire too often
THROTTLE_SECONDS = 0.5


# a quick script to display ICON_STRS and CLR_CODES in a nicegui app
if __name__ in {"__main__", "__mp_main__"}:
    from nicegui import ui

    def get_values(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith("__")]

    with ui.row().classes("place-content-center"):
        for icon in get_values(ICON_STRS):
            ui.icon(icon)

    with ui.row().classes("place-content-center"):
        for color in get_values(CLR_CODES):
            c = ui.card().style(f"background-color: {color};")

    ui.run()
