from nicegui import ui

from routine_butler.elements.header import Header
from routine_butler.elements.routines_sidebar import RoutinesSidebar
from routine_butler.elements.programs_sidebar import ProgramsSidebar
from routine_butler.database.models import (
    User,
    Routine,
    Program,
    Alarm,
    RoutineItem,
)


TEST_PROGRAM = Program()
TEST_ROUTINE_ITEM = RoutineItem(program=TEST_PROGRAM)
TEST_ALARM = Alarm()
TEST_ROUTINE = Routine(alarms=[TEST_ALARM], routine_items=[TEST_ROUTINE_ITEM])
TEST_USER = User(routines=[TEST_ROUTINE])


class clrs:
    primary = "#2e5cb8"  # buttons
    secondary = "#5c85d6"  # header
    accent = "#2399cf"
    positive = "#23cf59"
    negative = "#cf2342"
    info = "#85d2ed"
    warning = "#d6dd54"


def set_colors():
    ui.colors(
        primary=clrs.primary,
        secondary=clrs.secondary,
        accent=clrs.accent,
        positive=clrs.positive,
        negative=clrs.negative,
        info=clrs.info,
        warning=clrs.warning,
    )


def build_ui():
    header = Header()
    routines_sidebar = RoutinesSidebar(user=TEST_USER)
    programs_sidebar = ProgramsSidebar(user=TEST_USER)

    header.routines_button.on("click", routines_sidebar.toggle)
    header.programs_button.on("click", programs_sidebar.toggle)


def main():
    set_colors()
    build_ui()
    ui.run()
