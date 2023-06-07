from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.header import Header
from routine_butler.components.routine_configurer import RoutineConfigurer

from routine_butler.constants import PagePath

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


    with ui.card().classes(
        "absolute-center container flex items-stretch"
    ).style("top: 1rem").style("transform: translate(-50%,0%)"):

        routines_frame = ui.element("div")
        with routines_frame:
            for routine in state.user.get_routines(state.engine):
                RoutineConfigurer(
                    routine=routine,
                    parent_element=routines_frame,
                )
        ui.separator()
        add_routine_button = micro.add_button().classes("w-1/2 self-center")
        add_routine_button.on("click", handle_add_routine)
