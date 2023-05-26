from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.header import Header
from routine_butler.components.routine_configurer import RoutineConfigurer
from routine_butler.constants import RTNS_SDBR_WIDTH as DRAWER_WIDTH
from routine_butler.constants import SDBR, PagePath
from routine_butler.models.routine import Routine
from routine_butler.state import state
from routine_butler.utils import apply_color_theme, redirect_if_user_is_none


@ui.page(path=PagePath.SET_ROUTINES)
def configure_routines():
    def handle_add_routine():
        new_routine = Routine()
        new_routine.add_self_to_db(state.engine)
        state.user.add_routine(state.engine, new_routine)
        with routines_frame:
            RoutineConfigurer(
                routine=new_routine,
                parent_element=routines_frame,
            )

    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header()

    drawer = ui.left_drawer(value=True)
    drawer.classes(f"space-y-{SDBR.V_SPACE} text-center py-0")
    drawer.props(f"breakpoint={SDBR.BREAKPOINT} width={DRAWER_WIDTH} bordered")

    with drawer:
        routines_frame = ui.element("div")
        with routines_frame:
            for routine in state.user.get_routines(state.engine):
                RoutineConfigurer(
                    routine=routine,
                    parent_element=routines_frame,
                )
        ui.separator()
        add_routine_button = micro.add_button().classes("w-1/2")
        add_routine_button.on("click", handle_add_routine)
