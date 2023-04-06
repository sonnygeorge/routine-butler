import os
from datetime import datetime

from nicegui import ui

from routine_butler.elements.primitives.svg import SVG
from routine_butler.utils.constants import clrs

BUTTON_STYLE = "height: 45px; width: 45px;"
APP_NAME = "RoutineButler"
APP_NAME_SIZE = "1.9rem"
ROUTINES_SVG_SIZE: int = 30
PROGRAMS_SVG_SIZE: int = 25
LOGO_SIZE = "2.6rem"
TIME_SIZE = "1.1rem"
DATE_SIZE = ".7rem"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")


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
