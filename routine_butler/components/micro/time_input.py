from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS


def time_input(value: str) -> ui.time:
    time_input = ui.input(value=value)
    time_input.props(DFLT_INPUT_PRPS).classes("w-full")
    with time_input as input:
        with input.add_slot("append"):
            icon = ui.icon("access_time").classes("cursor-pointer")
            icon.on("click", lambda: menu.open())
            with ui.menu() as menu:
                time_ = ui.time()
                time_.bind_value(time_input)
    return time_
