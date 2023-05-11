from nicegui import ui

from routine_butler.constants import ICON_STRS
from routine_butler.constants import RTNS_SDBR_WIDTH as DRAWER_WIDTH
from routine_butler.constants import SDBR_BREAKPOINT as BREAKPOINT
from routine_butler.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.models.routine import Routine
from routine_butler.state import state
from routine_butler.ui.header import Header
from routine_butler.ui.routines_sidebar.routine_configurer import (
    RoutineConfigurer,
)
from routine_butler.utils import apply_color_theme, redirect_if_not_logged_in


@ui.page(path="/configure_routines")
def configure_routines():
    def handle_add_routine():
        # create the routine in the db
        new_routine = Routine()
        new_routine.add_self_to_db(state.engine)
        state.user.add_routine(state.engine, new_routine)
        # add the routine configurer to the drawer
        with routines_frame:
            RoutineConfigurer(
                engine=state.engine,
                user=state.user,
                routine=new_routine,
                parent_element=routines_frame,
            )

    redirect_if_not_logged_in()
    apply_color_theme()
    Header()

    drawer = ui.left_drawer(value=True)
    drawer.classes(f"space-y-{V_SPACE} text-center py-0")
    drawer.props(f"breakpoint={BREAKPOINT} width={DRAWER_WIDTH} bordered")

    with drawer:
        routines_frame = ui.element("div")
        with routines_frame:
            for routine in state.user.get_routines(state.engine):
                RoutineConfigurer(
                    engine=state.engine,
                    user=state.user,
                    routine=routine,
                    parent_element=routines_frame,
                )
        # add routine button
        ui.separator()
        add_routine_button = ui.button().classes("w-1/2")
        add_routine_button.props(f"icon={ICON_STRS.add}").on(
            "click", handle_add_routine
        )
