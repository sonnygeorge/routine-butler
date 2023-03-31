from nicegui import ui

from elements.header import Header
from elements.routines_sidebar import RoutinesSidebar
from elements.programs_sidebar import ProgramsSidebar


class Time:
    time = "03:10"


def build_ui():
    header = Header()
    routines_sidebar = RoutinesSidebar()
    programs_sidebar = ProgramsSidebar()

    header.routines_button.on("click", routines_sidebar.toggle)
    header.programs_button.on("click", programs_sidebar.toggle)

    with ui.input("hours").props("filled").bind_value(Time, "time") as hours:
        with hours.add_slot("append"):
            with ui.icon("access_time").classes("cursor-pointer"):
                with ui.element("q-popup-proxy").props(
                    'cover transition-show="scale" transition-hide="scale"'
                ):
                    ui.time().bind_value(Time, "time")


def main():
    build_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
