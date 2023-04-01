import os
from typing import Optional, Callable, Union

from nicegui import ui
from loguru import logger

from utils.constants import clrs
from database.models import User, Routine, Program, Schedule, RoutineItem

from elements.svg import SVG

DRAWER_WIDTH = "430"
DRAWER_BREAKPOINT = "0"
ROUTINES_SVG_SIZE: int = 28
PROGRAMS_SVG_SIZE: int = 26

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")


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
        with ui.element("q-list").props("bordered").classes(
            "rounded-borders w-full"
        ):
            super().__init__("")
            self.classes("w-full")

            with self.add_slot("header"):
                with ui.row().classes("justify-start items-center w-full"):
                    if isinstance(icon, str):
                        ui.icon(icon).props("size=sm")
                    else:
                        icon(**icon_kwargs)
                    self.label = ui.label(title).classes("text-left")

            with self:
                ui.separator()


class SidebarRow(ui.row):
    def __init__(self):
        super().__init__()
        self.classes("justify-between items-center w-full px-4 pb-4")


class ScheduleSetter(SidebarRow):
    def __init__(self, schedule: Schedule, parent_element: ui.element):
        self.schedule = schedule
        self.parent_element = parent_element

        super().__init__()

        with self:
            # time input
            self.time = ui.input(label="Time", value="12:00")
            with self.time as input:
                with input.add_slot("append"):
                    icon = ui.icon("access_time").classes("cursor-pointer")
                    icon.on("click", lambda: menu.open())
                    with ui.menu() as menu:
                        time_setter = ui.time()
                        time_setter.bind_value(self.time)
            self.time.on(
                "change", lambda: self.on_time_change(self.time.value)
            )

            # toggle switch
            switch = ui.switch()
            switch.on("change", lambda: self.on_toggle(switch.value))

            # delete button
            self.delete_button = ui.button()
            self.delete_button.props("icon=cancel color=negative")
            self.delete_button.on("click", self.on_delete)

    def on_toggle(self, value: bool):
        self.schedule.enabled = value
        logger.debug(f"Schedule {self.schedule.id} enabled changed to {value}")

    def on_time_change(self, new_time):
        self.schedule.set_time(new_time)
        logger.debug(f"Schedule {self.schedule.id} time changed to {new_time}")

    def on_delete(self):
        logger.debug(f"Deleting schedule {self.schedule.id}")
        self.parent_element.remove(self)
        self.parent_element.update()
        del self


class SchedulesConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")

        with self:
            self.schedules_frame = ui.element("div")
            with self.schedules_frame:
                for schedule in self.routine.schedules:
                    ScheduleSetter(
                        schedule=schedule, parent_element=self.schedules_frame
                    )

            with SidebarRow():
                self.add_schedule_button = ui.button().props("icon=add")
                self.add_schedule_button.classes("w-full")
                self.add_schedule_button.on("click", self.on_add_schedule)

    def on_add_schedule(self):
        schedule = Schedule()
        self.routine.schedules.append(schedule)
        with self.schedules_frame:
            ScheduleSetter(schedule, parent_element=self.schedules_frame)


class RoutineItemsConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")
        self.classes("justify-between items-center")

        with self:
            pass


class TitleSetter(SidebarRow):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__()
        self.classes("px-4")

        with self:
            self.input = ui.input(
                label="Set title...",
                value=self.routine.title,
            )
            self.button = ui.button().props("icon=save")


class RoutineConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        svg_kwargs = {
            "fpath": ROUTINE_SVG_FPATH,
            "size": ROUTINES_SVG_SIZE,
            "color": "black",
        }
        super().__init__(routine.title, icon=SVG, icon_kwargs=svg_kwargs)

        with self:
            # title setter
            title_setter = TitleSetter(routine)
            title_setter.button.on(
                "click", lambda: self.on_title_update(title_setter.input.value)
            )
            # schedules configurer
            with SidebarRow():
                SchedulesConfigurer(self.routine)

            # buttons
            with SidebarRow():
                # start routine
                self.start_button = ui.button().classes("w-3/4")
                self.start_button.props("icon=play_arrow color=positive")
                # delete routine
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props("icon=cancel color=negative")

    def on_title_update(self, new_title):
        self.label.set_text(new_title)


class RoutinesSidebar(ui.left_drawer):
    def __init__(self, user: User):
        self.user = user

        super().__init__()
        self.classes("space-y-4 text-center")
        self.props(
            f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered"
        )

        with self:
            self.routines_frame = ui.element("div")
            with self.routines_frame:
                for routine in self.user.routines:
                    RoutineConfigurer(routine)

            ui.separator().classes("space-y-4")

            # add routine button
            add_routine_button = ui.button().classes("w-1/2").props("icon=add")
            add_routine_button.on("click", self.add_routine)

    def add_routine(self):
        with self.routines_frame:
            pass
