from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.routine import Routine
from routine_butler.models.user import User
from routine_butler.ui.constants import ICON_STRS
from routine_butler.ui.constants import RTNS_SDBR_WIDTH as DRAWER_WIDTH
from routine_butler.ui.constants import SDBR_BREAKPOINT as BREAKPOINT
from routine_butler.ui.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.ui.routines_sidebar.routine_configurer import (
    RoutineConfigurer,
)


def routines_sidebar(engine: Engine, user: User):
    drawer = ui.left_drawer()
    drawer.classes(f"space-y-{V_SPACE} text-center py-0")
    drawer.props(f"breakpoint={BREAKPOINT} width={DRAWER_WIDTH} bordered")

    def handle_add_routine():
        # create the routine in the db
        new_routine = Routine()
        new_routine.add_self_to_db(engine)
        user.add_routine(engine, new_routine)
        # add the routine configurer to the drawer
        with routines_frame:
            RoutineConfigurer(
                engine=engine,
                user=user,
                routine=new_routine,
                parent_element=routines_frame,
            )

    with drawer:
        routines_frame = ui.element("div")
        with routines_frame:
            for routine in user.get_routines(engine):
                RoutineConfigurer(
                    engine=engine,
                    user=user,
                    routine=routine,
                    parent_element=routines_frame,
                )
        # add routine button
        ui.separator()
        add_routine_button = ui.button().classes("w-1/2")
        add_routine_button.props(f"icon={ICON_STRS.add}").on(
            "click", handle_add_routine
        )
    return drawer
