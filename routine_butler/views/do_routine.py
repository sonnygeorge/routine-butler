from nicegui import ui

from routine_butler.components.routine_administrator import (
    RoutineAdministrator,
)
from routine_butler.globals import PagePath
from routine_butler.state import state
from routine_butler.utils.misc import initialize_page, redirect_to_page


@ui.page(path=PagePath.DO_ROUTINE)
def do_routine():
    initialize_page(page=PagePath.DO_ROUTINE, state=state)

    if state.current_routine is None:
        ui.label("No routine to run...").classes("absolute-center")
        redirect_to_page(PagePath.HOME, n_seconds_before_redirect=2.5)
    else:
        RoutineAdministrator(routine=state.current_routine)
