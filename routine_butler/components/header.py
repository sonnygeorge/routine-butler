from datetime import datetime

from nicegui import ui

from routine_butler.components.primitives.svg import SVG
from routine_butler.constants import ABS_PROGRAM_SVG_PATH, ABS_ROUTINE_SVG_PATH
from routine_butler.constants import HDR_APP_NAME as APP_NAME
from routine_butler.constants import HDR_APP_NAME_SIZE as APP_NAME_SIZE
from routine_butler.constants import HDR_BUTTON_STYLE as BUTTON_STYLE
from routine_butler.constants import HDR_DATE_SIZE as DATE_SIZE
from routine_butler.constants import HDR_PRGRM_SVG_SIZE as PROGRAMS_SVG_SIZE
from routine_butler.constants import HDR_RTN_SVG_SIZE as ROUTINES_SVG_SIZE
from routine_butler.constants import HDR_TIME_SIZE as TIME_SIZE


class HeaderClock(ui.column):
    def __init__(self, *args, **kwargs):
        def update_time_and_date_labels():
            time_label.set_text(datetime.now().strftime("%H:%M:%S"))
            date_label.set_text(datetime.now().strftime("%b %d, %Y"))

        super().__init__(*args, **kwargs)

        self.classes("-space-y-1 gap-0 items-center")
        with self:
            time_label = ui.label().style(f"font-size: {TIME_SIZE}")
            time_label.classes("items-center")
            date_label = ui.label().style(f"font-size: {DATE_SIZE}")
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
                routines_button = ui.button().style(BUTTON_STYLE)
                with routines_button:
                    SVG(ABS_ROUTINE_SVG_PATH, ROUTINES_SVG_SIZE, color="white")
                ui.label(APP_NAME).style(f"font-size: {APP_NAME_SIZE}")
            with right_content:
                HeaderClock()
                programs_button = ui.button().style(BUTTON_STYLE)
                with programs_button:
                    SVG(ABS_PROGRAM_SVG_PATH, PROGRAMS_SVG_SIZE, color="white")

        routines_button.on("click", lambda: ui.open("/configure_routines"))
