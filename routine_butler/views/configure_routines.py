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

    content = ui.column().classes("justify-center items-center self-center")
    with content.classes("w-4/5 gap-y-4"):
        routines_frame = ui.column().classes("w-full")
        with routines_frame.classes("justify-center items-center gap-y-4"):
            for routine in state.user.get_routines(state.engine):
                RoutineConfigurer(
                    routine=routine, parent_element=routines_frame
                )

        add_routine_button = micro.add_button().classes("w-40 self-center")
        add_routine_button.on("click", handle_add_routine)
