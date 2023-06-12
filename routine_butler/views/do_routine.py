from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.components.routine_administrator import (
    RoutineAdministrator,
)
from routine_butler.constants import PagePath
from routine_butler.state import state
from routine_butler.utils import (
    apply_color_theme,
    redirect_if_user_is_none,
    redirect_to_page,
)


@ui.page(path=PagePath.DO_ROUTINE)
def routine_run():
    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header(hide_buttons=True)

    if state.pending_routine_to_run is None:
        ui.label("No routine to run... returning to home page")
        redirect_to_page(PagePath.HOME, n_seconds_before_redirect=2.5)
    else:
        RoutineAdministrator(routine=state.pending_routine_to_run)
