import os
from datetime import datetime

from nicegui import ui

from routine_butler.ui.primitives.svg import SVG
from routine_butler.ui.constants import HDR_APP_NAME as APP_NAME
from routine_butler.ui.constants import HDR_APP_NAME_SIZE as APP_NAME_SIZE
from routine_butler.ui.constants import HDR_BUTTON_STYLE as BUTTON_STYLE
from routine_butler.ui.constants import HDR_DATE_SIZE as DATE_SIZE
from routine_butler.ui.constants import HDR_PRGRM_SVG_SIZE as PROGRAMS_SVG_SIZE
from routine_butler.ui.constants import HDR_RTN_SVG_SIZE as ROUTINES_SVG_SIZE
from routine_butler.ui.constants import HDR_TIME_SIZE as TIME_SIZE


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")


# TODO: could be functions?


class Clock(ui.column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.classes("-space-y-1 gap-0 items-center")

        with self:
            # time
            time = ui.label().style(f"font-size: {TIME_SIZE}")
            time.classes("items-center")
            set_time = lambda: time.set_text(
                datetime.now().strftime("%H:%M:%S")
            )
            ui.timer(0.1, set_time)

            # date
            date = ui.label().style(f"font-size: {DATE_SIZE}")
            date.classes("items-center")
            set_date = lambda: date.set_text(
                datetime.now().strftime("%b %d, %Y")
            )
            ui.timer(1.0, set_date)


class Header(ui.header):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("justify-between items-center bg-secondary")
        self.props("elevated")

        with self:
            left_content = ui.row().style("align-items: center")
            right_content = ui.row().style("align-items: center")
            with left_content:
                # routines button
                self.routines_button = ui.button()
                self.routines_button.style(BUTTON_STYLE)
                with self.routines_button:
                    SVG(ROUTINE_SVG_FPATH, ROUTINES_SVG_SIZE, color="white")
                # app name
                ui.label(APP_NAME).style(f"font-size: {APP_NAME_SIZE}")
            with right_content:
                # clock
                Clock()
                # programs button
                self.programs_button = ui.button()
                self.programs_button.style(BUTTON_STYLE)
                with self.programs_button:
                    SVG(PROGRAM_SVG_FPATH, PROGRAMS_SVG_SIZE, color="white")
