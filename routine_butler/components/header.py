from datetime import datetime

from nicegui import ui

from routine_butler.components.primitives import SVG
from routine_butler.constants import (
    ABS_PROGRAM_SVG_PATH,
    ABS_ROUTINE_SVG_PATH,
    HDR,
    PagePath,
)


class HeaderClock(ui.column):
    def __init__(self, *args, **kwargs):
        def update_time_and_date_labels():
            time_label.set_text(datetime.now().strftime("%H:%M:%S"))
            date_label.set_text(datetime.now().strftime("%b %d, %Y"))

        super().__init__(*args, **kwargs)

        self.classes("-space-y-1 gap-0 items-center")
        with self:
            time_label = ui.label().style(f"font-size: {HDR.TIME_SIZE}")
            time_label.classes("items-center")
            date_label = ui.label().style(f"font-size: {HDR.DATE_SIZE}")
            date_label.classes("items-center")
            ui.timer(0.1, update_time_and_date_labels)


class Header(ui.header):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("justify-between items-center bg-secondary")
        self.props("elevated")

        with self:
            left_content = ui.row().style("align-items: center")
            right_content = ui.row().style("align-items: center")
            with left_content:
                routines_button = ui.button().style(HDR.BUTTON_STYLE)
                with routines_button:
                    SVG(ABS_ROUTINE_SVG_PATH, HDR.RTN_SVG_SIZE, color="white")
                ui.label(HDR.APP_NAME).style(f"font-size: {HDR.APP_NAME_SIZE}")
            with right_content:
                HeaderClock()
                programs_button = ui.button().style(HDR.BUTTON_STYLE)
                with programs_button:
                    SVG(
                        ABS_PROGRAM_SVG_PATH, HDR.PRGRM_SVG_SIZE, color="white"
                    )

        routines_button.on("click", lambda: ui.open(PagePath.SET_ROUTINES))
        programs_button.on("click", lambda: ui.open(PagePath.SET_PROGRAMS))
