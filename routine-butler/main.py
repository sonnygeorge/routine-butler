from nicegui import ui

from elements.header import Header
from elements.routines_sidebar import RoutinesSidebar
from elements.programs_sidebar import ProgramsSidebar
from database.models import User, Routine, Program, Schedule, RoutineItem


TEST_PROGRAM = Program()
TEST_ROUTINE_ITEM = RoutineItem(program=TEST_PROGRAM)
TEST_SCHEDULE = Schedule()
TEST_ROUTINE = Routine(
    schedules=[TEST_SCHEDULE], routine_items=[TEST_ROUTINE_ITEM]
)
TEST_USER = User(routines=[TEST_ROUTINE])


def build_ui():
    header = Header()
    routines_sidebar = RoutinesSidebar(user=TEST_USER)
    programs_sidebar = ProgramsSidebar(user=TEST_USER)

    header.routines_button.on("click", routines_sidebar.toggle)
    header.programs_button.on("click", programs_sidebar.toggle)


def main():
    build_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
