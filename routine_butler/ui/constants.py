"""A central location for stylistic UI constants for quick iteration/experimentation"""
import os

_CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
ABS_ROUTINE_SVG_PATH = os.path.join(_CURRENT_DIR, "../assets/routine-icon.svg")
ABS_PROGRAM_SVG_PATH = os.path.join(_CURRENT_DIR, "../assets/program-icon.svg")
ABS_REWARD_SVG_PATH = os.path.join(_CURRENT_DIR, "../assets/reward-icon.svg")


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


# header
HDR_BUTTON_STYLE = "height: 45px; width: 45px;"
HDR_APP_NAME = "RoutineButler"
HDR_APP_NAME_SIZE = "1.9rem"
HDR_RTN_SVG_SIZE: int = 30
HDR_PRGRM_SVG_SIZE: int = 25
HDR_TIME_SIZE = "1.1rem"
HDR_DATE_SIZE = ".7rem"

# sidebars
PROGRAM_SVG_SIZE: int = 21
ROUTINE_SVG_SIZE: int = 28
REWARD_SVG_SIZE: int = 17

SDBR_V_SPACE: int = 4
SDBR_BREAKPOINT: str = "0"
SDBR_DFLT_ROW_CLS: str = "justify-evenly items-center w-full px-4 pt-4"
SDBR_DFLT_INPUT_PRPS: str = "standout dense"

# routines sidebar
RTNS_SDBR_WIDTH: str = "540"

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
