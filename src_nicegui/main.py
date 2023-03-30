from elements.header import Header
from nicegui import ui


def build_ui():
    Header()


build_ui()
ui.run()


# from datetime import datetime
# from loguru import logger

# # models.py


# class Schedule:
#     def __init__(self, hour: int, minute: int, is_on: bool):
#         self.hour = hour
#         self.minute = minute
#         self.is_on = is_on

#     def get_time(self) -> str:
#         # return time as a string in the format "HH:MM"
#         return f"{self.hour:02d}:{self.minute:02d}"

#     def set_time(self, time: str):
#         # set time from a string in the format "HH:MM"
#         self.hour, self.minute = map(int, time.split(":"))


# class Routine:
#     def __init__(self, title: str, schedules):
#         self.title = title
#         self.schedules = schedules


# class DatabaseWrapper:
#     def add(self, obj):
#         logger.debug(f"Adding {obj} to database")

#     def delete(self, obj):
#         logger.debug(f"Deleting {obj} from database")

#     def update(self, obj):
#         logger.debug(f"Updating {obj} in database")


# # database.py

# database = DatabaseWrapper()

# # components.py


# def add_header_to_ui(ui):
#     with ui.header().style(
#         "box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); padding: .5rem 1rem;"
#     ):
#         with ui.row().style("width: 50%; align-items: center"):
#             # logo and app name
#             ui.icon("token").classes("text-[50px]")
#             ui.label().style("font-size: 2rem").set_text("RoutineBox")

#         with ui.row():
#             # date and time
#             date = ui.label().style("font-size: 2rem")
#             time = ui.label().style("font-size: 2rem")
#             set_date = lambda: date.set_text(
#                 datetime.now().strftime("%d/%m/%Y")
#             )
#             set_time = lambda: time.set_text(
#                 datetime.now().strftime("%H:%M:%S")
#             )
#             ui.timer(1.0, set_date)
#             ui.timer(0.1, set_time)


# class ScheduleSetter:
#     def __init__(self, schedule, parent_element):
#         self.schedule = schedule
#         self.parent_element = parent_element
#         self.element = None

#     def add_to_ui(self, ui):
#         self.element = ui.row()
#         with self.element:

#             ui.time(
#                 value=self.schedule.get_time(),
#                 on_change=self.update_schedule_time,
#             )

#             ui.switch(
#                 value=self.schedule.is_on,
#                 on_change=self.update_schedule_is_on,
#             )

#             ui.icon("delete").on("click", self.delete_schedule)

#     def update_schedule_time(self, e):
#         self.schedule.set_time(e.value)
#         database.update(self.schedule)

#     def update_schedule_is_on(self, e):
#         self.schedule.is_on = e.value
#         database.update(self.schedule)

#     def delete_schedule(self):
#         if self.element is not None:
#             self.parent_element.remove(self.element)
#             database.delete(self.schedule)
#             del self


# class ScheduleSettersExpansion:
#     def __init__(self, routine: Routine):
#         self.routine = routine
#         self.expansion = None

#     def add_to_ui(self, ui):
#         self.expansion = ui.expansion("Scheduled Times", icon="schedule")
#         with self.expansion:

#             for schedule in self.routine.schedules:
#                 ScheduleSetter(
#                     schedule, parent_element=self.expansion
#                 ).add_to_ui(ui)

#             ui.icon("add").on("click", self.add_schedule)

#     def add_schedule(self):
#         new_schedule = Schedule(0, 0, False)
#         database.add(new_schedule)

#         with self.expansion:
#             ScheduleSetter(
#                 new_schedule, parent_element=self.expansion
#             ).add_to_ui(ui)


# class RoutineConfigSetter:
#     def __init__(self, routine: Routine, parent_element):
#         self.routine = routine

#     def add_to_ui(self, ui):
#         expansion = ui.expansion(self.routine.title, icon="settings")
#         with expansion:
#             with ui.row():

#                 title_input = ui.input(
#                     label="Set title...",
#                     value=self.routine.title,
#                 )

#                 ui.icon("save").on(
#                     "click",
#                     lambda: self.on_title_update(title_input.value, expansion),
#                 )

#             ScheduleSettersExpansion(self.routine).add_to_ui(ui)

#             ui.icon("delete").on("click", self.delete)

#     def on_title_update(self, new_title, expansion):
#         expansion._props["label"] = new_title
#         expansion.update()

#     def delete(self):
#         self.parent_element.remove(self)
#         database.delete(self.routine)
#         del self


# class RoutineConfigSettersExpansion:
#     def __init__(self, routines):
#         self.routines = routines
#         self.expansion = None

#     def add_to_ui(self, ui):
#         self.expansion = ui.expansion("My Routines", icon="settings")
#         self.expansion.style("width: 100%;border: 1px solid #ccc;")
#         self.expansion.classes("rounded-md, bg-gray-100")
#         with self.expansion:

#             for routine in self.routines:
#                 card = ui.card()
#                 with card:
#                     RoutineConfigSetter(
#                         routine, parent_element=card
#                     ).add_to_ui(ui)

#             ui.icon("add").on("click", self.add_routine)

#     def add_routine(self):
#         new_routine = Routine("New Routine", [])
#         database.add(new_routine)

#         with self.expansion:
#             RoutineConfigSetter(
#                 new_routine, parent_element=self.expansion
#             ).add_to_ui(ui)


# # main.py

# from nicegui import ui

# # TEMP: dummy data
# ROUTINES = [
#     Routine(
#         title="Routine 1",
#         schedules=[Schedule(9, 0, True), Schedule(10, 30, False)],
#     ),
#     Routine(title="Routine 2", schedules=[Schedule(8, 0, True)]),
# ]


# def main():
#     add_header_to_ui(ui)
#     RoutineConfigSettersExpansion(ROUTINES).add_to_ui(ui)

#     ui.run()


# main()
