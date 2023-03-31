from nicegui import ui
from loguru import logger

from utils.constants import clrs
from database.models import User, Routine, Program, Schedule, RoutineItem

BUTTON_STYLE = f"background-color: {clrs.dark_green} !important;"
DRAWER_WIDTH = "400"
DRAWER_BREAKPOINT = "0"


class ScheduleSetter(ui.row):
    def __init__(self, schedule: Schedule, parent_element: ui.element):
        self.schedule = schedule
        self.parent_element = parent_element

        super().__init__()
        self.classes("justify-between items-center")

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
            self.delete_button = ui.button().props("icon=cancel")
            self.delete_button.style(BUTTON_STYLE)
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
        del self


class SchedulesConfigurer(ui.expansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")
        self.classes("justify-between items-center")

        with self:
            for schedule in self.routine.schedules:
                ScheduleSetter(schedule, parent_element=self)

            self.add_schedule_button = ui.button("Add Schedule")
            self.add_schedule_button.on("click", self.on_add_schedule)

    def on_add_schedule(self):
        schedule = Schedule()
        self.routine.schedules.append(schedule)
        with self:
            ScheduleSetter(schedule, parent_element=self)


class RoutineItemsConfigurer(ui.expansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")
        self.classes("justify-between items-center")

        with self:
            pass


class TitleSetter(ui.row):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__()
        self.classes("justify-between items-center")

        with self:
            self.input = ui.input(
                label="Set title...",
                value=self.routine.title,
            )
            self.button = ui.button().props("icon=save")
            self.button.style(BUTTON_STYLE)


class RoutineConfigurer(ui.expansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__(routine.title, icon="settings")

        with self:
            # title setter
            title_setter = TitleSetter(routine)
            title_setter.button.on(
                "click", lambda: self.on_title_update(title_setter.input.value)
            )
            # schedules configurer
            SchedulesConfigurer(self.routine)

    def on_title_update(self, new_title):
        self._props["label"] = new_title
        self.update()


class RoutinesSidebar(ui.left_drawer):
    def __init__(self, user: User):
        self.user = user

        super().__init__()
        self.classes("space-y-4 text-center")
        self.props(f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH}")
        self.style(f"background-color: {clrs.beige}")

        with self:
            self.routines_frame = ui.element("div")
            with self.routines_frame:
                for routine in self.user.routines:
                    RoutineConfigurer(routine)

            ui.separator()
            # add routine button
            add_routine_button = ui.button("Add Routine")
            add_routine_button.on("click", self.add_routine)
            style = BUTTON_STYLE
            add_routine_button.style(style)

    def add_routine(self):
        with self.routines_frame:
            pass
