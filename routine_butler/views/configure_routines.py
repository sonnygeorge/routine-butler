from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.routine_configurer import RoutineConfigurer
from routine_butler.globals import PagePath
from routine_butler.models import Routine
from routine_butler.state import state
from routine_butler.utils.misc import initialize_page


@ui.page(path=PagePath.SET_ROUTINES)
def configure_routines():
    def hdl_add_routine():
        new_routine = Routine()
        new_routine.add_self_to_db(state.engine)
        state.user.add_routine(state.engine, new_routine)
        with routines_frame:
            RoutineConfigurer(
                routine=new_routine,
                parent_element=routines_frame,
            )

    initialize_page(page=PagePath.SET_ROUTINES, state=state)

    if state.user is None:
        return

    content = ui.column().classes("justify-center items-center self-center")
    with content.classes("w-4/5 gap-y-4"):
        routines_frame = ui.column().classes("w-full")
        with routines_frame.classes("justify-center items-center gap-y-4"):
            for routine in state.user.get_routines(state.engine):
                RoutineConfigurer(
                    routine=routine, parent_element=routines_frame
                )

        add_routine_button = micro.add_button().classes("w-40 self-center")
        add_routine_button.on("click", hdl_add_routine)
