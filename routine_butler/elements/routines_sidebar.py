import os
from typing import Callable, Optional, Union

from loguru import logger
from nicegui import ui

from routine_butler.database.models import (
    Program,
    Routine,
    RoutineItem,
    Alarm,
    SoundInterval,
    User,
)
from routine_butler.elements.svg import SVG
from routine_butler.utils.constants import clrs, icons

DRAWER_WIDTH = "490"
DRAWER_BREAKPOINT = "0"
ROUTINES_SVG_SIZE: int = 28
PROGRAMS_SVG_SIZE: int = 26

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")

V_SPACE = 4
DFLT_ROW_CLASSES = "justify-evenly items-center w-full px-4 pt-4"
DFLT_INPUT_PROPS = "standout dense"


# TODO:
# - make routine "delete" and "add" delete and add
# - build out RoutineItemsConfigurer
# - use icon constants
# - connect everything to the database


class SidebarExpansion(ui.expansion):
    def __init__(
        self,
        title: str,
        icon: Optional[Union[str, Callable]] = None,
        icon_kwargs: Optional[dict] = None,
    ):
        self.frame = ui.element("q-list").props("bordered")
        self.frame.classes("rounded-borders w-full")
        with self.frame:
            super().__init__("")
            self.classes("w-full")

            with self.add_slot("header"):
                with ui.row().classes("justify-start items-center w-full"):
                    if isinstance(icon, str):
                        ui.icon(icon).props("size=sm")
                    else:
                        icon(**icon_kwargs)
                    self.header_label = ui.label(title).classes("text-left")

            with self:
                ui.separator()


class AlarmSetter(ui.row):
    def __init__(self, alarm: Alarm, parent_element: ui.element):
        self.alarm = alarm
        self.parent_element = parent_element

        super().__init__()
        self.classes(DFLT_ROW_CLASSES + " no-wrap")

        with self:
            # time input
            time_input = ui.input(value="12:00").style("width: 90px;")
            time_input.props(DFLT_INPUT_PROPS)
            with time_input as input:
                with input.add_slot("append"):
                    icon = ui.icon("access_time").classes("cursor-pointer")
                    icon.on("click", lambda: menu.open())
                    with ui.menu() as menu:
                        time_setter = ui.time()
                        time_setter.bind_value(time_input)
                        time_setter.on(
                            "change",
                            lambda: self.on_time_change(time_input.value),
                        )

            # volume knob
            vol_knob = ui.knob(self.alarm.volume, track_color="grey-2")
            vol_knob.props("size=lg thickness=0.3")
            with vol_knob:
                ui.icon("volume_up").props("size=xs")
            vol_knob.on(
                "change", lambda: self.on_change_volume(vol_knob.value)
            )

            # sound interval select
            sound_interval_select = ui.select(
                [e.value for e in SoundInterval],
                value=self.alarm.sound_interval,
            ).props(DFLT_INPUT_PROPS, remove="label")
            sound_interval_select.classes("w-1/4").style("width: 120px;")
            sound_interval_select.on(
                "change",
                lambda: self.on_select_sound_interval(
                    sound_interval_select.value
                ),
            )

            # toggle switch
            switch = ui.switch().props("dense")
            switch.on("click", lambda: self.on_toggle(switch.value))

            # delete button
            self.delete_button = ui.button().classes("w-9")
            self.delete_button.props("icon=cancel color=negative")
            self.delete_button.on("click", self.on_delete)

    def on_time_change(self, new_time):
        self.alarm.set_time(new_time)
        logger.debug(f"Alarm {self.alarm.id} time changed to {new_time}")

    def on_change_volume(self, new_volume):
        self.alarm.volume = new_volume
        logger.debug(
            f"Alarm {self.alarm.id} volume changed to " f"{new_volume}"
        )

    def on_select_sound_interval(self, new_interval):
        self.alarm.sound_interval = new_interval
        logger.debug(
            f"Alarm {self.alarm.id} sound interval changed to {new_interval}"
        )

    def on_toggle(self, value: bool):
        self.alarm.enabled = value
        logger.debug(f"Alarm {self.alarm.id} enabled changed to {value}")

    def on_delete(self):
        logger.debug(f"Deleting alarm {self.alarm.id}")
        self.parent_element.remove(self)
        self.parent_element.update()
        del self


class AlarmsConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Alarms", icon="alarm")

        with self:
            self.alarms_frame = ui.element("div")
            with self.alarms_frame:
                for alarm in self.routine.alarms:
                    AlarmSetter(alarm=alarm, parent_element=self.alarms_frame)
            # add alarm button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_alarm_button = ui.button().props("icon=add")
                self.add_alarm_button.classes("w-full")
                self.add_alarm_button.on("click", self.on_add_alarm)

    def on_add_alarm(self):
        logger.debug("Adding alarm")
        alarm = Alarm()
        self.routine.alarms.append(alarm)
        with self.alarms_frame:
            AlarmSetter(alarm, parent_element=self.alarms_frame)


class RoutineItemsConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Alarms", icon="alarm")
        self.classes("justify-between items-center")

        with self:
            pass


class RoutineConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine, parent_element: ui.element):
        self.routine = routine
        self.parent_element = parent_element

        svg_kwargs = {
            "fpath": ROUTINE_SVG_FPATH,
            "size": ROUTINES_SVG_SIZE,
            "color": "black",
        }
        super().__init__(routine.title, icon=SVG, icon_kwargs=svg_kwargs)
        self.frame.classes(f"mt-{V_SPACE}")

        with self:
            # top row for setting title
            with ui.row().classes(DFLT_ROW_CLASSES):
                ui.label("Title:")
                # title input
                self.title_input = ui.input(
                    value=self.routine.title,
                ).props(DFLT_INPUT_PROPS)
                # save button
                title_save_button = ui.button().props("icon=save")
                title_save_button.classes("w-1/5")
                title_save_button.on(
                    "click",
                    lambda: self.on_title_update(self.title_input.value),
                )

            # alarms configurer
            with ui.row().classes(DFLT_ROW_CLASSES):
                AlarmsConfigurer(self.routine)

            # row for target duration input
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
                ui.label("Target Duration:").style("width: 120px;")
                # target duration slider
                target_duration_slider = ui.slider(
                    min=0, max=120, value=self.routine.target_duration
                ).classes("w-1/3")
                target_duration_slider.on(
                    "change",
                    lambda: self.on_target_duration_change(
                        target_duration_slider.value
                    ),
                )
                # target duration label
                target_duration_label = ui.label().style("width: 35px;")
                target_duration_label.bind_text_from(
                    target_duration_slider, "value"
                )
                target_duration_label.set_text(
                    str(self.routine.target_duration)
                )
                ui.label("minutes").style("width: 52px;").classes("text-left")
                # target duration enabled toggle
                target_duration_toggle = ui.switch().props("dense")
                target_duration_toggle.on(
                    "click",
                    lambda: self.on_toggle_target_duration(
                        target_duration_toggle.value
                    ),
                )

            ui.separator()

            # bottom buttons
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # start routine
                self.start_button = ui.button().classes("w-3/4")
                self.start_button.props("icon=play_arrow color=positive")
                # delete routine
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props("icon=cancel color=negative")
                self.delete_button.on("click", self.on_delete)

    def on_title_update(self, new_title):
        logger.debug(
            f'Updating title of routine {self.routine.id} to "{new_title}"'
        )
        self.header_label.set_text(new_title)

    def on_target_duration_change(self, new_duration):
        self.routine.target_duration = new_duration
        logger.debug(
            f"Target duration of routine {self.routine.id} changed to {new_duration}"
        )

    def on_toggle_target_duration(self, value: bool):
        self.routine.target_duration_enabled = value
        logger.debug(
            f"Target duration enabled of routine {self.routine.id} changed to {value}"
        )

    def on_delete(self):
        logger.debug(f"Deleting routine {self.routine.id}")
        self.parent_element.remove(self.frame)
        self.parent_element.update()
        del self


class RoutinesSidebar(ui.left_drawer):
    def __init__(self, user: User):
        self.user = user

        super().__init__()
        self.classes(f"space-y-{V_SPACE} text-center py-0")
        self.props(
            f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered"
        )

        with self:
            self.routines_frame = ui.element("div")
            with self.routines_frame:
                for routine in self.user.routines:
                    RoutineConfigurer(routine, self.routines_frame)

            ui.separator()

            # add routine button
            add_routine_button = ui.button().classes("w-1/2").props("icon=add")
            add_routine_button.on("click", self.add_routine)

    def add_routine(self):
        routine = Routine()
        self.user.routines.append(routine)
        with self.routines_frame:
            RoutineConfigurer(routine, parent_element=self.routines_frame)
