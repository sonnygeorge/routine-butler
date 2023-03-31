from nicegui import ui

from utils.constants import clrs
from database.models import User

BUTTON_STYLE = f"background-color: {clrs.dark_green} !important;"
DRAWER_WIDTH = "400"
DRAWER_BREAKPOINT = "0"


class Time:
    time = "03:10"


class ScheduleSetter(ui.row):
    def __init__(self, schedule):
        self.schedule = schedule

        super().__init__()
        self.classes("justify-between items-center")

        with self:
            self.input = (
                ui.input("hours").props("filled").bind_value(Time, "time")
            )
            with self.input as input:
                with input.add_slot("append"):
                    with ui.icon("access_time").classes("cursor-pointer"):
                        with ui.element("q-popup-proxy").props(
                            'cover transition-show="scale" transition-hide="scale"'
                        ):
                            ui.time().bind_value(Time, "time")

            self.trash_button = ui.button().props("icon=cancel")
            self.trash_button.style(BUTTON_STYLE)


class SchedulesConfigurer(ui.expansion):
    def __init__(self, routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")
        self.classes("justify-between items-center")

        with self:
            for schedule in self.routine.schedules:
                ScheduleSetter(schedule)


class RoutineItemsConfigurer(ui.expansion):
    def __init__(self, routine):
        self.routine = routine

        super().__init__("Schedules", icon="schedule")
        self.classes("justify-between items-center")

        with self:
            pass


class TitleSetter(ui.row):
    def __init__(self, routine):
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
    def __init__(self, routine):
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
