from datetime import datetime
from typing import Optional

from loguru import logger
from nicegui import ui

from routine_butler.components import micro
from routine_butler.globals import (
    G_SUITE_CREDENTIALS_MANAGER,
    ICON_STRS,
    PagePath,
)

APP_NAME = "RoutineButler"
APP_NAME_SIZE = "1.7rem"
TEXT_BLOCK_WIDTH = "width: 4.5rem;"
ICON_BLOCK_WIDTH = "width: 2.7rem;"
APP_LOGO_SVG_SIZE: float = 22.0
RTN_SVG_SIZE: float = 27.0
PRGRM_SVG_SIZE: float = 20.75
LARGE_TEXT_SIZE = "1.1rem"
SMALL_TEXT_SIZE = ".6rem"


def header_button(*args, **kwargs) -> ui.button:
    return ui.button(*args, **kwargs).props("flat").style(ICON_BLOCK_WIDTH)


def header_clock():
    def update_time_and_date_labels():
        time_label.set_text(datetime.now().strftime("%H:%M:%S"))
        date_label.set_text(datetime.now().strftime("%b %d, %Y"))

    column = ui.column().style(TEXT_BLOCK_WIDTH)
    with column.classes("-space-y-1 gap-0 items-center"):
        time_label = ui.label().classes("items-center")
        time_label.style(f"font-size: {LARGE_TEXT_SIZE}")
        date_label = ui.label().classes("items-center")
        date_label.style(f"font-size: {SMALL_TEXT_SIZE}")
        ui.timer(0.1, update_time_and_date_labels)


class NextAlarmDisplay:
    DEFAULT_ALARM_STR = "─:─"

    def __init__(self, alarm_str: Optional[str] = None):
        alarm_str = alarm_str or self.DEFAULT_ALARM_STR
        column = ui.column().style(TEXT_BLOCK_WIDTH)
        with column.classes("-space-y-1 gap-0 items-center"):
            self.time_label = ui.label(alarm_str)
            self.time_label.style(f"font-size: {LARGE_TEXT_SIZE}")
            ui.label("Next Alarm").style(f"font-size: {SMALL_TEXT_SIZE}")

    def update(self, alarm_str: Optional[str] = None):
        alarm_str = alarm_str or self.DEFAULT_ALARM_STR
        self.time_label.set_text(alarm_str)


class Header(ui.header):
    def __init__(self, hide_navigation_buttons=False, is_dark_mode=False):
        super().__init__()
        self.classes("justify-between items-center bg-primary shadow-lg py-3")

        self._is_dark_mode = is_dark_mode
        dark_mode = ui.dark_mode()
        if self._is_dark_mode:
            dark_mode.enable()

        with self:
            left_row = ui.row().style("align-items: center").classes("pl-3")
            right_row = ui.row().style("align-items: center").classes("pr-3")

            with left_row:
                # app logo / home button
                micro.vertical_separator()
                home_button = header_button()
                with home_button:
                    micro.app_logo_svg(APP_LOGO_SVG_SIZE, color="white")
                # app name
                micro.vertical_separator()
                ui.label(APP_NAME).style(f"font-size: {APP_NAME_SIZE}")
                micro.vertical_separator()

            if not hide_navigation_buttons:
                with right_row:
                    micro.vertical_separator()
                    # configure-routines nav button
                    routine_button = header_button()
                    with routine_button:
                        micro.routine_svg(RTN_SVG_SIZE, color="white")
                    micro.vertical_separator()
                    # configure-programs nav button
                    program_button = header_button()
                    with program_button:
                        micro.program_svg(PRGRM_SVG_SIZE, color="white")

            with right_row:
                micro.vertical_separator()
                # dark mode button
                dark_button = header_button(
                    icon=ICON_STRS.dark_mode, on_click=dark_mode.enable
                ).props("text-color=white")
                dark_button.on("click", lambda: self.set_dark_mode(True))
                micro.vertical_separator()
                # light mode button
                light_button = header_button(
                    icon=ICON_STRS.light_mode, on_click=dark_mode.disable
                ).props("text-color=white")
                light_button.on("click", lambda: self.set_dark_mode(False))
                micro.vertical_separator()
                # g suite button
                header_button(
                    icon=ICON_STRS.g_suite,
                    on_click=self._hdl_g_suite_button_click,
                ).props("text-color=white")
                micro.vertical_separator()
                # next alarm display
                self.next_alarm_display = NextAlarmDisplay()
                micro.vertical_separator()
                # clock
                header_clock()
                micro.vertical_separator()

        if not hide_navigation_buttons:  # add handlers for nav buttons
            home_button.on("click", lambda: ui.open(PagePath.HOME))
            routine_button.on("click", lambda: ui.open(PagePath.SET_ROUTINES))
            program_button.on("click", lambda: ui.open(PagePath.SET_PROGRAMS))

    def set_dark_mode(self, is_dark_mode: bool):
        self._is_dark_mode = is_dark_mode

    async def _hdl_g_suite_button_click(self):
        logger.info("Manually asserting G Suite credentials...")
        await G_SUITE_CREDENTIALS_MANAGER.get_credentials()
        ui.notify("G Suite access is valid!")
